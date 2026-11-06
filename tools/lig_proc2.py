"""Second batch of ligaments missing from Z-Anatomy, checked against Terminologia Anatomica 2 (TA2).
Each is a band or sheet between landmarks found on this specimen's own bones (data space: x = patient left, y = posterior, z = up)."""
import numpy as np
from lig_proc import bezier, band

def merge(parts):
    V = []; T = []; o = 0
    for v, t in parts: V.append(v); T.append(t + o); o += len(v)
    return np.concatenate(V), np.concatenate(T)

def sheet(a, b, c, thick, n=8):
    """thin solid triangle a-b-c"""
    pts = []; idx = {}
    for i in range(n + 1):
        for j in range(n + 1 - i):
            idx[(i, j)] = len(pts); u, v = i / n, j / n; pts.append(a + (b - a) * u + (c - a) * v)
    P = np.array(pts); T = []
    for i in range(n):
        for j in range(n - i):
            T.append([idx[(i, j)], idx[(i + 1, j)], idx[(i, j + 1)]])
            if j < n - i - 1: T.append([idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]])
    T = np.array(T); nrm = np.cross(b - a, c - a); nrm /= np.linalg.norm(nrm); m = len(P)
    V = np.concatenate([P + nrm * thick / 2, P - nrm * thick / 2]); T2 = [T, T[:, ::-1] + m]
    E = {}
    for t in T:
        for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): k = tuple(sorted(e)); E[k] = E.get(k, 0) + 1
    rim = [[e[1], e[0], e[0] + m] for e, c2 in E.items() if c2 == 1] + [[e[1], e[0] + m, e[1] + m] for e, c2 in E.items() if c2 == 1]
    return V, np.concatenate(T2 + [np.array(rim)])

def near(V, p): return V[np.argmin(np.linalg.norm(V - p, axis=1))]

