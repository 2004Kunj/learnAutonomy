"""Professional pass 1: toolbar, styling, cached/robust loading, quality modes, error handling."""
p = 'site/index.html'; s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

# ---------- CSS ----------
CSS = r"""
/* ---- professional pass ---- */
.stage::after{content:'';position:absolute;inset:0;pointer-events:none;z-index:1;background:radial-gradient(ellipse 75% 70% at 50% 45%,transparent 55%,rgba(0,0,0,.38))}
.app.cad .stage::after{background:radial-gradient(ellipse 75% 70% at 50% 45%,transparent 50%,rgba(0,0,0,.45))}
.labels{z-index:2}.hud{z-index:3}.orient,.labbar,.selcard{z-index:3}
.hud .grp{display:inline-flex;gap:4px;align-items:center}
.hud .sep{width:1px;height:22px;background:rgba(255,255,255,.16);margin:0 3px}
.hud .spacer{flex:1}
.pill svg{width:15px;height:15px;flex:none;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.pill:hover:not(.ghost):not(.exp){background:rgba(38,50,57,.92)}
.pill[aria-pressed="true"]:hover{background:#FFFFFF}
.pill kbd,.dlg kbd,.palette kbd{font:500 10.5px var(--f-mono);padding:1px 5px;border-radius:4px;border:1px solid rgba(127,140,146,.45);color:inherit;opacity:.8}
.seg button:hover:not([aria-pressed="true"]){background:rgba(255,255,255,.08)}
@media (max-width:1180px){.pill .t{display:none}.pill{padding:6px 8px}}
@media (max-width:860px){.hud{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-bottom:8px}.hud::-webkit-scrollbar{display:none}.hud .spacer{display:none}}
.btn:hover:not(:disabled){border-color:var(--accent)}
.btn.pri:hover:not(:disabled){filter:brightness(1.08)}
.mode:hover,.unit:hover,.lnk:hover,.choice:hover:not(:disabled){border-color:var(--accent)}
.tabs button:hover{color:var(--ink)}
.pane{scrollbar-width:thin;scrollbar-color:var(--line) transparent}
/* selection card on the stage */
.selcard{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;align-items:center;gap:4px;background:rgba(14,20,23,.9);color:var(--stage-ink);
  border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:5px 5px 5px 12px;box-shadow:0 8px 28px rgba(0,0,0,.4);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);max-width:calc(100% - 24px)}
.selcard .nm{font:600 13.5px var(--f-body);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:34ch}
.selcard .kd{font:500 10.5px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--stage-muted);margin-right:6px;white-space:nowrap}
.selcard button{background:transparent;border:0;color:var(--stage-ink);border-radius:8px;padding:6px 8px;cursor:pointer;font:500 12px var(--f-body);display:inline-flex;gap:5px;align-items:center}
.selcard button:hover{background:rgba(255,255,255,.1)}
.selcard svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
@media (max-width:860px){.selcard{bottom:44px}.selcard .bt{display:none}}
.orient{bottom:14px}
.app.hassel .orient{display:none}
/* dialogs */
.scrim{position:fixed;inset:0;background:rgba(6,10,12,.55);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);z-index:50;display:flex;align-items:flex-start;justify-content:center;padding:10vh 16px 16px}
.palette,.dlg{width:min(560px,100%);background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.45);overflow:hidden}
.palette input{width:100%;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--ink);font:16px var(--f-body);padding:15px 18px;outline:none}
.palette ul{list-style:none;margin:0;padding:6px;max-height:52vh;overflow:auto}
.palette li{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer}
.palette li[aria-selected="true"]{background:var(--soft);box-shadow:inset 3px 0 0 var(--accent)}
.palette li small{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap}
.palette .foot{display:flex;gap:14px;padding:8px 14px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
.dlg{padding:20px 22px}
.dlg h2{font:700 1.4rem var(--f-display);margin:0 0 4px}
.dlg .grid{display:grid;grid-template-columns:auto 1fr;gap:7px 14px;margin:14px 0;font-size:14px;align-items:baseline}
.dlg .grid kbd{justify-self:start}
.dlg .steps{display:grid;gap:10px;margin:14px 0}
.dlg .steps div{display:grid;grid-template-columns:28px 1fr;gap:10px;font-size:14px}
.dlg .steps b{width:24px;height:24px;border-radius:50%;background:var(--accent);color:var(--accent-ink);display:grid;place-items:center;font:600 12px var(--f-mono)}
/* about text */
.about{margin-top:16px;border-top:1px solid var(--line);padding-top:12px;font-size:14px}
.about p{margin:6px 0}
.about details{margin-top:6px}.about summary{cursor:pointer;color:var(--accent);font-weight:600;font-size:13px}
.about h4{font:500 11px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:12px 0 2px}
.about .src{font-size:11.5px;color:var(--muted);margin-top:8px}
.loading .pct{font:500 12px var(--f-mono);color:var(--stage-muted)}
.loading .tipline{font-size:12.5px;color:var(--stage-muted);max-width:46ch;min-height:2.6em}
.fatal{position:absolute;inset:0;z-index:20;display:flex;flex-direction:column;gap:10px;align-items:center;justify-content:center;text-align:center;padding:24px;color:var(--stage-ink);background:rgba(8,12,14,.92)}
.fatal h2{font:700 1.4rem var(--f-display);margin:0}
.fatal p{margin:0;color:var(--stage-muted);max-width:46ch;font-size:14px}
"""
rep("</style>\n\n<div class=\"app\">", CSS + "</style>\n\n<div class=\"app\">")

