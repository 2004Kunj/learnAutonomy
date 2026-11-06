"""Rebuild the standard + HD mesh packs from Z-Anatomy geometry (BodyParts3D kept only where Z-Anatomy has no match)."""
import numpy as np, json, gzip, base64, pickle, os, re, sys, ctypes, collections
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
SITE = os.path.join(ROOT, 'site'); Z = os.path.join(ROOT, 'zsrc'); BK = os.path.join(ROOT, 'bp3d_backup'); HDD = os.path.join(ROOT, 'zbase_hd')
OFF = np.array([0, 101.0, 12.6]); SCL = 1.034
def z2b(V): return ((V - OFF) / SCL).astype(np.float64)

lib = ctypes.CDLL(os.path.join(HERE, 'libmeshopt.so'))
u32p = np.ctypeslib.ndpointer(np.uint32, flags='C'); f32p = np.ctypeslib.ndpointer(np.float32, flags='C')
lib.meshopt_simplify.restype = ctypes.c_size_t
lib.meshopt_simplify.argtypes = [u32p, u32p, ctypes.c_size_t, f32p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_float, ctypes.c_uint, ctypes.POINTER(ctypes.c_float)]
lib.meshopt_optimizeVertexCache.argtypes = [u32p, u32p, ctypes.c_size_t, ctypes.c_size_t]

def simplify(V, I, target_tris):
    V = np.ascontiguousarray(V, np.float32); I = np.ascontiguousarray(I.reshape(-1), np.uint32)
    if len(I) // 3 <= target_tris: out = I
    else:
        dst = np.zeros_like(I); err = ctypes.c_float()
        n = lib.meshopt_simplify(dst, I, len(I), V, len(V), 12, target_tris * 3, 0.05, 0, ctypes.byref(err)); out = dst[:n].copy()
    used, inv = np.unique(out, return_inverse=True)
    V2 = np.ascontiguousarray(V[used]); I2 = np.ascontiguousarray(inv.astype(np.uint32))
    I3 = np.zeros_like(I2); lib.meshopt_optimizeVertexCache(I3, I2, len(I2), len(V2))
    return V2, I3

def weld(V, T, tol=0.02):
    q = np.round(V / tol).astype(np.int64)
    _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    T = inv.reshape(-1)[T]
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    return V[first], T

def loop(V, T):
    """one level of Loop subdivision (boundary-aware)."""
    nv = len(V); E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); opp = np.concatenate([T[:, 2], T[:, 0], T[:, 1]])
    lo, hi = E.min(1), E.max(1); key = lo * nv + hi
    uk, inv, cnt = np.unique(key, return_inverse=True, return_counts=True); ne = len(uk)
    a, b = uk // nv, uk % nv
    osum = np.zeros((ne, 3)); np.add.at(osum, inv, V[opp])
    inner = cnt == 2
    ep = np.where(inner[:, None], 3 / 8 * (V[a] + V[b]) + osum / 8, (V[a] + V[b]) / 2)
    deg = np.zeros(nv); np.add.at(deg, a, 1); np.add.at(deg, b, 1)
    ns = np.zeros((nv, 3)); np.add.at(ns, a, V[b]); np.add.at(ns, b, V[a])
    beta = np.where(deg > 3, 3 / (8 * np.maximum(deg, 1)), 3 / 16)
    nV = (1 - deg * beta)[:, None] * V + beta[:, None] * ns
    bd = ~inner; bc = np.zeros(nv); bs = np.zeros((nv, 3))
    np.add.at(bc, a[bd], 1); np.add.at(bc, b[bd], 1); np.add.at(bs, a[bd], V[b[bd]]); np.add.at(bs, b[bd], V[a[bd]])
    nV = np.where((bc == 2)[:, None], 0.75 * V + bs / 8, np.where((bc > 0)[:, None], V, nV))
    nt = len(T); e = inv.reshape(3, nt).T + nv
    T2 = np.concatenate([np.stack([T[:, 0], e[:, 0], e[:, 2]], 1), np.stack([T[:, 1], e[:, 1], e[:, 0]], 1),
                         np.stack([T[:, 2], e[:, 2], e[:, 1]], 1), e])
    return np.concatenate([nV, ep]), T2

