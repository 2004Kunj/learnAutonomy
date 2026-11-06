const fs=require('fs'),path=require('path');const SITE=process.argv[2]||require('path').join(__dirname,'..','app');
const els={};
function mk(id){const e={id,hidden:false,style:{setProperty(){}},dataset:{},children:[],className:'',textContent:'',value:'',checked:false,disabled:false,_html:'',
  set innerHTML(v){this._html=v},get innerHTML(){return this._html},
  classList:{add(){},remove(){},toggle(){}},setAttribute(){},getAttribute(){return null},addEventListener(){},appendChild(c){this.children.push(c);return c},replaceChildren(...c){this.children=c},
  querySelector(s){return q(s)},querySelectorAll(){return []},focus(){},setSelectionRange(){},scrollIntoView(){},remove(){},
  getBoundingClientRect(){return {left:0,top:0,width:800,height:700}},getContext(){return {createRadialGradient(){return {addColorStop(){}}},fillRect(){},set fillStyle(v){}}},closest(){return null},clientWidth:800,clientHeight:700};return e}
function q(s){return els[s]||(els[s]=mk(s))}
global.window=global;global.addEventListener=()=>{};global.removeEventListener=()=>{};global.document={createDocumentFragment:()=>mk('frag'),addEventListener(){},querySelector:q,querySelectorAll:()=>[],createElement:()=>mk('x'),head:mk('head'),body:mk('body')};
global.claude={use:async n=>{if(n!=='sample')return null;
 const f=async(input,o={})=>{global.__lastInput=input;let t='**Deltoid** — the shoulder abductor.\n- find it on the cadaver\n- axillary nerve';
   if(o.tools){const r=await o.tools[0].execute({names:['Deltoid','Median nerve','Not a thing'],mode:'isolate'},{signal:null});global.__toolRes=r;t+='\nshown: '+r.shown.join(', ')}
   if(o.onText)o.onText({text:t,delta:t});return {text:t,truncated:false}};
 f.limits=async()=>({maxPromptBytes:262144,images:{maxCount:3},tools:{maxCount:5}});
 f.json=async(p,o={})=>{global.__prompt=p;global.__imgs=o.images;
   if(/bellringer/.test(p)){const keys=[...p.matchAll(/^([a-z0-9-]+): /gm)].map(m=>m[1]).slice(0,5);return keys.map(k=>({key:k,case:'A patient case pointing to '+k,hint:'region',why:'because'})).concat([{key:'nope',case:'x'}])}
   if(/lecture/.test(p))return {structures:['Teres major','Axillary nerve','Posterior circumflex humeral artery','Long head of triceps'],view:'posterior'};
   return {}};
 return f}};
global.Tesseract={createWorker:async(l,o,opt)=>{global.__opt=opt;return {recognize:async b=>({data:{text:'Posterior view\nTeres major\nQuadrangular space\nAxillary n.\nPost. circumflex humeral a.\nLong head of triceps'}})}}};global.location={href:'https://example.test/artifact/index.html'};global.URL.createObjectURL=()=>'blob:x';
global.localStorage={getItem:()=>null,setItem(){}};global.devicePixelRatio=1;global.ResizeObserver=class{observe(){}};
global.requestAnimationFrame=()=>0;global.__noop=1;global.performance=require('perf_hooks').performance;
global.fetch=async(u)=>{const p=path.join(SITE,u);const b=fs.readFileSync(p);
  return {ok:true,json:async()=>JSON.parse(b),text:async()=>b.toString(),body:{getReader(){let d=false;return {read:async()=>d?{done:true}:(d=true,{done:false,value:new Uint8Array(b)})}}}}};