# ---------- toolbar ----------
I = {
 'search': '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg>',
 'labels': '<svg viewBox="0 0 24 24"><path d="M4 5h11l5 7-5 7H4z"/><circle cx="8.5" cy="12" r="1.2"/></svg>',
 'nerve': '<svg viewBox="0 0 24 24"><path d="M12 3v6M12 9c-3 2-6 5-7 11M12 9c3 2 6 5 7 11M12 9v12"/></svg>',
 'vessel': '<svg viewBox="0 0 24 24"><path d="M7 3c0 6 4 6 4 12s-4 6-4 6M17 3c0 6-4 6-4 12"/></svg>',
 'lig': '<svg viewBox="0 0 24 24"><circle cx="7" cy="7" r="3"/><circle cx="17" cy="17" r="3"/><path d="M9 9l6 6M10 6l8 8"/></svg>',
 'cad': '<svg viewBox="0 0 24 24"><path d="M5 20c1-4 3-6 7-6s6 2 7 6"/><circle cx="12" cy="8" r="4"/></svg>',
 'hd': '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9v6M7 12h3M10 9v6M14 9v6h2a3 3 0 000-6z"/></svg>',
 'explode': '<svg viewBox="0 0 24 24"><path d="M12 3v5M12 16v5M3 12h5M16 12h5M5.6 5.6l3.5 3.5M14.9 14.9l3.5 3.5M5.6 18.4l3.5-3.5M14.9 9.1l3.5-3.5"/></svg>',
 'reset': '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 108-8 8 8 0 00-6 2.7"/><path d="M4 4v4h4"/></svg>',
 'layers': '<svg viewBox="0 0 24 24"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
 'help': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-1 .6-1.5 1.2-1.5 2.5M12 17h.01"/></svg>',
}
old_hud = s[s.index('    <div class="hud" id="hud">'):s.index('    <div class="drawer" id="drawer" hidden>')]
new_hud = f'''    <div class="hud" id="hud" role="toolbar" aria-label="Model controls">
      <button class="pill" id="bSearch" title="Find any structure (Ctrl K or /)">{I['search']}<span class="t">Find</span> <kbd class="t">/</kbd></button>
      <div class="seg" role="group" aria-label="Camera view">
        <button data-v="front" title="Anterior view (1)">Ant</button><button data-v="back" title="Posterior view (2)">Post</button><button data-v="right" title="Right lateral view (3)">R lat</button><button data-v="left" title="Left lateral view (4)">L lat</button><button data-v="top" title="Superior view (5)">Sup</button>
      </div>
      <span class="sep"></span>
      <div class="grp" role="group" aria-label="Show">
        <button class="pill" id="bLabels" aria-pressed="true" title="Labels (L)">{I['labels']}<span class="t">Labels</span></button>
        <button class="pill" id="bNerves" aria-pressed="false" title="Nerves (N)">{I['nerve']}<span class="t">Nerves</span></button>
        <button class="pill" id="bVessels" aria-pressed="false" title="Arteries and veins (V)">{I['vessel']}<span class="t">Vessels</span></button>
        <button class="pill" id="bLig" aria-pressed="false" title="Skeleton with ligaments, capsules and menisci — muscles hidden (G)">{I['lig']}<span class="t">Ligaments</span></button>
      </div>
      <span class="sep"></span>
      <button class="pill" id="bLook" aria-pressed="false" title="Preserved-cadaver tissue colouring (C)">{I['cad']}<span class="t">Cadaver</span></button>
      <label class="pill exp" title="Pull the muscles apart in layers; bones, nerves and vessels stay in place (E toggles)">{I['explode']}<span class="t">Explode</span> <input type="range" id="explode" min="0" max="1" step="0.01" value="0" aria-label="Explode muscles"><output id="expOut">0%</output></label>
      <span class="spacer"></span>
      <button class="pill" id="bHD" aria-pressed="false" title="High-detail meshes and sharper rendering (about 52 MB)">HD</button>
      <button class="pill" id="bLayers" aria-expanded="false" title="Layers, region, side, quality">{I['layers']}<span class="t">Layers</span></button>
      <button class="pill" id="bReset" title="Put everything back to the default view (R)">{I['reset']}<span class="t">Reset</span></button>
      <button class="pill" id="bHelp" title="Shortcuts and help (?)" aria-label="Help">{I['help']}</button>
    </div>
'''
s = s.replace(old_hud, new_hud)
rep('''      <div><h3>Specimen</h3><div class="row"><button class="pill" id="bRestore">Restore dissected</button></div></div>''',
    '''      <div><h3>Specimen</h3><div class="row"><button class="pill" id="bRestore">Restore dissected</button></div></div>
      <div><h3>Graphics quality</h3><div class="row" id="qRow"></div><div class="hint" id="qNote" style="color:var(--stage-muted);margin-top:6px"></div></div>''')
