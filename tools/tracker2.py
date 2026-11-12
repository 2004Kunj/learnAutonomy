p='site/index.html';s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:90],s.count(a)); s=s.replace(a,b)
rep("for(const [p,ks,l] of NGRP){const f=ks.filter(k=>byK[k]);if(f.length)term(p,f,l)}",
    "for(const [p,ks,l] of NGRP){const f=ks.filter(k=>byK[k]);if(f.length){term(p,f,l);TERMS[TERMS.length-1].grp=true}}")
rep(" ['cranial\\\\s+nerves',[],'Cranial nerves']];",
    " ['anterior\\\\s+divisions?',['p-anterior-division-of-superior-trunk','p-anterior-division-of-middle-trunk','p-anterior-division-of-inferior-trunk'],'Anterior divisions of brachial plexus'],\n ['posterior\\\\s+divisions?',['p-posterior-division-of-superior-trunk','p-posterior-division-of-middle-trunk','p-posterior-division-of-inferior-trunk'],'Posterior divisions of brachial plexus']];")
rep(" ['ophthalmic\\\\s+division','p-ophthalmic-nerve'],['maxillary\\\\s+division','z-maxillary-nerve'],['mandibular\\\\s+division','mandibular'],",
    " ['v1|ophthalmic(?:\\\\s+division)?(?!\\\\s+(?:arter|vein))','p-ophthalmic-nerve'],['v2|maxillary\\\\s+division','z-maxillary-nerve'],['v3|mandibular\\\\s+division','mandibular'],")
rep("hits.push({s:m.index,e:m.index+m[0].length,txt:m[0],keys:t.keys,label:t.label})}}","hits.push({s:m.index,e:m.index+m[0].length,txt:m[0],keys:t.keys,label:t.label,grp:t.grp})}}")
rep("if(ks.length>3&&regions.size){const f=ks.filter(k=>nearR.has(byK[k][0].region));if(f.length)ks=f}   /* group terms stay in the slide's region */\n    const id=",
    "if(ks.length>3&&regions.size&&!h.grp){const f=ks.filter(k=>nearR.has(byK[k][0].region));if(f.length)ks=f}   /* group terms stay in the slide's region */\n    const id=")
# lists: "upper, middle and lower trunks", "musculocutaneous, axillary, radial, median and ulnar nerves"
old="  t.replace(/\\b([a-z]+)\\s+([a-z]+)\\s*(?:,|&|and|\\/)\\s*([a-z]+)\\b/gi,(m,a,b,c)=>{extra+=` ${a} ${c}.`;return m});"
assert old in s
s=s.replace(old,r"""  t.replace(/\b([a-z]+)\s+([a-z]+)\s*(?:,|&|and|\/)\s*([a-z]+)\b/gi,(m,a,b,c)=>{if(!/^(?:nerves?|arter(?:y|ies)|veins?|muscles?|ligaments?|branch(?:es)?|trunks?|cords?|plexus)$/i.test(b))extra+=` ${a} ${c}.`;return m});
  t.replace(/([^.:;\n]*?)\b(?:and|or|&)\s+([a-z][a-z-]*(?:\s+[a-z][a-z-]*){0,2})\s+(nerves|arteries|veins|trunks|cords|divisions|ligaments|branches)\b/gi,(m,pre,last,noun)=>{
    const sg={nerves:'nerve',arteries:'artery',veins:'vein',trunks:'trunk',cords:'cord',divisions:'division',ligaments:'ligament',branches:'branch'}[noun.toLowerCase()];
    const parts=pre.split(',').map(x=>x.trim()).filter(x=>x&&x.split(/\s+/).length<=3&&!/\d/.test(x));
    for(const q of [...parts,last])extra+=` ${q} ${sg}.`;return m});""",1)
rep("const STOP=/\\b(?:of|the|and","const GENERIC=/^(?:terminal|cranial|spinal|peripheral|motor|sensory|cutaneous|muscular|major|main|other|named|these|collateral)\\s+(?:nerves?|branch(?:es)?|arteries|veins)$/i;\nconst STOP=/\\b(?:of|the|and")
rep("    if(words.length<2||STOP.test(words.slice(0,-1).join(' ')))continue;\n    if([...seen]","    if(words.length<2||STOP.test(words.slice(0,-1).join(' '))||GENERIC.test(low))continue;\n    if([...seen]")
open(p,'w').write(s);print('ok')
