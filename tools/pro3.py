"""Professional pass 3: 'About' text for every structure, study content for the new structures, tour finder."""
p = 'site/index.html'; s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

# About text (lazy-loaded defs.json)
rep("function renderExplore(){", """let DEFS=null,defsP=null;
function loadDefs(){if(!defsP)defsP=fetchJSON('defs.json').then(d=>DEFS=d).catch(()=>DEFS={});return defsP}
function firstSentences(t,n,max){const m=t.match(/[^.!?]+[.!?]+(\\s|$)/g)||[t];let o='';for(const x of m.slice(0,n)){if((o+x).length>max&&o)break;o+=x}return o.trim()}
function aboutHTML(st){const d=DEFS&&DEFS[st.k];if(!d)return '';const [intro,secs]=d;
  return `<div class="about"><div class="kick">About</div><p>${esc(intro)}</p>${secs.length?`<details><summary>Read more</summary>${secs.map(([t,b])=>`<h4>${esc(t)}</h4><p>${esc(b)}</p>`).join('')}</details>`:''}
  <div class="src">Text adapted from Wikipedia via Z-Anatomy (CC BY-SA). Check against your course notes.</div></div>`}
function renderExplore(){""")
rep("""   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="aS" ${ST.solo?'checked':''}> Show only this label</label>
   ${credit()}`;""", """   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="aS" ${ST.solo?'checked':''}> Show only this label</label>
   <div id="aboutBox">${aboutHTML(st)}</div>
   ${credit()}`;
  if(!DEFS){const id=st.id;loadDefs().then(()=>{const b=$('#aboutBox');if(b&&ST.sel===id&&ST.tab==='E')b.innerHTML=aboutHTML(st)})}""")

# study: include every structure with About text, 'which structure is described' questions
rep("function kOK(k){return byK[k]&&byK[k].length&&(C.MUS[k]||C.NER[k]||C.VES[k]||C.BON[k]||C.TEN[k]||LIG[k])}",
    "function kCore(k){return byK[k]&&byK[k].length&&(C.MUS[k]||C.NER[k]||C.VES[k]||C.BON[k]||C.TEN[k]||LIG[k])}\nfunction kOK(k){return kCore(k)||(SCFG.all&&byK[k]&&byK[k].length&&DEFS&&DEFS[k])}")
rep("&&(kindOfK(k)!=='ligament'||!!LIG[k][1])&&", "&&(kindOfK(k)!=='ligament'||!LIG[k]||!!LIG[k][1]||SCFG.all)&&")
rep("const QT={muscle:['find','name','nerve','action','origin','insertion','findclue'],nerve:['find','name','supplies','whichnerve'],vessel:['find','name','vsup'],bone:['find','name'],tendon:['find','name'],ligament:['find','name','ligjoint']};",
    "const QT={muscle:['find','name','nerve','action','origin','insertion','findclue','about'],nerve:['find','name','supplies','whichnerve','about'],vessel:['find','name','vsup','about'],bone:['find','name','about'],tendon:['find','name'],ligament:['find','name','ligjoint','about']};")
rep("  if(!(QT[kind]||[]).includes(type)||(['nerve','action','origin','insertion','findclue'].includes(type)&&!M))type='name';",
    "  if(type==='about'&&!(DEFS&&DEFS[k]))type=kCore(k)?'name':'find';\n  if(!(QT[kind]||[]).includes(type)||(['nerve','action','origin','insertion','findclue'].includes(type)&&!M))type='name';")
rep("    case 'vsup':{", """    case 'about':{let t=firstSentences(DEFS[k][0],2,300);const words=[nm,nm.replace(/ (muscle|nerve|artery|vein|ligament|bone)s?$/i,''),...(nm.match(/\\(([^)]+)\\)/)||[]).slice(1)].filter(w=>w&&w.length>3);
      for(const w of words)t=t.split(new RegExp(w.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'ig')).join('this structure');t=t.replace(/\\s*\\([A-Z]{2,6}\\)/g,'');
      q.prompt='Which structure is described? “'+t+'”';q.opts=shuffle([nm,...optsK(3).map(nameOfK)]).map(x=>({t:x,ok:x===nm}));break}
    case 'vsup':{""")
