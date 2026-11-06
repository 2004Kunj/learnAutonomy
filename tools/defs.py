"""Per-structure 'About' text from Z-Anatomy's definitions (adapted from Wikipedia, CC BY-SA). Writes site/defs.json."""
import json, re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
D = json.load(open(R + '/zsrc/defs.json')); M = json.load(open(R + '/site/manifest.json'))
N = json.load(open(R + '/site/nerves.json')); V = json.load(open(R + '/site/vessels.json'))
A = json.load(open(R + '/zsrc/assign.json'))   # BodyParts3D structure -> Z-Anatomy object(s)
def key(s): return re.sub(r'[^a-z0-9 ]', '', s.lower().replace('-', ' ')).strip()
DK = {}
for k in D: DK.setdefault(key(k), k)
def find(*names):
    for n in names:
        if not n: continue
        n = re.sub(r'\.(l|r)$', '', n).strip('()')
        for cand in (n, n + ' muscle', n + ' bone', re.sub(r' muscle$', '', n), n.replace('sacroiliac', 'sacro-iliac')):
            k = DK.get(key(cand))
            if k and len(D[k]) > 80: return k
    return None
ALIAS = {'Trapezius': 'Trapezius muscle', 'Latissimus dorsi': 'Latissimus dorsi muscle', 'Gluteus maximus': 'Gluteus maximus muscle', 'Sternocleidomastoid': 'Sternocleidomastoid muscle',
         'Brachial plexus': 'Brachial plexus', 'Spinal cord': 'Spinal cord', 'Intercostal nerves (T1–T12)': 'Intercostal nerves', 'Accessory nerve (CN XI)': 'Accessory nerve (XI)',
         'Facial nerve (CN VII)': 'Facial nerve (VII)', 'Mandibular nerve (CN V3)': 'Mandibular nerve', 'Intervertebral discs': 'Intervertebral disc', 'Heart': 'Heart', 'Aorta': 'Aorta'}
def clean(t):
    t = re.sub(r'^[A-Z0-9 ,()\'\-–/&.]+\n', '', t.strip())             # drop the upper-case title line
    t = re.sub(r'\n{3,}', '\n\n', t)
    parts = re.split(r'\n== (.+?) ==\n', t)                             # intro, title, body, title, body...
    intro = ' '.join(x.strip() for x in parts[0].split('\n') if x.strip())
    secs = []
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip(); body = ' '.join(x.strip() for x in parts[i + 1].split('\n') if x.strip() and not x.startswith('==='))
        if title.lower() in ('see also', 'references', 'external links', 'additional images', 'gallery', 'notes', 'history', 'etymology', 'other animals', 'in other animals'): continue
        if body: secs.append([title, body[:900]])
        if len(secs) >= 3: break
    return [intro[:900], secs]
out = {}; srcs = {}
for s in M['structures']:
    k = s['k']
    if k in out: continue
    z = None
    if s['id'] in A:
        zs = [x[1] for x in A[s['id']] if x[1]]
        z = find(*zs) if zs else None
    z = z or find(ALIAS.get(s['name']), s['name'])
    if z: out[k] = clean(D[z])
for n in N + V:
    if n['k'] in out: continue
    z = find(ALIAS.get(n['name']), n['name'], *([] if '&' not in n['name'] else n['name'].replace(' & ', '|').split('|')))
    if z: out[n['k']] = clean(D[z])
out = {k: v for k, v in out.items() if len(v[0]) > 40}
json.dump(out, open(R + '/site/defs.json', 'w'), ensure_ascii=False, separators=(',', ':'))
allk = {s['k'] for s in M['structures']} | {n['k'] for n in N + V}
print('structures with About text', len(out), 'of', len(allk), ' MB', round(os.path.getsize(R + '/site/defs.json') / 1e6, 2))
miss = sorted(allk - set(out)); print(len(miss), miss[:60])
