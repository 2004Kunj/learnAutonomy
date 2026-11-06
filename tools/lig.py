"""Append Z-Anatomy ligaments (and joint capsules, menisci, labra) to the live BodyParts3D packs (standard + HD)."""
import numpy as np, json, gzip, base64, pickle, os, re, sys, collections
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from zconvert import simplify, weld, loop, z2b
BK = os.path.join(ROOT, 'bp3d_backup'); Z = os.path.join(ROOT, 'zsrc'); OUT = os.path.join(ROOT, 'lig_out')
os.makedirs(OUT + '/std', exist_ok=True); os.makedirs(OUT + '/hd', exist_ok=True)

def unpack(blob, M):
    P = np.frombuffer(blob, np.uint16, M['nv'] * 3).reshape(-1, 3)
    off = M['posBytes'] + (2 if M['posBytes'] % 4 else 0); I = np.frombuffer(blob, np.uint16, M['ni'], off)
    return P, I
ZB = os.environ.get('ZBASE')   # build on the Z-Anatomy packs instead of BodyParts3D
if ZB:
    SB = os.path.join(ROOT, 'zbase'); HB = os.path.join(ROOT, 'zbase_hd'); OUT = os.path.join(ROOT, 'zlig_out')
    os.makedirs(OUT + '/std', exist_ok=True); os.makedirs(OUT + '/hd', exist_ok=True)
else: SB = HB = BK
M = json.load(open(os.path.join(SB, 'manifest.json')))
sraw = gzip.decompress(base64.b64decode(open(os.path.join(SB, 'anatomy.txt'), 'rb').read()))
SP, SI = unpack(sraw, M)
if ZB:
    H = json.load(open(os.path.join(HB, 'manifest.json'))); hraw = gzip.decompress(base64.b64decode(open(os.path.join(HB, 'anatomy.txt'), 'rb').read()))
    H['meshes'] = [r[2:6] for r in H['meshes']]
else:
    H = json.load(open(os.path.join(BK, 'hd.json')))
    hraw = gzip.decompress(base64.b64decode(b''.join(open(os.path.join(BK, p), 'rb').read() for p in H['parts'])))
HP, HI = unpack(hraw, H)
lo, sc = np.array(M['lo']), np.array(M['sc'])
SPf = SP.astype(np.float32) * sc + lo

# local alignment: per matched structure, offset BP3D centroid - Z centroid (after global transform)
match = json.load(open(os.path.join(Z, 'match.json')))
d = pickle.load(open(os.path.join(Z, 'z.pkl'), 'rb')); ZO = {r['name']: r for r in d['objs'] if r['type'] == 'mesh'}
kind = {s['id']: s['kind'] for s in M['structures']}; region = {s['id']: s['region'] for s in M['structures']}
anchors = []; deltas = []
for mi, v in ([] if ZB else match.items()):
    m = M['meshes'][int(mi)]
    if kind[m[0]] not in ('bone', 'disc') or not v['best'] or v['best'][0][0] > 7: continue
    zn = v['best'][0][3]; zc = z2b(ZO[zn]['V'][np.unique(ZO[zn]['T'])]).mean(0)
    bc = SPf[m[2]:m[2] + m[3]].mean(0); anchors.append(bc); deltas.append(bc - zc)
if ZB: anchors, deltas = [[0, 0, 0]], [[0, 0, 0]]
anchors = np.array(anchors, float); deltas = np.array(deltas, float); atree = cKDTree(anchors)
print('alignment anchors', len(anchors), 'mean |delta|', np.linalg.norm(deltas, axis=1).mean().round(2))
# bone surface for region lookup
bone_pts = []; bone_reg = []
for m in M['meshes']:
    if kind[m[0]] == 'bone':
        V = SPf[m[2]:m[2] + m[3]][::7]; bone_pts.append(V); bone_reg += [m[0]] * len(V)
btree = cKDTree(np.concatenate(bone_pts)); bone_reg = np.array(bone_reg)

SKIP = re.compile(r'^(Intervertebral disc|Nucleus pulposus|Joints$|Infrapatellar fat pad|Triradiate cartilage|Frenula capsulae|Interosseous membrane of (forearm|leg)|Long plantar ligament)')
MARK = re.compile(r'\.(j|t|g|i|s)$')
EXTRA = {'Extensor retinaculum of wrist', 'Flexor retinaculum of ankle', 'Inferior extensor retinaculum of ankle', 'Superior extensor retinaculum of ankle', 'Inferior fibular retinaculum', 'Superior fibular retinaculum',
         'Medial patellar retinaculum', 'Lateral patellar retinaculum', 'Plantar aponeurosis', 'Palmar aponeurosis', 'Posterior layer of thoracolumbar fascia', 'Superficial transverse metacarpal ligament', 'Superficial transverse metatarsal ligament'}