rep('''      <h2>Preparing the specimen</h2>
      <div class="bar"><i id="loadBar"></i></div>
      <p id="loadTxt">Downloading 3D anatomy (about 11 MB)…</p>''',
    '''      <h2>Preparing the specimen</h2>
      <div class="bar"><i id="loadBar"></i></div>
      <p id="loadTxt">Downloading 3D anatomy (about 15 MB)…</p><span class="pct" id="loadPct"></span>
      <p class="tipline" id="loadTip">Tip: press / to find any muscle, nerve or vessel by name.</p>''')
rep('''    <div class="orient" id="orient">Loading…</div>''', '''    <div class="orient" id="orient">Loading…</div>
    <div class="selcard" id="selcard" hidden></div>''')

# ---------- data loading: cached, retried, fast base64 ----------
rep('''const loadBar=$('#loadBar'),loadTxt=$('#loadTxt');
async function getBin(){
  const res=await fetch('anatomy.txt');if(!res.ok)throw new Error('mesh');const total=15496316;let got=0;const chunks=[];
  const rd=res.body.getReader();
  for(;;){const {done,value}=await rd.read();if(done)break;chunks.push(value);got+=value.length;loadBar.style.width=Math.min(94,got/total*94)+'%'}
  let txt=new Uint8Array(got),o=0;for(const c of chunks){txt.set(c,o);o+=c.length}
  loadTxt.textContent='Decoding meshes…';await new Promise(r=>setTimeout(r,16));
  const bin=atob(new TextDecoder().decode(txt).trim());let buf=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)buf[i]=bin.charCodeAt(i);''',
'''const loadBar=$('#loadBar'),loadTxt=$('#loadTxt');
/* downloads: kept in the browser cache after the first visit (versioned), retried on flaky connections */
const DATA_V='z25';const CACHE='kl-data-'+DATA_V;
try{if(window.caches)caches.keys().then(ks=>ks.filter(k=>k.startsWith('kl-data-')&&k!==CACHE).forEach(k=>caches.delete(k)))}catch(e){}
async function fetchData(url,onBytes){
  let cache=null;try{if(window.caches)cache=await caches.open(CACHE)}catch(e){}
  if(cache){try{const hit=await cache.match(url);if(hit){const b=new Uint8Array(await hit.arrayBuffer());if(onBytes)onBytes(b.length,true);return b}}catch(e){}}
  let err;for(let a=0;a<3;a++){
    try{const res=await fetch(url,{cache:'no-cache'});if(!res.ok)throw new Error(url+' '+res.status);
      const rd=res.body.getReader();const ch=[];let got=0;for(;;){const {done,value}=await rd.read();if(done)break;ch.push(value);got+=value.length;if(onBytes)onBytes(got,false)}
      const b=new Uint8Array(got);let o=0;for(const c of ch){b.set(c,o);o+=c.length}
      if(cache){try{await cache.put(url,new Response(b.slice()))}catch(e){}}
      return b}catch(e){err=e;await new Promise(r=>setTimeout(r,600*(a+1)))}}
  throw err}
async function fetchJSON(url){return JSON.parse(new TextDecoder().decode(await fetchData(url)))}
async function b64(bytes){
  try{const r=await fetch('data:application/octet-stream;base64,'+new TextDecoder().decode(bytes).trim());return new Uint8Array(await r.arrayBuffer())}
  catch(e){const bin=atob(new TextDecoder().decode(bytes).trim());const u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return u}}
const TIPS=['Tip: press / to find any muscle, nerve or vessel by name.','Tip: number keys 1–5 jump to anterior, posterior, lateral and superior views.','Tip: the Study tab schedules a daily review of what you have learned.','Tip: Cadaver lab runs timed bellringer cases like your lab practical.','Tip: press ? at any time for every shortcut.'];
let tipI=0;const tipT=setInterval(()=>{const t=$('#loadTip');if(t)t.textContent=TIPS[++tipI%TIPS.length]},3500);
async function getBin(){
  const total=15496316;
  const txt=await fetchData('anatomy.txt',(got,cached)=>{loadBar.style.width=Math.min(94,got/total*94)+'%';$('#loadPct').textContent=cached?'from this device':Math.round(got/1e6)+' / '+Math.round(total/1e6)+' MB'});
  loadTxt.textContent='Decoding meshes…';await new Promise(r=>setTimeout(r,16));
  let buf=await b64(txt);''')
