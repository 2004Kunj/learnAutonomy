p='site/index.html';s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:90],s.count(a)); s=s.replace(a,b)
rep("mid=mid||'';extra+=` ${a} ${mid}${u}. ${b} ${mid}${u}.`;return m});","mid=mid||'';if(!/^(?:nerves?|arter(?:y|ies)|veins?|muscles?|branch(?:es)?|to|of|the)$/i.test(a)&&!/^(?:to|of|the)$/i.test(b))extra+=` ${a} ${mid}${u}. ${b} ${mid}${u}.`;return m});")
rep("hits.sort((a,b)=>(b.e-b.s)-(a.e-a.s)||a.s-b.s);","hits.sort((a,b)=>(b.e-b.s)-(a.e-a.s)||(b.grp?1:0)-(a.grp?1:0)||a.s-b.s);")
s=s.replace("t.replace(/\\b([a-z]+)\\s*(?:,|&|and|\\/)\\s*([a-z]+)\\s+([a-z]+\\s+)?(arter","t.replace(/\\b([a-z]+)\\s*(?:&|and|\\/)\\s*([a-z]+)\\s+([a-z]+\\s+)?(arter")
s=s.replace("t.replace(/\\b([a-z]+)\\s+([a-z]+)\\s*(?:,|&|and|\\/)\\s*([a-z]+)\\b/gi","t.replace(/\\b([a-z]+)\\s+([a-z]+)\\s*(?:&|and|\\/)\\s*([a-z]+)\\b/gi")
s=s.replace('${it.src===\'img\'?\'<span class="said">from slide picture</span>\':\'\'}','${it.src===\'img\'?\' img\':\'\'}" data-ti="${i}" ${miss?\'\':\'role="button" tabindex="0"\'} style="--kc:${col}">\n      <span class="trk-n">${miss?\'–\':it.n}</span>\n      <span class="trk-b"><span class="trk-t">${esc(miss?it.said:it.label)}</span><span class="trk-s">${sub}${said}${it.src===\'img\'?\'<span class="said">from slide picture</span>\':it.src===\'ai\'?\'<span class="said">read by AI</span>\':\'\'}${!miss&&it.keys.length===1&&byK[it.keys[0]][0].src===\'modelled\'?\'<span class="said">path drawn between its divisions and branches</span>\':\'\'}')
open(p,'w').write(s);print('ok')
