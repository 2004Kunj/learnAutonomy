"""One structure per named nerve: split Z-Anatomy groups (brachial plexus parts, pectoral, subscapular, mandibular divisions)
into their own structures, add the cranial nerves, and model the lateral and medial cords between the plexus divisions and
their terminal nerves.  The original grouped items stay (course notes and quizzes are keyed to them)."""
import numpy as np, json, pickle, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
from zconvert import z2b, SCL
SITE = os.path.join(ROOT, 'site')
d = pickle.load(open(os.path.join(ROOT, 'zsrc', 'z.pkl'), 'rb'))
curves = [r for r in d['objs'] if r['type'] == 'curve']
N = json.load(open(os.path.join(SITE, 'nerves.json')))
N = [x for x in N if not x.get('part')]          # idempotent
def side_of(r): m = re.search(r'\.(l|r)$', r['name']); return {'l': 'L', 'r': 'R'}[m.group(1)] if m else ''
def resample(pts, rad, step=3.0):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
    if L < 1: return None, None
    t = np.linspace(0, L, max(2, int(np.ceil(L / step)) + 1))
    return np.stack([np.interp(t, s, pts[:, i]) for i in range(3)], 1), np.interp(t, s, rad)
def paths(name, side, rmin=0.8):
    P_, R_ = [], []
    for r in curves:
        b = re.sub(r'\.(l|r)$', '', r['name']).strip()
        b = b[1:-1] if b.startswith('(') and b.endswith(')') else b
        if b != name: continue
        if side and side_of(r) and side_of(r) != side: continue
        for p, rr in r['paths']:
            p = z2b(p.astype(np.float64)); rr = rr.astype(np.float64) / SCL
            if not np.isfinite(p).all() or len(p) < 2: continue
            q, qr = resample(p, rr)
            if q is None: continue
            P_.append(np.round(q, 1).tolist()); R_.append(np.round(np.maximum(qr, rmin), 2).tolist())
    return P_, R_
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
PARTS = [  # (z name, display name, parent k, region)
 ('Roots of brachial plexus', 'Roots of brachial plexus (C5–T1)', 'brachial-plexus', 'Neck'),
 ('Superior trunk of brachial plexus', 'Superior (upper) trunk of brachial plexus', 'brachial-plexus', 'Neck'),
 ('Middle trunk of brachial plexus', 'Middle trunk of brachial plexus', 'brachial-plexus', 'Neck'),
 ('Inferior trunk of brachial plexus', 'Inferior (lower) trunk of brachial plexus', 'brachial-plexus', 'Neck'),
 ('Anterior division of superior trunk of brachial plexus', 'Anterior division of superior trunk', 'brachial-plexus', 'Shoulder'),
 ('Anterior division of middle trunk of brachial plexus', 'Anterior division of middle trunk', 'brachial-plexus', 'Shoulder'),
 ('Anterior division of inferior trunk of brachial plexus', 'Anterior division of inferior trunk', 'brachial-plexus', 'Shoulder'),
 ('Posterior division of superior trunk of brachial plexus', 'Posterior division of superior trunk', 'brachial-plexus', 'Shoulder'),
 ('Posterior division of middle trunk of brachial plexus', 'Posterior division of middle trunk', 'brachial-plexus', 'Shoulder'),
 ('Posterior division of inferior trunk of brachial plexus', 'Posterior division of inferior trunk', 'brachial-plexus', 'Shoulder'),
 ('Posterior cord of brachial plexus', 'Posterior cord of brachial plexus', 'brachial-plexus', 'Shoulder'),
 ('Medial pectoral nerve', 'Medial pectoral nerve', 'pectoral', 'Thorax'),
 ('Lateral pectoral nerve', 'Lateral pectoral nerve', 'pectoral', 'Thorax'),
 ('Superior subscapular nerve', 'Upper (superior) subscapular nerve', 'subscapular', 'Shoulder'),
 ('Inferior subscapular nerve', 'Lower (inferior) subscapular nerve', 'subscapular', 'Shoulder'),
 ('Anterior division of mandibular nerve', 'Anterior division of mandibular nerve', 'mandibular', 'Skull'),
 ('Posterior division of mandibular nerve', 'Posterior division of mandibular nerve', 'mandibular', 'Skull'),
 ('Olfactory nerve (I)', 'Olfactory nerve (CN I)', '', 'Skull'), ('Optic nerve (II)', 'Optic nerve (CN II)', '', 'Skull'),
 ('Oculomotor nerve (III)', 'Oculomotor nerve (CN III)', '', 'Skull'), ('Trochlear nerve (IV)', 'Trochlear nerve (CN IV)', '', 'Skull'),
 ('Abducens nerve (VI)', 'Abducens nerve (CN VI)', '', 'Skull'), ('Ophthalmic nerve', 'Ophthalmic nerve (CN V1)', '', 'Skull'),
 ('Vestibulocochlear nerve (VIII)', 'Vestibulocochlear nerve (CN VIII)', '', 'Skull'), ('Cochlear nerve', 'Cochlear nerve', '', 'Skull'),
 ('Vestibular nerve', 'Vestibular nerve', '', 'Skull'), ('Chorda tympani', 'Chorda tympani', '', 'Skull'),
]
out = []; miss = []
for zn, nm, par, reg in PARTS:
    for side in ('R', 'L'):
        P_, R_ = paths(zn, side)
        if not P_: miss.append((zn, side)); continue
        k = 'p-' + slug(re.sub(r'\s*\(.*?\)', '', nm))
        out.append(dict(id=k + '-' + side, k=k, name=nm, side=side, r=round(max(max(x) for x in R_), 2), region=reg, paths=P_, rads=R_, src='z', new=True, part=True, grp=par))