rep("try{[META,NERV,VESS,C,BUF]=await Promise.all([fetch('manifest.json').then(r=>r.json()),fetch('nerves.json').then(r=>r.json()),fetch('vessels.json').then(r=>r.json()),fetch('content.json').then(r=>r.json()),getBin()])}\ncatch(e){loadTxt.textContent='The anatomy data could not be downloaded. Reload the page to try again.';return}",
    "try{[META,NERV,VESS,C,BUF]=await Promise.all([fetchJSON('manifest.json'),fetchJSON('nerves.json'),fetchJSON('vessels.json'),fetchJSON('content.json'),getBin()])}\ncatch(e){clearInterval(tipT);loadTxt.textContent='The anatomy data could not be downloaded. Check your connection, then reload the page.';$('#loadPct').textContent=String(e&&e.message||'');return}")
# HD through the same cache
rep('''    const meta=await fetch('hd.json').then(r=>r.json());let got=0;const strs=[];
    for(const p of meta.parts){const r=await fetch(p);if(!r.ok)throw new Error('hd');const rd=r.body.getReader();const ch=[];
      for(;;){const {done,value}=await rd.read();if(done)break;ch.push(value);got+=value.length;b.textContent='HD '+Math.round(got/meta.bytes*90)+'%'}
      strs.push(ch.map(c=>new TextDecoder().decode(c)).join(''))}
    b.textContent='HD …';await new Promise(r=>setTimeout(r,20));
    const bin=atob(strs.join('').trim());let u8=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u8[i]=bin.charCodeAt(i);''',
'''    const meta=await fetchJSON('hd.json');let done0=0;const parts=[];
    for(const p of meta.parts){const part=await fetchData(p,got=>{b.textContent='HD '+Math.round((done0+got)/meta.bytes*90)+'%'});done0+=part.length;parts.push(part)}
    b.textContent='HD …';await new Promise(r=>setTimeout(r,20));
    const all=new Uint8Array(done0);{let o=0;for(const q of parts){all.set(q,o);o+=q.length}}
    let u8=await b64(all);''')

