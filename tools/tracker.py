p='site/index.html';s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:90],s.count(a)); s=s.replace(a,b)
def cut(a,b):  # return [start,end) of text starting at a and ending after b
    i=s.index(a); j=s.index(b,i)+len(b); return i,j

# ---------- 1. nerve aliases: every named nerve resolves to exactly one structure ----------
NERVE_TERMS=r'''/* --- nerves: one slide term -> one nerve structure --- */
const ROMAN=['','i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii'];
for(const k in byK){const st=byK[k][0];if(st.kind!=='nerve')continue;const full=st.name,al=new Set();
  const base=full.replace(/\s*\(.*?\)/g,'').replace(/ & /g,' and ').trim().toLowerCase();al.add(base);
  full.replace(/(\w+)\s+\(([a-z]+)\)/g,(m,a,b)=>{al.add(full.replace(m,b).replace(/\s*\(.*?\)/g,'').trim().toLowerCase());return m});   /* "Superior (upper) trunk" -> "upper trunk" */
  for(const a of [...al]){
    if(/ of (?:forearm|foot)$/.test(a))al.add(a.replace(/ of (?:forearm|foot)$/,''));
    if(/ of brachial plexus$/.test(a)){al.add(a.replace(/ of brachial plexus$/,''));al.add(a.replace(/ of brachial plexus$/,' of the brachial plexus'))}
    const b=a.match(/^(superficial|deep|dorsal|palmar) branch of (?:the )?(\w+) nerve$/);if(b){al.add(`${b[1]} ${b[2]} nerve`);al.add(`${b[2]} nerve ${b[1]} branch`);al.add(`${b[1]} branch of the ${b[2]} nerve`)}
    const c=a.match(/^(.+?) branch(es)? of (?:the )?(.+)$/);if(c)al.add(`${c[1]} branch${c[2]||''} of the ${c[3]}`);
    const sub=a.match(/^(anterior|posterior) division of (superior|middle|inferior) trunk$/);if(sub)al.add(`${sub[1]} division of the ${sub[2]} trunk`);
  }
  for(const a of al)if(a.length>=4)term(reEsc(a).replace(/\s+/g,'\\s+').replace(/-/g,'[-\\s]?')+'s?',[k],st.name);
  const cn=full.match(/\((?:CN\s+)?([IVX]+)(\d?)\)/);
  if(cn){const r=cn[1].toLowerCase(),n=ROMAN.indexOf(r),sub=cn[2];
    if(n>0)term(`(?:cn|c\\.n\\.|cranial\\s+nerve)\\s*(?:${r}|${n})${sub?`\\s*-?\\s*${sub}|v\\s*${sub}\\s+division`:'(?![\\divx])'}`,[k],st.name)}
}
const NSYN=[
 ['deep\\s+radial\\s+nerve|deep\\s+branch\\s+of\\s+(?:the\\s+)?radial','z-deep-branch-of-radial-nerve'],['superficial\\s+radial(?:\\s+nerve)?','z-superficial-branch-of-radial-nerve'],
 ['deep\\s+ulnar(?:\\s+nerve)?','z-deep-branch-of-ulnar-nerve'],['superficial\\s+ulnar(?:\\s+nerve)?','z-superficial-branch-of-ulnar-nerve'],
 ['lateral\\s+cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?forearm|lateral\\s+antebrachial\\s+cutaneous','z-lateral-antebrachial-cutaneous-nerve'],
 ['medial\\s+cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?forearm','z-medial-antebrachial-cutaneous-nerve'],['medial\\s+cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?arm','z-medial-brachial-cutaneous-nerve'],
 ['posterior\\s+cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?forearm','z-posterior-antebrachial-cutaneous-nerve'],
 ['posterior\\s+(?:femoral\\s+cutaneous|cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?thigh)(?:\\s+nerve)?','z-posterior-femoral-cutaneous-nerve'],
 ['lateral\\s+(?:femoral\\s+cutaneous|cutaneous\\s+nerve\\s+of\\s+(?:the\\s+)?thigh)(?:\\s+nerve)?|lfcn|meralgia\\s+paraesthetica|meralgia\\s+paresthetica','z-lateral-femoral-cutaneous-nerve'],
 ['upper\\s+subscapular(?:\\s+nerve)?|superior\\s+subscapular(?:\\s+nerve)?','p-upper-subscapular-nerve'],['lower\\s+subscapular(?:\\s+nerve)?|inferior\\s+subscapular(?:\\s+nerve)?','p-lower-subscapular-nerve'],
 ['middle\\s+subscapular(?:\\s+nerve)?','thoracodorsal'],['nerve\\s+to\\s+(?:the\\s+)?subclavius|subclavian\\s+nerve','z-subclavian-nerve'],
 ['spinal\\s+accessory(?:\\s+nerve)?','accessory'],['nerve\\s+of\\s+bell','long-thoracic'],['sympathetic\\s+(?:chain|trunk)','z-sympathetic-trunk'],
 ['ophthalmic\\s+division','p-ophthalmic-nerve'],['maxillary\\s+division','z-maxillary-nerve'],['mandibular\\s+division','mandibular'],
 ['(?:roots|ventral\\s+rami)\\s+of\\s+(?:the\\s+)?brachial\\s+plexus|c5\\s*[-–]\\s*t1\\s+(?:roots|ventral\\s+rami)|brachial\\s+plexus\\s+roots','p-roots-of-brachial-plexus'],
 ['upper\\s+trunk','p-superior-trunk-of-brachial-plexus'],['lower\\s+trunk','p-inferior-trunk-of-brachial-plexus'],
 ['digital\\s+nerves?\\s+of\\s+(?:the\\s+)?hand|palmar\\s+digital\\s+nerves?','z-proper-palmar-digital-branches-of-median-nerve'],['plantar\\s+digital\\s+nerves?','z-proper-plantar-digital-branches-of-medial-plantar-nerve'],
 ['nerve\\s+to\\s+(?:the\\s+)?piriformis','z-nerve-to-piriformis-muscle'],['nerve\\s+to\\s+(?:the\\s+)?quadratus\\s+femoris','z-nerve-to-quadratus-femoris-muscle'],['nerve\\s+to\\s+(?:the\\s+)?mylohyoid','z-nerve-to-mylohyoid-muscle'],
 ['dorsal\\s+roots?|posterior\\s+roots?(?!\\s+of\\s+(?:the\\s+)?post)','z-posterior-root-of-spinal-nerve'],['ventral\\s+roots?|anterior\\s+roots?(?!\\s+of\\s+(?:the\\s+)?post)','z-anterior-root-of-spinal-nerve'],
 ['lateral\\s+(?:and|&)\\s+medial\\s+pectoral\\s+nerves|medial\\s+(?:and|&)\\s+lateral\\s+pectoral\\s+nerves','pectoral'],['pectoral\\s+nerves','pectoral'],
];
for(const [p,k] of NSYN)if(byK[k])term(p,[k],byK[k][0].name);
const NGRP=[['lumbar\\s+plexus',['z-iliohypogastric-nerve','z-ilio-inguinal-nerve','z-genitofemoral-nerve','z-lateral-femoral-cutaneous-nerve','femoral','obturator'],'Lumbar plexus'],
 ['sacral\\s+plexus',['sciatic','superior-gluteal','inferior-gluteal','pudendal','z-posterior-femoral-cutaneous-nerve','z-nerve-to-piriformis-muscle','z-nerve-to-quadratus-femoris-muscle'],'Sacral plexus'],
 ['lumbosacral\\s+plexus',['z-iliohypogastric-nerve','z-ilio-inguinal-nerve','z-genitofemoral-nerve','z-lateral-femoral-cutaneous-nerve','femoral','obturator','sciatic','superior-gluteal','inferior-gluteal','pudendal','z-posterior-femoral-cutaneous-nerve'],'Lumbosacral plexus'],
 ['cords\\s+of\\s+(?:the\\s+)?brachial\\s+plexus|brachial[-\\s]plexus[-\\s]cords',['p-lateral-cord-of-brachial-plexus','p-medial-cord-of-brachial-plexus','p-posterior-cord-of-brachial-plexus'],'Cords of brachial plexus'],
 ['trunks\\s+of\\s+(?:the\\s+)?brachial\\s+plexus',['p-superior-trunk-of-brachial-plexus','p-middle-trunk-of-brachial-plexus','p-inferior-trunk-of-brachial-plexus'],'Trunks of brachial plexus'],
 ['divisions\\s+of\\s+(?:the\\s+)?brachial\\s+plexus',['p-anterior-division-of-superior-trunk','p-anterior-division-of-middle-trunk','p-anterior-division-of-inferior-trunk','p-posterior-division-of-superior-trunk','p-posterior-division-of-middle-trunk','p-posterior-division-of-inferior-trunk'],'Divisions of brachial plexus'],
 ['terminal\\s+(?:branches|nerves)\\s+of\\s+(?:the\\s+)?brachial\\s+plexus',['musculocutaneous','axillary','radial','median','ulnar'],'Terminal branches of brachial plexus'],
 ['cranial\\s+nerves',[],'Cranial nerves']];
for(const [p,ks,l] of NGRP){const f=ks.filter(k=>byK[k]);if(f.length)term(p,f,l)}
'''
rep("const LATIN=[[",NERVE_TERMS+"const LATIN=[[")
# 'cords of brachial plexus' was rewritten by LATIN into a parent alias; keep the phrase intact instead
rep("const LATIN=[['cords?\\\\s+of\\\\s+(?:the\\\\s+)?brachial\\\\s+plexus','brachial-plexus-cords'],","const LATIN=[")
rep("PIN:'radial',AIN:'median'","PIN:'z-posterior-interosseous-nerve-of-forearm',AIN:'z-anterior-interosseous-nerve-of-forearm',LFCN:'z-lateral-femoral-cutaneous-nerve'")
# BRANCH: nerves that are now their own structures no longer route to a parent
i,j=cut(" ['(?:lateral|medial|posterior)\\\\s+cords?','brachial-plexus',0]","['ansa\\\\s+cervicalis','phrenic',0]];")
s=s[:i]+" ['intercostobrachial(?:\\\\s+nerve)?','intercostal',0],['subcostal\\\\s+nerve','intercostal',0],['recurrent\\\\s+(?:branch|motor\\\\s+branch)\\\\s+of\\\\s+(?:the\\\\s+)?median(?:\\\\s+nerve)?','z-muscular-branches-of-median-nerve',0]];"+s[j:]

