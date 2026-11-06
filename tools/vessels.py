"""Traced limb/neck vessels (right side authored, mirrored). Superficial veins follow the real muscle surface."""
import numpy as np, json, os
from lm import V
HERE = os.path.dirname(os.path.abspath(__file__))

def surf(muscles, z, d, out=3.0):
    vs = np.concatenate([V(m) for m in muscles]); s = vs[np.abs(vs[:, 2] - z) < 5]
    d = np.array(d, float); d /= np.linalg.norm(d); c = s.mean(0)
    i = np.argmax((s[:, :2] - c[:2]) @ d[:2]); p = s[i].copy(); p[:2] += d[:2] * out; return [round(float(x), 1) for x in p]

ARM = ['right biceps brachii' if False else 'long head of right biceps brachii', 'short head of right biceps brachii', 'right brachialis', 'long head of right triceps brachii', 'lateral head of right triceps brachii', 'medial head of right triceps brachii', 'right coracobrachialis']
FORE = ['right brachioradialis', 'right flexor carpi radialis', 'humeroulnar head of right flexor digitorum superficialis', 'humeral head of right flexor carpi ulnaris', 'right palmaris longus', 'right extensor carpi radialis longus', 'right abductor pollicis longus', 'right flexor digitorum profundus', 'humeral head of right pronator teres']
LEG = ['medial head of right gastrocnemius', 'lateral head of right gastrocnemius', 'right soleus', 'right tibialis anterior', 'right fibularis longus', 'right flexor digitorum longus']
THIGH = ['right sartorius', 'right gracilis', 'right vastus medialis', 'right adductor longus', 'right adductor magnus', 'right semimembranosus', 'right semitendinosus']

V_ = []
def ves(id, name, kind, r, *paths, region=None, bil=True): V_.append({'id': id, 'name': name, 'kind': kind, 'r': r, 'paths': paths, 'region': region, 'bil': bil})

