p='site/index.html';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
rep('      <button class="pill" id="bVessels" aria-pressed="false">Vessels</button>',
    '      <button class="pill" id="bVessels" aria-pressed="false">Vessels</button>\n      <button class="pill" id="bLig" aria-pressed="false" title="Show the skeleton with its ligaments, capsules and menisci (muscles hidden)">Ligaments</button>')
rep("$('#bVessels').onclick=","function ligView(on,reg){ST.ly.ligament=true;ST.ly.bone=true;ST.ly.muscle=!on;ST.ly.tendon=!on;if(on){ST.xray=false;ST.opacity=1}if(reg){ST.region=reg;isolate=null}syncDrawer();applyVis();if(reg)view(lastViewName())}\n$('#bLig').onclick=()=>{ligView(!(!ST.ly.muscle&&ST.ly.ligament))};\n$('#bVessels').onclick=")
rep("$('#bNerves').setAttribute('aria-pressed',ST.ly.nerve);","$('#bNerves').setAttribute('aria-pressed',ST.ly.nerve);$('#bLig').setAttribute('aria-pressed',!ST.ly.muscle&&!!ST.ly.ligament);")
rep("""    <button class="unit" data-jn="1"><strong>Nerves</strong><span>Plexuses &amp; peripheral nerves</span></button></div>""",
    """    <button class="unit" data-jn="1"><strong>Nerves</strong><span>Plexuses &amp; peripheral nerves</span></button>
    <button class="unit" data-jl="lower"><strong>Leg ligaments</strong><span>Hip, knee, ankle &amp; foot</span></button>
    <button class="unit" data-jl="upper"><strong>Arm ligaments</strong><span>Shoulder, elbow, wrist &amp; hand</span></button></div>""")
rep("    pane.querySelector('[data-jn]').onclick=","    pane.querySelectorAll('[data-jl]').forEach(b=>b.onclick=()=>ligView(true,b.dataset.jl));\n    pane.querySelector('[data-jn]').onclick=")
open(p,'w').write(s);print('ok')
