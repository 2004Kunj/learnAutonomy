"""Professional pass 2: command palette, shortcuts, help, welcome, selection card, outline, floor shadow."""
p = 'site/index.html'; s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

# keep helpers out of the id-buffer pass
rep("function idPass(w,h,cam){\n  idRT.setSize(w,h);const swaps=[];",
    "function idPass(w,h,cam){\n  idRT.setSize(w,h);const swaps=[];const deco=DECO.filter(o=>o.visible);for(const o of deco)o.visible=false;")
rep("  table.visible=tv;pinG.visible=pv;return px;", "  table.visible=tv;pinG.visible=pv;for(const o of deco)o.visible=true;return px;")
rep("const idRT=new THREE.WebGLRenderTarget(4,4);", "const DECO=[];const idRT=new THREE.WebGLRenderTarget(4,4);")

# selection outline (inverted hull) — rebuilt only when the selection changes
rep("function highlight(){\n  Q.dirty=true;\n", """const OUTL={sel:null,meshes:[],mat:null};
function outlineMat(){if(OUTL.mat)return OUTL.mat;const m=new THREE.MeshBasicMaterial({color:0xFFC14D,side:THREE.BackSide,transparent:true,opacity:.95,depthWrite:false});
  m.onBeforeCompile=sh=>{sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\\ntransformed+=normalize(normal)*1.15;')};m.customProgramCacheKey=()=>'outline';return OUTL.mat=m}
function updateOutline(){const id=ST.sel&&!(lab.active&&!(lab.cur&&lab.cur.done))?ST.sel:null;if(id===OUTL.sel)return;OUTL.sel=id;
  for(const o of OUTL.meshes){o.parent&&o.parent.remove(o);const i=DECO.indexOf(o);if(i>=0)DECO.splice(i,1)}OUTL.meshes=[];
  const st=id&&S[id];if(!st)return;
  for(const m of st.meshes){if(!m.geometry.attributes.normal)continue;const o=new THREE.Mesh(m.geometry,outlineMat());o.renderOrder=-1;o.raycast=()=>{};m.add(o);OUTL.meshes.push(o);DECO.push(o)}}
function highlight(){
  Q.dirty=true;updateOutline();renderSelcard();
""")

# soft floor shadow under the standing body
rep("function setPose(p){\n  shadowDirty();\n", """let floorM=null;
function floorShadow(){
  if(!floorM){const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');const gr=g.createRadialGradient(128,128,4,128,128,128);
    gr.addColorStop(0,'rgba(0,0,0,.55)');gr.addColorStop(.45,'rgba(0,0,0,.22)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,256,256);
    floorM=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(c),transparent:true,depthWrite:false}));floorM.rotation.x=-Math.PI/2;floorM.raycast=()=>{};scene.add(floorM);DECO.push(floorM)}
  const bb=new THREE.Box3().setFromObject(body);floorM.position.set((bb.min.x+bb.max.x)/2,bb.min.y-1,(bb.min.z+bb.max.z)/2);floorM.scale.set(560,380,1);floorM.visible=ST.pose==='stand'}
function setPose(p){
  shadowDirty();
""")
rep("  key.position.set(p==='stand'?600:260,", "  floorShadow();\n  key.position.set(p==='stand'?600:260,")