# ---- arteries ----
ves('axillary-a', 'Axillary artery', 'artery', 2.6, [[-82, -103, 1349], [-104, -100, 1326], [-124, -95, 1301], [-138, -91, 1280], [-150, -88, 1256]])
ves('brachial-a', 'Brachial artery', 'artery', 2.2, [[-150, -88, 1256], [-168, -86, 1182], [-186, -83, 1110], [-202, -84, 1064], [-212, -88, 1040]])
ves('radial-a', 'Radial artery', 'artery', 1.6, [[-212, -88, 1040], [-226, -98, 972], [-242, -110, 892], [-256, -124, 822], [-262, -130, 800]])
ves('ulnar-a', 'Ulnar artery', 'artery', 1.6, [[-212, -88, 1040], [-218, -102, 980], [-228, -112, 900], [-236, -126, 820], [-241, -136, 797], [-252, -148, 766], [-264, -150, 760]])
ves('femoral-a', 'Femoral artery', 'artery', 3.0, [[-49, -158, 828], [-56, -146, 792], [-60, -132, 722], [-58, -116, 642], [-56, -100, 562], [-60, -72, 482]])
ves('deep-femoral-a', 'Deep artery of the thigh', 'artery', 2.0, [[-56, -144, 780], [-66, -126, 720], [-72, -104, 640], [-76, -86, 560]])
ves('popliteal-a', 'Popliteal artery', 'artery', 2.4, [[-60, -72, 482], [-70, -50, 440], [-73, -50, 385], [-74, -54, 350]])
ves('ant-tibial-a', 'Anterior tibial artery', 'artery', 1.5, [[-74, -54, 350], [-90, -70, 332], [-90, -78, 242], [-85, -84, 122], [-80, -92, 62]])
ves('dorsalis-pedis', 'Dorsalis pedis artery', 'artery', 1.2, [[-80, -92, 62], [-80, -118, 42], [-80, -160, 25]])
ves('post-tibial-a', 'Posterior tibial artery', 'artery', 1.6, [[-74, -54, 350], [-72, -55, 250], [-66, -56, 140], [-58, -57, 72], [-64, -88, 20]])
ves('fibular-a', 'Fibular artery', 'artery', 1.2, [[-74, -55, 330], [-94, -57, 250], [-100, -55, 120], [-104, -50, 60]])
ves('internal-carotid', 'Internal carotid artery', 'artery', 2.0, [[-16, -108, 1385], [-18, -100, 1420], [-22, -90, 1460], [-24, -82, 1494]])
ves('external-carotid', 'External carotid artery', 'artery', 1.6, [[-16, -108, 1385], [-22, -114, 1420], [-32, -120, 1450], [-42, -118, 1482], [-50, -112, 1520]])
ves('vertebral-a', 'Vertebral artery', 'artery', 1.3, [[-30, -100, 1356], [-28, -90, 1380], [-25, -84, 1420], [-24, -80, 1460], [-14, -74, 1490]])
# ---- veins ----
ves('axillary-v', 'Axillary vein', 'vein', 3.0, [[-152, -94, 1256], [-138, -97, 1282], [-124, -102, 1302], [-104, -108, 1326], [-87, -111, 1344]])
ves('brachial-v', 'Brachial veins', 'vein', 1.6, [[-214, -84, 1040], [-204, -80, 1064], [-188, -79, 1110], [-170, -82, 1182], [-152, -94, 1256]])
ceph = [surf(FORE, z, (-1, -0.9)) for z in (812, 860, 920, 980, 1030)] + [surf(ARM, z, (-1, -1.1)) for z in (1070, 1130, 1190, 1240)] + [[-158, -118, 1290], [-130, -112, 1316], [-104, -108, 1326]]
ves('cephalic', 'Cephalic vein', 'vein', 1.6, ceph)
bas = [surf(FORE, z, (0.9, -0.8)) for z in (806, 860, 920, 980, 1040)] + [surf(ARM, z, (1, -0.6)) for z in (1080, 1130)] + [[-178, -82, 1175], [-166, -88, 1215], [-152, -94, 1256]]
ves('basilic', 'Basilic vein', 'vein', 1.6, bas)
c1 = surf(FORE, 1028, (-0.5, -1)); c2 = surf(ARM, 1070, (0.6, -1))
ves('median-cubital', 'Median cubital vein', 'vein', 1.4, [ceph[4], c1, c2, bas[5]])
ves('femoral-v', 'Femoral vein', 'vein', 3.4, [[-42, -148, 828], [-48, -140, 792], [-52, -126, 722], [-53, -110, 642], [-53, -96, 562], [-62, -68, 482]])
ves('popliteal-v', 'Popliteal vein', 'vein', 2.8, [[-62, -68, 482], [-68, -44, 440], [-70, -44, 385], [-72, -48, 350]])
gs = [[-52, -88, 56], [-50, -80, 90]] + [surf(LEG, z, (1, -0.25)) for z in (140, 220, 300, 360)] + [surf(THIGH, z, (1, 0.15)) for z in (430, 520)] + [surf(THIGH, z, (0.9, -0.6)) for z in (610, 700, 770)] + [[-50, -150, 800], [-46, -148, 812]]
ves('great-saphenous', 'Great saphenous vein', 'vein', 1.7, gs)
ss = [[-108, -34, 48], [-102, -24, 90]] + [surf(LEG, z, (-0.1, 1)) for z in (150, 220, 290, 350)] + [[-72, -36, 400], [-70, -44, 410]]
ves('small-saphenous', 'Small saphenous vein', 'vein', 1.4, ss)
ves('ijv-upper', 'Internal jugular vein (upper)', 'vein', 3.2, [[-26, -114, 1393], [-28, -104, 1430], [-28, -92, 1462], [-26, -80, 1492]])
ves('external-jugular', 'External jugular vein', 'vein', 1.3, [[-50, -122, 1472], [-50, -112, 1430], [-52, -100, 1390], [-62, -104, 1358], [-80, -110, 1346]])


# ======== expanded venous system ========
import json as _j
NV = {n['id']: n for n in _j.load(open(os.path.join(HERE, '..', 'site', 'nerves.json'))) if n['side'] in ('R', '')}
def nv(k, i=0): return NV[k + '-R']['paths'][i] if k + '-R' in NV else NV[k]['paths'][i]
def off(path, d): return [[round(p[0] + d[0], 1), round(p[1] + d[1], 1), round(p[2] + d[2], 1)] for p in path]
def apath(k): return next(v for v in V_ if v['id'] == k)['paths'][0]
def top(muscles, x0, y0, out=3.0):
    vs = np.concatenate([V(m) for m in muscles]); s_ = vs[(np.abs(vs[:, 0] - x0) < 6) & (np.abs(vs[:, 1] - y0) < 6)]
    if not len(s_): return [x0, y0, 40.0]
    return [round(x0, 1), round(y0, 1), round(float(s_[:, 2].max()) + out, 1)]
