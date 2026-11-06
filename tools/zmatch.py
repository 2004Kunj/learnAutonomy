"""Match every part in the current pack to its Z-Anatomy object by geometry. Writes zsrc/match.json"""
import numpy as np, json, gzip, base64, pickle, os, re
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
SITE = os.path.join(ROOT, 'site'); Z = os.path.join(ROOT, 'zsrc')
OFF = np.array([0, 101.0, 12.6]); SCL = 1.034
def z2b(V): return ((V - OFF) / SCL).astype(np.float32)

M = json.load(open(os.path.join(SITE, 'manifest.json')))
raw = gzip.decompress(base64.b64decode(open(os.path.join(SITE, 'anatomy.txt'), 'rb').read()))
P = np.frombuffer(raw, np.uint16, M['nv'] * 3).reshape(-1, 3).astype(np.float32) * np.array(M['sc'], np.float32) + np.array(M['lo'], np.float32)
d = pickle.load(open(os.path.join(Z, 'z.pkl'), 'rb'))
MARK = re.compile(r'\.(j|t|g|i|s|e[lr]?|o[lr]?)$')
cand = []
for r in d['objs']:
    if r['type'] != 'mesh' or len(r['T']) < 40: continue
    if '2: Muscular insertions' in r['cols'] or MARK.search(r['name']): continue
    V = z2b(r['V']); used = np.unique(r['T']); V = V[used]
    cand.append(dict(name=r['name'], V=V, lo=V.min(0), hi=V.max(0), c=V.mean(0), cols=r['cols']))
print('candidates', len(cand))
trees = {}
def tree(i):
    if i not in trees: trees[i] = cKDTree(cand[i]['V'])
    return trees[i]
LO = np.array([c['lo'] for c in cand]); HI = np.array([c['hi'] for c in cand])
rng = np.random.default_rng(0)
out = {}
for mi, m in enumerate(M['meshes']):
    V = P[m[2]:m[2] + m[3]]; lo, hi = V.min(0), V.max(0)
    ov = np.all((LO < hi + 5) & (HI > lo - 5), 1)
    S = V[rng.choice(len(V), min(600, len(V)), replace=False)]
    best = []
    for i in np.nonzero(ov)[0]:
        c = cand[i]
        d1 = tree(i).query(S)[0]
        if np.median(d1) > 8: continue
        T = c['V'][rng.choice(len(c['V']), min(600, len(c['V'])), replace=False)]
        d2 = cKDTree(V).query(T)[0]
        best.append((max(np.percentile(d1, 80), np.percentile(d2, 80)), np.median(d1), np.median(d2), c['name']))
    best.sort()
    out[mi] = dict(sid=m[0], part=m[1], best=[(round(float(a), 2), round(float(b), 2), round(float(e), 2), n) for a, b, e, n in best[:3]])
json.dump(out, open(os.path.join(Z, 'match.json'), 'w'), indent=0)
ok = [v for v in out.values() if v['best'] and v['best'][0][0] < 4]
print('matched <4mm', len(ok), 'of', len(out))
for v in list(out.values()):
    if not v['best'] or v['best'][0][0] >= 4: print('  weak', v['sid'], v['part'], v['best'][:2])