global.Response=Response;global.Blob=Blob;global.DecompressionStream=DecompressionStream;
global.THREE=require(path.resolve(SITE,'lib/three.min.js'));
eval(fs.readFileSync(path.join(SITE,'lib/OrbitControls.js'),'utf8'));
THREE.WebGLRenderer=class{constructor(){this.domElement=mk("cv");this.shadowMap={};this.info={programs:[]}}setPixelRatio(){}setSize(){}render(){}setClearColor(){}setRenderTarget(){}clear(){}readRenderTargetPixels(rt,x,y,w,h,px){for(let i=0;i<px.length;i+=4){px[i+2]=(i/4)%60+1}}};
THREE.PMREMGenerator=class{fromScene(){return {texture:null}}};THREE.RoomEnvironment=class{};
const html=fs.readFileSync(path.join(SITE,'index.html'),'utf8');const js=html.match(/<script>([\s\S]*?)<\/script>/g).pop().replace(/<\/?script>/g,'').replace("clearInterval(tipT);$('#loading').hidden=true;","clearInterval(tipT);$('#loading').hidden=true;window.__t={resetModel,normText,LECr:()=>LEC,loadHD,REAL,HD,lab,select,setTab,view,bellNext,bellTap,bellReveal,pinStart,pinGrade,lab,ST,S,renderPane,expose,drawLabels,pickAt,setPose,applyLook,camera,controls,setExplode,analyze,applyAnalysis,LEC,sampleDeck,enterLecture,showSlide,byK,isolateRef:()=>isolate,QZ,DIS,TOUR,startQuiz,mcq,quizTap,startDis,startTour,tourGo,renderStudy,SRS,STATS,nextQ,finishQuiz,computeLayers,mkQ,poolKeys,dueKeys,newKeys,deckKeys,randQ,SCFG,loop,Q,openPalette,closePalette,palItems,showHelp,renderSelcard,selAction,setQuality,QUAL,OUTL,deselect,loadDefs,renderTourPick,mkQ2:(k,t)=>mkQ(k,t),SCFGr:()=>SCFG,AI,aiOK,renderTutor,sendTutor,aiExplain,aiWhy,aiCases,aiReadSlide,resolveName,factsFor,md};");
(async()=>{
  const t0=Date.now();
  await eval(js);
  await new Promise(r=>setTimeout(r,200));
  const T=global.__t;if(!T){console.log('loading hidden:',q('#loading').hidden,'|',q('#loadTxt').textContent,'| pane',q('#pane').innerHTML.length);process.exit(0)}
  console.log('boot ms',Date.now()-t0,'structures',Object.keys(T.S).length);
  console.log('pane chars',q('#pane').innerHTML.length);
  T.camera.updateMatrixWorld();
  let p=T.pickAt(400,300);console.log('pick centre:',p&&p.st.id,p&&p.part);
  T.select('deltoid-R',{fly:true});console.log('explore deltoid ok',q('#pane').innerHTML.includes('Axillary'));
  T.select('median-R');console.log('nerve page', q('#pane').innerHTML.includes('Muscles it supplies'));
  T.select('humerus-L');console.log('bone page attaching', q('#pane').innerHTML.includes('Muscles attaching'));
  T.setTab('I');console.log('index ok',q('#pane').innerHTML.split('class="it"').length-1);
  let t1=Date.now();T.drawLabels();console.log('labels ms',Date.now()-t1,'count',q('#labels').children.length);
  T.setTab('L');T.lab.active=true;T.lab.mode='bell';T.setPose('table');T.applyLook();T.bellNext();console.log('bell case:',T.lab.cur.b[0].slice(0,60));
  const tg=T.lab.cur.b[1][0];T.bellTap({st:T.S['femur-R'],part:''});console.log('wrong tap wrong count',T.lab.cur.wrong);
  T.bellTap({st:T.S[tg],part:''});console.log('correct ->done',T.lab.cur.done,'score',T.lab.score);
  T.bellNext();t1=Date.now();T.bellReveal();await new Promise(r=>setTimeout(r,900));console.log('reveal ok, hidden',T.ST.hidden.size,'ms',Date.now()-t1);
  T.lab.mode='pin';t1=Date.now();T.pinStart();console.log('pin station',T.lab.cur.st.id,'choices',T.lab.cur.choices.map(s=>s.k).join(','),'hidden',T.ST.hidden.size,'ms',Date.now()-t1);
  T.lab.cur.ans=T.lab.cur.st.k;T.pinGrade();console.log('pin graded score',T.lab.score);
  T.select('supraspinatus-R',{reveal:true});t1=Date.now();const n=T.expose(T.S['supraspinatus-R']);console.log('expose removed',n,'ms',Date.now()-t1);
  // --- new features ---
  T.setExplode(1);console.log('explode deltoid offset', T.S['deltoid-R'].meshes[0].position.toArray().map(x=>x|0));
  T.select('femoral-a-R');console.log('vessel page',q('#pane').innerHTML.includes('Supplies'));
  T.ST.look='cadaver';T.applyLook();console.log('cadaver uCad',T.S['deltoid-R'].meshes[0].material.userData.u.uCad.value);
  T.setExplode(0);
  for(const txt of ['The foot: plantar muscles in four layers abductor hallucis flexor digitorum brevis','Rotator cuff (SITS)','Brachial plexus — terminal branches musculocutaneous axillary radial median ulnar nerves','Knee joint femur tibia patella','Posterior compartment of the thigh hamstrings sciatic nerve','Action potentials resting membrane potential','Muscles of the leg','The femoral triangle','Bones of the hand: scaphoid lunate']){
    const an=T.analyze(txt);const ok=T.applyAnalysis(an,false);const iso=T.isolateRef();
    console.log(JSON.stringify(txt.slice(0,40)),'->',ok,[...an.keys].slice(0,8).join(','),'| regions',[...an.regions].join(','),'| shown',iso?iso.size:'region:'+T.ST.cregions.join('/'));
  }
  T.LEC.deck=T.sampleDeck();T.setTab('C');T.enterLecture();await T.showSlide(0);console.log('lecture pane has slide', q('#pane').innerHTML.includes('slideBox'));
  T.lab.active=true;T.lab.mode='pin';T.pinStart();console.log('pin tip',!!T.lab.pinTip,'aux attr',!!T.S['deltoid-R'].meshes[0].geometry.attributes.aux,'clearcoat',T.S['deltoid-R'].meshes[0].material.clearcoat);
  //hd skipped
  if(0)await T.loadHD();console.log('HD loaded',T.HD.loaded,'tris',T.REAL.reduce((a,m)=>a+m.geometry.index.count/3,0),'ms',Date.now()-t1);

  console.log('NORM:',T.normText('Great (long) saphenous v., small saphenous v.'));
  console.log('NORM2:',T.normText('pec major, tib ant and glute med'));
  { const txt=require('fs').readFileSync(process.env.SLIDE||require('path').join(__dirname,'slide9.txt'),'utf8');const an=T.analyze(txt);T.applyAnalysis(an,false);
    console.log('\n=== SLIDE 9 CHECKLIST');for(const it of an.items)console.log(' ',{ok:'✓',parent:'≈',missing:'✗'}[it.status],it.label,it.via?'-> '+it.via:'',it.seen===false?'(NOT VISIBLE)':'');
    const L=T.LECr();console.log('  shown ids:',[...L.ids].join(', '));console.log('  side',T.ST.side,'opacity',T.ST.opacity,'fixed',an.fixed); }
  const slides=[
   'Anterior Forearm — Superficial layer\nPronator teres, FCR, palmaris longus, FCU\nInnervation: median n. (except FCU – ulnar n.)',
   'Blood supply of the upper limb\nSubclavian a. → axillary a. → brachial a.\nRadial and ulnar arteries',
   'Median Nerve\nC6–T1, lateral and medial cords\nCarpal tunnel syndrome',
   'Muscles of the Gluteal Region\nGluteus maximus – inferior gluteal n.\nGluteus medius & minimus – superior gluteal n.',
   'Leg: Lateral compartment\nPeroneus longus & brevis\nSuperficial peroneal nerve',
   'Foot — neurovascular\nMedial & lateral plantar nerves (tibial n.)\nDorsalis pedis artery',
   'Venous drainage of the lower limb\nGreat (long) saphenous v., small saphenous v.\nFemoral vein, popliteal vein',
   'Rotator cuff muscles and their innervation',
   'Quadriceps femoris\nRF, VL, VMO, vastus intermedius\nFemoral nerve L2–L4',
   'Learning objectives\nDescribe the sliding filament theory'];
  for(const t of slides){const an=T.analyze(t);T.applyAnalysis(an,false);const L=T.LECr();const sh=(L.shown||[]);
    const by=k=>sh.filter(s=>k.includes(s.kind)).map(s=>s.name).join(', ');
    console.log('\n## '+t.split('\n')[0]+'\n  muscles: '+by(['muscle','tendon'])+'\n  nerves: '+by(['nerve'])+'\n  vessels: '+by(['artery','vein'])+'\n  regions: '+[...an.regions].join(',')+'  opacity '+T.ST.opacity+' xray '+T.ST.xray);}
  { const L=T.LECr(); L.deck={name:'test.pdf',n:1,texts:['Posterior shoulder'],render:async()=>{},imageBlob:async()=>new Blob(['x'],{type:'image/jpeg'})};
    T.setTab('C');await T.showSlide(0);await new Promise(r=>setTimeout(r,300));
    console.log('\n=== OCR MERGE', 'corePath',global.__opt&&global.__opt.corePath);for(const it of L.an.items)console.log(' ',{ok:'✓',parent:'≈',missing:'✗'}[it.status],it.label,it.src||'');
    console.log('  view',L.an.view,'ids',[...L.ids].join(','));}

  // ---- STUDY ----
  T.setTab('S');console.log('\n=== STUDY home', q('#pane').innerHTML.includes('Daily review'));
  let bad=0;for(const k of Object.keys(T.byK)){if(!T.poolKeys('all',null).includes(k))continue;for(const ty of ['find','name','nerve','action','origin','insertion','findclue','supplies','whichnerve','vsup']){
    let Q;try{Q=T.mkQ(k,ty,{side:'R'})}catch(e){console.log('mkQ ERR',k,ty,e.message);bad++;continue}
    if(!Q||!T.S[Q.id]){console.log('noid',k,ty);bad++;continue}if(Q.opts&&(Q.opts.filter(o=>o.ok).length!==1||new Set(Q.opts.map(o=>o.t)).size!==Q.opts.length)){bad++;if(bad<8)console.log('opts problem',k,ty,JSON.stringify(Q.opts))}}}
  console.log('mkQ problems',bad);
  for(const ty of ['nerve','action','origin','insertion','findclue']){const Q=T.mkQ('supraspinatus',ty);console.log(' ',ty,'|',Q.prompt,'|',Q.opts?Q.opts.map(o=>(o.ok?'*':'')+o.t.slice(0,40)).join(' / '):'click')}
  {const Q=T.mkQ('median','supplies');console.log('  supplies |',Q.prompt,Q.opts.map(o=>(o.ok?'*':'')+o.t).join(' / '))}
  {const Q=T.mkQ('femoral-a','vsup');console.log('  vsup |',Q.prompt,Q.opts.map(o=>(o.ok?'*':'')+o.t.slice(0,30)).join(' / '))}
  // review session
  const ks=T.newKeys(10,'all');console.log('new keys',ks.join(','));
  T.startQuiz('review',ks,{srs:true,title:'Daily review'});
  for(let i=0;i<40&&T.QZ.active&&!T.QZ.summary;i++){const Q=T.QZ.q;
    if(Q.click){ if(i%3===0)T.quizTap({st:T.S['femur-R'].id===Q.id?T.S['tibia-R']:T.S['femur-R'],part:''}); T.quizTap({st:T.S[Q.id],part:''}); }
    else{const j=Q.opts.findIndex(o=>o.ok);T.mcq(i%4===1?(j+1)%Q.opts.length:j)}
    if(!Q.done)console.log('not done!',Q.type);T.QZ.i++;T.nextQ();}
  console.log('review summary', T.QZ.summary, 'results',T.QZ.res.length,'right',T.QZ.res.filter(r=>r.ok).length,'srs cards',Object.keys(T.SRS).length,'due now',T.dueKeys().length);
  console.log('summary pane', q('#pane').innerHTML.slice(0,140).replace(/\s+/g,' '));
  T.setTab('E');T.setTab('S');console.log('home again: weak spots', q('#pane').innerHTML.includes('Drill my weak spots'));
  // find drill with side
  T.SCFG.side=true;T.startQuiz('find',T.poolKeys('upper','muscle').slice(0,3).map(k=>({k,types:['find']})),{title:'Find'});
  {const Q=T.QZ.q;console.log('find prompt:',Q.prompt,'side',Q.side,'region',T.ST.region,'labels',T.ST.labels);
   const other=T.S[Q.id].side?T.S[Q.id.replace(/-(R|L)$/,m=>m==='-R'?'-L':'-R')]:null;if(other){T.quizTap({st:other,part:''});console.log('  wrong side tries',Q.tries)}
   T.QZ.peel=true;T.quizTap({st:T.S['humerus-R'],part:''});console.log('  peel hid humerus',T.ST.hidden.has('humerus-R'));T.QZ.peel=false;
   T.quizTap({st:T.S[Q.id],part:''});console.log('  done',Q.done,Q.ok)}
  // exam with time limit
  T.startQuiz('exam',T.poolKeys('all',null).slice(0,20),{limit:1000,title:'Practice exam'});await new Promise(r=>setTimeout(r,1500));console.log('exam timed out -> summary',T.QZ.summary);
  // lecture quiz keys
  T.LECr().deck=T.sampleDeck();console.log('deck keys',T.deckKeys().length);
  // dissection
  T.setTab('S');let t2=Date.now();const L=T.computeLayers('upper');console.log('layers upper',L.map(l=>l.length).join('/'),'ms',Date.now()-t2);
  T.startDis('back');await new Promise(r=>setTimeout(r,100));console.log('dis active',T.DIS.active,'layers',T.DIS.layers.map(l=>l.length).join('/'),'pane',q('#pane').innerHTML.includes('Peel next layer'));
  // tour
  T.startTour('median-R');console.log('tour stops',T.TOUR.stops.map(s=>s.t).join(' > '));
  T.startTour('axillary-a-R');console.log('vessel tour stops',T.TOUR.stops.map(s=>s.t).join(' > '));
  T.startTour('great-saphenous-L');console.log('vein tour stops',T.TOUR.stops.map(s=>s.t).join(' > '));
  T.setTab('E');console.log('left study: QZ',T.QZ.active,'DIS',T.DIS.active,'labels',T.ST.labels);
  T.select('biceps-brachii-R');console.log('memory aid shown',q('#pane').innerHTML.includes('Memory aid'));

  {let t=1000;for(let i=0;i<5;i++){T.loop(t+=16)}console.log('idle PR',T.Q.cur);T.Q.lastMove=t;for(let i=0;i<30;i++){T.Q.lastMove=t;T.loop(t+=40)}console.log('moving slow PR',T.Q.cur,'ema',T.Q.ema|0);
   for(let i=0;i<20;i++)T.loop(t+=16);console.log('after stop PR',T.Q.cur);}
  // ---- LIGAMENTS ----
  {const ligs=Object.values(T.S).filter(s=>s.kind==='ligament');console.log('\n=== LIGAMENTS',ligs.length,'structures, visible',ligs.filter(s=>s.meshes[0].visible).length);
   T.setTab('E');T.select('lig-anterior-cruciate-ligament-R');console.log('ACL page',q('#pane').innerHTML.includes('Lachman'));
   for(const t of ['Knee joint: ACL, PCL, MCL, LCL and the menisci','Ankle sprain — ATFL and calcaneofibular ligament; deltoid ligament medially','Hip joint ligaments: iliofemoral (Y ligament), pubofemoral, ischiofemoral','Coracoclavicular ligament and glenoid labrum']){const an=T.analyze(t);T.applyAnalysis(an,false);console.log(' ',t.slice(0,34),'->',[...an.keys].join(','),'| lig layer',T.ST.ly.ligament)}
   T.ST.iq='sacroiliac';T.setTab('I');console.log('index "sacroiliac" hits',(q('#pane').innerHTML.match(/class="it"/g)||[]).length);T.ST.iq='';
   for(const t of ['Anterior sacroiliac ligament','Craniovertebral ligaments: alar ligaments, transverse ligament of atlas, tectorial membrane','Ligament of Wrisberg and Humphry','Femoral ring: lacunar ligament, Cooper\'s ligament']){const an=T.analyze(t);console.log(' ',t.slice(0,40),'->',[...an.keys].join(','))}
   console.log('lig pill exists',!!q('#bLig').onclick);
   T.SCFG.kind='ligament';console.log('lig pool',T.poolKeys('all','ligament').length);for(const ty of ['find','name','ligjoint']){const Q=T.mkQ('lig-anterior-talofibular-ligament',ty);console.log('  ',ty,Q.prompt.slice(0,120),Q.opts?Q.opts.map(o=>(o.ok?'*':'')+o.t).join(' / '):'')}}
  // ---- PRO ----
  console.log('\n=== PRO');console.log('palette "saph":',T.palItems('saph').slice(0,4).map(x=>x.st.name).join(' | '));console.log('palette "acl":',T.palItems('anterior cruciate').slice(0,2).map(x=>x.st.name).join(' | '));
  T.setTab('E');T.select('deltoid-R');console.log('selcard shown',!q('#selcard').hidden,'outline meshes',T.OUTL.meshes.length);
  T.selAction('i');console.log('isolate via card',!!T.isolateRef());T.selAction('i');T.deselect();console.log('deselect -> outline',T.OUTL.meshes.length,'selcard hidden',q('#selcard').hidden);
  T.setQuality(true);console.log('low quality material',T.S['deltoid-R'].meshes[0].material.type);T.setQuality(false);console.log('high quality material',T.S['deltoid-R'].meshes[0].material.type);
  await T.loadDefs();T.select('median-R');console.log('about on median page',q('#pane').innerHTML.includes('About'));
  T.SCFGr().all=true;console.log('pool core vs all',(()=>{T.SCFGr().all=false;const a=T.poolKeys('all',null).length;T.SCFGr().all=true;const b=T.poolKeys('all',null).length;return a+' / '+b})());
  {const Q=T.mkQ2('great-saphenous','about');console.log('about Q:',Q.type,Q.prompt.slice(0,160),'|',Q.opts&&Q.opts.map(o=>(o.ok?'*':'')+o.t).join(' / '))}
  T.setTab('S');T.renderTourPick('plantar');console.log('tour filter plantar buttons',(q('#pane').innerHTML.match(/data-tr=/g)||[]).length);T.SCFGr().all=false;
  T.showHelp();console.log('help dialog ok');
  // ---- AI ----
  console.log('\n=== AI');await new Promise(r=>setTimeout(r,50));console.log('aiOK',T.aiOK(),'tools',!!(T.AI.limits&&T.AI.limits.tools));
  console.log('resolve:',['deltoid','left median nerve','ACL','great saphenous'].map(n=>{const st=T.resolveName(n);return st?st.id:'—'}).join(', '));
  T.setTab('E');T.select('deltoid-R');T.aiExplain(T.S['deltoid-R']);await new Promise(r=>setTimeout(r,20));console.log('explain prompt has facts',/Axillary/.test(global.__lastInput),'| md:',T.md('**Bold** text\n- a\n- b').slice(0,60));
  T.setTab('A');await T.sendTutor('Show me the deltoid');console.log('tutor turns',T.AI.chat.length,'tool result',JSON.stringify(global.__toolRes),'isolate',T.isolateRef()&&[...T.isolateRef()].join(','));
  T.setTab('S');const fake={disabled:false,innerHTML:''};await T.aiCases(fake);console.log('ai cases quiz',T.QZ.active,T.QZ.title,T.QZ.queue.length,'|',T.QZ.q&&T.QZ.q.prompt);
  T.quizTap({st:T.S[T.QZ.q.id],part:''});T.aiWhy(T.QZ.q);await new Promise(r=>setTimeout(r,20));console.log('why prompt ok',/Correct answer/.test(global.__lastInput));
  {const L=T.LECr();L.deck={name:'ai.pdf',n:1,texts:['Posterior shoulder'],render:async()=>{},imageBlob:async()=>new Blob(['x'],{type:'image/jpeg'})};L.i=0;T.setTab('C');await T.showSlide(0);await new Promise(r=>setTimeout(r,200));
   await T.aiReadSlide({disabled:false});console.log('ai slide read: imgs',global.__imgs&&global.__imgs.length,'| ai items',L.an.items.filter(i=>i.src==='ai').map(i=>i.label).join(', '))}
  T.setExplode(.8);T.resetModel();console.log('reset ok: explode',T.ST.explode,'look',T.ST.look,'region',T.ST.region,'hidden',T.ST.hidden.size);
  console.log('ALL OK');process.exit(0);
})().catch(e=>{console.log('ERR',e.stack);process.exit(1)});
