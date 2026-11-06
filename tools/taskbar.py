import re
p='site/index.html';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:80],s.count(a)); s=s.replace(a,b)
i=s.index('    <div class="hud" id="hud" role="toolbar" aria-label="Model controls">'); j=s.index('    <div class="orient" id="orient">')
old=s[i:j]
def grab(pat):
    m=re.search(pat,old,re.S); assert m,pat; return m.group(0)
bSearch=grab(r'<button class="pill" id="bSearch".*?</button>')
seg=grab(r'<div class="seg".*?</div>')
show=[grab(r'<button class="pill" id="%s".*?</button>'%x) for x in ('bLabels','bNerves','bVessels','bLig')]
bLook=grab(r'<button class="pill" id="bLook".*?</button>'); expl=grab(r'<label class="pill exp".*?</label>')
bHD=grab(r'<button class="pill" id="bHD".*?</button>'); bReset=grab(r'<button class="pill" id="bReset".*?</button>'); bHelp=grab(r'<button class="pill" id="bHelp".*?</button>')
layers=grab(r'<div><h3>Show</h3>.*?</div></div>'); opac=grab(r'<div><h3>Muscle opacity</h3>.*?</div>')
reg=grab(r'<div><h3>Region</h3>.*?</div></div>'); side=grab(r'<div><h3>Side</h3>.*?</div></div>'); spec=grab(r'<div><h3>Specimen</h3>.*?</div></div>')
qual=grab(r'<div><h3>Graphics quality</h3>.*?id="qNote"[^>]*></div></div>')
CHEV='<svg class="chev" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>'
ICON_L='<svg viewBox="0 0 24 24"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>'
ICON_R='<svg viewBox="0 0 24 24"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0112 2.5a7 7 0 017 7c0 5.3-7 11.5-7 11.5z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
ICON_S='<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/></svg>'
def pop(id,title,body): return f'''    <div class="pop" id="{id}" role="dialog" aria-label="{title}" hidden><div class="pophd"><h3>{title}</h3><button class="popx" data-close aria-label="Close {title}"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>
{body}
    </div>
'''
new=f'''    <div class="taskbar hud" id="hud" role="toolbar" aria-label="Model controls">
      <div class="tg" role="group" aria-label="Find"><span class="cap">Find</span><div class="tr">{bSearch}</div></div>
      <div class="tg" role="group" aria-label="Camera view"><span class="cap">View</span><div class="tr">{seg}</div></div>
      <div class="tg" role="group" aria-label="Show"><span class="cap">Show</span><div class="tr">{''.join(show)}<button class="pill more" id="bLayers" data-pop="popLayers" aria-expanded="false" aria-haspopup="dialog" title="All layers, see-through and muscle opacity">{ICON_L}<span class="t2">Layers</span>{CHEV}</button></div></div>
      <div class="tg" role="group" aria-label="Model"><span class="cap">Model</span><div class="tr">{bLook}{expl}<button class="pill more" id="bRegion" data-pop="popRegion" aria-expanded="false" aria-haspopup="dialog" title="Region, side and dissected structures">{ICON_R}<span class="t2">Region</span>{CHEV}</button></div></div>
      <span class="spacer"></span>
      <div class="tg" role="group" aria-label="App"><span class="cap">App</span><div class="tr">{bHD}<button class="pill more" id="bSettings" data-pop="popSettings" aria-expanded="false" aria-haspopup="dialog" title="Graphics quality and controls">{ICON_S}{CHEV}</button>{bReset}{bHelp}</div></div>
    </div>
{pop('popLayers','Layers',layers+chr(10)+'      '+opac)}{pop('popRegion','Region &amp; specimen',reg+chr(10)+'      '+side+chr(10)+'      '+spec)}{pop('popSettings','Settings',qual+chr(10)+'      <div class="hint" style="color:var(--stage-muted)">Drag to rotate · right-drag or two fingers to pan · scroll or pinch to zoom · click a structure to select. Press ? for every shortcut.</div>')}'''
s=s[:i]+new+s[j:]
CSS=r'''
/* ---- taskbar ---- */
.taskbar{position:absolute;left:0;right:0;top:0;z-index:4;display:flex;align-items:stretch;gap:6px;flex-wrap:wrap;padding:7px 10px 8px;
  background:linear-gradient(180deg,rgba(9,14,17,.92),rgba(9,14,17,.78));border-bottom:1px solid rgba(255,255,255,.08);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);pointer-events:auto}
.taskbar .tg{display:flex;flex-direction:column;gap:3px;padding:3px 7px 4px;border-radius:10px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.05)}
.taskbar .cap{font:500 9.5px var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--stage-muted);padding-left:2px;line-height:1.2}
.taskbar .tr{display:flex;align-items:center;gap:3px}
.taskbar .pill{background:transparent;border-color:transparent;padding:5px 8px;backdrop-filter:none;-webkit-backdrop-filter:none}
.taskbar .pill:hover:not(.exp){background:rgba(255,255,255,.09)}
.taskbar .pill[aria-pressed="true"],.taskbar .pill[aria-expanded="true"]{background:#E6EEF0;color:#0B1013}
.taskbar .seg{background:transparent;border-color:rgba(255,255,255,.1)}
.taskbar .pill.exp{padding:3px 6px}
.taskbar .spacer{flex:1}
.pill .chev{width:12px;height:12px;margin-left:-2px;opacity:.7;transition:transform .15s}
.pill[aria-expanded="true"] .chev{transform:rotate(180deg)}
.pop{position:absolute;z-index:7;width:min(300px,calc(100% - 20px));max-height:calc(100% - 90px);overflow:auto;background:rgba(14,20,23,.97);color:var(--stage-ink);
  border:1px solid rgba(255,255,255,.14);border-radius:12px;padding:12px 14px 14px;display:flex;flex-direction:column;gap:12px;font-size:13px;box-shadow:0 18px 50px rgba(0,0,0,.5)}
.pop .pophd{display:flex;align-items:center;justify-content:space-between;margin:-2px -4px 0 0}
.pop h3{margin:0;font:500 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--stage-muted)}
.pop .pophd h3{color:var(--stage-ink);font-size:11.5px}
.pop label{display:flex;align-items:center;gap:8px;cursor:pointer}
.pop .row{display:flex;flex-wrap:wrap;gap:6px}
.pop input[type=range]{width:100%;accent-color:#E6EEF0}
.popx{background:transparent;border:0;color:var(--stage-ink);width:30px;height:30px;border-radius:8px;display:grid;place-items:center;cursor:pointer}
.popx:hover{background:rgba(255,255,255,.1)}
.popx svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round}
.labels{top:64px}
@media (max-width:1460px){.taskbar .cap{font-size:9px}}
@media (max-width:860px){.taskbar{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding:6px 8px}.taskbar::-webkit-scrollbar{display:none}.taskbar>*{flex:none}.taskbar .cap{display:none}.taskbar .tg{padding:2px 4px}.labels{top:52px}}
'''
rep("/* ---- AI ---- */",CSS+"\n/* ---- AI ---- */")
rep("const drawer=$('#drawer');\n$('#bLayers').onclick=()=>{drawer.hidden=!drawer.hidden;$('#bLayers').setAttribute('aria-expanded',!drawer.hidden)};",
r'''/* taskbar popovers: one open at a time; close with ×, Esc, a click outside, or the same button */
let openPop=null;
function closePop(){if(!openPop)return;openPop.el.hidden=true;openPop.btn.setAttribute('aria-expanded','false');openPop=null}
function togglePop(btn){const el=$('#'+btn.dataset.pop);if(openPop&&openPop.el===el){closePop();return}closePop();
  el.hidden=false;btn.setAttribute('aria-expanded','true');openPop={el,btn};
  const sr=stage.getBoundingClientRect(),br=btn.getBoundingClientRect(),tb=$('#hud').getBoundingClientRect();
  const w=el.offsetWidth;el.style.top=(tb.bottom-sr.top+6)+'px';el.style.left=Math.max(10,Math.min(sr.width-w-10,br.left-sr.left+br.width/2-w/2))+'px'}
document.querySelectorAll('[data-pop]').forEach(b=>b.onclick=e=>{e.stopPropagation();togglePop(b)});
document.querySelectorAll('.pop [data-close]').forEach(b=>b.onclick=()=>closePop());
document.addEventListener('pointerdown',e=>{if(openPop&&!openPop.el.contains(e.target)&&!openPop.btn.contains(e.target))closePop()},true);
addEventListener('keydown',e=>{if(e.key==='Escape'&&openPop){closePop();e.stopPropagation()}},true);
addEventListener('resize',()=>closePop());''')
open(p,'w').write(s);print('ok')
