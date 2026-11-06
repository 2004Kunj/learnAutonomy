import numpy as np, ctypes, json, gzip, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from spec import SPEC, BONES, DISCS, VESSELS

HERE = os.path.dirname(os.path.abspath(__file__))
STL = '/home/claude/kevin-mattheus-moerman/bodyparts3d/assets/BodyParts3D_data/stl/'
lib = ctypes.CDLL(os.path.join(HERE, 'libmeshopt.so'))
u32p = np.ctypeslib.ndpointer(np.uint32, flags='C')
f32p = np.ctypeslib.ndpointer(np.float32, flags='C')
lib.meshopt_simplify.restype = ctypes.c_size_t
lib.meshopt_simplify.argtypes = [u32p, u32p, ctypes.c_size_t, f32p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_float, ctypes.c_uint, ctypes.POINTER(ctypes.c_float)]
lib.meshopt_optimizeVertexCache.argtypes = [u32p, u32p, ctypes.c_size_t, ctypes.c_size_t]

names = {}
for l in open(os.path.join(HERE, '..', 'have.tsv')):
    f, n, s = l.rstrip('\n').split('\t'); names[n] = f

def load(fid):
    b = open(STL + fid + '.stl', 'rb').read()
    n = int(np.frombuffer(b, dtype='<u4', count=1, offset=80)[0])
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    return np.frombuffer(b, dtype=dt, count=n, offset=84)['v'].reshape(-1, 3)

def weld(tri):
    q = np.round(tri * 50).astype(np.int64)
    _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    V = tri[first].astype(np.float32)
    I = inv.astype(np.uint32).reshape(-1, 3)
    I = I[(I[:, 0] != I[:, 1]) & (I[:, 1] != I[:, 2]) & (I[:, 0] != I[:, 2])]
    return np.ascontiguousarray(V), np.ascontiguousarray(I.reshape(-1))

def simplify(V, I, target_tris):
    if len(I) // 3 <= target_tris: out = I
    else:
        dst = np.zeros_like(I); err = ctypes.c_float()
        n = lib.meshopt_simplify(dst, I, len(I), V, len(V), 12, target_tris * 3, 0.05, 0, ctypes.byref(err))
        out = dst[:n].copy()
    used, inv = np.unique(out, return_inverse=True)
    V2 = np.ascontiguousarray(V[used]); I2 = np.ascontiguousarray(inv.astype(np.uint32))
    I3 = np.zeros_like(I2); lib.meshopt_optimizeVertexCache(I3, I2, len(I2), len(V2))
    return V2, I3

def target(kind, ntri, key):
    if kind == 'muscle': return max(400, min(30000 if 'intercostal' in key else 16000, int(ntri * 0.4)))
    if kind == 'tendon': return max(300, min(8000, int(ntri * 0.4)))
    if kind == 'disc': return max(300, min(1500, int(ntri * 0.3)))
    if kind == 'organ': return 22000
    if kind in ('artery','vein'): return max(400, min(6000, int(ntri * 0.5)))
    big = key in ('frontal','parietal','temporal','occipital','sphenoid','hip-bone','femur','sacrum','scapula','mandible','maxilla','tibia','humerus')
    return max(300, min(14000 if big else 7000, int(ntri * 0.3)))

structures = []; meshes = []; missing = []
def add(key, name, kind, region, bilat, parts):
    for side in (['R', 'L'] if bilat else ['']):
        sid = key + ('-' + side if side else '')
        st = {'id': sid, 'k': key, 'name': name, 'kind': kind, 'region': region, 'side': side, 'parts': []}
        for label, pat in parts:
            nm = pat.replace('{s}', {'R': 'right', 'L': 'left', '': ''}[side]).strip()
            if nm not in names: missing.append(nm); continue
            tri = load(names[nm])
            V, I = weld(tri)
            V2, I2 = simplify(V, I, target(kind, len(I) // 3, key))
            st['parts'].append(len(meshes))
            meshes.append({'s': sid, 'p': label, 'V': V2, 'I': I2, 'fma': names[nm]})
        if st['parts']: structures.append(st)

for k, (n, kind, reg, bil, parts) in SPEC.items(): add(k, n, kind, reg, bil, parts)
for k, (n, reg, bil, parts) in BONES.items(): add(k, n, 'bone', reg, bil, parts)
add('discs', 'Intervertebral discs', 'disc', 'Vertebral column', 0, DISCS)
for k, (n, kind, reg, bil, parts) in VESSELS.items(): add(k, n, kind, reg, bil, parts)
print('missing:', missing)

allV = np.concatenate([m['V'] for m in meshes])
lo = allV.min(0) - 1; hi = allV.max(0) + 1; sc = (hi - lo) / 65535.0
pos = []; idx = []; man = []; voff = 0; ioff = 0
for m in meshes:
    q = np.round((m['V'] - lo) / sc).astype(np.uint16)
    V = m['V']; c = V.mean(0)
    # principal axis for fibre direction
    X = V - c; w, vec = np.linalg.eigh(X.T @ X); ax = vec[:, -1]
    assert len(V) < 65536
    pos.append(q); idx.append(m['I'].astype(np.uint16))
    man.append([m['s'], m['p'], voff, len(V), ioff, len(m['I']), [round(float(x), 1) for x in c], [round(float(x), 3) for x in ax]])
    voff += len(V); ioff += len(m['I'])
P = np.concatenate(pos); Ix = np.concatenate(idx)
blob = P.tobytes() + (b'\0\0' if len(P.tobytes()) % 4 else b'') + Ix.tobytes()
outdir = os.path.join(HERE, '..', 'hd'); os.makedirs(outdir, exist_ok=True)
with gzip.open(os.path.join(outdir, 'anatomy.bin.gz'), 'wb', compresslevel=9) as f: f.write(blob)
meta = {'lo': [float(x) for x in lo], 'sc': [float(x) for x in sc], 'nv': int(voff), 'ni': int(ioff), 'posBytes': len(P.tobytes()),
        'meshes': man, 'structures': [{k: v for k, v in s.items()} for s in structures]}
json.dump(meta, open(os.path.join(outdir, 'manifest.json'), 'w'), separators=(',', ':'))
print('meshes', len(meshes), 'structures', len(structures), 'verts', voff, 'tris', ioff // 3,
      'raw MB', round(len(blob) / 1e6, 2), 'gz MB', round(os.path.getsize(os.path.join(outdir, 'anatomy.bin.gz')) / 1e6, 2))
print('bbox', lo, hi)

import base64
open(os.path.join(outdir,'anatomy.txt'),'wb').write(base64.b64encode(open(os.path.join(outdir,'anatomy.bin.gz'),'rb').read()))
os.remove(os.path.join(outdir,'anatomy.bin.gz'))
print('txt MB',round(os.path.getsize(os.path.join(outdir,'anatomy.txt'))/1e6,2))