rep("  if(MN[k])h+=`<div class=\"note\"><b>Memory aid</b>${esc(MN[k])}</div>`;return h}",
    "  if(!h&&DEFS&&DEFS[k])h=`<p style=\"margin:6px 0 0\">${esc(firstSentences(DEFS[k][0],3,420))}</p>`;\n  if(MN[k])h+=`<div class=\"note\"><b>Memory aid</b>${esc(MN[k])}</div>`;return h}")
rep("""   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="sSi" """,
    """   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="sAll" ${SCFG.all?'checked':''}> Include every structure (minor branches, small ligaments)</label>
   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="sSi" """)
rep("$('#sSi').onchange=e=>{SCFG.side=e.target.checked;sv()};", "$('#sSi').onchange=e=>{SCFG.side=e.target.checked;sv()};$('#sAll').onchange=e=>{SCFG.all=e.target.checked;sv();renderStudy()};")
rep("function renderStudy(){\n", "function renderStudy(){\n  if(!DEFS){loadDefs().then(()=>{if(ST.tab==='S')renderStudy()})}\n")

# tour picker: every nerve and vessel, with a filter box
old = s[s.index("function renderTourPick(){"):s.index("function renderTour(){")]
new = r"""function renderTourPick(q){
  q=(q||'').toLowerCase();const ok=x=>S[x.id]&&x.side!=='L'&&(C.NER[x.k]||C.VES[x.k]||(DEFS&&DEFS[x.k])||x.paths.reduce((a,p)=>a+p.length,0)>40)&&(!q||x.name.toLowerCase().includes(q));
  const core=x=>C.NER[x.k]||C.VES[x.k];
  const nv=NERV.filter(ok),ar=VESS.filter(v=>v.kind==='artery'&&ok(v)),ve=VESS.filter(v=>v.kind==='vein'&&ok(v));
  const row=(t,L)=>L.length?`<div class="kick" style="margin-top:14px">${t} · ${L.length}</div><div class="links" style="margin-top:6px">${L.sort((a,b)=>(core(b)?1:0)-(core(a)?1:0)||a.name.localeCompare(b.name)).slice(0,q?200:60).map(x=>`<button class="lnk${S[x.id].kind==='nerve'?' nv':''}" data-tr="${x.id}" ${core(x)?'style="font-weight:600"':''}>${esc(x.name)}</button>`).join('')}${!q&&L.length>60?`<span class="hint" style="align-self:center">+${L.length-60} more — type to filter</span>`:''}</div>`:'';
  pane.innerHTML=`<div class="kick">Follow a structure</div><h2 class="name">Pick a nerve or vessel</h2><p class="hint">The camera flies along its course and stops at each muscle it supplies, or at each branch and continuation. Course-core structures are in bold.</p>
   <input class="search" id="tF" type="search" placeholder="Filter, e.g. median, saphenous, plantar" value="${esc(q)}" style="margin-top:8px" autocomplete="off">
   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:10px;cursor:pointer"><input type="checkbox" id="tQz" ${TOUR.quiz?'checked':''}> Quiz me at each muscle before naming it</label>
   ${row('Nerves',nv)}${row('Arteries',ar)}${row('Veins',ve)}${!nv.length&&!ar.length&&!ve.length?'<p class="hint">No nerve or vessel matches.</p>':''}<div class="acts"><button class="btn" id="sB">Back</button></div>`;
  const f=$('#tF');f.oninput=()=>{renderTourPick(f.value);const g=$('#tF');g.focus();g.setSelectionRange(g.value.length,g.value.length)};
  $('#tQz').onchange=e=>{TOUR.quiz=e.target.checked};
  pane.querySelectorAll('[data-tr]').forEach(b=>b.onclick=()=>startTour(b.dataset.tr));$('#sB').onclick=()=>renderStudy();
}
"""
s = s.replace(old, new)
open(p, 'w').write(s); print('pro3 ok')
