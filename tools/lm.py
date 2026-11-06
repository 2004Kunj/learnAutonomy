import numpy as np, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
STL = '/home/claude/kevin-mattheus-moerman/bodyparts3d/assets/BodyParts3D_data/stl/'
names = {}
for l in open(os.path.join(HERE, '..', 'have.tsv')):
    f, n, s = l.rstrip('\n').split('\t'); names[n] = f
_c = {}
def V(nm):
    if nm in _c: return _c[nm]
    b = open(STL + names[nm] + '.stl', 'rb').read()
    n = int(np.frombuffer(b, dtype='<u4', count=1, offset=80)[0])
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    v = np.frombuffer(b, dtype=dt, count=n, offset=84)['v'].reshape(-1, 3)[::3].astype(np.float64)
    _c[nm] = v; return v

def ext(nm, axis, fn, frac=0.02):
    """mean of the extreme `frac` of vertices along axis (fn=min|max)"""
    v = V(nm); a = v[:, axis]; k = max(5, int(len(v) * frac))
    o = np.argsort(a); sel = o[:k] if fn == 'min' else o[-k:]
    return v[sel].mean(0)

def slab(nm, z0, z1):
    v = V(nm); m = (v[:, 2] >= z0) & (v[:, 2] <= z1); return v[m]

def canal(nm):
    v = V(nm); m = np.abs(v[:, 0]) < 3; y = np.sort(v[m, 1]); z = v[m, 2]
    if len(y) < 10: return None
    g = np.diff(y); i = np.argmax(g); cy = (y[i] + y[i + 1]) / 2
    return np.array([0, cy, np.median(z)])

def axis_pts(nm, ts):
    v = V(nm); c = v.mean(0); X = v - c; w, vec = np.linalg.eigh(X.T @ X); a = vec[:, -1]
    if a[2] < 0: a = -a
    p = X @ a; top = c + a * np.percentile(p, 99); bot = c + a * np.percentile(p, 1)
    return [top + (bot - top) * t for t in ts]
