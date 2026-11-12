"""Gluteal aponeurosis: the thick deep fascia over the superficial (uncovered) part of gluteus medius, from the iliac crest
down to the upper border of gluteus maximus, where it continues as the fascia lata.  Z-Anatomy has no mesh for it, so it is
built on this specimen's own gluteus medius surface (offset 1 mm, 0.9 mm thick) and appended to the standard and HD packs."""
import numpy as np, json, gzip, base64, os, sys
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); SITE = os.path.join(ROOT, 'site')
K = 'gluteal-apo'
def unpack(raw, M):
    P = np.frombuffer(raw, np.uint16, M['nv'] * 3).reshape(-1, 3).copy()
    io = M['posBytes'] + (2 if M['posBytes'] % 4 else 0); I = np.frombuffer(raw, np.uint16, M['ni'], io).copy()
    A = np.frombuffer(raw, np.uint8, M['nv'] * 2, M['auxOff']).reshape(-1, 2).copy(); return P, I, A
def pack(P, I, A):
    pb = P.astype('<u2').tobytes(); pad = b'\0\0' if len(pb) % 4 else b''; ib = I.astype('<u2').tobytes()
    blob = pb + pad + ib; return blob + A.astype(np.uint8).tobytes(), len(pb), len(blob)
M = json.load(open(os.path.join(SITE, 'manifest.json')))
assert not any(e[0].startswith(K) for e in M['meshes']), 'already added'
sraw = gzip.decompress(base64.b64decode(open(os.path.join(SITE, 'anatomy.txt'), 'rb').read()))
SP, SI, SA = unpack(sraw, M)
H = json.load(open(os.path.join(SITE, 'hd.json')))
hraw = gzip.decompress(base64.b64decode(b''.join(open(os.path.join(SITE, p), 'rb').read() for p in H['parts'])))
HP, HI, HA = unpack(hraw, H)
idx = {e[0]: i for i, e in enumerate(M['meshes'])}
def mesh(i, hd=True):
    vo, vc, io, ic = H['meshes'][i] if hd else M['meshes'][i][2:6]
    P, I, lo, sc = (HP, HI, H['lo'], H['sc']) if hd else (SP, SI, M['lo'], M['sc'])
    return P[vo:vo + vc].astype(np.float64) * sc + lo, I[io:io + ic].reshape(-1, 3).astype(np.int64)
def vnormals(V, T):
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]); N = np.zeros_like(V)
    for j in range(3): np.add.at(N, T[:, j], fn)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-9), fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9)
def build(side):
    sgn = 1 if side == 'L' else -1
    V, T = mesh(idx['glute-med-' + side]); VN, FN = vnormals(V, T)
    c = V.mean(0)
    if (np.einsum('ij,ij->i', FN, V[T].mean(1) - c) < 0).mean() > .5: T = T[:, ::-1]; VN, FN = -VN, -FN   # outward normals
    gm, _ = mesh(idx['glute-max-' + side]); tf, _ = mesh(idx['tfl-' + side]); cov = cKDTree(np.concatenate([gm, tf]))
    dV, _ = cov.query(V)
    out = np.array([sgn, 0.25, 0.15]); out /= np.linalg.norm(out)
    keep = (FN @ out > 0.2) & (dV[T].min(1) > 3.5)
    T = T[keep]
    # largest connected patch only
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); A = coo_matrix((np.ones(len(E)), (E[:, 0], E[:, 1])), shape=(len(V), len(V)))
    _, lab = connected_components(A, directed=False); fl = lab[T[:, 0]]; big = np.bincount(fl).argmax(); T = T[fl == big]
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V = V[used]; N = VN[used]; T = remap[T]
    # relax the sheet a little so it reads as fascia rather than a copy of the muscle's fibres
    nb = [[] for _ in range(len(V))]
    for a, b in np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]): nb[a].append(b); nb[b].append(a)
    for _ in range(3): V = np.array([V[n].mean(0) * .5 + V[i] * .5 if n else V[i] for i, n in enumerate(nb)])
    N, _ = vnormals(V, T)
    if (np.einsum('ij,ij->i', N, V - c) < 0).mean() > .5: N = -N
    outer, inner = V + N * 1.9, V + N * 1.0; m = len(V)
    Vs = np.concatenate([outer, inner]); Ts = [T, T[:, ::-1] + m]
    ec = {}
    for t in T:
        for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): ec[tuple(sorted(e))] = ec.get(tuple(sorted(e)), 0) + 1
    oe = {}
    for t in T:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if ec[tuple(sorted((a, b)))] == 1: oe[(a, b)] = 1
    rim = [[b, a, a + m] for a, b in oe] + [[b, a + m, b + m] for a, b in oe]
    Ts = np.concatenate(Ts + [np.array(rim)]); print(side, 'verts', len(Vs), 'tris', len(Ts), 'area mm2', round(float(np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1).sum() / 2)))
    assert len(Vs) < 65535
    return Vs, Ts