def back(muscles, x0, z0, out=3.0):
    vs = np.concatenate([V(m) for m in muscles]); s_ = vs[(np.abs(vs[:, 0] - x0) < 6) & (np.abs(vs[:, 2] - z0) < 6)]
    if not len(s_): return None
    return [round(x0, 1), round(float(s_[:, 1].max()) + out, 1), round(z0, 1)]
# venae comitantes (paired deep veins hugging each artery)
for k, a, nm, rg in [('radial-v', 'radial-a', 'Radial veins', 'Forearm'), ('ulnar-v', 'ulnar-a', 'Ulnar veins', 'Forearm'), ('ant-tibial-v', 'ant-tibial-a', 'Anterior tibial veins', 'Leg'),
                     ('post-tibial-v', 'post-tibial-a', 'Posterior tibial veins', 'Leg'), ('fibular-v', 'fibular-a', 'Fibular veins', 'Leg'), ('deep-femoral-v', 'deep-femoral-a', 'Deep femoral vein', 'Thigh')]:
    p = apath(a); ves(k, nm, 'vein', 1.1, off(p, (2.6, 1.2, 0)), off(p, (-2.6, -1.2, 0)), region=rg)
HANDM = ['right ' + o + ' metacarpal bone' for o in ['first', 'second', 'third', 'fourth', 'fifth']] + ['set of dorsal interossei of right hand']
dv = [back(HANDM, x, 772) for x in (-278, -272, -265, -258, -251, -245)]; dv = [p for p in dv if p]
ves('dorsal-venous-hand', 'Dorsal venous network (hand)', 'vein', 1.0, [ceph[0]] + dv + [bas[0]], region='Hand')
ves('palmar-venous-arch', 'Palmar venous arches', 'vein', 0.9, off(apath('ulnar-a')[-3:], (0, -2.5, 1.5)), region='Hand')
mav = [surf(FORE, z, (0.15, -1)) for z in (818, 870, 930, 990, 1030)]
ves('median-antebrachial', 'Median antebrachial vein', 'vein', 1.1, mav, region='Forearm')
ves('ant-circ-humeral-v', 'Anterior circumflex humeral vein', 'vein', 1.0, [[-150, -95, 1298], [-162, -92, 1303], [-176, -80, 1306]], region='Shoulder')
ves('post-circ-humeral-v', 'Posterior circumflex humeral vein', 'vein', 1.1, off(nv('axillary'), (0, 2, -3)), region='Shoulder')
ves('subscapular-v', 'Subscapular & circumflex scapular veins', 'vein', 1.3, [[-138, -95, 1278], [-133, -72, 1270], [-128, -55, 1256]], [[-133, -72, 1270], [-141, -46, 1265], [-125, -24, 1270]], region='Shoulder')
ves('thoracodorsal-v', 'Thoracodorsal vein', 'vein', 1.2, off(nv('thoracodorsal'), (-2.5, 0, 0)), region='Back')
ves('lateral-thoracic-v', 'Lateral thoracic vein', 'vein', 1.2, [[-128, -112, 1150], [-133, -102, 1215], [-136, -97, 1280]], region='Thorax')
ves('suprascapular-v', 'Suprascapular vein', 'vein', 1.1, [[-62, -104, 1358]] + off(nv('suprascapular')[1:], (0, 0, 3)), region='Shoulder')
ves('transverse-cervical-v', 'Transverse cervical vein', 'vein', 1.0, [[-62, -104, 1358], [-72, -80, 1368], [-78, -50, 1372]], region='Neck')
ves('anterior-jugular', 'Anterior jugular vein', 'vein', 1.0, [[-10, -150, 1460], [-12, -146, 1420], [-16, -141, 1385], [-28, -133, 1352], [-50, -113, 1348]], region='Neck')
ves('facial-v', 'Facial vein', 'vein', 1.2, [[-16, -172, 1525], [-28, -170, 1495], [-40, -160, 1470], [-46, -140, 1448], [-38, -121, 1428], [-30, -112, 1418]], region='Head')
ves('retromandibular-v', 'Retromandibular vein', 'vein', 1.2, [[-46, -116, 1510], [-47, -119, 1470], [-42, -118, 1440], [-38, -121, 1428]], region='Head')
ves('superficial-temporal-v', 'Superficial temporal vein', 'vein', 1.0, [[-46, -116, 1510], [-62, -126, 1525], [-66, -130, 1560], [-62, -116, 1595]], region='Head')
ves('vertebral-v', 'Vertebral vein', 'vein', 1.2, off(apath('vertebral-a'), (-2.2, 1.5, 0)), region='Neck')
ves('internal-thoracic-v', 'Internal thoracic & superior epigastric veins', 'vein', 1.3, [[-25, -128, 1320], [-28, -150, 1300], [-30, -168, 1250], [-30, -175, 1200], [-35, -180, 1170], [-40, -177, 1120], [-45, -181, 1050], [-45, -181, 1010]], region='Thorax')
ves('inferior-epigastric-v', 'Inferior epigastric vein', 'vein', 1.3, [[-44, -141, 838], [-50, -160, 880], [-48, -175, 940], [-45, -181, 1005]], region='Abdomen')
ves('superficial-epigastric-v', 'Superficial epigastric vein', 'vein', 1.0, [[-50, -150, 805], [-54, -168, 832], [-58, -196, 882], [-62, -211, 940], [-60, -214, 1000]], region='Abdomen')
ves('thoracoepigastric-v', 'Thoracoepigastric vein', 'vein', 1.0, [[-60, -214, 1000], [-95, -191, 1060], [-120, -151, 1130], [-134, -111, 1200], [-137, -101, 1250], [-136, -97, 1281]], region='Thorax')
ves('lumbar-v', 'Lumbar veins & ascending lumbar vein', 'vein', 1.1, *[[[-12, -112, z], [-30, -96, z], [-42, -76, z]] for z in (1040, 1012, 985, 958)], [[-25, -96, 930], [-28, -92, 980], [-28, -90, 1030], [-22, -96, 1062], [-14, -101, 1078]], region='Back')
gp = nv('superior-gluteal'); ves('sup-gluteal-v', 'Superior gluteal veins', 'vein', 1.3, off(gp, (0, -2, 2.5)), region='Hip')
ves('inf-gluteal-v', 'Inferior gluteal veins', 'vein', 1.3, off(nv('inferior-gluteal'), (0, -2, 2.5)), region='Hip')
ves('internal-pudendal-v', 'Internal pudendal vein', 'vein', 1.1, off(nv('pudendal'), (0, -2, 2)), region='Pelvis')
ves('obturator-v', 'Obturator vein', 'vein', 1.1, off(nv('obturator'), (0, 2.5, -2)), region='Thigh')
ves('circ-femoral-v', 'Medial & lateral circumflex femoral veins', 'vein', 1.2, [[-60, -140, 776], [-85, -135, 770], [-110, -120, 765]], [[-58, -138, 776], [-54, -110, 770], [-70, -80, 775]], region='Thigh')
THM = ['right rectus femoris', 'right vastus lateralis', 'right sartorius', 'right tensor fasciae latae', 'right vastus medialis']
acc = [surf(THM, z, (-0.35, -1)) for z in (560, 640, 720)] + [[-48, -150, 790]]
ves('accessory-saphenous', 'Accessory saphenous vein', 'vein', 1.0, acc, region='Thigh')
ves('perforating-v', 'Perforating veins (leg)', 'vein', 0.9, [gs[2], [-64, -58, 140]], [gs[3], [-70, -56, 222]], [gs[4], [-73, -54, 300]], region='Leg')
FOOTM = ['right ' + o + ' metatarsal bone' for o in ['first', 'second', 'third', 'fourth', 'fifth']] + ['right extensor digitorum brevis', 'right extensor hallucis brevis', 'right cuboid bone', 'navicular bone of right foot', 'right intermediate cuneiform bone']
dva = [top(FOOTM, x, y) for x, y in [(-62, -104), (-68, -126), (-80, -140), (-96, -138), (-110, -118), (-114, -90)]]
ves('dorsal-venous-arch', 'Dorsal venous arch (foot)', 'vein', 1.1, [[-52, -88, 56]] + dva + [[-110, -55, 44], [-108, -34, 48]], region='Foot')
tp = nv('tibial', 1); tl = nv('tibial', 2)
ves('plantar-v', 'Medial & lateral plantar veins', 'vein', 1.0, off(tp, (2.5, 0, 2)), off(tl, (0, 2.5, 2)), region='Foot')
# unilateral trunk veins
ves('azygos', 'Azygos vein', 'vein', 2.2, [[-14, -108, 1040], [-14, -100, 1078], [-14, -90, 1120], [-14, -70, 1200], [-14, -64, 1260], [-14, -62, 1300], [-18, -80, 1314], [-17, -100, 1305]], region='Thorax', bil=False)
ves('hemiazygos', 'Hemiazygos vein', 'vein', 1.6, [[14, -106, 1045], [14, -92, 1100], [14, -74, 1175], [5, -70, 1200], [-12, -66, 1206]], region='Thorax', bil=False)
ves('accessory-hemiazygos', 'Accessory hemiazygos vein', 'vein', 1.5, [[16, -80, 1322], [14, -68, 1300], [14, -70, 1240], [0, -72, 1226], [-12, -66, 1222]], region='Thorax', bil=False)
ves('portal-v', 'Hepatic portal vein', 'vein', 2.6, [[-5, -128, 1068], [-20, -125, 1095], [-40, -118, 1125]], region='Abdomen', bil=False)
ves('ima-v', 'Inferior mesenteric vein', 'vein', 1.4, [[20, -110, 1090], [35, -110, 1060], [45, -115, 1000], [40, -110, 950]], region='Abdomen', bil=False)
ves('hepatic-v', 'Hepatic veins', 'vein', 2.0, [[-24, -118, 1198], [-50, -125, 1185]], [[-18, -120, 1200], [-25, -140, 1195]], [[-12, -118, 1200], [5, -135, 1190]], region='Abdomen', bil=False)
ves('testicular-v-R', 'Right testicular vein', 'vein', 1.1, [[-10, -120, 1035], [-35, -120, 990], [-50, -125, 930], [-58, -145, 875], [-40, -160, 820], [-25, -160, 780]], region='Pelvis', bil=False)
ves('testicular-v-L', 'Left testicular vein', 'vein', 1.1, [[30, -110, 1052], [35, -118, 990], [50, -125, 930], [58, -145, 875], [40, -160, 820], [25, -160, 780]], region='Pelvis', bil=False)
# posterior intercostal veins: just above each intercostal nerve (VAN), draining to azygos (right) / hemiazygos systems (left)
icp = NV['intercostal-R']['paths']
ves('post-intercostal-v', 'Posterior intercostal veins', 'vein', 0.9, *[[[-14, -66, p[2][2] + 2.5]] + off(p[2:], (0, 0, 2.6)) for p in icp], region='Thorax')

