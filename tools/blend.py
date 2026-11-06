"""Minimal pure-Python .blend reader (64-bit little-endian), enough to pull meshes/objects."""
import struct, mmap, re, numpy as np

class Blend:
    def __init__(self, path):
        f = open(path, 'rb'); self.mm = mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        assert mm[:7] == b'BLENDER' and mm[7:8] == b'-' and mm[8:9] == b'v'
        self.blocks = []; self.byptr = {}
        o = 12
        while True:
            code = mm[o:o+4]; ln, = struct.unpack_from('<i', mm, o+4); ptr, = struct.unpack_from('<Q', mm, o+8)
            sdna, cnt = struct.unpack_from('<ii', mm, o+16)
            b = (code.rstrip(b'\0').decode('latin1'), o+24, ln, ptr, sdna, cnt)
            if b[0] == 'ENDB': break
            self.blocks.append(b); self.byptr.setdefault(ptr, b) if False else self.byptr.__setitem__(ptr, b)
            if b[0] == 'DNA1': self._dna(o+24)
            o += 24 + ln
        self.sorted = sorted(self.byptr); self.bidx = {b[1]: i for i, b in enumerate(self.blocks)}; self.home = None

    def _dna(self, o):
        mm = self.mm; o0 = o; A = lambda x: o0 + ((x - o0 + 3) & ~3); assert mm[o:o+4] == b'SDNA'; o += 4
        def strs(o, tag):
            assert mm[o:o+4] == tag, tag; n, = struct.unpack_from('<i', mm, o+4); o += 8; out = []
            for _ in range(n):
                e = mm.find(b'\0', o); out.append(mm[o:e].decode('latin1')); o = e+1
            return out, A(o)
        self.names, o = strs(o, b'NAME'); self.types, o = strs(o, b'TYPE')
        assert mm[o:o+4] == b'TLEN'; o += 4; nt = len(self.types)
        self.tlen = struct.unpack_from('<%dh' % nt, mm, o); o = A(o + 2*nt)
        assert mm[o:o+4] == b'STRC'; n, = struct.unpack_from('<i', mm, o+4); o += 8
        self.structs = []; self.sidx = {}
        for i in range(n):
            t, nf = struct.unpack_from('<hh', mm, o); o += 4
            fl = struct.unpack_from('<%dh' % (2*nf), mm, o); o += 4*nf
            fields = {}; off = 0
            for j in range(nf):
                ft, fn = self.types[fl[2*j]], self.names[fl[2*j+1]]
                isptr = fn.startswith('*') or fn.startswith('(*')
                dims = [int(x) for x in re.findall(r'\[(\d+)\]', fn)]; cnt = int(np.prod(dims)) if dims else 1
                base = re.sub(r'\[.*', '', fn).lstrip('*').strip('()*')
                sz = 8 if isptr else self.tlen[fl[2*j]]
                fields[base] = (off, ft, isptr, cnt, sz); off += sz * cnt
            self.structs.append((self.types[t], fields)); self.sidx[self.types[t]] = i

    def local(self, ptr):
        """resolve ptr among DATA blocks written right after the block at file offset self.home"""
        i = self.bidx[self.home] + 1
        while i < len(self.blocks) and self.blocks[i][0] == 'DATA':
            b = self.blocks[i]
            if b[3] <= ptr < b[3] + max(1, b[2]): return b, ptr - b[3]
            i += 1
        return None

    def sname(self, b): return self.structs[b[4]][0]

    def resolve(self, ptr):
        """block containing ptr -> (block, offset into data)"""
        if ptr == 0: return None
        if getattr(self, 'home', None) is not None:
            r = self.local(ptr)
            if r: return r
        if ptr in self.byptr: return self.byptr[ptr], 0
        import bisect
        i = bisect.bisect_right(self.sorted, ptr) - 1
        b = self.byptr[self.sorted[i]]
        if ptr < b[3] + b[2]: return b, ptr - b[3]
        return None

class S:
    """view of struct `stype` at absolute file offset o"""
    PRIM = {'char': 'b', 'uchar': 'B', 'short': 'h', 'ushort': 'H', 'int': 'i', 'uint': 'I', 'float': 'f', 'double': 'd',
            'int64_t': 'q', 'uint64_t': 'Q', 'int8_t': 'b', 'int16_t': 'h', 'int32_t': 'i'}
    def __init__(self, bl, stype, o): self.bl, self.t, self.o = bl, stype, o; self.f = bl.structs[bl.sidx[stype]][1]
    def has(self, k): return k in self.f
    def __getitem__(self, k):
        off, ft, isptr, cnt, sz = self.f[k]; mm = self.bl.mm; a = self.o + off
        if isptr:
            v = struct.unpack_from('<%dQ' % cnt, mm, a); return v[0] if cnt == 1 else v
        if ft == 'char' and cnt > 1: return mm[a:a+cnt].split(b'\0')[0].decode('utf8', 'replace')
        if ft in self.PRIM:
            v = struct.unpack_from('<%d%s' % (cnt, self.PRIM[ft]), mm, a); return v[0] if cnt == 1 else v
        return S(self.bl, ft, a)
    def deref(self, k, stype=None):
        r = self.bl.resolve(self[k])
        if not r: return None
        b, d = r; return S(self.bl, stype or self.bl.sname(b), b[1] + d)

def block_view(bl, b): return S(bl, bl.sname(b), b[1])

def listbase(bl, lb, stype=None):
    p = lb['first']; out = []
    while p:
        r = bl.resolve(p)
        if not r: break
        b, d = r; s = S(bl, stype or bl.sname(b), b[1] + d); out.append(s); p = s['next']
    return out
