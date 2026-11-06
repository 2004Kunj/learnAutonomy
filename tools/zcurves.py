"""Replace the hand-traced nerves/vessels with Z-Anatomy's modelled curves (keeping existing ids so content, lecture
matching and quizzes still work) and add every other Z-Anatomy nerve and vessel as a new structure."""
import numpy as np, json, pickle, re, os, sys, gzip, base64, collections
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
from zconvert import z2b, SCL
SITE = os.path.join(ROOT, 'site'); OLD = os.path.join(ROOT, 'live_v23')
d = pickle.load(open(os.path.join(ROOT, 'zsrc', 'z.pkl'), 'rb'))
curves = [r for r in d['objs'] if r['type'] == 'curve']
N0 = json.load(open(os.path.join(OLD, 'nerves.json'))); V0 = json.load(open(os.path.join(OLD, 'vessels.json')))
M = json.load(open(os.path.join(SITE, 'manifest.json')))
raw = gzip.decompress(base64.b64decode(open(os.path.join(SITE, 'anatomy.txt'), 'rb').read()))
P = np.frombuffer(raw, np.uint16, M['nv'] * 3).reshape(-1, 3).astype(np.float32) * np.array(M['sc'], np.float32) + np.array(M['lo'], np.float32)
kind = {s['id']: s['kind'] for s in M['structures']}; region = {s['id']: s['region'] for s in M['structures']}
ves_pts = []; bone_pts = []; bone_id = []
for m in M['meshes']:
    V = P[m[2]:m[2] + m[3]]
    if kind[m[0]] in ('artery', 'vein', 'organ'): ves_pts.append(V)
    if kind[m[0]] == 'bone': bone_pts.append(V[::5]); bone_id += [m[0]] * len(V[::5])
vtree = cKDTree(np.concatenate(ves_pts)); btree = cKDTree(np.concatenate(bone_pts)); bone_id = np.array(bone_id)

SKIP = re.compile(r'bronch|duct\b|ureter|urethra|deferens|oesophag|jejunum|bezier|\?|central canal|medulla-path|-curve|-profile|of (left|right) lung|lobar|intrarenal|lingular|ciliary|retinal|ophthalmic|ethmoid|cerebr|callosomarginal|pericallosal|sulcus|gyrus|striate|pontine|frontobasal|orbitofrontal|prefrontal|parieto|parietal (artery|branch)|temporal branch|occipital artery$|^(lateral|medial) occipital artery|temporo-occipital|postcentral|insular|sinus$|cerebell|basilar|communicating artery|meningeal|olfactory|optic nerve|oculomotor|trochlear|abducens|cochlear|vestibul|chorda|^\(?anteromedial', re.I)
def norm(s):
    s = s.lower().replace('-', ' ').replace('(cn ', '(').replace('&', 'and')
    s = re.sub(r'\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|v3)\)', '', s); s = re.sub(r'[()]', '', s)
    return re.sub(r'\s+', ' ', s).strip()
ALIAS = {
 'Brachial plexus': ['Roots of brachial plexus', 'Superior trunk of brachial plexus', 'Middle trunk of brachial plexus', 'Inferior trunk of brachial plexus',
                     'Anterior division of superior trunk of brachial plexus', 'Anterior division of middle trunk of brachial plexus', 'Anterior division of inferior trunk of brachial plexus',
                     'Posterior division of superior trunk of brachial plexus', 'Posterior division of middle trunk of brachial plexus', 'Posterior division of inferior trunk of brachial plexus', 'Posterior cord of brachial plexus'],
 'Mandibular nerve (CN V3)': ['Anterior division of mandibular nerve', 'Posterior division of mandibular nerve'],
 'Intercostal nerves (T1–T12)': ['Intercostal nerves'],
 'Medial & lateral pectoral nerves': ['Medial pectoral nerve', 'Lateral pectoral nerve'],
 'Subscapular nerves': ['Superior subscapular nerve', 'Inferior subscapular nerve'],
 'Accessory nerve (CN XI)': ['Accessory nerve (XI)'], 'Facial nerve (CN VII)': ['Facial nerve (VII)'],
 'Thoracoacromial artery': ['Thoraco-acromial artery'], 'Deep artery of the arm (profunda brachii)': ['Deep brachial artery'],
 'Deep artery of the thigh': ['Deep femoral artery'], 'Dorsal venous arch (foot)': ['Dorsal venous arch of foot'], 'Dorsal venous network (hand)': ['Dorsal venous network of hand'],
 'Genicular arteries': ['Superior medial genicular artery', 'Superior lateral genicular artery', 'Inferior medial genicular artery', 'Inferior lateral genicular artery', 'Middle genicular artery'],
 'Internal jugular vein (upper)': ['Internal jugular vein'],
 'Internal thoracic & superior epigastric arteries': ['Internal thoracic artery', 'Superior epigastric artery'],
 'Internal thoracic & superior epigastric veins': ['Internal thoracic veins', 'Superior epigastric veins'],
 'Lumbar veins & ascending lumbar vein': ['Lumbar veins', '{S} ascending lumbar vein'],
 'Medial & lateral circumflex femoral arteries': ['Medial circumflex femoral artery', 'Lateral circumflex femoral artery'],
 'Medial & lateral circumflex femoral veins': ['Medial circumflex femoral veins', 'Lateral circumflex femoral veins'],
 'Medial & lateral plantar arteries': ['Medial plantar artery', 'Lateral plantar artery'], 'Medial & lateral plantar veins': ['Medial plantar veins', 'Lateral plantar veins'],
 'Palmar venous arches': ['Superficial venous palmar arch', 'Deep venous palmar arch'], 'Perforating veins (leg)': ['Perforating veins'],
 'Subscapular & circumflex scapular veins': ['Subscapular vein', 'Circumflex scapular vein'], 'Superficial temporal vein': ['Superficial temporal veins'],
 'Ulnar recurrent arteries': ['(Ulnar recurrent artery)'], 'Hemiazygos vein': ['Hemi-azygos vein'], 'Accessory hemiazygos vein': ['Accessory hemi-azygos vein'],
 'External pudendal arteries': ['Superficial external pudendal artery', 'Deep external pudendal artery'],
 'Posterior intercostal arteries': ['Posterior intercostal arteries', 'First posterior intercostal artery', 'Second posterior intercostal artery'],
 'Hepatic veins': [], 'Hepatic portal vein': [],   # sit inside the BodyParts3D liver/portal meshes
}
byname = collections.defaultdict(list)
for r in curves: byname[re.sub(r'\.(l|r)$', '', r['name'])].append(r)
bynorm = {norm(k): k for k in byname}
def side_of(r): m = re.search(r'\.(l|r)$', r['name']); return {'l': 'L', 'r': 'R'}[m.group(1)] if m else ''

