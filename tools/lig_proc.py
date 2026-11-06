"""Ligaments Z-Anatomy lacks, modelled as bands/sheets between landmarks found on this specimen's own bones."""
import numpy as np
def bezier(p0, c, p1, n):
    t = np.linspace(0, 1, n)[:, None]; return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p1
def band(path, width, thick, wide_dir, seg=14):
    path = np.asarray(path, float); n = len(path); V = []; T = []
    for i in range(n):
        tg = path[min(n - 1, i + 1)] - path[max(0, i - 1)]; tg /= np.linalg.norm(tg) + 1e-9
        w = np.asarray(wide_dir, float) - tg * np.dot(wide_dir, tg); w /= np.linalg.norm(w) + 1e-9; h = np.cross(tg, w)
        taper = 0.75 + 0.25 * np.sin(np.pi * i / (n - 1))
        for j in range(seg):
            a = 2 * np.pi * j / seg; V.append(path[i] + w * np.cos(a) * width / 2 * taper + h * np.sin(a) * thick / 2)
    for i in range(n - 1):
        for j in range(seg):
            a, b, c, d = i * seg + j, i * seg + (j + 1) % seg, (i + 1) * seg + j, (i + 1) * seg + (j + 1) % seg
            T += [[a, c, b], [b, c, d]]
    V = np.array(V); c0 = len(V); c1 = c0 + 1; V = np.vstack([V, path[0], path[-1]])
    for j in range(seg):
        T.append([c0, j, (j + 1) % seg]); T.append([c1, (n - 1) * seg + (j + 1) % seg, (n - 1) * seg + j])
    return V, np.array(T, np.int64)