def q(V, lo, sc):
    Q = np.round((V - lo) / sc); assert (Q >= 0).all() and (Q <= 65535).all(); return Q.astype(np.uint16)
newS = []; newH = []
for side in ('R', 'L'):
    V, T = build(side); gme = M['meshes'][idx['glute-med-' + side]]
    sid = K + '-' + side; cen = np.round(V.mean(0), 1).tolist()
    for (P, I, A, lo, sc, lst) in ((SP, SI, SA, M['lo'], M['sc'], newS), (HP, HI, HA, H['lo'], H['sc'], newH)):
        lst.append((q(V, np.array(lo), np.array(sc)), T.astype(np.uint16).ravel()))
    M['meshes'].append([sid, '', 0, len(V), 0, T.size, cen, gme[7], gme[8]])
    H['meshes'].append([0, len(V), 0, T.size])
    M['structures'].append(dict(id=sid, k=K, name='Gluteal aponeurosis', kind='tendon', region='Hip', side=side, parts=[]))
def append(P, I, A, meta, new, entries):
    vo, io = len(P), len(I); Ps, Is, As = [P], [I], [A]
    for (Q, T), e in zip(new, entries):
        e[-7 if len(e) > 4 else 0] = vo if len(e) > 4 else vo
        if len(e) > 4: e[2], e[4] = vo, io
        else: e[0], e[2] = vo, io
        Ps.append(Q); Is.append(T); As.append(np.tile(np.array([130, 0], np.uint8), (len(Q), 1))); vo += len(Q); io += len(T)
    P2, I2, A2 = np.concatenate(Ps), np.concatenate(Is), np.concatenate(As)
    blob, pb, ao = pack(P2, I2, A2); meta.update(nv=len(P2), ni=len(I2), posBytes=pb, auxOff=ao); return blob
sb = append(SP, SI, SA, M, newS, M['meshes'][-2:])
hb = append(HP, HI, HA, H, newH, H['meshes'][-2:])
open(os.path.join(SITE, 'anatomy.txt'), 'wb').write(base64.b64encode(gzip.compress(sb, 9)))
json.dump(M, open(os.path.join(SITE, 'manifest.json'), 'w'), separators=(',', ':'))
txt = base64.b64encode(gzip.compress(hb, 9)); n = 4; L = -(-len(txt) // n)
old = H['parts']; H['parts'] = ['hd%d.txt' % (i + 5) for i in range(n)]
for i, nm in enumerate(H['parts']): open(os.path.join(SITE, nm), 'wb').write(txt[i * L:(i + 1) * L])
H['bytes'] = len(txt); json.dump(H, open(os.path.join(SITE, 'hd.json'), 'w'), separators=(',', ':'))
C = json.load(open(os.path.join(SITE, 'content.json')))
C['TEN'][K] = ['Thick deep fascia over the uncovered part of gluteus medius, from the outer lip of the iliac crest down to the upper border of gluteus maximus, where it splits to enclose gluteus maximus and continues as the fascia lata. Gluteus medius takes some of its origin from its deep surface.',
               'It is the tough, shiny sheet you cut through above gluteus maximus in the lab to reach gluteus medius; the superior gluteal nerve and vessels lie deep to gluteus medius, beneath it.']
json.dump(C, open(os.path.join(SITE, 'content.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
print('std MB', round(os.path.getsize(os.path.join(SITE, 'anatomy.txt')) / 1e6, 2), 'hd parts MB', [round(os.path.getsize(os.path.join(SITE, p)) / 1e6, 2) for p in H['parts']], 'old parts', old)
