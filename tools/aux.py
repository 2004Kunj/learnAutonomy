"""Per-vertex cadaver attributes: crevice (closeness to a neighbouring structure) and tendon (near a muscle's ends)."""
import numpy as np, json, gzip, base64, os
from scipy.spatial import cKDTree
SITE = os.environ.get('SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
M = json.load(open(os.path.join(SITE, 'manifest.json')))
raw = gzip.decompress(base64.b64decode(open(os.path.join(SITE, 'anatomy.txt'), 'rb').read()))
nv, ni = M['nv'], M['ni']; pb = M['posBytes']; ioff = pb + (2 if pb % 4 else 0)
raw = raw[:ioff + ni * 2]   # drop any old aux block
P = np.frombuffer(raw, np.uint16, nv * 3).reshape(-1, 3).astype(np.float32) * np.array(M['sc'], np.float32) + np.array(M['lo'], np.float32)
kind = {s['id']: s['kind'] for s in M['structures']}
lab = np.zeros(nv, np.int32); tend = np.zeros(nv, np.float32)
for mi, m in enumerate(M['meshes']):
    vo, vc = m[2], m[3]; lab[vo:vo + vc] = mi
    if kind[m[0]] == 'muscle':
        V = P[vo:vo + vc]; c = V.mean(0); X = V - c
        w, vec = np.linalg.eigh(X.T @ X); a = vec[:, -1]; t = X @ a
        if w[-1] > 2.2 * w[-2]:          # elongated muscles only
            t = (t - t.min()) / max(1e-6, np.ptp(t)); e = np.minimum(t, 1 - t)
            tend[vo:vo + vc] = np.clip(1 - e / 0.13, 0, 1) ** 1.5
# vertex normals
I = np.frombuffer(raw, np.uint16, ni, ioff).astype(np.int64)
N = np.zeros_like(P)
for m in M['meshes']:
    vo, io, ic = m[2], m[4], m[5]; f = I[io:io + ic].reshape(-1, 3) + vo
    fn = np.cross(P[f[:, 1]] - P[f[:, 0]], P[f[:, 2]] - P[f[:, 0]])
    for j in range(3): np.add.at(N, f[:, j], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
R = 14.0
tree = cKDTree(P)
crev = np.zeros(nv, np.float32)
for c0 in range(0, nv, 200000):
    sl = slice(c0, min(nv, c0 + 200000))
    d, idx = tree.query(P[sl], k=40, distance_upper_bound=R, workers=-1)
    ok = idx < nv; ii = np.minimum(idx, nv - 1)
    diffm = ok & (lab[ii] != lab[sl][:, None])
    vec = P[ii] - P[sl][:, None, :]
    front = np.einsum('ijk,ik->ij', vec, N[sl]) > 0.35 * d
    w = np.where(diffm & front, 1 - d / R, 0)
    crev[sl] = np.clip(w.sum(1) / 4.0, 0, 1) ** 0.9
# aponeuroses painted by anatomical position (vertebral levels from this specimen)
sid = np.array([M['meshes'][l][0] for l in range(len(M['meshes']))])[lab]
k_of = {st['id']: st['k'] for st in M['structures']}
key = np.vectorize(lambda x: k_of[x])(sid)
x, y, z = np.abs(P[:, 0]), P[:, 1], P[:, 2]
rng = np.random.default_rng(1)
def soft(v, w): return np.clip(v / w, 0, 1)
apo = np.zeros(nv, np.float32)
tr = key == 'trapezius'
dia = 1 - (x / 42 + np.abs(z - 1382) / 72)                      # tendinous diamond over C6-T2
strip = (x < 6) & (z > 1170) & (z < 1480)
tri = np.minimum((x - 62) / 8, ((x - 62) * 0.55 - np.abs(z - 1318)) / 6) * (x < 98)   # triangle at root of the scapular spine, apex medial
apo[tr] = np.maximum.reduce([soft(dia[tr], .25), strip[tr] * 0.9, soft(tri[tr], 1.0)])
la = key == 'lats'
w = np.interp(z, [880, 930, 975, 1050, 1110, 1185], [40, 70, 92, 78, 40, 4])
apo[la] = np.maximum(apo[la], soft((w - x)[la], 14) * (z[la] < 1190))
gm = key == 'glute-max'
apo[gm] = np.maximum(apo[gm], soft((48 - x)[gm], 18) * soft((z[gm] - 860), 30))
ld = key == 'deltoid'
apo[ld] = np.maximum(apo[ld], soft((z[ld] - 1335), 12) * 0.6)    # tendinous upper rim
apo *= (0.85 + 0.15 * rng.random(nv)).astype(np.float32)
print('aponeurosis verts', int((apo > .5).sum()))
tend = np.maximum(tend * 0.85, apo)
aux = np.stack([np.round(crev * 255), np.round(tend * 255)], 1).astype(np.uint8)
blob = raw + aux.tobytes()
M['auxOff'] = len(raw)
open(os.path.join(SITE, 'anatomy.txt'), 'wb').write(base64.b64encode(gzip.compress(blob, 9)))
json.dump(M, open(os.path.join(SITE, 'manifest.json'), 'w'), separators=(',', ':'))
print('crevice mean', crev.mean().round(3), '>0.5:', (crev > .5).mean().round(3), 'tendon verts', (tend > .3).mean().round(3),
      'txt MB', round(os.path.getsize(os.path.join(SITE, 'anatomy.txt')) / 1e6, 2))