def build(G):
    out = []
    def add(name, side, region, joint, VT): out.append(dict(name=name, side=side, region=region, joint=joint, V=VT[0], T=VT[1]))
    X = np.array([1., 0, 0]); Y = np.array([0, 1., 0]); Z = np.array([0, 0, 1.])
    verts = [('thoracic', 'T%d' % i) for i in range(1, 13)] + [('lumbar', 'L%d' % i) for i in range(1, 6)]
    VB = {p: G(s, p) for s, p in verts}
    at = G('atlas', ''); ax = G('axis', ''); oc = G('occipital', '')
    dens = ax[np.argmax(ax[:, 2])]
    for side, sgn in (('R', -1), ('L', 1)):
        S = '-' + side
        tip = {p: V[np.argmax(V[:, 0] * sgn)] for p, V in VB.items()}
        # intertransverse ligaments between neighbouring transverse processes
        names = [p for _, p in verts]
        add('Intertransverse ligaments', side, 'Back', 'Vertebral column',
            merge([band(bezier(tip[a], (tip[a] + tip[b]) / 2, tip[b], 6), 3.2, 1.6, Y) for a, b in zip(names, names[1:])]))
        ribs = {n: G('ribs' + S, 'Rib %d' % n) for n in range(1, 13)}
        lat, sup = [], []
        for n in range(1, 13):
            r = ribs[n]; tp = tip['T%d' % n]
            head = r[np.argmin(np.abs(r[:, 0]))]; tub = near(r, tp + [sgn * 2, 3, 0])
            if n <= 10: lat.append(band(bezier(tp, (tp + tub) / 2 + [0, 3, 0], near(r, tp + [sgn * 9, 4, -1]), 5), 4.5, 2, Z))
            if n >= 2:
                neck = near(r, (head + tub) / 2); above = VB['T%d' % (n - 1)]; above = above[above[:, 0] * sgn > 12]
                tgt = near(above, neck + [0, 2, 14]); sup.append(band(bezier(neck, (neck + tgt) / 2, tgt, 6), 6, 2, X))
        add('Lateral costotransverse ligament', side, 'Thorax', 'Costotransverse joint', merge(lat))
        add('Superior costotransverse ligament', side, 'Thorax', 'Costotransverse joint', merge(sup))
        l1 = tip['L1']; r12 = near(ribs[12], l1 + [sgn * 10, 0, 18])
        add('Lumbocostal ligament', side, 'Back', 'Costovertebral', band(bezier(l1, (l1 + r12) / 2, r12, 8), 6, 2, Y))
        # arcuate ligaments of the diaphragm (bands over psoas and quadratus lumborum)
        L1 = VB['L1']; body = L1[np.abs(L1[:, 0]) < 22]; bf = body[np.argmin(body[:, 1])]; zt = L1[:, 2].max()
        bs = near(L1, np.array([sgn * 17, bf[1] + 12, zt - 8]))
        add('Medial arcuate ligament', side, 'Abdomen', 'Diaphragm', band(bezier(bs, (bs + l1) / 2 + [0, -32, 4], l1, 12), 5, 2, Z))
        add('Lateral arcuate ligament', side, 'Abdomen', 'Diaphragm', band(bezier(l1, (l1 + r12) / 2 + [sgn * 10, -22, 6], near(ribs[12], l1 + [sgn * 45, 10, 25]), 12), 5, 2, Z))
        # lateral atlanto-occipital
        c1t = at[np.argmax(at[:, 0] * sgn)]; oc2 = oc[oc[:, 0] * sgn > 22]; jt = near(oc2, c1t + [-sgn * 4, 2, 14])
        add('Lateral atlanto-occipital ligament', side, 'Neck', 'Atlanto-occipital joint', band(bezier(c1t, (c1t + jt) / 2, jt, 8), 5, 2.5, Y))
        # sternocostal: radiate sternochondral ligaments (cartilages 1-7) on the front of the sternum
        st = np.concatenate([G('manubrium', ''), G('sternum-body', ''), G('xiphoid', '')])
        rad = []; carts = {n: G('costal-cart' + S, 'Costal cartilage %d' % n) for n in range(1, 8)}
        for n, c in carts.items():
            e = c[np.argmin(np.abs(c[:, 0]))]; s = near(st, e + [-sgn * 9, -3, 0])
            rad.append(band(bezier(e + [0, -1.5, 0], (e + s) / 2 + [0, -2.5, 0], s + [0, -1, 0], 6), 10, 1.3, Z))
        add('Radiate sternochondral ligaments', side, 'Thorax', 'Sternocostal joints', merge(rad))
        low = G('costal-cart' + S, 'Costal cartilage (lower)'); ic = []
        for a, b in ((carts[5], carts[6]), (carts[6], carts[7]), (carts[7], low)):
            d = np.linalg.norm(a[::3, None] - b[None, ::3], axis=2); i, j = np.unravel_index(np.argmin(d), d.shape); pa, pb = a[::3][i], b[::3][j]
            ic.append(band(bezier(pa, (pa + pb) / 2 + [0, -2, 0], pb, 5), 6, 2, X))
        add('Interchondral ligaments', side, 'Thorax', 'Interchondral joints', merge(ic))
        xi = G('xiphoid', ''); c7 = carts[7]; p7 = near(c7, xi.mean(0)); px = near(xi, p7)
        add('Xiphichondral ligament', side, 'Thorax', 'Xiphisternal region', band(bezier(p7, (p7 + px) / 2 + [0, -2, 0], px, 6), 5, 1.6, Z))
        # costocoracoid ligament: coracoid process -> 1st rib/cartilage
        sc = G('scapula' + S, ''); cor = sc[np.argmin(sc[:, 1] + 0.3 * np.abs(sc[:, 2] - np.percentile(sc[:, 2], 92)))]
        r1 = np.concatenate([ribs[1], carts[1]]); t1 = near(r1, cor + [-sgn * 40, -5, 15])
        add('Costocoracoid ligament', side, 'Shoulder', 'Clavipectoral fascia', band(bezier(cor, (cor + t1) / 2 + [0, -6, 10], t1, 10), 8, 1.5, Y))
        # suprapleural membrane (Sibson fascia): C7 transverse process -> inner border of rib 1
        c7v = G('cervical', 'C7'); c7t = c7v[np.argmax(c7v[:, 0] * sgn)]; rin = ribs[1][np.argsort(np.abs(ribs[1][:, 0]))[:max(20, len(ribs[1]) // 3)]]
        ri = near(rin, c7t + [sgn * 10, -30, -12])
        add('Suprapleural membrane', side, 'Neck', 'Thoracic inlet', band(bezier(c7t, (c7t + ri) / 2 + [sgn * 6, -6, 14], ri, 10), 22, 1.2, X))
        # knee: medial patellofemoral and patellotibial ligaments
        pa = G('patella' + S, ''); fe = G('femur' + S, ''); tb = G('tibia' + S, '')
        pm = pa[np.argmax(pa[:, 0] * -sgn)]; zone = fe[np.abs(fe[:, 2] - (pm[2] + 6)) < 18]; me = zone[np.argmax(zone[:, 0] * -sgn)]; me = near(zone, me + [0, 14, 4])
        add('Medial patellofemoral ligament', side, 'Thigh', 'Knee joint', band(bezier(pm, (pm + me) / 2 + [-sgn * 6, -4, 0], me, 10), 11, 1.6, Z))
        pinf = pa[pa[:, 2] < pa[:, 2].min() + 8]; ttop = tb[tb[:, 2] > tb[:, 2].max() - 25]; pt = []
        for s2 in (-1, 1):
            a = pinf[np.argmax(pinf[:, 0] * s2)]; b = near(ttop, a + [s2 * 12, 0, -28]); pt.append(band(bezier(a, (a + b) / 2 + [s2 * 3, -3, 0], b, 8), 6, 1.6, Y))
        add('Patellotibial ligaments', side, 'Leg', 'Knee joint', merge(pt))
        # bicipital aponeurosis: distal biceps -> medial forearm fascia over pronator teres / flexors
        bi = np.concatenate([G('biceps-brachii' + S, 'Long head'), G('biceps-brachii' + S, 'Short head')]); bl = bi[bi[:, 2] < bi[:, 2].min() + 25]
        a = bl[np.argmax(bl[:, 0] * -sgn)]; ptv = G('pronator-teres' + S, 'Humeral head'); b = near(ptv, a + [-sgn * 22, -8, -45])
        add('Bicipital aponeurosis', side, 'Forearm', 'Cubital fossa', band(bezier(a, (a + b) / 2 + [0, -6, 0], b, 10), 14, 1.2, Z))
        # wrist: palmar radiocarpal components that Z-Anatomy lacks
        rd = G('radius' + S, ''); rdd = rd[rd[:, 2] < rd[:, 2].min() + 10]; pal = rdd[rdd[:, 1] < np.percentile(rdd[:, 1], 30)]
        lun = G('carpals' + S, 'Lunate'); sca = G('carpals' + S, 'Scaphoid')
        uln_edge = pal[np.argmax(pal[:, 0] * -sgn)]; mid = near(pal, pal.mean(0))
        lp = near(lun, lun.mean(0) + [0, -12, 0]); sp = near(sca, (sca.mean(0) + lun.mean(0)) / 2 + [0, -10, 0])
        add('Long radiolunate ligament', side, 'Hand', 'Wrist joint', band(bezier(mid, (mid + lp) / 2 + [0, -2, 0], lp, 6), 5, 2, X))
        add('Short radiolunate ligament', side, 'Hand', 'Wrist joint', band(bezier(uln_edge, (uln_edge + lp) / 2 + [0, -1, 0], lp + [0, 1, 2], 6), 4, 2, X))
        add('Radioscapholunate ligament', side, 'Hand', 'Wrist joint', band(bezier(mid + [0, 2, 0], (mid + sp) / 2 + [0, 2, 0], sp + [0, 2, 0], 6), 3, 1.8, X))
        # palmar plates of the MCP joints
        pp = []
        for mc, ph in (('First', 'Thumb'), ('Second', 'index'), ('Third', 'middle'), ('Fourth', 'ring'), ('Fifth', 'little')):
            m = G('metacarpals' + S, mc + ' metacarpal'); f = G('phalanges-hand' + S, ph + ' proximal')
            mh = m[m[:, 2] < np.percentile(m[:, 2], 12)]; a = mh[np.argmin(mh[:, 1])]; b = near(f[f[:, 2] > np.percentile(f[:, 2], 88)], a + [0, 0, -8])
            pp.append(band(bezier(a, (a + b) / 2 + [0, -2, 0], b, 6), 7, 2, X))
        add('Palmar metacarpophalangeal ligaments', side, 'Hand', 'Metacarpophalangeal joints', merge(pp))
        # foot: calcaneometatarsal ligament (lateral band of the plantar aponeurosis)
        ca = G('tarsals' + S, 'Calcaneus'); m5 = G('metatarsals' + S, 'Fifth metatarsal')
        cl = ca[ca[:, 2] < ca[:, 2].min() + 8]; a = cl[np.argmax(cl[:, 0] * sgn)]; b = near(m5, m5[np.argmax(m5[:, 1])])
        add('Calcaneometatarsal ligament', side, 'Foot', 'Plantar aponeurosis', band(bezier(a, (a + b) / 2 + [sgn * 2, 0, -3], b, 10), 7, 1.8, X))
        # reflected inguinal ligament
        ig = G('inguinal-lig' + S, ''); pt0 = ig[np.argmin(np.abs(ig[:, 0]))]
        add('Reflected inguinal ligament', side, 'Abdomen', 'Inguinal region', band(bezier(pt0 + [0, 2, 2], pt0 + [-sgn * 6, -2, 14], np.array([sgn * 2, pt0[1] - 4, pt0[2] + 30]), 8), 9, 1.4, Z * 0 + Y))
        # palmar carpal ligament: thickened fascia across the front of the wrist, just above the flexor retinaculum
        ul = G('ulna' + S, ''); z0 = rd[:, 2].min() + 14
        ra = rd[np.abs(rd[:, 2] - z0) < 5]; ua = ul[np.abs(ul[:, 2] - z0) < 5]
        if len(ra) and len(ua):
            a = ra[np.argmin(ra[:, 1])] + [0, -4, 0]; b = ua[np.argmin(ua[:, 1])] + [0, -4, 0]
            add('Palmar carpal ligament', side, 'Hand', 'Wrist (deep fascia)', band(bezier(a, (a + b) / 2 + [0, -7, 0], b, 10), 12, 1.2, Z))
        # ligamentum mucosum (infrapatellar plica): intercondylar notch -> infrapatellar fat pad region
        fz = fe[:, 2].min(); cond = fe[fe[:, 2] < fz + 25]; notch = near(fe, np.array([cond[:, 0].mean(), cond[:, 1].mean() - 4, fz + 18]))
        apx = pa[np.argmin(pa[:, 2])] + [0, 9, -8]
        add('Ligamentum mucosum', side, 'Leg', 'Knee joint', band(bezier(notch, (notch + apx) / 2 + [0, 0, -6], apx, 8), 4, 1.2, X))
        # medial temporomandibular ligament
        mb = G('mandible', ''); mbs = mb[mb[:, 0] * sgn > 25]; con = mbs[mbs[:, 2] > np.percentile(mbs[:, 2], 97)]; cm = con[np.argmin(con[:, 0] * sgn)]
        tv = G('temporal' + S, ''); tt = near(tv, cm + [0, 0, 9])
        add('Medial temporomandibular ligament', side, 'Skull', 'Temporomandibular joint', band(bezier(cm, (cm + tt) / 2 + [-sgn * 2, 0, 0], tt, 6), 5, 1.8, Y))
        # costocoracoid membrane: sheet between coracoid, clavicle and 1st rib (clavipectoral fascia)
        cv = G('clavicle' + S, ''); cc = near(cv, (cor + t1) / 2 + [0, 0, 18])
        add('Costocoracoid membrane', side, 'Shoulder', 'Clavipectoral fascia', sheet(cor + [0, -2, 0], cc + [0, 3, -4], t1 + [0, -2, 2], 1.0))
        # vasto-adductor membrane: roof of the adductor canal between vastus medialis and the adductors
        vm = G('vastus-medialis' + S, ''); ad = np.concatenate([G('adductor-longus' + S, ''), G('adductor-magnus' + S, '')]); path = []; wid = []
        for z in np.linspace(560, 470, 7):
            a1 = vm[np.abs(vm[:, 2] - z) < 6]; b1 = ad[np.abs(ad[:, 2] - z) < 6]
            if len(a1) < 3 or len(b1) < 3: continue
            d = np.linalg.norm(a1[:, None] - b1[None], axis=2); i, j = np.unravel_index(np.argmin(d), d.shape)
            path.append((a1[i] + b1[j]) / 2 + [0, -5, 0]); wid.append(max(12, d[i, j] + 8))
        if len(path) >= 3:
            add('Vasto-adductor membrane', side, 'Thigh', 'Adductor canal', band(np.array(path), float(np.median(wid)), 1.0, X))
        # intra-articular sternochondral ligament (2nd sternocostal joint)
        e2 = carts[2][np.argmin(np.abs(carts[2][:, 0]))]; s2 = near(st, e2)
        add('Intra-articular sternochondral ligament', side, 'Thorax', 'Sternocostal joint (2nd)', band(bezier(e2, (e2 + s2) / 2, s2 + (s2 - e2) * 0.3 + [0, 0, 0.01], 5), 3, 1.2, Z))
    # midline / unpaired
    L1 = VB['L1']; body = L1[np.abs(L1[:, 0]) < 22]; bf = body[np.argmin(body[:, 1])]; zt = L1[:, 2].max()
    a = np.array([14, bf[1] + 4, zt + 4]); b = np.array([-14, bf[1] + 4, zt + 4])
    add('Median arcuate ligament', '', 'Abdomen', 'Diaphragm (aortic hiatus)', band(bezier(a, np.array([0, bf[1] - 30, zt + 8]), b, 12), 6, 2.4, Z))
    aa = at[(np.abs(at[:, 0]) < 7)]; aaf = aa[aa[:, 1] < np.percentile(aa[:, 1], 25)]; a1 = aaf[np.argmin(aaf[:, 2])]
    axf = ax[(np.abs(ax[:, 0]) < 7) & (ax[:, 2] < dens[2] - 18)]; b1 = axf[np.argmin(axf[:, 1])]
    add('Anterior atlantoaxial membrane', '', 'Neck', 'Atlanto-axial joint', band(bezier(a1, (a1 + b1) / 2 + [0, -2, 0], b1, 8), 18, 1.4, X))
    aab = aa[aa[:, 1] > np.percentile(aa[:, 1], 75)]; a2 = aab[np.argmin(aab[:, 2])]; axb = ax[(np.abs(ax[:, 0]) < 7)]; axb = axb[axb[:, 1] > np.percentile(axb[:, 1], 70)]; b2 = axb[np.argmax(axb[:, 2])]
    add('Posterior atlantoaxial membrane', '', 'Neck', 'Atlanto-axial joint', band(bezier(a2, (a2 + b2) / 2 + [0, 2, 0], b2, 8), 22, 1.4, X))
    inner = aaf[np.argmax(aaf[:, 1])]; df = near(ax[ax[:, 2] > dens[2] - 16], inner + [0, 4, 0])
    add('Anterior atlantodental ligament', '', 'Neck', 'Atlanto-axial joint', band(bezier(inner, (inner + df) / 2, df, 5), 5, 1.6, X))
    # cruciform ligament longitudinal bands (vertical limbs behind the transverse ligament)
    zc = dens[2] - 9; back = ax[(np.abs(ax[:, 0]) < 4) & (np.abs(ax[:, 2] - zc) < 4)]; db = (back[np.argmax(back[:, 1])] if len(back) else dens + [0, 5, -9]) + [0, 6, 0]
    mid = oc[np.abs(oc[:, 0]) < 5]; basion = near(mid[mid[:, 2] < dens[2] + 30], dens)
    c2b = ax[(np.abs(ax[:, 0]) < 6) & (ax[:, 2] < dens[2] - 22)]; c2b = c2b[np.argsort(c2b[:, 1])[len(c2b) // 3]] + [0, 5, 0]
    add('Superior longitudinal band of cruciform ligament', '', 'Neck', 'Atlanto-axial joint', band(bezier(db, (db + basion) / 2 + [0, 4, 0], basion + [0, 4, 2], 8), 5, 2, X))
    add('Inferior longitudinal band of cruciform ligament', '', 'Neck', 'Atlanto-axial joint', band(bezier(db, (db + c2b) / 2 + [0, 1, 0], c2b, 8), 5, 2, X))
    # sternal membrane over the front of the sternum
    st = np.concatenate([G('manubrium', ''), G('sternum-body', '')]); zs = np.linspace(st[:, 2].max() - 6, st[:, 2].min() + 6, 9); path = []
    for z in zs:
        sl = st[(np.abs(st[:, 2] - z) < 4) & (np.abs(st[:, 0]) < 8)]
        if len(sl): path.append(sl[np.argmin(sl[:, 1])] + [0, -1.2, 0])
    add('Sternal membrane', '', 'Thorax', 'Sternum', band(np.array(path), 26, 1.0, X))
    # perineal membrane: triangle between the ischiopubic rami below the pubic symphysis
    hR = G('hip-bone-R', ''); hL = G('hip-bone-L', ''); sym = np.concatenate([hR[np.abs(hR[:, 0]) < 8], hL[np.abs(hL[:, 0]) < 8]]); apex = sym[np.argmin(sym[:, 2])] + [0, 4, -3]
    tR = hR[np.argmin(hR[:, 2])] + [12, -8, 8]; tL = hL[np.argmin(hL[:, 2])] + [-12, -8, 8]
    add('Perineal membrane', '', 'Pelvis', 'Urogenital triangle', sheet(apex, tR, tL, 1.6))
    add('Transverse perineal ligament', '', 'Pelvis', 'Urogenital triangle', band(bezier(apex + [12, 0, -2], apex + [0, -1, -4], apex + [-12, 0, -2], 8), 4, 2, Y))
    return out