# ---------- 2. span-based matching: longest term wins, one row per slide term ----------
i,j=cut("function slideItems(text,keys,labels,raw){","  return items;\n}\n")
s=s[:i]+r'''function termHits(text){
  const hits=[];
  for(const t of TERMS){const g=t.g||(t.g=new RegExp(t.re.source,'gi'));g.lastIndex=0;let m;
    while((m=g.exec(text))){if(!m[0]){g.lastIndex++;continue}hits.push({s:m.index,e:m.index+m[0].length,txt:m[0],keys:t.keys,label:t.label})}}
  ABBR_RE.lastIndex=0;for(const m of text.matchAll(ABBR_RE)){const k=ABBR[m[1]];if(byK[k])hits.push({s:m.index,e:m.index+m[0].length,txt:m[1],keys:[k],label:byK[k][0].name})}
  hits.sort((a,b)=>(b.e-b.s)-(a.e-a.s)||a.s-b.s);
  const taken=[],out=[];
  for(const h of hits){if(taken.some(([s,e])=>h.s<e&&h.e>s))continue;taken.push([h.s,h.e]);out.push(h)}
  return out.sort((a,b)=>a.s-b.s);
}
const KORD={nerve:0,muscle:1,tendon:1,artery:2,vein:3,organ:3,bone:4,disc:4,ligament:5};
const KGRP={nerve:'Nerves',muscle:'Muscles',tendon:'Muscles',artery:'Arteries',vein:'Veins',organ:'Veins',bone:'Bones',disc:'Bones',ligament:'Ligaments'};
function guessKind(p){p=p.toLowerCase();return /nerve|plexus|cord|trunk|ramus|rami|root|branch/.test(p)?'nerve':/arter|arch/.test(p)?'artery':/vein|venous/.test(p)?'vein':/ligament|capsule|retinaculum|aponeurosis|fascia/.test(p)?'ligament':/tendon/.test(p)?'muscle':'other'}
function slideItems(text,rows,labels,raw){
  const items=[...rows.values()],seen=new Set();
  for(const it of items){seen.add(it.said.toLowerCase());for(const k of it.keys)seen.add(byK[k][0].name.toLowerCase().replace(/\s*\(.*?\)/g,''))}
  for(const l of labels||[])seen.add(String(l).toLowerCase().replace(/\s*\(.*?\)/g,''));
  const have=new Set(items.flatMap(i=>i.keys));
  for(const [re,k,,self] of BRANCH_RE){const m=text.match(re);if(!m||!byK[k])continue;const said=cap(m[0].trim());
    if(seen.has(said.toLowerCase())||(self&&have.has(k)))continue;seen.add(said.toLowerCase());have.add(k);
    items.push({label:self?byK[k][0].name:said,said,status:self?'ok':'parent',keys:[k],via:byK[k][0].name,kind:byK[k][0].kind})}
  const head=t=>t.split(' ').slice(0,-1).join(' ');
  for(const line of String(raw||text).split(/\n|[•–—]|\s-\s|;/)){const lt=normText(line).split('  ')[0];
   for(const m of lt.matchAll(PHRASE_RE)){const p=m[0].trim().replace(/\s+/g,' ');const low=p.toLowerCase();const words=low.split(' ');
    if(words.length<2||STOP.test(words.slice(0,-1).join(' ')))continue;
    if([...seen].some(n=>n.includes(low)||low.includes(n)||head(n)===head(low)))continue;
    if(BRANCH_RE.some(([re])=>re.test(low)))continue;
    seen.add(low);items.push({label:cap(p),said:cap(p),status:'missing',keys:[],kind:guessKind(p)})}}
  for(const it of items)if(!it.kind)it.kind=it.keys.length?byK[it.keys[0]][0].kind:'other';
  return items;
}
'''+s[j:]
i,j=cut("  for(const t of TERMS){if(t.re.test(text)){let ks=t.keys;","  for(const t of RTERMS)if(t.re.test(text))for(const r of t.regions)regions.add(r);\n  const low=text.toLowerCase();")
s=s[:i]+r'''  const rows=new Map();
  for(const h of termHits(text)){let ks=h.keys.filter(k=>byK[k]);if(!ks.length)continue;
    if(ks.length>3&&regions.size){const f=ks.filter(k=>nearR.has(byK[k][0].region));if(f.length)ks=f}   /* group terms stay in the slide's region */
    const id=ks.slice().sort().join('|');const said=cap(h.txt.replace(/\s+/g,' ').trim());
    if(!rows.has(id))rows.set(id,{label:ks.length>1?h.label:byK[ks[0]][0].name,said,keys:ks,status:ks.length>1?'group':'ok'});
    else if(!rows.get(id).alts){rows.get(id).alts=new Set([said.toLowerCase()])}
    for(const k of ks)keys.add(k);labels.push(h.label)}
  for(const t of RTERMS)if(t.re.test(text))for(const r of t.regions)regions.add(r);
  const low=text.toLowerCase();'''+s[j:]
