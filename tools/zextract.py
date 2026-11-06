"""Pull every mesh + curve object out of Z-Anatomy Startup.blend in world space (mm), applying Mirror and Subdivision."""
import numpy as np, struct, pickle, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from blend import Blend, S, block_view, listbase
HERE = os.path.dirname(os.path.abspath(__file__)); Z = os.path.join(HERE, '..', 'zsrc')
bl = Blend(os.path.join(Z, 'ex/Z-Anatomy/Startup.blend')); mm = bl.mm

def arr(ptr, dtype, n):
    r = bl.resolve(ptr)
    if not r or n == 0: return None
    b, d = r; return np.frombuffer(mm, dtype, n, b[1] + d)

MV = np.dtype([('co', '<f4', 3), ('f', 'u1', 4)]); MP = np.dtype([('ls', '<i4'), ('n', '<i4'), ('m', '<i2'), ('f', 'u1', 2)])
ML = np.dtype([('v', '<i4'), ('e', '<i4')])
SKIN = np.dtype([('r', '<f4', 3), ('f', '<i4')])

def mesh_polys(me):
    nv, npo, nl = me['totvert'], me['totpoly'], me['totloop']
    V = arr(me['mvert'], MV, nv); P = arr(me['mpoly'], MP, npo); L = arr(me['mloop'], ML, nl)
    if V is None or P is None or L is None: return None, None
    lv = L['v'].astype(np.int64)
    return V['co'].astype(np.float64).copy(), (P['ls'].astype(np.int64), P['n'].astype(np.int64), lv)

def catmull_clark(V, F):
    """V (n,3); F (starts, counts, loopverts). Returns same structure, one level (Blender-like: boundary smooth)."""
    ls, cnt, lv = F; nf = len(ls); nv = len(V)
    face_of_loop = np.repeat(np.arange(nf), cnt)
    idx_in = np.arange(len(lv)) - np.repeat(ls, cnt)
    nxt = np.repeat(ls, cnt) + (idx_in + 1) % np.repeat(cnt, cnt)
    a = lv; b = lv[nxt]
    fp = np.zeros((nf, 3)); np.add.at(fp, face_of_loop, V[a]); fp /= cnt[:, None]
    lo, hi = np.minimum(a, b), np.maximum(a, b); key = lo * (nv + 1) + hi
    ek, einv, ecount = np.unique(key, return_inverse=True, return_counts=True)
    ne = len(ek); e0 = ek // (nv + 1); e1 = ek % (nv + 1)
    efs = np.zeros((ne, 3)); np.add.at(efs, einv, fp[face_of_loop])
    bnd = ecount == 1
    ep = np.where(bnd[:, None], (V[e0] + V[e1]) / 2, (V[e0] + V[e1] + efs) / (2 + ecount[:, None]))
    # vertex update
    val = np.zeros(nv); np.add.at(val, e0, 1); np.add.at(val, e1, 1)
    fsum = np.zeros((nv, 3)); fn = np.zeros(nv); np.add.at(fsum, a, fp[face_of_loop]); np.add.at(fn, a, 1)
    mid = (V[e0] + V[e1]) / 2; rsum = np.zeros((nv, 3)); np.add.at(rsum, e0, mid); np.add.at(rsum, e1, mid)
    isb = np.zeros(nv, bool); isb[e0[bnd]] = True; isb[e1[bnd]] = True
    n = np.maximum(val, 1)[:, None]
    newV = (fsum / np.maximum(fn, 1)[:, None] + 2 * rsum / n + (n - 3) * V) / n
    bsum = np.zeros((nv, 3)); bc = np.zeros(nv)
    np.add.at(bsum, e0[bnd], V[e1[bnd]]); np.add.at(bsum, e1[bnd], V[e0[bnd]]); np.add.at(bc, e0[bnd], 1); np.add.at(bc, e1[bnd], 1)
    bv = np.where((bc == 2)[:, None], 0.75 * V + bsum / 8, V)
    newV = np.where(isb[:, None], bv, newV); newV = np.where((val == 0)[:, None], V, newV)
    # new quads: per loop i: (v_i, e_i, f, e_{i-1})
    prv = np.repeat(ls, cnt) + (idx_in - 1) % np.repeat(cnt, cnt)
    eid_loop = einv  # edge for (loop -> next)
    Vout = np.concatenate([newV, ep, fp])
    q = np.stack([a, nv + eid_loop, nv + ne + face_of_loop, nv + eid_loop[prv]], 1).reshape(-1)
    nq = len(lv)
    return Vout, (np.arange(nq) * 4, np.full(nq, 4), q)

def tris(F):
    ls, cnt, lv = F; out = []
    for k in range(3, int(cnt.max()) + 1 if len(cnt) else 3):
        sel = cnt == k
        if not sel.any(): continue
        s = ls[sel]
        for j in range(1, k - 1): out.append(np.stack([lv[s], lv[s + j], lv[s + j + 1]], 1))
    return np.concatenate(out) if out else np.zeros((0, 3), np.int64)

def mat(o): return np.array(o['obmat'], np.float64).reshape(4, 4)

def mods_of(o):
    h = bl.home; bl.home = o.o - 24 + 24 if False else None
    # modifiers are DATA blocks after the OB block
    bl.home = o.o; ms = listbase(bl, o['modifiers'], 'ModifierData'); bl.home = h; return ms

