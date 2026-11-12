p='site/index.html';s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:90],s.count(a)); s=s.replace(a,b)
rep("for(const [p,ks,l] of NGRP){","/* named nerves this specimen does not have: claim the words so they are listed as missing, not matched to a muscle */\nfor(const p of ['nerve\\\\s+to\\\\s+(?:the\\\\s+)?(?!piriformis|quadratus\\\\s+femoris|mylohyoid|subclavius)[a-z]+(?:\\\\s+(?:internus|externus|major|minor|longus|brevis|femoris|scapulae|superior|inferior|anterior|posterior))?','great\\\\s+auricular(?:\\\\s+nerve)?','lesser\\\\s+occipital(?:\\\\s+nerve)?','greater\\\\s+occipital(?:\\\\s+nerve)?','transverse\\\\s+cervical\\\\s+nerve','supraclavicular\\\\s+nerves?','ansa\\\\s+cervicalis']){term(p,[],'');TERMS[TERMS.length-1].miss=true}\nfor(const [p,ks,l] of NGRP){")
rep("hits.push({s:m.index,e:m.index+m[0].length,txt:m[0],keys:t.keys,label:t.label,grp:t.grp})}}","hits.push({s:m.index,e:m.index+m[0].length,txt:m[0],keys:t.keys,label:t.label,grp:t.grp,miss:t.miss})}}")
rep("  for(const h of termHits(text)){let ks=h.keys.filter(k=>byK[k]);if(!ks.length)continue;",
    "  for(const h of termHits(text)){let ks=h.keys.filter(k=>byK[k]);\n    if(!ks.length){if(h.miss){const said=cap(h.txt.replace(/\\s+/g,' ').trim());rows.set('miss:'+said.toLowerCase(),{label:said,said,keys:[],status:'missing',kind:'nerve'})}continue}")
open(p,'w').write(s);print('ok')