rep("const items=slideItems(text,keys,labels,raw);","const items=slideItems(text,rows,labels,raw);")

# ---------- 3. tracker panel ----------
i,j=cut("function renderMatch(applied){","  const ap=$('#lecApply');if(ap)ap.onclick=()=>{applyAnalysis(LEC.an);renderMatch(true)};\n")
j=s.index("\n",s.index("el.querySelectorAll('[data-ci]')",j))+1
if s[j:].startswith('}\n'): j+=2
s=s[:i]+r'''const KCOL={nerve:'#E5BE1F',muscle:'#B23A32',tendon:'#B23A32',artery:'#E0473C',vein:'#3B6FD8',organ:'#3B6FD8',bone:'#C9B98F',disc:'#C9B98F',ligament:'#7FA3BA',other:'#8A949A'};
const EYE='<svg viewBox="0 0 24 24"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',EYEX='<svg viewBox="0 0 24 24"><path d="M3 3l18 18M10.6 5.1A10 10 0 0112 5c6.4 0 10 7 10 7a17 17 0 01-3.3 4.2M6.6 6.6A17 17 0 002 12s3.6 7 10 7a9.6 9.6 0 004.2-.9"/><path d="M9.9 9.9a3 3 0 004.2 4.2"/></svg>',PINI='<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2M11 8v6M8 11h6"/></svg>';
function trackRows(an){
  const items=(an.items||[]).slice();
  items.sort((a,b)=>(KORD[a.kind]??6)-(KORD[b.kind]??6)||(a.status==='missing')-(b.status==='missing'));
  let n=0;LEC.num=new Map();
  for(const it of items){if(it.status==='missing'){it.n=0;continue}it.n=++n;for(const k of it.keys)if(!LEC.num.has(k))LEC.num.set(k,n)}
  return items;
}
function renderMatch(applied){
  const an=LEC.an,el=$('#lecMatch');if(!el)return;
  if(!an.keys.size&&!an.regions.size&&!(an.items||[]).length){LEC.num=new Map();el.innerHTML=`<div class="trk"><div class="trk-empty"><b>No anatomy on this slide</b>The model stays as it was. Type a focus below to show something.</div></div>`;queueLabels();return}
  const items=trackRows(an);LEC.rows=items;
  const nOk=items.filter(i=>i.status==='ok').length,nGrp=items.filter(i=>i.status==='group').length,nPar=items.filter(i=>i.status==='parent').length,nMiss=items.filter(i=>i.status==='missing').length;
  const tot=items.length,on=tot-nMiss,pct=tot?on/tot:1;
  const fil=LEC.filter||'all';
  const kinds=[...new Set(items.map(i=>KGRP[i.kind]||'Other'))];
  const shownRow=it=>fil==='all'||(fil==='missing'?it.status==='missing':(KGRP[it.kind]||'Other')===fil);
  const C2=2*Math.PI*19;
  const hidden=k=>(byK[k]||[]).every(st=>ST.hidden.has(st.id));
  const row=(it,i)=>{const col=KCOL[it.kind]||KCOL.other,miss=it.status==='missing';
    const names=it.keys.map(k=>byK[k][0].name);
    const sub=miss?`<span class="tag miss">Not in this 3D model</span>`:it.status==='parent'?`<span class="tag par">Not modelled on its own</span> highlighted on the ${esc(it.via)}`:
      it.status==='group'?`<span class="tag grp">Group · ${it.keys.length}</span> ${esc(names.slice(0,4).join(', '))}${names.length>4?` +${names.length-4}`:''}`:`<span class="tag ok">Exact match</span>`;
    const said=it.said&&it.said.toLowerCase()!==it.label.toLowerCase().replace(/\s*\(.*?\)/g,'')?`<span class="said">“${esc(it.said)}” on slide</span>`:'';
    return `<div class="trk-r ${it.status}${it.src==='img'?' img':''}" data-ti="${i}" ${miss?'':'role="button" tabindex="0"'} style="--kc:${col}">
      <span class="trk-n">${miss?'–':it.n}</span>
      <span class="trk-b"><span class="trk-t">${esc(miss?it.said:it.label)}</span><span class="trk-s">${sub}${said}${it.src==='img'?'<span class="said">from slide picture</span>':''}</span></span>
      ${miss?'':`<span class="trk-a"><button class="ib" data-eye="${i}" title="${hidden(it.keys[0])?'Show':'Hide'} on the model" aria-label="Show or hide">${hidden(it.keys[0])?EYEX:EYE}</button><button class="ib" data-go="${i}" title="Zoom to it" aria-label="Zoom to it">${PINI}</button></span>`}
    </div>`};
  let body='',last='';
  items.forEach((it,i)=>{if(!shownRow(it))return;const g=KGRP[it.kind]||'Other';if(g!==last){last=g;const cnt=items.filter(x=>(KGRP[x.kind]||'Other')===g);body+=`<div class="trk-g"><i style="background:${KCOL[it.kind]||KCOL.other}"></i>${g}<span>${cnt.filter(x=>x.status!=='missing').length}/${cnt.length} on model</span></div>`}body+=row(it,i)});
  el.innerHTML=`<div class="trk">
    <div class="trk-hd">
      <svg class="ring" viewBox="0 0 44 44"><circle cx="22" cy="22" r="19" class="bg"/><circle cx="22" cy="22" r="19" class="fg" style="stroke-dasharray:${C2*pct} ${C2}" transform="rotate(-90 22 22)"/><text x="22" y="26.5" text-anchor="middle">${Math.round(pct*100)}%</text></svg>
      <div><div class="trk-h1">${on} of ${tot} slide term${tot===1?'':'s'} on the model</div>
      <div class="trk-h2">${[nOk&&`<b class="d ok"></b>${nOk} exact`,nGrp&&`<b class="d grp"></b>${nGrp} group${nGrp>1?'s':''}`,nPar&&`<b class="d par"></b>${nPar} on parent`,nMiss&&`<b class="d miss"></b>${nMiss} not modelled`].filter(Boolean).join(' · ')}</div></div>
    </div>
    <div class="trk-bar">${[['ok',nOk],['grp',nGrp],['par',nPar],['miss',nMiss]].filter(x=>x[1]).map(([c,v])=>`<i class="${c}" style="flex:${v}"></i>`).join('')}</div>
    <div class="trk-f">${['all',...kinds,...(nMiss?['missing']:[])].map(f=>`<button data-tf="${f}" aria-pressed="${fil===f}">${f==='all'?'All':f==='missing'?'Not modelled':f} <span>${f==='all'?tot:f==='missing'?nMiss:items.filter(i=>(KGRP[i.kind]||'Other')===f).length}</span></button>`).join('')}</div>
    <div class="trk-l">${body||'<div class="trk-empty">Nothing in this filter.</div>'}</div>
    <div class="trk-ft">Numbers match the tags on the model. ${applied?'':'<button class="btn pri" id="lecApply">Show this on the model</button>'}</div>
  </div>`;
  const pickSt=it=>{const st=byK[it.keys[0]].find(s=>s.side!=='L')||byK[it.keys[0]][0];return st};
  el.querySelectorAll('[data-tf]').forEach(b=>b.onclick=()=>{LEC.filter=b.dataset.tf;renderMatch(applied)});
  el.querySelectorAll('.trk-r[role=button]').forEach(r=>{const it=items[+r.dataset.ti];
    r.onclick=e=>{if(e.target.closest('.ib'))return;const st=pickSt(it);if(isolate)isolate.add(st.id);ST.hidden.delete(st.id);select(st.id,{reveal:!isolate});focus(st)};
    r.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();r.click()}};
    r.onmouseenter=()=>hotLabel(it.n,true);r.onmouseleave=()=>hotLabel(it.n,false)});
  el.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{const it=items[+b.dataset.go];const st=pickSt(it);if(isolate)isolate.add(st.id);ST.hidden.delete(st.id);applyVis();focus(st)});
  el.querySelectorAll('[data-eye]').forEach(b=>b.onclick=()=>{const it=items[+b.dataset.eye];const hide=!hidden(it.keys[0]);
    for(const k of it.keys)for(const st of byK[k])hide?ST.hidden.add(st.id):ST.hidden.delete(st.id);applyVis();syncDrawer();renderMatch(applied)});
  const ap=$('#lecApply');if(ap)ap.onclick=()=>{applyAnalysis(LEC.an);renderMatch(true)};
  queueLabels();
}
function hotLabel(n,on){if(!n)return;for(const l of labelsEl.querySelectorAll(`.lb[data-n="${n}"]`))l.classList.toggle('hot',on)}
'''+s[j:]