# ======== arterial branches (companions of the veins above + named branches) ========
def vpath(k, i=0): return next(v for v in V_ if v['id'] == k)['paths'][i]
def A(id, name, r, *paths, region=None, bil=True): ves(id, name, 'artery', r, *paths, region=region, bil=bil)
A('thoracoacromial-a', 'Thoracoacromial artery', 1.3, [[-110, -99, 1320], [-112, -120, 1326]],
  [[-112, -120, 1326], [-140, -110, 1345], [-160, -82, 1350]], [[-112, -120, 1326], [-140, -121, 1320], [-156, -118, 1298]],
  [[-112, -120, 1326], [-100, -142, 1300], [-80, -160, 1280]], [[-112, -120, 1326], [-95, -121, 1341]], region='Shoulder')
A('superior-thoracic-a', 'Superior thoracic artery', 0.9, [[-92, -102, 1340], [-80, -125, 1325], [-70, -140, 1310]], region='Thorax')
A('lateral-thoracic-a', 'Lateral thoracic artery', 1.1, off(vpath('lateral-thoracic-v'), (2.5, -2.5, 0)), region='Thorax')
A('subscapular-a', 'Subscapular artery', 1.4, [[-138, -91, 1280], [-133, -70, 1268], [-128, -52, 1254]], region='Shoulder')
A('circumflex-scapular-a', 'Circumflex scapular artery', 1.0, off(vpath('subscapular-v', 1), (0, -2, -2.5)), region='Shoulder')
A('thoracodorsal-a', 'Thoracodorsal artery', 1.1, off(nv('thoracodorsal'), (2.5, 0, 0)), region='Back')
A('ant-circ-humeral-a', 'Anterior circumflex humeral artery', 0.9, off(vpath('ant-circ-humeral-v'), (0, -2.5, -2)), region='Shoulder')
A('post-circ-humeral-a', 'Posterior circumflex humeral artery', 1.1, off(nv('axillary'), (0, -2, 2.5)), region='Shoulder')
A('thyrocervical-trunk', 'Thyrocervical trunk', 1.4, [[-36, -100, 1360], [-38, -103, 1372]], region='Neck')
A('suprascapular-a', 'Suprascapular artery', 1.1, [[-38, -103, 1372], [-62, -102, 1362]] + off(nv('suprascapular')[1:], (0, 0, 5.5)), region='Shoulder')
A('transverse-cervical-a', 'Transverse cervical artery', 1.0, [[-38, -103, 1372]] + off(vpath('transverse-cervical-v')[1:], (0, 0, 3)), region='Neck')
A('dorsal-scapular-a', 'Dorsal scapular artery', 1.0, off(nv('dorsal-scapular')[1:], (2, 0, 0)), region='Back')
A('costocervical-trunk', 'Costocervical trunk', 1.0, [[-30, -96, 1358], [-28, -82, 1372], [-24, -66, 1380]], region='Neck')
A('internal-thoracic-a', 'Internal thoracic & superior epigastric arteries', 1.3, off(vpath('internal-thoracic-v'), (4, -1, 0)), region='Thorax')
A('profunda-brachii', 'Deep artery of the arm (profunda brachii)', 1.3, [[-152, -88, 1250]] + off(nv('radial')[2:7], (2.5, 0, 2.5)), region='Arm')
A('superior-ulnar-collateral', 'Superior ulnar collateral artery', 0.9, [[-168, -86, 1185]] + off(nv('ulnar')[3:6], (2.5, 0, 0)), region='Arm')
A('inferior-ulnar-collateral', 'Inferior ulnar collateral artery', 0.8, [[-200, -84, 1080], [-190, -76, 1066], [-180, -66, 1060]], region='Arm')
A('radial-recurrent', 'Radial recurrent artery', 0.8, [[-220, -92, 1028], [-232, -80, 1048], [-236, -74, 1060]], region='Forearm')
A('ulnar-recurrent', 'Ulnar recurrent arteries', 0.8, [[-214, -94, 1028], [-200, -80, 1048], [-182, -62, 1062]], region='Forearm')
A('common-interosseous', 'Common interosseous artery', 1.1, [[-216, -96, 1022], [-224, -90, 1000]], region='Forearm')
A('anterior-interosseous-a', 'Anterior interosseous artery', 0.9, [[-224, -90, 1000], [-236, -93, 930], [-246, -104, 860], [-252, -112, 825]], region='Forearm')
A('posterior-interosseous-a', 'Posterior interosseous artery', 0.9, [[-224, -90, 1000], [-232, -76, 980], [-238, -72, 930], [-248, -86, 850]], region='Forearm')
ua = apath('ulnar-a'); ra = apath('radial-a')
A('superficial-palmar-arch', 'Superficial palmar arch', 1.0, [ua[-2], ua[-1], [-272, -152, 770], [-277, -146, 786]], region='Hand')
A('deep-palmar-arch', 'Deep palmar arch', 1.0, [ra[-1], [-258, -135, 782], [-248, -137, 776], [-240, -138, 781]], region='Hand')
A('genicular-a', 'Genicular arteries', 0.8, [[-71, -49, 430], [-55, -66, 432], [-48, -84, 428]], [[-73, -49, 430], [-96, -64, 432], [-108, -80, 428]],
  [[-73, -51, 385], [-58, -72, 378], [-52, -88, 372]], [[-74, -51, 385], [-100, -66, 380], [-110, -80, 375]], region='Leg')