# selection card + palette + help + welcome + shortcuts (defined before first use at boot)
rep("/* ---------- graphics quality ---------- */", r"""/* ---------- selection card ---------- */
const SVG={focus:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M3 9V5a2 2 0 012-2h4M15 3h4a2 2 0 012 2v4M21 15v4a2 2 0 01-2 2h-4M9 21H5a2 2 0 01-2-2v-4"/></svg>',
  hide:'<svg viewBox="0 0 24 24"><path d="M3 3l18 18M10.6 6.1A9.6 9.6 0 0112 6c5 0 9 6 9 6a17 17 0 01-3.2 3.7M6.6 6.6C4.3 8.1 3 12 3 12s4 6 9 6a9 9 0 004.4-1.1"/></svg>',
  iso:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/></svg>',
  info:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/></svg>',
  x:'<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>'};
function deselect(){ST.sel=null;ST.selPart='';applyVis();if(ST.tab==='E')renderExplore()}
function renderSelcard(){const el=$('#selcard');if(!el)return;const st=S[ST.sel];
  const hide=!st||lab.active||(typeof QZ!=='undefined'&&QZ.active)||(typeof TOUR!=='undefined'&&TOUR.active&&TOUR.opts&&!TOUR.ans);
  $('.app').classList.toggle('hassel',!hide);if(hide){el.hidden=true;el.dataset.id='';return}
  if(el.dataset.id===st.id+(isolate?'i':'')&&!el.hidden)return;el.dataset.id=st.id+(isolate?'i':'');el.hidden=false;
  el.innerHTML=`<span class="kd">${esc(KINDW[st.kind]||st.kind)}</span><span class="nm">${esc(titleName(st))}</span>
   <button data-a="f" title="Zoom to it (F)">${SVG.focus}<span class="bt">Zoom</span></button><button data-a="i" title="Isolate (I)">${SVG.iso}<span class="bt">${isolate?'Show all':'Isolate'}</span></button>
   <button data-a="h" title="Dissect away (H)">${SVG.hide}<span class="bt">Hide</span></button><button data-a="d" title="Details">${SVG.info}</button><button data-a="x" title="Deselect (Esc)" aria-label="Deselect">${SVG.x}</button>`;
  el.querySelectorAll('[data-a]').forEach(b=>b.onclick=()=>selAction(b.dataset.a))}
function selAction(a){const st=S[ST.sel];if(!st)return;
  if(a==='f')focus(st);
  else if(a==='i'){isolate=isolate?null:new Set([st.id]);applyVis();syncDrawer();if(isolate)focus(st);if(ST.tab==='E')renderExplore();renderSelcard()}
  else if(a==='h'){ST.hidden.add(st.id);toast(`${displayName(st)} dissected away · Restore in Layers`);deselect();syncDrawer()}
  else if(a==='d'){if(ST.tab!=='E')setTab('E');renderExplore()}
  else if(a==='x')deselect()}

/* ---------- command palette: find anything ---------- */
let PAL=null;
function palItems(q){q=q.trim().toLowerCase().replace(/[-\s]+/g,' ');const seen=new Set(),out=[];
  for(const st of ALL){if(seen.has(st.k))continue;seen.add(st.k);const n=st.name.toLowerCase().replace(/[-\s]+/g,' ');let sc=0;
    if(!q)sc=ST.studied.has(st.k)?2:0;else if(n.startsWith(q))sc=5;else if((' '+n).includes(' '+q))sc=4;else if(n.includes(q))sc=3;
    else{const w=q.split(' ');if(w.every(x=>n.includes(x)))sc=2;else continue}
    if(q&&!sc)continue;out.push({st,sc:sc-n.length/400})}
  return out.sort((a,b)=>b.sc-a.sc).slice(0,q?40:12)}
function openPalette(){if(PAL)return;const sc=document.createElement('div');sc.className='scrim';sc.innerHTML=`<div class="palette" role="dialog" aria-label="Find a structure"><input id="palQ" placeholder="Find a muscle, bone, ligament, nerve or vessel…" autocomplete="off" aria-label="Search"><ul id="palL" role="listbox"></ul><div class="foot"><span><kbd>↑</kbd> <kbd>↓</kbd> move</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span></div></div>`;
  document.body.appendChild(sc);PAL={el:sc,i:0,items:[]};const inp=$('#palQ');
  const col={muscle:'var(--c-muscle)',nerve:'var(--c-nerve)',bone:'var(--c-bone)',disc:'var(--c-bone)',tendon:'var(--c-tendon)',ligament:'#7FA3B8',artery:'#C8302A',vein:'#3B5FB8',organ:'#9A3A34'};
  const draw=()=>{PAL.items=palItems(inp.value);PAL.i=Math.min(PAL.i,Math.max(0,PAL.items.length-1));
    $('#palL').innerHTML=PAL.items.length?PAL.items.map((it,i)=>`<li role="option" data-i="${i}" aria-selected="${i===PAL.i}"><i class="dot" style="background:${col[it.st.kind]}"></i>${esc(it.st.name)}<small>${esc(KINDW[it.st.kind]||'')} · ${esc(it.st.region)}</small></li>`).join(''):'<li style="cursor:default;color:var(--muted)">No match — try part of a name, e.g. “cruciate” or “saphenous”.</li>';
    $('#palL').querySelectorAll('[data-i]').forEach(li=>li.onclick=()=>{PAL.i=+li.dataset.i;go()})};
  const go=()=>{const it=PAL.items[PAL.i];closePalette();if(!it)return;const id=sameSide(it.st.k,'R');const t=S[id];if(t.kind==='nerve'||isVes(t.kind))ST.xray=true;select(id,{reveal:true,stay:ST.tab!=='E'&&ST.tab!=='I'});focus(t);if(ST.tab==='I')setTab('E')};
  inp.oninput=()=>{PAL.i=0;draw()};
  inp.onkeydown=e=>{if(e.key==='ArrowDown'){PAL.i=Math.min(PAL.items.length-1,PAL.i+1);draw();e.preventDefault()}else if(e.key==='ArrowUp'){PAL.i=Math.max(0,PAL.i-1);draw();e.preventDefault()}else if(e.key==='Enter'){go();e.preventDefault()}else if(e.key==='Escape'){closePalette()}};
  sc.onclick=e=>{if(e.target===sc)closePalette()};draw();inp.focus()}
function closePalette(){if(PAL){PAL.el.remove();PAL=null}}

/* ---------- help & welcome ---------- */
function dialog(html){const sc=document.createElement('div');sc.className='scrim';sc.innerHTML=`<div class="dlg" role="dialog">${html}</div>`;document.body.appendChild(sc);
  const close=()=>sc.remove();sc.onclick=e=>{if(e.target===sc||e.target.closest('[data-close]'))close()};const k=e=>{if(e.key==='Escape'){close();removeEventListener('keydown',k,true)}};addEventListener('keydown',k,true);return sc}
function showHelp(){dialog(`<h2>Shortcuts &amp; controls</h2><p class="hint" style="margin:0">Drag to rotate · right-drag or two fingers to pan · scroll or pinch to zoom · click a structure to select it.</p>
  <div class="grid"><kbd>/</kbd><span>Find any structure (also Ctrl K / ⌘K)</span><kbd>1</kbd><span>Anterior view</span><kbd>2</kbd><span>Posterior view</span><kbd>3</kbd><span>Right lateral</span><kbd>4</kbd><span>Left lateral</span><kbd>5</kbd><span>Superior view</span>
  <kbd>L</kbd><span>Labels on / off</span><kbd>N</kbd><span>Nerves</span><kbd>V</kbd><span>Vessels</span><kbd>G</kbd><span>Ligaments view</span><kbd>C</kbd><span>Cadaver colouring</span><kbd>E</kbd><span>Explode muscles</span>
  <kbd>F</kbd><span>Zoom to the selected structure</span><kbd>I</kbd><span>Isolate / show everything</span><kbd>H</kbd><span>Dissect away the selection</span><kbd>Esc</kbd><span>Deselect · close</span><kbd>R</kbd><span>Reset the model</span><kbd>?</kbd><span>This help</span></div>
  <div class="acts"><button class="btn" id="hW">Show the welcome guide</button><button class="btn pri" data-close>Done</button></div>`);$('#hW').onclick=()=>{document.querySelector('.scrim').remove();showWelcome()}}
function showWelcome(){LS.set('kl.welcomed',1);dialog(`<div class="kick">KNES 259 · Anatomy Lab</div><h2>Welcome to the specimen</h2>
  <div class="steps"><div><b>1</b><span><strong>Explore.</strong> Rotate the 3D model and click any muscle, bone, ligament, nerve or vessel for its origin, insertion, action, innervation and notes.</span></div>
  <div><b>2</b><span><strong>Find.</strong> Press <kbd>/</kbd> to search by name. Use the toolbar to show nerves, vessels or ligaments, explode the muscles, or switch to cadaver colouring.</span></div>
  <div><b>3</b><span><strong>Learn from your lectures.</strong> Open your slides in <strong>Lecture</strong> — the model follows each slide.</span></div>
  <div><b>4</b><span><strong>Practise.</strong> <strong>Cadaver lab</strong> runs timed bellringers; <strong>Study</strong> gives you daily review, drills, quizzes and practice exams.</span></div></div>
  <div class="acts"><button class="btn pri" data-close>Start exploring</button></div>`)}
$('#bSearch').onclick=openPalette;$('#bHelp').onclick=showHelp;
addEventListener('keydown',e=>{
  const t=e.target;if(t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.isContentEditable)){return}
  if(document.querySelector('.scrim')&&e.key!=='Escape')return;
  const k=e.key.toLowerCase();
  if((e.ctrlKey||e.metaKey)&&k==='k'){e.preventDefault();openPalette();return}
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  const click=id=>{const b=$(id);if(b)b.click()};
  if(k==='/'){e.preventDefault();openPalette()}else if(e.key==='?'){showHelp()}
  else if('12345'.includes(k)&&k){view(['front','back','right','left','top'][+k-1])}
  else if(k==='l')click('#bLabels');else if(k==='n')click('#bNerves');else if(k==='v')click('#bVessels');else if(k==='g')click('#bLig');else if(k==='c')click('#bLook');else if(k==='r')click('#bReset');
  else if(k==='e'){setExplode(ST.explode>.05?0:.6)}
  else if(k==='f')selAction('f');else if(k==='i')selAction('i');else if(k==='h')selAction('h');
  else if(k==='escape'){if(ST.sel)deselect();else if(isolate){isolate=null;applyVis();syncDrawer()}}
});
if(!LS.get('kl.welcomed',0)&&!new URLSearchParams(location.search).get('lite'))setTimeout(showWelcome,600);

/* ---------- graphics quality ---------- */""")
open(p, 'w').write(s); print('pro2 ok')