def resample(pts, rad, step=3.0):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
    if L < 1: return None, None
    t = np.linspace(0, L, max(2, int(np.ceil(L / step)) + 1))
    return np.stack([np.interp(t, s, pts[:, i]) for i in range(3)], 1), np.interp(t, s, rad)
def paths_of(objs, kd):
    P_, R_ = [], []
    for r in objs:
        for p, rr in r['paths']:
            p = z2b(p.astype(np.float64)); rr = rr.astype(np.float64) / SCL
            if not np.isfinite(p).all() or len(p) < 2: continue
            q, qr = resample(p, rr)
            if q is None: continue
            qr = np.maximum(qr, 0.8 if kd == 'nerve' else 0.7)
            P_.append(np.round(q, 1).tolist()); R_.append(np.round(qr, 2).tolist())
    return P_, R_
def kind_of(name, cols):
    n = name.lower()
    if '7: Nervous system & Sense organs' in cols or re.search(r'nerve|plexus|cauda|sympathetic|branch(es)? of .*nerve', n): return 'nerve'
    if re.search(r'vein|venous|vena|sinus|azygos', n) or 'Systemic veins' in cols: return 'vein'
    return 'artery'

used = set(); out_n, out_v = [], []; replaced = 0; kept = 0
def take(item, kd, zl):
    global replaced, kept
    objs = []
    for zn in zl:
        zn = zn.replace('{S}', {'R': 'Right', 'L': 'Left', '': ''}[item.get('side', '')]).strip()
        key = zn if zn in byname else bynorm.get(norm(zn))
        if not key: continue
        for r in byname[key]:
            if item.get('side') and side_of(r) and side_of(r) != item['side']: continue
            objs.append(r); used.add(r['name'])
    if objs:
        P_, R_ = paths_of(objs, kd)
        if P_: item = dict(item, paths=P_, rads=R_, r=round(float(max(max(x) for x in R_)), 2), src='z'); replaced += 1; return item
    kept += 1; return item
for n in N0:
    out_n.append(take(n, 'nerve', ALIAS.get(n['name'], [n['name']])))
for v in V0:
    out_v.append(take(v, v['kind'], ALIAS.get(v['name'], [v['name']])))
print('existing items re-sourced from Z-Anatomy:', replaced, ' kept as traced:', kept)
print('  still traced:', [x['name'] for x in out_n + out_v if x.get('src') != 'z'])

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
existing_k = {x['k'] for x in out_n + out_v} | set(kind)
added = collections.Counter(); skipped = collections.Counter()
groups = collections.defaultdict(list)
for r in curves:
    if r['name'] in used: continue
    base = re.sub(r'\.(l|r)$', '', r['name']).strip(); base = base[1:-1] if base.startswith('(') and base.endswith(')') else base
    if SKIP.search(base) or not any(c in r['cols'] for c in ('5: Cardiovascular system', '7: Nervous system & Sense organs')): skipped['category'] += 1; continue
    groups[(base, side_of(r))].append(r)
for (base, side), objs in sorted(groups.items()):
    kd = kind_of(base, objs[0]['cols']); P_, R_ = paths_of(objs, kd)
    if not P_: continue
    allp = np.concatenate([np.array(p) for p in P_]); rmax = max(max(x) for x in R_)
    if kd != 'nerve':
        dd, _ = vtree.query(allp);
        if (dd < max(rmax, 2) + 5).mean() > 0.6: skipped['inside a scanned vessel'] += 1; continue
    k = 'z-' + slug(base)
    if k in existing_k and not side: k += '-z'
    _, bi = btree.query(allp.mean(0)); reg = region[bone_id[bi]]
    item = dict(id=k + ('-' + side if side else ''), k=k, name=base, side=side, r=round(float(rmax), 2), kind=kd, region=reg, paths=P_, rads=R_, src='z', new=True)
    (out_n if kd == 'nerve' else out_v).append(item); added[kd] += 1
print('new Z-Anatomy structures:', dict(added), ' skipped:', dict(skipped))
for o in out_n:
    if 'kind' in o: o.pop('kind')
json.dump(out_n, open(os.path.join(SITE, 'nerves.json'), 'w'), separators=(',', ':'))
json.dump(out_v, open(os.path.join(SITE, 'vessels.json'), 'w'), separators=(',', ':'))
print('nerves.json MB', round(os.path.getsize(os.path.join(SITE, 'nerves.json')) / 1e6, 2), 'vessels.json MB', round(os.path.getsize(os.path.join(SITE, 'vessels.json')) / 1e6, 2),
      'items', len(out_n), len(out_v), 'points', sum(len(p) for x in out_n + out_v for p in x['paths']))