objs = [r for r in d['objs'] if r['type'] == 'mesh' and ('3: Joints' in r['cols'] or re.sub(r'\.(l|r)$', '', r['name']) in EXTRA) and not MARK.search(r['name'])]
# patellar ligament: Z-Anatomy only has its two attachment patches, so wrap them in a hull
from scipy.spatial import ConvexHull
for sd in 'lr':
    pts = np.concatenate([ZO['Patellar ligament.e' + sd]['V'], ZO['Patellar ligament.o' + sd]['V']]).astype(np.float64)
    h = ConvexHull(pts); objs.append(dict(name='Patellar ligament.' + sd, V=pts.astype(np.float32), T=h.simplices.astype(np.int32), mods=[], cols=['Knee joint']))
objs = [r for r in objs if not SKIP.match(re.sub(r'\.(l|r)$', '', r['name'])) and not r['name'].startswith('(')]
print('ligament objects', len(objs))

def solidify(V, T, t):
    nv = len(V); fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    N = np.zeros_like(V); [np.add.at(N, T[:, j], fn) for j in range(3)]; N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    A = V + N * t / 2; B = V - N * t / 2
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); key = np.minimum(E[:, 0], E[:, 1]) * nv + np.maximum(E[:, 0], E[:, 1])
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True); bnd = E[cnt[inv] == 1]
    rim = np.concatenate([np.stack([bnd[:, 1], bnd[:, 0], bnd[:, 0] + nv], 1), np.stack([bnd[:, 1], bnd[:, 0] + nv, bnd[:, 1] + nv], 1)])
    return np.concatenate([A, B]), np.concatenate([T, T[:, ::-1] + nv, rim])

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
new = []   # (sid, k, name, side, region, Vstd, Istd, Vhd, Ihd, joint)
for r in objs:
    base = re.sub(r'\.(l|r)$', '', r['name']); side = {'l': 'L', 'r': 'R'}.get(r['name'][-1], '') if re.search(r'\.(l|r)$', r['name']) else ''
    V = z2b(r['V']); T = r['T'].astype(np.int64)
    used = np.unique(T); remap = -np.ones(len(V), np.int64); remap[used] = np.arange(len(used)); V = V[used]; T = remap[T]
    c = V.mean(0); dd, ii = atree.query(c, k=min(3, len(anchors))); dd, ii = np.atleast_1d(dd), np.atleast_1d(ii); w = 1 / (dd + 5); V = V + (deltas[ii] * w[:, None]).sum(0) / w.sum()
    V, T = weld(V, T, 0.05)
    if len(T) < 2: continue
    ext = np.ptp(V, 0); thin = 'Solidify' in r['mods'] or np.sort(ext)[0] < 0.8
    if 'Patellar ligament' in base:   # hull winding fix: orient faces outward
        fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]); out = ((V[T].mean(1) - V.mean(0)) * fn).sum(1) < 0; T[out] = T[out][:, ::-1]; thin = False
    if thin: V, T = solidify(V, T, 2.4 if len(T) <= 4 else 1.6 if 'capsule' not in base.lower() else 1.1)
    if len(T) < 40: V, T = loop(V, T)
    V1, T1 = loop(V, T)
    V2, T2 = loop(V1, T1) if len(T1) < 40000 else (V1, T1)
    if len(T1) < 900: V1, T1 = loop(V1, T1)
    a = simplify(V1, T1, 1200 if 'capsule' in base.lower() else 700)
    b = simplify(V2, T2, 4000 if 'capsule' in base.lower() else 2400)
    _, bi = btree.query(a[0].mean(0)); reg = region[bone_reg[bi]]
    joint = 'Knee joint' if 'patellar' in base.lower() else next((x for x in r['cols'] if re.search(r'joint|ligament|Arthrology|membrane|symphys', x, re.I) and x not in ('3: Joints',) and x != base), '')
    k = 'lig-' + slug(base); sid = k + ('-' + side if side else '')
    new.append(dict(sid=sid, k=k, name=base, side=side, region=reg, std=a, hd=b, joint=joint, nearbone=bone_reg[bi]))
# ---- ligaments Z-Anatomy lacks, modelled on this specimen's bones ----
from lig_proc import build
from lig_proc2 import build as build2
HPf = HP.astype(np.float32) * np.array(H['sc']) + np.array(H['lo'])
hrow = {}
for i, m in enumerate(M['meshes']): hrow[(m[0], m[1])] = H['meshes'][i]
zrow = {(e['sid'], ''): e for e in new}
def G(sid, part):
    if (sid, part) in hrow: r = hrow[(sid, part)]; return HPf[r[0]:r[0] + r[1]]
    rows = [hrow[k] for k in hrow if k[0] == sid]
    if rows and (sid, part) not in zrow: return np.concatenate([HPf[r[0]:r[0] + r[1]] for r in rows])
    return zrow[(sid, part)]['hd'][0]