A('sural-a', 'Sural arteries', 0.9, [[-73, -50, 400], [-82, -36, 372]], [[-71, -50, 400], [-62, -36, 372]], region='Leg')
A('ant-tibial-recurrent', 'Anterior tibial recurrent artery', 0.7, [[-90, -72, 330], [-94, -82, 352], [-92, -90, 368]], region='Leg')
A('plantar-a', 'Medial & lateral plantar arteries', 1.0, off(tp, (-2.5, 0, 1.5)), off(tl, (0, -2.5, 1.5)), region='Foot')
A('arcuate-a', 'Arcuate artery', 0.8, [[-80, -120, 40], [-95, -126, 34], [-110, -110, 30]], region='Foot')
A('superior-thyroid-a', 'Superior thyroid artery', 0.9, [[-18, -112, 1405], [-20, -130, 1395], [-15, -140, 1380]], region='Neck')
A('lingual-a', 'Lingual artery', 0.9, [[-22, -114, 1420], [-25, -135, 1440], [-18, -150, 1450]], region='Neck')
A('facial-a', 'Facial artery', 1.0, [[-25, -116, 1425], [-36, -138, 1446], [-45, -150, 1452], [-38, -165, 1480], [-22, -173, 1510]], region='Head')
A('occipital-a', 'Occipital artery', 0.9, [[-24, -110, 1440], [-40, -80, 1470], [-35, -30, 1505]], region='Head')
A('maxillary-a', 'Maxillary artery', 1.0, [[-42, -118, 1482], [-35, -125, 1490], [-25, -130, 1495]], region='Head')
A('superficial-temporal-a', 'Superficial temporal artery', 0.9, off(vpath('superficial-temporal-v'), (0, -2.5, 0)), region='Head')
A('post-intercostal-a', 'Posterior intercostal arteries', 0.8, *[[[6, -64, p[1][2] - 5]] + off(p[1:], (0, 0, -2.6)) for p in vpath_all] if (vpath_all := next(v for v in V_ if v['id'] == 'post-intercostal-v')['paths']) else [], region='Thorax')
A('lumbar-a', 'Lumbar arteries', 0.9, *[[[2, -100, p[0][2]]] + off(p[1:], (0, 0, 3)) for p in next(v for v in V_ if v['id'] == 'lumbar-v')['paths'][:4]], region='Back')
A('superficial-epigastric-a', 'Superficial epigastric artery', 0.8, off(vpath('superficial-epigastric-v'), (2.5, 0, 0)), region='Abdomen')
A('superficial-circumflex-iliac-a', 'Superficial circumflex iliac artery', 0.8, [[-56, -146, 792], [-80, -156, 822], [-100, -150, 870]], region='Hip')
A('external-pudendal-a', 'External pudendal arteries', 0.8, [[-56, -146, 792], [-40, -151, 790], [-20, -151, 800]], region='Pelvis')
A('descending-genicular-a', 'Descending genicular artery', 0.8, [[-58, -102, 545], [-50, -90, 472], [-46, -82, 430]], region='Thigh')
A('deep-circumflex-iliac-a', 'Deep circumflex iliac artery', 0.9, [[-49, -158, 828], [-75, -151, 850], [-100, -141, 880]], region='Hip')
A('inferior-epigastric-a', 'Inferior epigastric artery', 1.1, off(vpath('inferior-epigastric-v'), (-3, 0, 0)), region='Abdomen')
A('sup-gluteal-a', 'Superior gluteal artery', 1.4, off(gp, (0, 2, -2.5)), region='Hip')
A('inf-gluteal-a', 'Inferior gluteal artery', 1.3, off(nv('inferior-gluteal'), (0, 2, -2.5)), region='Hip')
A('internal-pudendal-a', 'Internal pudendal artery', 1.1, off(nv('pudendal'), (0, 2, -2)), region='Pelvis')
A('obturator-a', 'Obturator artery', 1.1, off(nv('obturator'), (0, -2.5, 2)), region='Thigh')
A('circ-femoral-a', 'Medial & lateral circumflex femoral arteries', 1.2, off(vpath('circ-femoral-v', 0), (0, 2.5, 2.5)), off(vpath('circ-femoral-v', 1), (0, 2.5, 2.5)), region='Thigh')
out = []
for v in V_:
    if not v.get('bil', True):
        out.append({'id': v['id'], 'k': v['id'], 'name': v['name'], 'kind': v['kind'], 'side': '', 'r': v['r'], 'region': v.get('region'),
                    'paths': [[[round(float(c), 1) for c in p] for p in path] for path in v['paths']]}); continue
    for side, sx in (('R', 1), ('L', -1)):
        out.append({'id': v['id'] + '-' + side, 'k': v['id'], 'name': v['name'], 'kind': v['kind'], 'side': side, 'r': v['r'], 'region': v.get('region'),
                    'paths': [[[round(float(p[0]) * sx, 1), float(p[1]), float(p[2])] for p in path] for path in v['paths']]})
json.dump(out, open(os.path.join(HERE, '..', 'site', 'vessels.json'), 'w'), separators=(',', ':'))
print(len(out), 'traced vessels')
print('cephalic', ceph[:3], 'gs', gs[2:5])