# ---------- 4. numbered tags on the model, one per tracked structure ----------
rep("cand.push({st,n:a.n*(st.kind==='nerve'||st.kind==='artery'||st.kind==='vein'?6:1)*(st.id===ST.sel?1e6:1),x:(bx+.5)/w*W,y:H-(by+.5)/h*H})}",
    "const num=onlyIds&&LEC.num?LEC.num.get(st.k)||0:0;\n    cand.push({st,num,n:a.n*(st.kind==='nerve'||st.kind==='artery'||st.kind==='vein'?6:1)*(st.id===ST.sel?1e6:1)*(num?1e4:1),x:(bx+.5)/w*W,y:H-(by+.5)/h*H})}")
rep("for(const cd of cand){if(n>=maxN)break;if(cd.n<minPx)break;\n    const nm=displayName(cd.st);const lw=nm.length*6.2+12;",
    "const tagged=new Set();\n  for(const cd of cand){if(n>=maxN)break;if(cd.n<minPx&&!cd.num)continue;if(cd.num&&tagged.has(cd.num))continue;\n    const nm=displayName(cd.st);const lw=nm.length*6.2+12+(cd.num?20:0);")
rep("    placed.push(box);n++;","    placed.push(box);n++;if(cd.num)tagged.add(cd.num);")
rep("el.innerHTML=`<span>${esc(nm)}</span><i></i><b></b>`;\n    el.onclick=()=>select(cd.st.id);",
    "el.innerHTML=`<span>${cd.num?`<em>${cd.num}</em>`:''}${esc(nm)}</span><i></i><b></b>`;if(cd.num){el.dataset.n=cd.num;el.onmouseenter=()=>{const r=document.querySelector(`.trk-r[data-ti] .trk-n`);document.querySelectorAll('.trk-r').forEach(x=>x.classList.toggle('hot',x.querySelector('.trk-n').textContent==String(cd.num)))};el.onmouseleave=()=>document.querySelectorAll('.trk-r.hot').forEach(x=>x.classList.remove('hot'))}\n    el.onclick=()=>select(cd.st.id);")