for e in build(G) + build2(G):
    V, T = e['V'], e['T']; V1, T1 = loop(V, T); V2, T2 = loop(V1, T1)
    a = simplify(V1, T1, 500); b = simplify(V2, T2, 1600)
    k = 'lig-' + slug(e['name']); sid = k + ('-' + e['side'] if e['side'] else '')
    new.append(dict(sid=sid, k=k, name=e['name'], side=e['side'], region=e['region'], std=a, hd=b, joint=e['joint'], nearbone='', proc=True))
print('built', len(new), 'meshes;', len(set(n['k'] for n in new)), 'ligaments')

def write(outdir, meta, P, I, part, entries):
    pos = [P]; idx = [I]; vo = meta['nv']; io = meta['ni']; meshes = list(meta['meshes']); lo = np.array(meta['lo']); sc = np.array(meta['sc'])
    for e in entries:
        V, Ix = e[part]; q = np.clip(np.round((V - lo) / sc), 0, 65535).astype(np.uint16)
        pos.append(q); idx.append(Ix.astype(np.uint16))
        if part == 'std':
            cen = V.mean(0); X = V - cen; w, vec = np.linalg.eigh(X.T @ X)
            meshes.append([e['sid'], '', vo, len(V), io, len(Ix), [round(float(x), 1) for x in cen], [round(float(x), 3) for x in vec[:, -1]], [0, 0, 0]])
        else: meshes.append([vo, len(V), io, len(Ix)])
        vo += len(V); io += len(Ix)
    Pq = np.concatenate(pos).tobytes(); blob = Pq + (b'\0\0' if len(Pq) % 4 else b'') + np.concatenate(idx).tobytes()
    m2 = dict(meta, nv=int(vo), ni=int(io), posBytes=len(Pq), meshes=meshes); m2.pop('auxOff', None)
    open(os.path.join(outdir, 'anatomy.txt'), 'wb').write(base64.b64encode(gzip.compress(blob, 9)))
    json.dump(m2, open(os.path.join(outdir, 'manifest.json'), 'w'), separators=(',', ':'))
    return m2
structs = list(M['structures']); seen = set()
for e in new:
    if e['sid'] in seen: continue
    seen.add(e['sid']); structs.append({'id': e['sid'], 'k': e['k'], 'name': e['name'], 'kind': 'ligament', 'region': e['region'], 'side': e['side'], 'parts': []})
Ms = dict(M, structures=structs)
write(OUT + '/std', Ms, SP, SI, 'std', new)
# HD manifest needs structures too for aux.py
Hm = dict(H, structures=structs, meshes=[[m[0], m[1]] + list(h) for m, h in zip(M['meshes'], H['meshes'])])
# aux.py expects standard-style mesh rows: [sid, part, vo, vc, io, ic, ...]
Hm['meshes'] = [[M['meshes'][i][0], M['meshes'][i][1]] + list(H['meshes'][i]) for i in range(len(H['meshes']))]
# simpler: append manually with sid rows
def write_hd():
    pos = [HP]; idx = [HI]; vo = H['nv']; io = H['ni']; rows = [list(r) for r in Hm['meshes']]
    for e in new:
        V, Ix = e['hd']; q = np.clip(np.round((V - np.array(H['lo'])) / np.array(H['sc'])), 0, 65535).astype(np.uint16)
        pos.append(q); idx.append(Ix.astype(np.uint16)); rows.append([e['sid'], '', vo, len(V), io, len(Ix)]); vo += len(V); io += len(Ix)
    Pq = np.concatenate(pos).tobytes(); blob = Pq + (b'\0\0' if len(Pq) % 4 else b'') + np.concatenate(idx).tobytes()
    m2 = dict(lo=H['lo'], sc=H['sc'], nv=int(vo), ni=int(io), posBytes=len(Pq), meshes=rows, structures=structs)
    open(os.path.join(OUT, 'hd', 'anatomy.txt'), 'wb').write(base64.b64encode(gzip.compress(blob, 9)))
    json.dump(m2, open(os.path.join(OUT, 'hd', 'manifest.json'), 'w'), separators=(',', ':'))
write_hd()
json.dump([{k: e[k] for k in ('sid', 'k', 'name', 'side', 'region', 'joint', 'nearbone')} for e in new], open(os.path.join(OUT, 'ligs.json'), 'w'), indent=0)
print('std tris added', sum(len(e['std'][1]) // 3 for e in new), 'hd tris added', sum(len(e['hd'][1]) // 3 for e in new))