def build(G):
    """G(sid, part) -> HD vertex array of a bone/structure in data space. Returns list of dicts."""
    out = []
    def add(name, side, region, joint, V, T): out.append(dict(name=name, side=side, region=region, joint=joint, V=V, T=T))
    ax = G('axis', ''); at = G('atlas', ''); oc = G('occipital', '')
    dens = ax[np.argmax(ax[:, 2])]; dz = dens[2]
    # basion: occipital point near the midline closest to the dens tip; opisthion: most posterior midline rim point at the same level
    mid = oc[np.abs(oc[:, 0]) < 5]; low = mid[mid[:, 2] < dz + 30]
    basion = low[np.argmin(np.linalg.norm(low - dens, axis=1))]
    rim = low[(low[:, 2] < basion[2] + 12) & (low[:, 1] > basion[1] + 15)]; opisthion = rim[np.argmin(rim[:, 2])] if len(rim) else basion + [0, 35, 4]
    up = np.array([0, 0, 1.]); lat = np.array([1., 0, 0])
    # apical ligament
    add('Apical ligament of dens', '', 'Neck', 'Atlanto-axial joint', *band(bezier(dens, (dens + basion) / 2 + [0, 1, 0], basion, 10), 4, 2.2, lat))
    # transverse ligament of atlas: behind the dens between the lateral masses
    zc = dens[2] - 9; ring = at[np.abs(at[:, 2] - zc) < 6]
    back = ax[(np.abs(ax[:, 0]) < 4) & (np.abs(ax[:, 2] - zc) < 4)]; db = back[np.argmax(back[:, 1])] if len(back) else dens + [0, 5, -9]
    ends = []
    for sgn in (-1, 1):
        cand = ring[(ring[:, 0] * sgn > 6) & (np.abs(ring[:, 1] - db[1]) < 10)]
        ends.append(cand[np.argmin(np.abs(cand[:, 0]))] if len(cand) else db + [sgn * 11, -2, 0])
    add('Transverse ligament of atlas', '', 'Neck', 'Atlanto-axial joint', *band(bezier(ends[0], db + np.array([0, 7., 0]), ends[1], 14), 7, 2.6, up))
    # alar ligaments: upper sides of the dens -> medial occipital condyles
    for side, sgn in (('R', -1), ('L', 1)):
        cond = oc[(oc[:, 0] * sgn > 6) & (oc[:, 0] * sgn < 26)]; cond = cond[cond[:, 2] < np.percentile(cond[:, 2], 6)]
        tgt = cond[np.argmin(np.abs(cond[:, 0]))]
        src = dens + [sgn * 3, 1, -3]
        add('Alar ligament', side, 'Neck', 'Atlanto-occipital joint', *band(bezier(src, (src + tgt) / 2 + [0, 0, 2], tgt, 10), 6, 4, up))
    # tectorial membrane: back of C2 body -> clivus inside the foramen magnum
    c2b = ax[(np.abs(ax[:, 0]) < 6) & (ax[:, 2] < dz - 20)]; c2b = c2b[np.argmax(c2b[:, 1]) if False else np.argsort(c2b[:, 1])[len(c2b) // 3]] if len(c2b) else dens + [0, 6, -25]
    clivus = basion + [0, 3, 14]
    add('Tectorial membrane', '', 'Neck', 'Craniovertebral joints', *band(bezier(c2b + [0, 7, 0], (c2b + clivus) / 2 + [0, 9, 0], clivus, 12), 22, 1.6, lat))
    # atlanto-occipital membranes
    aa = at[np.argmin(at[:, 1])]; aa = at[(np.abs(at[:, 0]) < 6) & (at[:, 1] < aa[1] + 4)]; aa = aa[np.argmax(aa[:, 2])]
    pa = at[np.argmax(at[:, 1])]; pa = at[(np.abs(at[:, 0]) < 6) & (at[:, 1] > pa[1] - 4)]; pa = pa[np.argmax(pa[:, 2])]
    add('Anterior atlanto-occipital membrane', '', 'Neck', 'Atlanto-occipital joint', *band(bezier(aa, (aa + basion) / 2 + [0, -2, 0], basion + [0, -2, 0], 10), 24, 1.6, lat))
    add('Posterior atlanto-occipital membrane', '', 'Neck', 'Atlanto-occipital joint', *band(bezier(pa, (pa + opisthion) / 2 + [0, 2, 0], opisthion, 10), 30, 1.4, lat))
    for side, sgn in (('R', -1), ('L', 1)):
        S = '-' + side
        # anterior tibiotalar (deltoid part)
        tb = G('tibia' + S, ''); bot = tb[tb[:, 2] < tb[:, 2].min() + 14]; mal = bot[np.argmax(bot[:, 0] * -sgn)]   # most medial low point
        ant = bot[(np.abs(bot[:, 0] - mal[0]) < 7)]; ant = ant[np.argmin(ant[:, 1])]
        ta = G('tarsals' + S, 'Talus'); tq = ant + [0, -12, -12]; tt = ta[np.argmin(np.linalg.norm(ta - tq, axis=1))]
        add('Anterior tibiotalar ligament', side, 'Foot', 'Medial collateral ligament', *band(bezier(ant, (ant + tt) / 2 + [-sgn * 2, 0, 0], tt, 10), 7, 2.2, np.array([0, 1., 0])))
        # meniscofemoral ligaments: posterior horn of lateral meniscus -> medial femoral condyle (notch side)
        lm = G('lig-lateral-meniscus' + S, ''); ph = lm[lm[:, 1] > np.percentile(lm[:, 1], 85)]; ph = ph[np.argmax(ph[:, 0] * -sgn)] if len(ph) else lm[np.argmax(lm[:, 1])]
        pcl = G('lig-posterior-cruciate-ligament' + S, ''); fa = pcl[np.argmax(pcl[:, 2])]
        for nm, dy in (('Posterior meniscofemoral ligament', 5), ('Anterior meniscofemoral ligament', -5)):
            add(nm, side, 'Leg', 'Knee joint', *band(bezier(ph, (ph + fa) / 2 + [0, dy, 0], fa, 12), 4, 2.2, lat))
        # lacunar and pectineal ligaments from the medial end of the inguinal ligament
        ig = G('inguinal-lig' + S, ''); pt = ig[np.argmin(np.abs(ig[:, 0]))]   # pubic tubercle end
        hb = G('hip-bone' + S, ''); xs = np.linspace(0, 32, 9); line = []
        for dx in xs:
            sl = hb[(np.abs(hb[:, 0] - (pt[0] + sgn * dx)) < 2.5) & (hb[:, 1] > pt[1] - 4) & (hb[:, 1] < pt[1] + 30) & (np.abs(hb[:, 2] - pt[2]) < 22)]
            if len(sl): line.append(sl[np.argmax(sl[:, 2])])
        line = np.array(line)
        if len(line) >= 4:
            add('Pectineal ligament', side, 'Pelvis', 'Pubis', *band(line + [0, 0, 1.2], 3.4, 2.4, np.array([0, 1., 0])))
            a, b = pt + [0, 2, 1], line[2] + [0, 0, 1.5]
            add('Lacunar ligament', side, 'Pelvis', 'Inguinal region', *band(bezier(a, (a + b) / 2 + [0, 0, -3], b, 8), 9, 1.6, np.array([0, 0, 1.])))
    return out