def apply_mods(o, V, F):
    notes = []
    for m in mods_of(o):
        t = m['type']; nm = m['name']
        if m['mode'] & 1 == 0 and m['mode'] & 2 == 0: continue   # disabled in viewport & render
        if t == 5:  # mirror
            mi = S(bl, 'MirrorModifierData', m.o); fl = mi['flag']; ax = [(fl >> (3 + i)) & 1 for i in range(3)]
            if not any(ax): ax = [1, 0, 0]
            M = np.eye(4)
            if mi['mirror_ob']:
                r = bl.resolve(mi['mirror_ob']); mo = S(bl, 'Object', r[0][1] + r[1])
                M = np.linalg.inv(mat(o).T) @ mat(mo).T   # mirror-object frame in local coords
            Mi = np.linalg.inv(M)
            for i in range(3):
                if not ax[i]: continue
                D = np.eye(4); D[i, i] = -1; T = M @ D @ Mi
                V2 = V @ T[:3, :3].T + T[:3, 3]
                ls, cnt, lv = F; nv = len(V)
                # reversed winding for mirrored copy
                rev = np.concatenate([lv[s:s + c][::-1] for s, c in zip(ls, cnt)]) if len(ls) < 200000 else lv
                F = (np.concatenate([ls, ls + len(lv)]), np.concatenate([cnt, cnt]), np.concatenate([lv, rev + nv]))
                V = np.concatenate([V, V2])
            notes.append('mirror')
        elif t == 1:  # subsurf
            ss = S(bl, 'SubsurfModifierData', m.o); lv_ = max(1, min(2, ss['levels']))
            for _ in range(lv_):
                if len(F[2]) > 400000: break
                V, F = catmull_clark(V, F)
            notes.append('subsurf%d' % lv_)
        else: notes.append(nm)
    return V, F, notes

# ---- curves ----
def bez_points(n, res):
    bz = arr(n['bezt'], np.dtype([('vec', '<f4', 9), ('alfa', '<f4'), ('w', '<f4'), ('r', '<f4'), ('pad', 'u1', 24)]), n['pntsu'])
    if bz is None: return None
    v = bz['vec'].reshape(-1, 3, 3); r = bz['r']; cyc = n['flagu'] & 1
    segs = len(v) - (0 if cyc else 1); pts = []; rad = []
    t = np.linspace(0, 1, max(2, res) + 1)[:-1][:, None]
    for i in range(segs):
        j = (i + 1) % len(v)
        P0, P1, P2, P3 = v[i, 1], v[i, 2], v[j, 0], v[j, 1]
        pts.append((1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3)
        rad.append(r[i] + (r[j] - r[i]) * t[:, 0])
    if not cyc: pts.append(v[-1:, 1]); rad.append(r[-1:])
    return np.concatenate(pts).astype(np.float64), np.concatenate(rad)

def poly_points(n):
    bp = arr(n['bp'], np.dtype([('vec', '<f4', 4), ('alfa', '<f4'), ('w', '<f4'), ('f', 'u1', 4), ('r', '<f4'), ('pad', 'u1', 4)]), n['pntsu'] * max(1, n['pntsv']))
    if bp is None: return None
    return bp['vec'][:, :3].astype(np.float64), bp['r'].astype(np.float64)

# ---- collections ----
obcol = {}; parent = {}
for b in bl.blocks:
    if b[0] == 'GR':
        g = block_view(bl, b); gn = g['id']['name'][2:]
        for co in listbase(bl, g['gobject'], 'CollectionObject'): obcol.setdefault(co['ob'], []).append(gn)
        for c in listbase(bl, g['children'], 'CollectionChild'):
            r = bl.resolve(c['collection']); parent.setdefault(S(bl, 'Collection', r[0][1] + r[1])['id']['name'][2:], []).append(gn)

out = []; mcache = {}
for b in bl.blocks:
    if b[0] != 'OB': continue
    o = block_view(bl, b); name = o['id']['name'][2:]; t = o['type']
    if t not in (1, 2): continue
    r = bl.resolve(o['data'])
    if not r: continue
    W = mat(o)   # row-major as stored: rows are axes, row 3 translation
    rec = dict(name=name, cols=obcol.get(b[3], []), hide=bool(o['restrictflag'] & 1), vis=o['visibility_flag'] if o.has('visibility_flag') else 0)
    if t == 1:
        bl.home = r[0][1]; me = S(bl, 'Mesh', r[0][1] + r[1]); key = r[0][3]
        if me['totvert'] == 0: continue
        V, F = mesh_polys(me)
        if V is None: continue
        bl.home = None; V, F, notes = apply_mods(o, V, F)
        T = tris(F); Vw = V @ W[:3, :3] + W[3, :3]
        if np.linalg.det(W[:3, :3]) < 0: T = T[:, ::-1]
        rec.update(type='mesh', V=(Vw * 1000).astype(np.float32), T=T.astype(np.int32), mods=notes, mesh=me['id']['name'][2:])
    else:
        bl.home = r[0][1]; cu = S(bl, 'Curve', r[0][1] + r[1])
        if cu['vfont']: continue
        paths = []
        for n in listbase(bl, cu['nurb'], 'Nurb'):
            pr = bez_points(n, n['resolu'] or cu['resolu']) if n['type'] == 1 else poly_points(n)
            if pr is None: continue
            p, rr = pr; pw = p @ W[:3, :3] + W[3, :3]
            sc = np.cbrt(abs(np.linalg.det(W[:3, :3])))
            paths.append(((pw * 1000).astype(np.float32), (rr * cu['ext2'] * sc * 1000).astype(np.float32)))
        bl.home = None
        if not paths: continue
        rec.update(type='curve', paths=paths, bevel=cu['ext2'], bevobj=bool(cu['bevobj']))
    out.append(rec)
pickle.dump(dict(objs=out, colparent=parent), open(os.path.join(Z, 'z.pkl'), 'wb'), protocol=4)
import collections
print(len(out), collections.Counter(r['type'] for r in out), collections.Counter(m for r in out if r['type'] == 'mesh' for m in r['mods']).most_common(12))