# lecture checklist must not crash on nerves without course notes
rep("else if(st.kind==='nerve')line=esc(C.NER[st.k][2]);","else if(st.kind==='nerve')line=esc((C.NER[st.k]||[])[2]||'');")

CSS=r'''
/* ---- lecture tracker ---- */
.trk{border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:10px 0;background:var(--bg,#fff)}
.trk-hd{display:flex;gap:12px;align-items:center;padding:12px 14px 10px}
.trk .ring{width:46px;height:46px;flex:none}.ring .bg{fill:none;stroke:var(--soft);stroke-width:5}.ring .fg{fill:none;stroke:#2E9E5B;stroke-width:5;stroke-linecap:round;transition:stroke-dasharray .4s}
.ring text{font:700 11px var(--f-body);fill:var(--ink,#111)}
.trk-h1{font:650 15px var(--f-body)}.trk-h2{font-size:12.5px;color:var(--muted);margin-top:2px;display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.trk .d{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:3px}
.d.ok,.trk-bar .ok{background:#2E9E5B}.d.grp,.trk-bar .grp{background:#2F7FD8}.d.par,.trk-bar .par{background:#D9921E}.d.miss,.trk-bar .miss{background:#C5CBCE}
.trk-bar{display:flex;height:5px;gap:2px;margin:0 14px 10px;border-radius:3px;overflow:hidden}.trk-bar i{display:block}
.trk-f{display:flex;gap:6px;padding:0 14px 10px;overflow-x:auto;scrollbar-width:none}.trk-f::-webkit-scrollbar{display:none}
.trk-f button{flex:none;border:1px solid var(--line);background:transparent;border-radius:999px;padding:4px 10px;font:500 12.5px var(--f-body);color:inherit;cursor:pointer}
.trk-f button span{color:var(--muted);margin-left:2px}.trk-f button[aria-pressed="true"]{background:#14191C;color:#fff;border-color:#14191C}.trk-f button[aria-pressed="true"] span{color:rgba(255,255,255,.65)}
.trk-l{max-height:min(46vh,420px);overflow:auto;border-top:1px solid var(--line)}
.trk-g{position:sticky;top:0;z-index:1;display:flex;align-items:center;gap:7px;padding:7px 14px 5px;background:var(--soft);font:650 11.5px var(--f-body);letter-spacing:.04em;text-transform:uppercase}
.trk-g i{width:8px;height:8px;border-radius:50%}.trk-g span{margin-left:auto;font-weight:500;color:var(--muted);text-transform:none;letter-spacing:0}
.trk-r{display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;padding:8px 10px 8px 14px;border-bottom:1px solid var(--line);transition:background .12s}
.trk-r[role=button]{cursor:pointer}.trk-r[role=button]:hover,.trk-r.hot{background:color-mix(in srgb,var(--kc) 10%,transparent)}
.trk-n{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--kc);color:#fff;font:700 11.5px var(--f-body);box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
.trk-r.nerve .trk-n,.trk-r[style*="#E5BE1F"] .trk-n,.trk-r[style*="#C9B98F"] .trk-n{color:#1A1405}
.trk-r.missing .trk-n{background:transparent;color:var(--muted);box-shadow:inset 0 0 0 1.5px var(--line);border:1px dashed var(--muted)}
.trk-b{min-width:0;display:flex;flex-direction:column;gap:2px}.trk-t{font:600 14px var(--f-body);overflow-wrap:anywhere}
.trk-r.missing .trk-t{color:var(--muted);font-weight:500}
.trk-s{font-size:12px;color:var(--muted);display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center}
.trk .tag{font:600 10.5px var(--f-body);padding:1px 6px;border-radius:5px}
.tag.ok{background:#E3F4EA;color:#1D7A44}.tag.grp{background:#E3EEFB;color:#1F62B0}.tag.par{background:#FBF0DC;color:#9A6410}.tag.miss{background:#EEF0F1;color:#6A7378}
.said{font-style:italic}
.trk-a{display:flex;gap:2px}.ib{width:30px;height:30px;border:0;background:transparent;border-radius:8px;display:grid;place-items:center;cursor:pointer;color:var(--muted)}
.ib:hover{background:var(--soft);color:inherit}.ib svg{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.trk-ft{padding:9px 14px;font-size:12px;color:var(--muted);display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.trk-empty{padding:16px;color:var(--muted);font-size:13.5px}.trk-empty b{display:block;color:inherit;margin-bottom:2px}
.lb em{display:inline-grid;place-items:center;min-width:16px;height:16px;padding:0 4px;margin:-1px 5px -1px -3px;border-radius:8px;background:#14191C;color:#fff;font:700 10px/1 var(--f-body);font-style:normal;vertical-align:1px}
.lb.hot span{box-shadow:0 0 0 2px #0A84FF,0 2px 10px rgba(0,0,0,.4);transform:scale(1.08)}.lb span{transition:transform .12s}
'''
rep("\n/* ---- AI ---- */",CSS+"\n/* ---- AI ---- */")
open(p,'w').write(s);print('ok')
