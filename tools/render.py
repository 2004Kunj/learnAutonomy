"""Point-splat z-buffer renderer to sanity-check meshes + nerves. usage: render.py view(front|back|right|left) out.png [zmin zmax xmin xmax] [hide_kinds]"""
import numpy as np, json, gzip, sys, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.join(HERE, '..', 'site')
meta = json.load(open(os.path.join(SITE, 'manifest.json')))
import base64
blob = gzip.decompress(base64.b64decode(open(os.path.join(SITE, 'anatomy.txt'),'rb').read()))
P = np.frombuffer(blob, dtype=np.uint16, count=meta['nv'] * 3).reshape(-1, 3).astype(np.float32) * np.array(meta['sc']) + np.array(meta['lo'])
off = meta['posBytes'] + (2 if meta['posBytes'] % 4 else 0)
I = np.frombuffer(blob, dtype=np.uint16, count=meta['ni'], offset=off).astype(np.int64)
AUX = np.frombuffer(blob, np.uint8, meta['nv']*2, meta['auxOff']).reshape(-1,2).astype(np.float32)/255 if 'auxOff' in meta else None
kind = {s['id']: s['kind'] for s in meta['structures']}
view = sys.argv[1]; out = sys.argv[2]
win = [float(x) for x in sys.argv[3:7]] if len(sys.argv) >= 7 else [-20, 1660, -340, 340]
hide = sys.argv[7].split(',') if len(sys.argv) >= 8 else []
cols = {'artery':(220,40,40),'vein':(50,80,200),'organ':(150,40,50),'muscle': (176, 70, 62), 'bone': (225, 215, 190), 'tendon': (230, 230, 220), 'disc': (150, 170, 200), 'cartilage': (200, 220, 230)}
T = []; C = []
for m in meta['meshes']:
    k = kind[m[0]]
    if k in hide: continue
    vo, vc, io, ic = m[2], m[3], m[4], m[5]
    tri = P[vo + I[io:io + ic].reshape(-1, 3)] + np.array(m[8] if len(m)>8 else [0,0,0])*float(os.environ.get('EX','0'))
    col = np.tile(np.array(cols[k],np.float32), (len(tri), 1))
    if AUX is not None and os.environ.get('CAD'):
        a = AUX[vo + I[io:io + ic].reshape(-1, 3)].mean(1)
        base = {'muscle':(96,66,64),'bone':(220,207,174),'tendon':(201,194,179)}.get(k,(150,140,130))
        col = np.tile(np.array(base,np.float32),(len(tri),1))
        if k=='muscle': col = col*(1-a[:,1:2]*.85) + np.array([218,207,174],np.float32)*a[:,1:2]*.85
        col = col*(1-a[:,0:1]*.6)
    T.append(tri); C.append(col)
T = np.concatenate(T); C = np.concatenate(C).astype(np.float32)
cen = T.mean(1); T4 = np.concatenate([T.mean(1,keepdims=True), (T*0.6+T.mean(1,keepdims=True)*0.4)],1); nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
# view transform: u (screen x), depth d (smaller = closer)
if view == 'front': u, d, L = cen[:, 0], cen[:, 1], np.array([0, -1, .3])
elif view == 'back': u, d, L = -cen[:, 0], -cen[:, 1], np.array([0, 1, .3])
elif view == 'right': u, d, L = cen[:, 1], cen[:, 0], np.array([-1, 0, .3])
else: u, d, L = -cen[:, 1], -cen[:, 0], np.array([1, 0, .3])
L = L / np.linalg.norm(L)
sh = np.abs(nrm @ L) * 0.8 + 0.2
BW=np.array([[1/3,1/3,1/3],[.6,.2,.2],[.2,.6,.2],[.2,.2,.6],[.8,.1,.1],[.1,.8,.1],[.1,.1,.8],[.45,.45,.1],[.1,.45,.45],[.45,.1,.45]],np.float32)
T4=np.einsum('sk,tkd->tsd',BW,T); nrep=len(BW)
cen = T4.reshape(-1,3); sh=np.repeat(sh,nrep); C=np.repeat(C,nrep,0)
if view == 'front': u, d = cen[:, 0], cen[:, 1]
elif view == 'back': u, d = -cen[:, 0], -cen[:, 1]
elif view == 'right': u, d = cen[:, 1], cen[:, 0]
else: u, d = -cen[:, 1], -cen[:, 0]
zmin, zmax, xmin, xmax = win; S = float(os.environ.get('H','900')) / (zmax - zmin)
W = int((xmax - xmin) * S); H = int(os.environ.get('H','900'))
px = ((u - xmin) * S).astype(int); py = ((zmax - cen[:, 2]) * S).astype(int)
ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
zb = np.full((H, W), 1e9); img = np.full((H, W, 3), 30.0)
order = np.argsort(-d[ok]); pxo, pyo, co, so = px[ok][order], py[ok][order], C[ok][order], sh[ok][order]
for dx in (-1,0, 1):
    for dy in (-1,0, 1):
        img[np.clip(pyo + dy, 0, H - 1), np.clip(pxo + dx, 0, W - 1)] = co * so[:, None]
# nerves on top
nv = json.load(open(os.path.join(SITE, 'nerves.json')))+json.load(open(os.path.join(SITE, 'vessels.json')))
from PIL import ImageDraw
im = Image.fromarray(img.clip(0, 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
for n in ([] if os.environ.get('NONERVE') else [x for x in nv if not os.environ.get('VONLY') or x.get('kind')=='vein']):
    for p in n['paths']:
        p = np.array(p)
        if view == 'front': uu = p[:, 0]
        elif view == 'back': uu = -p[:, 0]
        elif view == 'right': uu = p[:, 1]
        else: uu = -p[:, 1]
        pts = list(zip(((uu - xmin) * S), ((zmax - p[:, 2]) * S)))
        dr.line(pts, fill={'artery':(255,60,60),'vein':(80,140,255)}.get(n.get('kind'),(255,225,40)), width=max(1, int(n['r'] * S * 1.2)))
im.save(out); print('saved', out, im.size)