# lateral and medial cords: bridge the anterior divisions to the terminal nerves they form
byk = {}
for x in N: byk.setdefault((x['k'], x['side']), x)
def ends(pp): return [np.array(p[0]) for p in pp] + [np.array(p[-1]) for p in pp]
def closest(A, B):
    best = None
    for a in A:
        for b in B:
            dd = np.linalg.norm(a - b)
            if best is None or dd < best[0]: best = (dd, a, b)
    return best
def bridge(a, b, r=1.6):
    L = np.linalg.norm(b - a); n = max(3, int(L / 3))
    t = np.linspace(0, 1, n)[:, None]; mid = (a + b) / 2
    pts = a * (1 - t) + b * t
    return [np.round(pts, 1).tolist()], [[r] * n]
for side in ('R', 'L'):
    divs = {o['name']: o for o in out if o['side'] == side}
    def startpt(k):
        it = byk.get((k, side)); pts = [np.array(p[0]) for p in it['paths']] + [np.array(p[-1]) for p in it['paths']]
        return it, pts
    # lateral cord: anterior divisions of superior + middle trunks -> musculocutaneous nerve
    A = ends(divs['Anterior division of superior trunk']['paths']) + ends(divs['Anterior division of middle trunk']['paths'])
    _, M = startpt('musculocutaneous'); _, Md = startpt('median')
    dd, a, b = closest(A, M + Md); print('lateral cord', side, 'gap mm', round(dd, 1))
    P_, R_ = bridge(a, b)
    out.append(dict(id='p-lateral-cord-of-brachial-plexus-' + side, k='p-lateral-cord-of-brachial-plexus', name='Lateral cord of brachial plexus', side=side, r=1.6, region='Shoulder', paths=P_, rads=R_, src='modelled', new=True, part=True, grp='brachial-plexus'))
    A = ends(divs['Anterior division of inferior trunk']['paths']); _, U = startpt('ulnar')
    dd, a, b = closest(A, U + Md); print('medial cord', side, 'gap mm', round(dd, 1))
    if dd > 3: P_, R_ = bridge(a, b)
    else:   # the division runs straight into the ulnar nerve: the cord is the first ~28 mm of that trunk
        it = byk[('ulnar', side)]; pth = max(it['paths'], key=len); arr = np.array(pth)
        if np.linalg.norm(arr[-1] - b) < np.linalg.norm(arr[0] - b): arr = arr[::-1]
        seg = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(arr, axis=0), axis=1))]); arr = arr[seg <= 28]
        P_, R_ = [np.round(arr, 1).tolist()], [[1.6] * len(arr)]
    out.append(dict(id='p-medial-cord-of-brachial-plexus-' + side, k='p-medial-cord-of-brachial-plexus', name='Medial cord of brachial plexus', side=side, r=1.6, region='Shoulder', paths=P_, rads=R_, src='modelled', new=True, part=True, grp='brachial-plexus'))
print('added', len(out), 'missing', miss)
json.dump(N + out, open(os.path.join(SITE, 'nerves.json'), 'w'), separators=(',', ':'))
print('nerves.json MB', round(os.path.getsize(os.path.join(SITE, 'nerves.json')) / 1e6, 2), 'items', len(N + out))