# ---------- renderer guard, context loss, global errors, quality modes ----------
rep("const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true});",
'''function fatal(title,msg){const d=document.createElement('div');d.className='fatal';d.innerHTML=`<h2>${esc(title)}</h2><p>${esc(msg)}</p><button class="btn pri" onclick="location.reload()">Reload</button>`;$('#stage').appendChild(d)}
let renderer;try{renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true,powerPreference:'high-performance'})}
catch(e){$('#loading').hidden=true;fatal('3D graphics are unavailable','This browser or device has WebGL turned off. Try Chrome, Edge, Safari or Firefox with hardware acceleration enabled.');return}
cv.addEventListener('webglcontextlost',e=>{e.preventDefault();fatal('The graphics card was reset','This happens when the device runs low on memory (often in HD mode). Reload to continue — your study progress is saved.')});
let errShown=0;const onErr=e=>{console.error(e);if(errShown++<1&&typeof toast==='function')toast('Something went wrong — press Reset if the model looks wrong','bad')};
window.addEventListener('error',e=>onErr(e.error||e.message));window.addEventListener('unhandledrejection',e=>onErr(e.reason));''')

# quality presets: high = full tissue shading; low = simple materials, no shadows, capped resolution
rep("setPose('stand');applyLook();resize();\nconst {c:bc,r:br}=bodyCenterWorld();",
'''/* ---------- graphics quality ---------- */
const QUAL={mode:new URLSearchParams(location.search).get('lite')?'low':LS.get('kl.quality','auto'),low:false};
function liteMat(m){const L=new THREE.MeshStandardMaterial({color:m.color.clone(),roughness:m.roughness,metalness:0,side:m.side,transparent:m.transparent,opacity:m.opacity,depthWrite:m.depthWrite});L.userData=m.userData;return L}
function setQuality(low){
  if(low===QUAL.low)return;QUAL.low=low;
  for(const st of ALL)for(const m of st.meshes){if(low){m.userData.hiMat=m.userData.hiMat||m.material;m.material=liteMat(m.userData.hiMat)}else if(m.userData.hiMat){m.material=m.userData.hiMat}}
  renderer.shadowMap.enabled=!low;Q.capPR=low?1:0;Q.cur=0;applyLook();renderQual()}
function renderQual(){const r=$('#qRow');if(!r)return;r.innerHTML=[['auto','Auto'],['high','High'],['low','Low (faster)']].map(([k,t])=>`<button class="pill" data-q="${k}" aria-pressed="${QUAL.mode===k}">${t}</button>`).join('');
  r.querySelectorAll('[data-q]').forEach(b=>b.onclick=()=>{QUAL.mode=b.dataset.q;LS.set('kl.quality',QUAL.mode);setQuality(QUAL.mode==='low');renderQual()});
  $('#qNote').textContent=QUAL.low?'Low: simple shading, no shadows — smoother on laptops and phones.':'High: full tissue shading and shadows.'+(QUAL.mode==='auto'?' Auto switches to Low if movement gets slow.':'')}
setPose('stand');applyLook();resize();
if(QUAL.mode==='low')setQuality(true);renderQual();
/* auto: if the first few seconds of movement run below ~24 fps, switch to low quality once */
setInterval(()=>{if(QUAL.mode!=='auto'||QUAL.low||!Q.moving)return;if(Q.ema>42&&Q.f<=.62){setQuality(true);toast('Switched to Low graphics for smoother movement — change it under Layers')}},1500);
const {c:bc,r:br}=bodyCenterWorld();''')
rep("function fullPR(){const d=window.devicePixelRatio||1;return Q.hd?","function fullPR(){const d=window.devicePixelRatio||1;if(Q.capPR)return Math.min(d,Q.capPR);return Q.hd?")
rep("requestAnimationFrame(loop);\n$('#loading').hidden=true;","requestAnimationFrame(loop);\nclearInterval(tipT);$('#loading').hidden=true;")
open(p, 'w').write(s); print('pro1 ok')
