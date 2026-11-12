import re
p='site/index.html';s=open(p).read()
i=s.index('    <div class="taskbar hud" id="hud"'); j=s.index('    <div class="orient" id="orient">')
old=s[i:j]
def g(pat):
    m=re.search(pat,old,re.S); assert m,pat; return m.group(0)
lys=re.findall(r'<label><input type="checkbox" id="ly\w+"[^>]*>.*?</label>',old)
assert len(lys)==7
lys=[x.replace('<label>','<label class="mi ck">') for x in lys]
CH='<svg class="chev" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>'
def item(id,text,key,extra=''):return f'<button class="mi tg" id="{id}" aria-pressed="false"{extra}><span>{text}</span><kbd>{key}</kbd></button>'
new=f'''    <div class="mbar hud" id="hud" role="toolbar" aria-label="Model controls">
      <button class="mb" id="bSearch" title="Find any structure (Ctrl K or /)"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg><span>Find</span></button>
      <button class="mb" id="bView" data-pop="popView" aria-expanded="false" aria-haspopup="menu"><span>View</span>{CH}</button>
      <button class="mb" id="bLayers" data-pop="popLayers" aria-expanded="false" aria-haspopup="menu"><span>Layers</span>{CH}</button>
    </div>
    <div class="pop menu" id="popView" role="menu" aria-label="View" hidden>
      <div class="mh">Camera</div>
      <button class="mi" data-v="front" data-shut><span>Anterior</span><kbd>1</kbd></button>
      <button class="mi" data-v="back" data-shut><span>Posterior</span><kbd>2</kbd></button>
      <button class="mi" data-v="right" data-shut><span>Right lateral</span><kbd>3</kbd></button>
      <button class="mi" data-v="left" data-shut><span>Left lateral</span><kbd>4</kbd></button>
      <button class="mi" data-v="top" data-shut><span>Superior</span><kbd>5</kbd></button>
      <hr>
      <div class="mh">Specimen</div>
      {item('bLook','Cadaver colouring','C')}
      <label class="mi sl"><span>Explode</span><input type="range" id="explode" min="0" max="1" step="0.01" value="0" aria-label="Explode muscles"><output id="expOut">0%</output></label>
      <div class="mh">Region</div><div class="chips" id="regRow"></div>
      <div class="mh">Side</div><div class="chips" id="sideRow"></div>
      <hr>
      <div class="mh">Display</div>
      <button class="mi tg" id="bHD" aria-pressed="false" title="High-detail meshes and sharper rendering (about 52 MB)">HD</button>
      <div class="chips" id="qRow"></div><div class="mnote" id="qNote"></div>
      <hr>
      <button class="mi" id="bReset" data-shut><span>Reset everything</span><kbd>R</kbd></button>
      <button class="mi" id="bHelp" data-shut><span>Shortcuts &amp; help</span><kbd>?</kbd></button>
    </div>
    <div class="pop menu" id="popLayers" role="menu" aria-label="Layers" hidden>
      <div class="mh">Overlays</div>
      {item('bLabels','Labels','L').replace('aria-pressed="false"','aria-pressed="true"')}
      {item('bNerves','Nerves','N')}
      {item('bVessels','Arteries &amp; veins','V')}
      {item('bLig','Ligaments only','G')}
      <hr>
      <div class="mh">Tissues</div>
      {chr(10).join('      '+x for x in lys[:6]).lstrip()}
      {lys[6].replace(' Nerves &amp; vessels visible through tissue','<span>See nerves &amp; vessels through tissue</span>')}
      <label class="mi sl"><span>Muscle opacity</span><input type="range" id="opac" min="0.08" max="1" step="0.01" value="1" aria-label="Muscle opacity"></label>
      <hr>
      <button class="mi" id="bRestore" data-shut>Restore dissected</button>
    </div>
'''
s=s[:i]+new+s[j:]
CSS=r'''
/* ---- macOS-style menu bar ---- */
.mbar.hud{position:absolute;left:50%;right:auto;top:12px;transform:translateX(-50%);z-index:4;display:flex;flex-wrap:nowrap;align-items:center;gap:2px;padding:4px;
  background:rgba(32,34,38,.62);border:.5px solid rgba(255,255,255,.14);border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.35),inset 0 .5px 0 rgba(255,255,255,.08);
  backdrop-filter:blur(24px) saturate(180%);-webkit-backdrop-filter:blur(24px) saturate(180%);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter",system-ui,sans-serif;overflow:visible}
.mb{display:flex;align-items:center;gap:6px;background:transparent;border:0;color:#F2F4F5;font:500 13px/1 inherit;font-family:inherit;padding:8px 13px;border-radius:10px;cursor:pointer;transition:background .12s}
.mb svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.mb .chev{width:11px;height:11px;opacity:.6;stroke-width:2.4;transition:transform .18s}
.mb:hover{background:rgba(255,255,255,.1)}.mb[aria-expanded="true"]{background:rgba(255,255,255,.18)}
.mb[aria-expanded="true"] .chev{transform:rotate(180deg)}
.mb:focus-visible,.mi:focus-visible{outline:2px solid #0A84FF;outline-offset:1px}
.pop.menu{position:absolute;z-index:30;width:252px;max-height:calc(100% - 80px);overflow:auto;padding:5px;gap:0;display:block;
  background:rgba(38,40,44,.78);border:.5px solid rgba(255,255,255,.16);border-radius:12px;color:#F2F4F5;
  box-shadow:0 22px 60px rgba(0,0,0,.5),0 0 0 .5px rgba(0,0,0,.6);backdrop-filter:blur(30px) saturate(190%);-webkit-backdrop-filter:blur(30px) saturate(190%);
  font:13px/1.2 -apple-system,BlinkMacSystemFont,"SF Pro Text","Inter",system-ui,sans-serif;transform-origin:top center;animation:menuIn .14s ease-out;scrollbar-width:thin}
@keyframes menuIn{from{opacity:0;transform:scale(.97) translateY(-4px)}to{opacity:1;transform:none}}
.menu .mh{font-size:11px;font-weight:600;color:rgba(235,238,240,.45);padding:7px 10px 3px 26px}
.menu hr{border:0;height:.5px;background:rgba(255,255,255,.14);margin:5px 10px}
.menu .mi{position:relative;display:flex;align-items:center;gap:8px;width:100%;min-height:26px;padding:4px 10px 4px 26px;border:0;border-radius:6px;background:transparent;color:inherit;
  font:inherit;text-align:left;cursor:default}
.menu .mi>span{flex:1}
.menu .mi kbd{font:inherit;color:rgba(235,238,240,.45);background:none;border:0;padding:0;min-width:0;box-shadow:none}
.menu button.mi:hover,.menu label.ck:hover{background:#0A84FF;color:#fff}
.menu button.mi:hover kbd{color:rgba(255,255,255,.75)}
.menu .tg[aria-pressed="true"]::before,.menu .ck:has(input:checked)::before{content:"";position:absolute;left:9px;top:50%;width:10px;height:10px;margin-top:-6px;
  background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M1.5 6.5l3 3 6-7' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;
  mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M1.5 6.5l3 3 6-7' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
.menu .ck input{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.menu .ck .sw{width:9px;height:9px;border-radius:50%;flex:none;box-shadow:0 0 0 .5px rgba(255,255,255,.3)}
.menu .ck:not(:has(.sw)) span{flex:1}
#bHD::after{content:"High-detail meshes · 52 MB";margin-left:auto;color:rgba(235,238,240,.45);font-size:12px}
#bHD:hover::after{color:rgba(255,255,255,.75)}
.menu .sl{cursor:default;gap:10px}.menu .sl>span{flex:none;min-width:58px}
.menu .sl input[type=range]{flex:1;min-width:0;accent-color:#0A84FF;height:16px}
.menu .sl output{font-size:11.5px;color:rgba(235,238,240,.55);min-width:30px;text-align:right;font-variant-numeric:tabular-nums}
.menu .chips{display:flex;flex-wrap:wrap;gap:4px;padding:2px 8px 4px 24px}
.menu .chips .pill{font:500 12px inherit;font-family:inherit;padding:4px 9px;border-radius:7px;background:rgba(255,255,255,.07);border:.5px solid rgba(255,255,255,.1);color:inherit;backdrop-filter:none}
.menu .chips .pill:hover{background:rgba(255,255,255,.14)}
.menu .chips .pill[aria-pressed="true"]{background:#0A84FF;border-color:#0A84FF;color:#fff}
.menu .mnote{font-size:11.5px;color:rgba(235,238,240,.45);padding:0 10px 4px 26px}
.menu .mnote:empty{display:none}
@media (max-width:860px){.mbar.hud{top:8px;overflow:visible;padding:3px}.mb{padding:8px 12px;font-size:14px}.pop.menu{width:min(280px,calc(100% - 16px))}.menu .mi{min-height:34px}}
'''
s=s.replace("\n/* ---- AI ---- */",CSS+"\n/* ---- AI ---- */",1)
# close menu after one-shot actions
a="document.querySelectorAll('.pop [data-close]').forEach(b=>b.onclick=()=>closePop());"
assert a in s
s=s.replace(a,a+"\ndocument.querySelectorAll('.pop [data-shut]').forEach(b=>b.addEventListener('click',()=>setTimeout(closePop,0)));")
open(p,'w').write(s);print('ok')
