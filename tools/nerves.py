"""Nerve routes in BodyParts3D space (mm; -x = right, -y = anterior, +z = up).
Right-side routes are authored by hand from bone/muscle landmarks and mirrored for the left."""
import numpy as np, json, os
from lm import V, canal, names
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- spinal canal centreline from the real vertebrae ----
vert = ['axis'] + [f'{o} cervical vertebra' for o in ['third','fourth','fifth','sixth','seventh']] + \
       [f'{o} thoracic vertebra' for o in ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth']] + \
       [f'{o} lumbar vertebra' for o in ['first','second','third','fourth','fifth']]
CAN = []
for v in vert:
    if v in names:
        c = canal(v)
        if c is not None: CAN.append(c)
CAN = sorted(CAN, key=lambda p: -p[2])
canz = np.array([p[2] for p in CAN]); cany = np.array([p[1] for p in CAN])
def cy(z): return float(np.interp(-z, -canz, cany))
def cp(z, x=0): return [x, cy(z), z]

N = []   # entries: id, name, r, paths, bilateral
def nerve(id, name, r, *paths, bil=True): N.append({'id': id, 'name': name, 'r': r, 'paths': [list(map(list, p)) for p in paths], 'bil': bil})

# Spinal cord + cauda equina (midline)
top = [0, -72, 1492]
cord = [top] + [cp(z) for z in np.arange(1470, 1029, -15)] + [cp(1030)]
nerve('spinal-cord', 'Spinal cord', 4.2, cord, bil=False)
cauda = [cp(1035)] + [cp(z) for z in [1000, 970, 945]] + [[0, -40, 905], [0, -28, 860]]
nerve('cauda-equina', 'Cauda equina', 2.2, cauda, bil=False)

# ---- Brachial plexus (roots C5–T1 -> trunks -> cords) ----
roots = []
for z in [1422, 1406, 1392, 1378, 1364]:
    roots.append([cp(z), [-22, cy(z) - 12, z - 4], [-42, -92, z - 12], [-62, -94, 1356 + (z - 1392) * 0.35], [-92, -96, 1336], [-118, -96, 1302], [-134, -93, 1284]])
nerve('brachial-plexus', 'Brachial plexus', 2.0, *roots)
A = [-134, -93, 1284]   # axilla, cords around the axillary artery
nerve('musculocutaneous', 'Musculocutaneous nerve', 1.7, [A, [-150, -90, 1262], [-162, -84, 1238], [-186, -84, 1180], [-206, -80, 1110], [-226, -80, 1062], [-238, -92, 1000], [-250, -100, 940]])
nerve('median', 'Median nerve', 2.0, [A, [-152, -92, 1250], [-170, -86, 1180], [-188, -82, 1110], [-204, -80, 1062], [-218, -88, 1010], [-232, -102, 935], [-244, -118, 860], [-252, -132, 808], [-258, -140, 780]],
      [[-258, -140, 780], [-268, -138, 792], [-276, -134, 800]],          # recurrent (thenar) branch
      [[-258, -140, 780], [-262, -150, 745], [-268, -165, 715]],
      [[-258, -140, 780], [-252, -150, 745], [-252, -165, 715]])
nerve('ulnar', 'Ulnar nerve', 1.9, [A, [-150, -86, 1250], [-160, -76, 1190], [-170, -64, 1110], [-176, -52, 1064], [-188, -62, 1030], [-206, -82, 975], [-226, -106, 880], [-236, -124, 815], [-240, -134, 795]],
      [[-240, -134, 795], [-244, -148, 760], [-242, -165, 720]])
nerve('radial', 'Radial nerve', 2.1, [A, [-146, -78, 1272], [-160, -58, 1240], [-182, -47, 1200], [-204, -48, 1160], [-222, -58, 1118], [-234, -70, 1080], [-238, -74, 1052]],
      [[-238, -74, 1052], [-244, -62, 1012], [-252, -56, 960], [-258, -66, 890], [-262, -82, 840]],    # deep branch / posterior interosseous
      [[-238, -74, 1052], [-250, -88, 975], [-262, -104, 880], [-270, -114, 820], [-276, -118, 790]])  # superficial branch
nerve('axillary', 'Axillary nerve', 1.6, [A, [-148, -68, 1296], [-160, -54, 1306], [-176, -56, 1304], [-184, -72, 1296], [-180, -92, 1290]])
nerve('long-thoracic', 'Long thoracic nerve', 1.1, [[-30, -80, 1395], [-62, -82, 1352], [-100, -84, 1310], [-126, -86, 1262], [-138, -84, 1210], [-141, -80, 1150]])
nerve('suprascapular', 'Suprascapular nerve', 1.3, [[-62, -94, 1362], [-96, -78, 1352], [-122, -60, 1350], [-142, -46, 1340], [-158, -36, 1318], [-150, -22, 1290]])
nerve('dorsal-scapular', 'Dorsal scapular nerve', 1.1, [[-25, -78, 1415], [-48, -62, 1398], [-62, -40, 1376], [-72, -18, 1335], [-78, -6, 1280], [-84, -2, 1225]])
nerve('thoracodorsal', 'Thoracodorsal nerve', 1.2, [[-128, -92, 1290], [-140, -66, 1262], [-148, -46, 1220], [-148, -36, 1165]])
nerve('subscapular', 'Subscapular nerves', 1.0, [[-118, -94, 1302], [-124, -76, 1300], [-128, -62, 1290]], [[-126, -90, 1290], [-136, -62, 1262], [-142, -42, 1240]])
nerve('pectoral', 'Medial & lateral pectoral nerves', 1.0, [[-112, -98, 1312], [-110, -120, 1300], [-100, -146, 1290]], [[-128, -96, 1290], [-118, -128, 1278], [-104, -150, 1262]])

# ---- Cranial & cervical ----
nerve('accessory', 'Accessory nerve (CN XI)', 1.3, [[-24, -66, 1494], [-36, -88, 1462], [-44, -96, 1440], [-56, -70, 1410], [-70, -40, 1384], [-72, -22, 1350], [-52, -10, 1300]])
fac0 = [-40, -104, 1492]; par = [-52, -124, 1490]
nerve('facial', 'Facial nerve (CN VII)', 1.2, [fac0, par, [-56, -136, 1520], [-60, -142, 1545]], [par, [-58, -150, 1510], [-52, -162, 1518]],
      [par, [-54, -150, 1494], [-44, -166, 1490]], [par, [-48, -140, 1470], [-38, -158, 1458]], [par, [-46, -126, 1462], [-44, -128, 1438]])
v3 = [-24, -112, 1508]
nerve('mandibular', 'Mandibular nerve (CN V3)', 1.2, [v3, [-36, -116, 1500], [-46, -120, 1490]], [v3, [-40, -118, 1516], [-54, -120, 1532]], [v3, [-30, -130, 1490], [-38, -150, 1470]])
nerve('phrenic', 'Phrenic nerve', 1.2, [[-28, -78, 1428], [-34, -100, 1400], [-34, -104, 1365], [-30, -110, 1330], [-42, -128, 1280], [-55, -140, 1220], [-60, -134, 1175]])

# ---- Intercostal / thoracoabdominal nerves from the real ribs ----
ORD = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth']
ic_paths = []
for i, o in enumerate(ORD):
    r = V(f'right {o} rib')
    ang = np.arctan2(r[:, 1] + 95, -r[:, 0])
    bins = np.linspace(ang.max() - 0.02, ang.min() + 0.02, 22)
    pts = []
    for a0, a1 in zip(bins[:-1], bins[1:]):
        m = (ang <= a0) & (ang > a1)
        if m.sum() < 8: continue
        s = r[m]; c = s.mean(0); zlow = np.percentile(s[:, 2], 8)
        cx, cyy = c[0] * 0.96, -95 + (c[1] + 95) * 0.96
        pts.append([cx, cyy, zlow + 1.5])
    if len(pts) < 4: continue
    pts = pts[::2] + ([pts[-1]] if len(pts) % 2 == 0 else [])
    p0 = pts[0]; z0 = p0[2]
    path = [cp(z0 + 8), [-14, cy(z0 + 8) + 2, z0 + 4]] + pts
    if i >= 6:   # thoracoabdominal nerves continue to the rectus sheath
        e = pts[-1]; path += [[e[0] * 0.75, e[1] - 6, e[2] - 28], [-42, -168 + (i - 6) * 4, e[2] - 55 - (i - 6) * 6]]
    ic_paths.append(path)
nerve('intercostal', 'Intercostal nerves (T1–T12)', 0.9, *ic_paths)

# ---- Lumbar plexus ----
nerve('femoral', 'Femoral nerve', 1.9, [cp(1020, -14), [-34, -92, 990], [-46, -100, 940], [-62, -112, 885], [-70, -132, 848], [-72, -146, 818], [-74, -146, 790]],
      [[-74, -146, 790], [-92, -140, 740], [-98, -138, 690]], [[-74, -146, 790], [-80, -150, 740], [-80, -146, 690]],
      [[-74, -146, 790], [-62, -132, 720], [-56, -118, 640], [-50, -100, 540], [-44, -84, 440], [-50, -76, 330], [-54, -80, 200], [-54, -86, 80], [-58, -110, 32]])
nerve('obturator', 'Obturator nerve', 1.5, [cp(1015, -12), [-26, -84, 975], [-36, -82, 915], [-44, -96, 850], [-46, -104, 800], [-50, -112, 760]],
      [[-50, -112, 760], [-54, -124, 700], [-54, -122, 640]], [[-50, -112, 760], [-48, -100, 700], [-50, -92, 620]])
# ---- Sacral plexus ----
sp = [-34, -46, 868]
nerve('sciatic', 'Sciatic nerve', 3.0, [[-18, -50, 930], [-28, -48, 890], sp, [-58, -40, 838], [-76, -36, 810], [-88, -42, 778], [-88, -45, 720], [-84, -47, 640], [-80, -47, 560], [-78, -46, 480]])
nerve('tibial', 'Tibial nerve', 2.2, [[-78, -46, 480], [-74, -42, 430], [-74, -46, 380], [-74, -52, 300], [-70, -56, 210], [-64, -56, 130], [-58, -52, 75], [-60, -62, 40]],
      [[-60, -62, 40], [-66, -95, 14], [-72, -140, 6], [-78, -185, 3]], [[-60, -62, 40], [-80, -90, 10], [-104, -130, 6], [-116, -160, 4]])
nerve('common-fibular', 'Common fibular nerve', 1.8, [[-78, -46, 480], [-92, -44, 440], [-108, -46, 405], [-120, -52, 378], [-122, -62, 362]],
      [[-122, -62, 362], [-126, -66, 300], [-120, -76, 200], [-110, -88, 100], [-100, -112, 45], [-96, -150, 30]],
      [[-122, -62, 362], [-112, -76, 340], [-98, -76, 260], [-90, -80, 160], [-82, -92, 70], [-80, -130, 40], [-80, -170, 22]])
nerve('superior-gluteal', 'Superior gluteal nerve', 1.3, [[-30, -46, 892], [-62, -42, 882], [-92, -52, 885], [-116, -72, 880], [-128, -100, 866]])
nerve('inferior-gluteal', 'Inferior gluteal nerve', 1.3, [[-34, -44, 860], [-62, -30, 832], [-76, -12, 818], [-74, 0, 790]])
nerve('pudendal', 'Pudendal nerve', 1.0, [[-28, -44, 872], [-46, -38, 832], [-44, -56, 800], [-34, -80, 785], [-14, -100, 790]])

out = []
for n in N:
    if n['bil']:
        for side, sx in (('R', 1), ('L', -1)):
            out.append({'id': n['id'] + '-' + side, 'k': n['id'], 'name': n['name'], 'side': side, 'r': n['r'],
                        'paths': [[[round(p[0] * sx, 1), round(p[1], 1), round(p[2], 1)] for p in path] for path in n['paths']]})
    else:
        out.append({'id': n['id'], 'k': n['id'], 'name': n['name'], 'side': '', 'r': n['r'],
                    'paths': [[[round(float(c), 1) for c in p] for p in path] for path in n['paths']]})
json.dump(out, open(os.path.join(HERE, '..', 'site', 'nerves.json'), 'w'), separators=(',', ':'))
print(len(out), 'nerve structures', sum(len(n['paths']) for n in out), 'paths')