def read_pack(man, txt):
    M = json.load(open(man)); raw = gzip.decompress(base64.b64decode(open(txt, 'rb').read()))
    P = np.frombuffer(raw, np.uint16, M['nv'] * 3).reshape(-1, 3).astype(np.float32) * np.array(M['sc'], np.float32) + np.array(M['lo'], np.float32)
    off = M['posBytes'] + (2 if M['posBytes'] % 4 else 0); I = np.frombuffer(raw, np.uint16, M['ni'], off)
    return M, P, I

if __name__ == '__main__':
    M, P, I = read_pack(os.path.join(BK, 'manifest.json'), os.path.join(BK, 'anatomy.txt'))
    H = json.load(open(os.path.join(BK, 'hd.json')))
    hraw = gzip.decompress(base64.b64decode(b''.join(open(os.path.join(BK, p), 'rb').read() for p in H['parts'])))
    HP = np.frombuffer(hraw, np.uint16, H['nv'] * 3).reshape(-1, 3).astype(np.float32) * np.array(H['sc'], np.float32) + np.array(H['lo'], np.float32)
    hoff = H['posBytes'] + (2 if H['posBytes'] % 4 else 0); HI = np.frombuffer(hraw, np.uint16, H['ni'], hoff)
    match = json.load(open(os.path.join(Z, 'match.json')))
    d = pickle.load(open(os.path.join(Z, 'z.pkl'), 'rb')); ZO = {r['name']: r for r in d['objs'] if r['type'] == 'mesh'}
    info = {s['id']: s for s in M['structures']}
    def norm(s): return re.sub(r'\b(muscle|muscles|of|the|part|bone)\b|[^a-z ]', ' ', s.lower()).split()

    # ---- decide Z object(s) per structure ----
    assign = collections.defaultdict(list)    # sid -> list of (part label, zname | ('bp', meshindex))
    owner = collections.Counter()
    for k, v in match.items():
        for b in v['best'][:1]: owner[(b[3], v['sid'])] += 1
    used = set()
    for mi, m in enumerate(M['meshes']):
        v = match[str(mi)]; sid = m[0]; st = info[sid]; b = v['best']; pick = None
        if b:
            a = b[0]; clear = len(b) < 2 or b[1][0] > 1.5 * a[0]
            if a[0] < 4 or (a[0] < 10 and clear): pick = a[3]
            elif a[1] < 2.6 and (set(norm(st['name'])) <= set(norm(a[3])) or owner[(a[3], sid)] > 1): pick = a[3]   # part lies on a bigger Z object of the same muscle
            elif st['kind'] in ('muscle', 'tendon') and len(b) > 1 and b[1][1] < 2.6 and set(norm(st['name'])) <= set(norm(b[1][3])): pick = b[1][3]
        if st['kind'] in ('artery', 'vein', 'organ'): pick = None
        if pick and (pick, sid) in used: continue      # same Z object already covers this structure
        if pick: used.add((pick, sid)); assign[sid].append((m[1] if owner[(pick, sid)] <= 1 else '', pick, mi))
        else: assign[sid].append((m[1], None, mi))
    # a Z object claimed by two structures: keep it for the closer one, other falls back
    claim = collections.defaultdict(list)
    for sid, L in assign.items():
        for (lab, z, mi) in L:
            if z: claim[z].append((match[str(mi)]['best'][0][0] if match[str(mi)]['best'][0][3] == z else 9, sid, mi))
    for z, L in claim.items():
        if len(set(s for _, s, _ in L)) > 1:
            L.sort(); keep = L[0][1]
            for _, s, mi in L:
                if s != keep: assign[s] = [(lab, (None if zz == z else zz), mm) for (lab, zz, mm) in assign[s]]
    nz = sum(1 for L in assign.values() for x in L if x[1]); nb = sum(1 for L in assign.values() for x in L if not x[1])
    print('Z meshes', nz, 'BP3D fallback', nb)
    for sid, L in assign.items():
        fb = [lab for lab, z, mi in L if not z]
        if fb and info[sid]['kind'] not in ('artery', 'vein', 'organ'): print('  fallback', sid, fb)
    json.dump({k: v for k, v in assign.items()}, open(os.path.join(Z, 'assign.json'), 'w'), indent=0)

    # ---- geometry ----
    def tgt(kind, key, hd):
        f = 1.7 if hd else 0.52
        if kind == 'muscle': return int((9000 if 'intercostal' in key else 5200) * f)
        if kind == 'tendon': return int(3000 * f)
        if kind == 'disc': return int(600 * f)
        big = key in ('frontal', 'parietal', 'temporal', 'occipital', 'sphenoid', 'hip-bone', 'femur', 'sacrum', 'scapula', 'mandible', 'maxilla', 'tibia', 'humerus')
        return int((5000 if big else 2600) * f)
    zcache = {}
    def zgeom(name):
        if name not in zcache:
            r = ZO[name]; V, T = weld(z2b(r['V']), r['T'].astype(np.int64))
            V1, T1 = loop(V, T)
            V2, T2 = (loop(V1, T1) if len(T1) < 60000 else (V1, T1))
            zcache[name] = (V1, T1, V2, T2)
        return zcache[name]
    std, hd = [], []
    for st in M['structures']:
        sid = st['id']; parts = []
        for lab, z, mi in assign[sid]:
            m = M['meshes'][mi]; hm = H['meshes'][mi]
            if z:
                V1, T1, V2, T2 = zgeom(z)
                # split into <65k-vertex pieces if needed via simplify targets
                a = simplify(V1, T1, tgt(st['kind'], st['k'], False)); b = simplify(V2, T2, tgt(st['kind'], st['k'], True))
            else:
                a = (P[m[2]:m[2] + m[3]].copy(), I[m[4]:m[4] + m[5]].astype(np.uint32))
                b = (HP[hm[0]:hm[0] + hm[1]].copy(), HI[hm[2]:hm[2] + hm[3]].astype(np.uint32))
            while len(b[0]) >= 65536: b = simplify(b[0], b[1].reshape(-1, 3), int(len(b[1]) // 3 * 0.8))
            while len(a[0]) >= 65536: a = simplify(a[0], a[1].reshape(-1, 3), int(len(a[1]) // 3 * 0.8))
            std.append((sid, lab, a, z)); hd.append((sid, lab, b, z))
        st['parts'] = []
    def write(meshes, outdir, keep_meta):
        allV = np.concatenate([g[0] for _, _, g, _ in meshes]); lo = allV.min(0) - 1; hi = allV.max(0) + 1; sc = (hi - lo) / 65535.0
        pos, idx, man = [], [], []; vo = io = 0
        for sid, lab, (V, Ix), z in meshes:
            q = np.round((V - lo) / sc).astype(np.uint16); c = V.mean(0); X = V - c; w, vec = np.linalg.eigh(X.T @ X); ax = vec[:, -1]
            pos.append(q); idx.append(Ix.astype(np.uint16))
            man.append([sid, lab, vo, len(V), io, len(Ix), [round(float(x), 1) for x in c], [round(float(x), 3) for x in ax]]); vo += len(V); io += len(Ix)
        Pq = np.concatenate(pos).tobytes(); blob = Pq + (b'\0\0' if len(Pq) % 4 else b'') + np.concatenate(idx).tobytes()
        meta = dict(keep_meta, lo=[float(x) for x in lo], sc=[float(x) for x in sc], nv=int(vo), ni=int(io), posBytes=len(Pq), meshes=man)
        meta.pop('auxOff', None)
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, 'anatomy.txt'), 'wb').write(base64.b64encode(gzip.compress(blob, 9)))
        json.dump(meta, open(os.path.join(outdir, 'manifest.json'), 'w'), separators=(',', ':'))
        print(outdir, 'meshes', len(man), 'tris', io // 3, 'txt MB', round(os.path.getsize(os.path.join(outdir, 'anatomy.txt')) / 1e6, 2))
        return meta
    meta = write(std, os.path.join(ROOT, 'zbase'), {'structures': M['structures'], 'source': 'Z-Anatomy (CC BY-SA 4.0), derived from BodyParts3D (CC BY-SA 2.1 JP)'})
    for i, s in enumerate(meta['meshes']): pass
    write(hd, HDD, {'structures': M['structures']})
