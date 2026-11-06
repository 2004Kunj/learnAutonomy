/* ---------- study: spaced review, find-it drills, OIAI quiz, exams, weak spots, layer dissection, tours ---------- */
const MN=C.MNEM||{};
const DAY=864e5;const today=()=>Math.floor((Date.now()-new Date().getTimezoneOffset()*6e4)/DAY);
const SRS=LS.get('kl.srs',{}),STATS=LS.get('kl.stats',{});
const QZ={active:false,mode:'',queue:[],i:0,q:null,res:[],t0:0,limit:0,peel:false,cfg:{}};
const SCFG=Object.assign({reg:'all',kind:'muscle',clue:false,cad:false,side:true,n:10},LS.get('kl.scfg',{}));
const DIS={active:false,reg:'upper',layers:null,step:0,tap:null};
const TOUR={active:false,id:null,pts:null,stops:[],si:0,quiz:false,ans:null,tap:null};
let qTick=null;
const REGN={all:'whole body',head:'head & neck',back:'back & spine',trunk:'thorax & abdomen',upper:'upper limb',lower:'lower limb'};
function kOK(k){return byK[k]&&byK[k].length&&(C.MUS[k]||C.NER[k]||C.VES[k]||C.BON[k]||C.TEN[k])}
function kindOfK(k){const s=byK[k][0];return s.kind==='disc'?'bone':isVes(s.kind)?'vessel':s.kind}
function regOfK(k){return regionKeyOf(byK[k][0])}
function nameOfK(k){return byK[k][0].name}
function poolKeys(reg,kind){return Object.keys(byK).filter(k=>kOK(k)&&kindOfK(k)!=='disc'&&(!kind||kind==='all'||kindOfK(k)===kind)&&(reg==='all'||regOfK(k)===reg)&&!(kindOfK(k)==='muscle'&&PIN_SKIP.has(k)&&reg!=='trunk'&&reg!=='back'))}
function words(t){return new Set(t.toLowerCase().replace(/[^a-z ]/g,' ').split(/\s+/).filter(w=>w.length>3&&!/^(with|from|into|that|this|part|side|bone|surface|lower|upper|their|each|over|along)$/.test(w)))}
function overlap(a,b){const A=words(a),B=words(b);let n=0;for(const w of A)if(B.has(w))n++;return n}
function pick(arr,n,avoid){const o=[];for(const x of shuffle(arr)){if(o.length>=n)break;if(!(avoid&&avoid(x,o)))o.push(x)}return o}
function record(k,ok){const s=STATS[k]||(STATS[k]={c:0,w:0});ok?s.c++:s.w++;s.t=Date.now();LS.set('kl.stats',STATS);
  const days=LS.get('kl.days',[]);const d=today();if(days[days.length-1]!==d){days.push(d);LS.set('kl.days',days.slice(-400))}}
function dayStreak(){const days=LS.get('kl.days',[]);let n=0,d=today();if(days[days.length-1]!==d)d--;for(let i=days.length-1;i>=0;i--){if(days[i]===d){n++;d--}else if(days[i]<d)break}return n}
function srsGrade(k,ok){const c=SRS[k]||{i:0,e:2.5,r:0,l:0};
  if(ok){c.r++;c.i=c.r===1?1:c.r===2?3:Math.round(Math.max(c.i,1)*c.e);c.e=Math.min(2.8,c.e+.05);c.d=today()+c.i}
  else{c.l++;c.r=0;c.i=0;c.e=Math.max(1.3,c.e-.2);c.d=today()}
  SRS[k]=c;LS.set('kl.srs',SRS)}
function dueKeys(){const t=today();return Object.keys(SRS).filter(k=>kOK(k)&&SRS[k].d<=t)}
function newKeys(n,reg){
  const have=new Set(Object.keys(SRS));const deck=typeof LEC!=='undefined'&&LEC.deck?deckKeys():[];
  const order=[...deck,...[...ST.studied],...poolKeys(reg||'all','muscle'),...poolKeys(reg||'all','nerve'),...poolKeys(reg||'all','vessel'),...poolKeys(reg||'all','bone')];
  const o=[];for(const k of order){if(o.length>=n)break;if(kOK(k)&&!have.has(k)&&!o.includes(k)&&(reg==='all'||!reg||regOfK(k)===reg))o.push(k)}return o}
function deckKeys(){const ks=new Set();try{for(const t of (LEC.deck.texts||[]))for(const k of analyze(t||'').keys)ks.add(k)}catch(e){}return [...ks].filter(kOK)}

/* question generation */
const QT={muscle:['find','name','nerve','action','origin','insertion','findclue'],nerve:['find','name','supplies','whichnerve'],vessel:['find','name','vsup'],bone:['find','name'],tendon:['find','name']};
function mkQ(k,type,o={}){
  const kind=kindOfK(k),st0=byK[k][0],nm=st0.name,M=C.MUS[k],side=o.side&&st0.side?o.side:'';
  const same=poolKeys('all',kind).filter(x=>x!==k);const sameReg=same.filter(x=>regOfK(x)===regOfK(k));
  const optsK=n=>pick(sameReg.length>=n?sameReg:same,n);
  const q={k,type,kind,side,click:false,opts:null,tries:0,done:false,ok:null};
  const sideW=side?`the patient’s ${side==='R'?'right':'left'} `:'the ';
  switch(type){
    case 'find':q.click=true;q.prompt=`Tap ${sideW}${nm.toLowerCase()}`;q.short=`Find: ${side?(side==='R'?'R ':'L '):''}${nm}`;break;
    case 'findclue':{q.click=true;const n=M[3];q.prompt=`Tap ${side?sideW:'the '}muscle that ${M[2].charAt(0).toLowerCase()+M[2].slice(1)}${/\.$/.test(M[2])?'':'.'} Nerve: ${n}.`;q.short='Find the muscle from its action';break}
    case 'name':q.show=true;q.prompt='Name the highlighted structure.';q.opts=shuffle([nm,...optsK(3).map(nameOfK)]).map(t=>({t,ok:t===nm}));break;
    case 'nerve':{const ks=new Set(M[4]);const ds=pick(Object.entries(C.MUS).filter(([x,v])=>x!==k&&!v[4].some(n=>ks.has(n))).map(([x,v])=>v[3]),3,(t,o)=>o.includes(t));
      q.prompt=`What innervates the ${nm.toLowerCase()}?`;q.opts=shuffle([M[3],...ds]).map(t=>({t,ok:t===M[3]}));break}
    case 'action':{const ds=pick(Object.entries(C.MUS).filter(([x,v])=>x!==k&&overlap(v[2],M[2])<2).map(([x,v])=>v[2]),3,(t,o)=>o.includes(t));
      q.prompt=`What is the main action of the ${nm.toLowerCase()}?`;q.opts=shuffle([M[2],...ds]).map(t=>({t,ok:t===M[2]}));break}
    case 'origin':case 'insertion':{const i=type==='origin'?0:1;const ds=pick(Object.entries(C.MUS).filter(([x,v])=>x!==k&&byK[x]&&overlap(v[i],M[i])<2&&(regOfK(x)===regOfK(k))).map(([x])=>x),3);
      const more=ds.length<3?pick(Object.keys(C.MUS).filter(x=>x!==k&&byK[x]&&!ds.includes(x)&&overlap(C.MUS[x][i],M[i])<2),3-ds.length):[];
      q.prompt=`Which muscle ${type==='origin'?'arises from':'inserts on'}: ${M[i]}?`;q.opts=shuffle([k,...ds,...more]).map(x=>({t:nameOfK(x),ok:x===k}));break}
    case 'supplies':{const sup=(SUPPLIES[k]||[]).filter(x=>byK[x]);if(!sup.length)return mkQ(k,'name',o);const right=sup[Math.random()*sup.length|0];
      const ds=pick(Object.keys(C.MUS).filter(x=>byK[x]&&!sup.includes(x)&&regOfK(x)===regOfK(right)),3);
      q.prompt=`Which of these muscles is supplied by the ${nm.toLowerCase()}?`;q.opts=shuffle([right,...ds]).map(x=>({t:nameOfK(x),ok:x===right}));q.alsoK=right;break}
    case 'whichnerve':{const sup=(SUPPLIES[k]||[]).filter(x=>byK[x]);if(!sup.length)return mkQ(k,'name',o);const m=sup[Math.random()*sup.length|0];
      const ds=pick(Object.keys(C.NER).filter(x=>x!==k&&byK[x]&&!C.MUS[m][4].includes(x)),3);
      q.prompt=`Which nerve supplies the ${nameOfK(m).toLowerCase()}?`;q.opts=shuffle([k,...ds]).map(x=>({t:nameOfK(x),ok:x===k}));break}
    case 'vsup':{const v=C.VES[k];if(!v||!v[2])return mkQ(k,'name',o);const ds=pick(Object.entries(C.VES).filter(([x,w])=>x!==k&&w[2]&&overlap(w[2],v[2])<2).map(([x,w])=>w[2]),3,(t,o2)=>o2.includes(t));
      q.prompt=`What does the ${nm.toLowerCase()} ${st0.kind==='vein'?'drain':'supply'}?`;q.opts=shuffle([v[2],...ds]).map(t=>({t,ok:t===v[2]}));break}
  }
  if(q.opts&&q.opts.length<2)return mkQ(k,'find',o);
  q.id=sameSide(k,side||'R');return q;
}
function randQ(k,types,o={}){const kind=kindOfK(k);let ts=(QT[kind]||['find','name']).filter(t=>!types||types.includes(t));if(!ts.length)ts=['find'];
  return mkQ(k,ts[Math.random()*ts.length|0],{side:o.side&&Math.random()<.5?(Math.random()<.5?'R':'L'):''})}
function explainHTML(k){const kind=kindOfK(k);let h='';
  if(C.MUS[k]){const m=C.MUS[k];h=`<dl class="f"><dt>Origin</dt><dd>${esc(m[0])}</dd><dt>Insertion</dt><dd>${esc(m[1])}</dd><dt>Action</dt><dd>${esc(m[2])}</dd><dt>Nerve</dt><dd>${esc(m[3])}</dd></dl>`}
  else if(C.NER[k]){const n=C.NER[k];const sup=(SUPPLIES[k]||[]).filter(x=>byK[x]).map(nameOfK);h=`<dl class="f"><dt>Roots</dt><dd>${esc(n[0])}</dd><dt>Motor</dt><dd>${esc(n[2])}</dd>${sup.length?`<dt>Supplies</dt><dd>${esc(sup.join(', '))}</dd>`:''}</dl>`}
  else if(C.VES[k]){const v=C.VES[k];h=`<dl class="f"><dt>Begins</dt><dd>${esc(v[0])}</dd><dt>Ends</dt><dd>${esc(v[1])}</dd><dt>${byK[k][0].kind==='vein'?'Drains':'Supplies'}</dt><dd>${esc(v[2])}</dd></dl>`}
  else if(C.BON[k])h=`<p style="margin:6px 0 0">${esc(C.BON[k][0])}</p>`;else if(C.TEN[k])h=`<p style="margin:6px 0 0">${esc(C.TEN[k][0])}</p>`;
  if(MN[k])h+=`<div class="note"><b>Memory aid</b>${esc(MN[k])}</div>`;return h}

/* model staging */
function stageFor(q){
  const st=S[q.id];ST.hidden.clear();isolate=null;ST.sel=null;ST.fade=false;ST.labels=false;$('#bLabels').setAttribute('aria-pressed',false);flash=null;
  if(ST.explode)setExplode(0);if(ST.pose!=='stand')setPose('stand');
  ST.look=SCFG.cad&&QZ.mode==='find'?'cadaver':'atlas';$('#bLook').setAttribute('aria-pressed',ST.look==='cadaver');
  const kd=layerOf(st);ST.ly={bone:true,muscle:true,tendon:true,nerve:kd==='nerve',vessel:kd==='vessel'};
  ST.xray=kd==='nerve'||kd==='vessel';ST.opacity=ST.xray?.45:1;
  ST.side='both';ST.region=q.click||q.show?regionKeyOf(st):'all';
  applyLook();syncDrawer();
  if(q.show){ST.sel=st.id;applyVis();focus(st,outwardDir(st));setTimeout(()=>{if(QZ.q===q&&!q.done){expose(st);flashStruct(st.id,0xd09a00,1400)}},720)}
  else{applyVis();view(lastViewName())}
}
function regWord(st){return REGN[regionKeyOf(st)]||'body'}

/* sessions */
function startQuiz(mode,keys,o={}){
  if(lab.active)labStop();DIS.active=false;TOUR.active=false;
  QZ.active=true;QZ.mode=mode;QZ.i=0;QZ.res=[];QZ.peel=false;QZ.t0=performance.now();QZ.limit=o.limit||0;QZ.title=o.title||'Quiz';
  QZ.queue=keys.map(k=>typeof k==='string'?{k,types:o.types}:k);QZ.srs=!!o.srs;
  clearInterval(qTick);qTick=setInterval(quizTick,250);nextQ();
}
function nextQ(){
  if(QZ.i>=QZ.queue.length){finishQuiz();return}
  const it=QZ.queue[QZ.i];QZ.q=it.q||randQ(it.k,it.types,{side:QZ.mode!=='review'&&SCFG.side});QZ.q.t0=performance.now();
  stageFor(QZ.q);renderStudy();
}
function answer(ok){const q=QZ.q;q.done=true;q.ok=ok;
  const first=ok&&q.tries===0;record(q.k,first);if(q.alsoK)record(q.alsoK,first);
  if(QZ.srs||QZ.mode==='review'){srsGrade(q.k,first);if(!first&&!QZ.queue.slice(QZ.i+1).some(x=>x.k===q.k))QZ.queue.splice(Math.min(QZ.queue.length,QZ.i+4),0,{k:q.k,again:true})}
  QZ.res.push({k:q.k,ok:first,prompt:q.prompt});
  const st=S[q.id];ensureShown(st);ST.sel=st.id;applyVis();
  if(q.click&&!ok){focus(st,outwardDir(st));setTimeout(()=>{expose(st);flashStruct(st.id,0xd09a00,1800)},700)}
  renderStudy();
}
function quizTap(p){
  const q=QZ.q;if(!q||q.done||!q.click||!p)return;
  if(QZ.peel){ST.hidden.add(p.st.id);ST.sel=null;applyVis();syncDrawer();toast(`${displayName(p.st)} dissected away`);return}
  const okK=p.st.k===q.k,okS=!q.side||p.st.side===q.side||!p.st.side;
  if(okK&&okS){flashStruct(p.st.id,0x1f7a3f,1400);toast('Correct — '+displayName(p.st),'ok');answer(true)}
  else{q.tries++;q.last=p.st;flashStruct(p.st.id,0x8a1d12,700);toast(okK?'Right structure, wrong side — check orientation':'Not it: '+displayName(p.st),'bad');
    if(q.tries>=3)answer(false);else renderStudy()}
}
function mcq(i){const q=QZ.q;if(!q||q.done)return;q.pick=i;const ok=q.opts[i].ok;if(!ok)q.tries++;answer(ok)}
function quizTick(){if(!QZ.active)return;const el=$('#qt'),el2=$('#lbt');
  if(QZ.limit){const left=QZ.limit-(performance.now()-QZ.t0);const t=fmt(Math.max(0,left));if(el){el.textContent=t;el.classList.toggle('low',left<60000)}if(el2)el2.textContent=t;if(left<=0&&!QZ.ended){QZ.ended=true;ring();finishQuiz()}}
  else if(QZ.q&&!QZ.q.done){const t=fmt(performance.now()-QZ.q.t0);if(el)el.textContent=t;if(el2)el2.textContent=t}}
function finishQuiz(){clearInterval(qTick);QZ.q=null;QZ.summary=true;QZ.ended=true;$('#labbar').hidden=true;renderStudy()}
function stopStudy(){
  const was=QZ.active||DIS.active||TOUR.active;QZ.active=false;QZ.summary=false;QZ.ended=false;QZ.q=null;DIS.active=false;TOUR.active=false;clearInterval(qTick);anim=null;
  $('#labbar').hidden=true;if(was){ST.labels=true;$('#bLabels').setAttribute('aria-pressed',true);ST.hidden.clear();isolate=null;ST.region='all';ST.opacity=1;ST.xray=false;ST.ly={bone:true,muscle:true,tendon:true,nerve:false,vessel:false};ST.look='atlas';$('#bLook').setAttribute('aria-pressed',false);applyLook();syncDrawer()}
}

/* layer dissection: find what is visible from outside, peel it, repeat */
const disCam=new THREE.PerspectiveCamera(30,.8,5,20000);
function computeLayers(reg){
  const R=REGIONS[reg][1];const inR=st=>!R||R.includes(st.region);
  const musc=ALL.filter(st=>(st.kind==='muscle'||st.kind==='tendon')&&inR(st));
  const all=ALL.flatMap(st=>st.meshes);const vis0=all.map(m=>m.visible);const op0=ST.opacity;ST.opacity=1;
  for(const st of ALL)for(const m of st.meshes){const mt=m.material;if(mt.opacity<1){mt.opacity=1;mt.transparent=false}}
  const bb=new THREE.Box3();for(const st of musc)bb.union(st.box);const c=dataToWorld(bb.getCenter(new THREE.Vector3()));const r=bb.getSize(new THREE.Vector3()).length()/2;
  const dist=r/Math.tan(15*Math.PI/180)*1.05;const dirs=[];for(let a=0;a<8;a++){const t=a/8*Math.PI*2;dirs.push(new THREE.Vector3(Math.cos(t),Math.sin(t),0))}dirs.push(new THREE.Vector3(0,-.4,1).normalize(),new THREE.Vector3(0,.4,-1).normalize());
  let rem=new Set(musc.map(s=>s.id));const layers=[];const savedCam=camera;
  for(let L=0;L<5&&rem.size;L++){
    for(const st of ALL)for(const m of st.meshes)m.visible=rem.has(st.id);
    for(const st of ALL)if(st.ghosts)for(const g of st.ghosts)g.visible=false;
    const cnt=new Map();
    for(const d of dirs){const w=dirToWorld(d);disCam.position.copy(c).addScaledVector(w,dist);disCam.up.copy(dirToWorld(new THREE.Vector3(0,0,1)));if(Math.abs(d.z)>.8)disCam.up.copy(dirToWorld(new THREE.Vector3(0,1,0)));disCam.lookAt(c);disCam.updateMatrixWorld();disCam.updateProjectionMatrix();
      const px=idPass(128,160,disCam);for(let i=0;i<px.length;i+=4){const id=px[i]<<16|px[i+1]<<8|px[i+2];if(id)cnt.set(id,(cnt.get(id)||0)+1)}}
    const lay=[...rem].filter(id=>(cnt.get(S[id].idx)||0)>=6);
    if(!lay.length||L===4){layers.push([...rem]);break}
    layers.push(lay);for(const id of lay)rem.delete(id);
  }
  all.forEach((m,i)=>m.visible=vis0[i]);ST.opacity=op0;applyVis();
  return layers;
}
const LAYN=['Superficial muscles','Second layer','Third layer','Deep muscles','Deepest muscles'];
function disSteps(){const s=DIS.layers.map((l,i)=>({t:LAYN[Math.min(i,4)],ids:l,i}));s.push({t:'Nerves & vessels',nv:true});s.push({t:'Skeleton',bone:true});return s}
function disApply(){
  const steps=disSteps(),cur=steps[DIS.step];ST.hidden.clear();isolate=null;ST.region=DIS.reg;ST.side='both';ST.opacity=1;ST.fade=false;
  for(let i=0;i<DIS.step&&i<DIS.layers.length;i++)for(const id of DIS.layers[i])ST.hidden.add(id);
  ST.ly={bone:true,muscle:!cur.nv&&!cur.bone,tendon:!cur.nv&&!cur.bone,nerve:!!cur.nv,vessel:!!cur.nv};ST.xray=false;ST.labels=true;$('#bLabels').setAttribute('aria-pressed',true);
  applyVis();syncDrawer();
}
function startDis(reg){if(lab.active)labStop();QZ.active=false;TOUR.active=false;DIS.reg=reg;DIS.step=0;DIS.tap=null;ST.sel=null;setExplode(0);if(ST.pose!=='stand')setPose('stand');ST.look='atlas';applyLook();
  toast('Working out the layers…');setTimeout(()=>{DIS.layers=computeLayers(reg);DIS.active=true;disApply();view(lastViewName());renderStudy()},30)}

/* tours: follow a nerve or vessel from start to finish */
function tourData(id){return NERV.find(n=>n.id===id)||VESS.find(n=>n.id===id)}
function resample(path,step){const P=path.map(q=>new THREE.Vector3(q[0],q[1],q[2]));if(P.length<2)return P;const c=new THREE.CatmullRomCurve3(P,false,'centripetal');const n=Math.max(2,Math.round(c.getLength()/step));return c.getSpacedPoints(n)}
function startTour(id){
  if(lab.active)labStop();QZ.active=false;DIS.active=false;
  const st=S[id],n=tourData(id);if(!n)return;const path=n.paths.reduce((a,b)=>b.length>a.length?b:a);const pts=resample(path,6);
  const near=c=>{let bi=0,bd=1e18;pts.forEach((p,i)=>{const d=p.distanceToSquared(c);if(d<bd){bd=d;bi=i}});return [bi,Math.sqrt(bd)]};
  const stops=[{i:0,t:'Start',txt:st.kind==='nerve'?(C.NER[st.k]?'Roots: '+C.NER[st.k][0]:'Origin'):(C.VES[st.k]?'Begins: '+C.VES[st.k][0]:'Origin')}];
  if(st.kind==='nerve'){for(const mk of (SUPPLIES[st.k]||[])){const mid=sameSide(mk,st.side);if(!mid)continue;const m=S[mid];const [i,d]=near(m.center);if(d<120)stops.push({i,t:m.name,txt:'Supplies the '+m.name.toLowerCase()+(C.MUS[mk]?' — '+C.MUS[mk][2].charAt(0).toLowerCase()+C.MUS[mk][2].slice(1):''),m:mid})}}
  else{const own=new Set(n.paths.flat().map(String));
    for(const o of VESS){if(o.id===id||o.side&&o.side!==st.side||o.kind!==st.kind)continue;const p0=o.paths[0][0],p1=o.paths[0][o.paths[0].length-1];
      for(const [q,lab2] of [[p0,'branch'],[p1,'joins']]){const [i,d]=near(new THREE.Vector3(...q));if(d<14&&i>0){stops.push({i,t:o.name,txt:(st.kind==='artery'?(i>=pts.length-2?'Continues as the ':'Gives off the '):(i>=pts.length-2?'Drains into / continues as the ':'Receives the '))+o.name.toLowerCase(),m:o.id});break}}}}
  stops.push({i:pts.length-1,t:'End',txt:st.kind==='nerve'?(C.NER[st.k]?C.NER[st.k][3]:'Termination'):(C.VES[st.k]?'Ends: '+C.VES[st.k][1]:'Termination')});
  stops.sort((a,b)=>a.i-b.i);const seen=new Set();TOUR.stops=stops.filter(s=>{const key=s.t;if(seen.has(key))return false;seen.add(key);return true});
  Object.assign(TOUR,{active:true,id,pts,si:0,ans:null,tap:null});
  ST.hidden.clear();isolate=null;ST.region='all';ST.side='both';ST.ly={bone:true,muscle:true,tendon:true,nerve:st.kind==='nerve',vessel:st.kind!=='nerve'};ST.xray=true;ST.opacity=.35;ST.sel=id;ST.labels=false;$('#bLabels').setAttribute('aria-pressed',false);
  setExplode(0);if(ST.pose!=='stand')setPose('stand');applyLook();syncDrawer();
  tourGo(0,true);
}
function tourGo(si,jump){
  const a=TOUR.stops[TOUR.si],b=TOUR.stops[si];TOUR.si=si;TOUR.ans=null;TOUR.opts=null;renderStudy();
  const off=camera.position.clone().sub(controls.target);const L=Math.min(320,Math.max(220,off.length()));off.setLength(L);
  const from=jump?b.i:a.i,to=b.i;const dir=to>=from?1:-1;const idxs=[];for(let i=from;dir>0?i<=to:i>=to;i+=dir)idxs.push(i);
  const wp=idxs.map(i=>dataToWorld(TOUR.pts[i]));const t0=performance.now(),dur=jump?650:Math.min(4200,Math.max(700,wp.length*45));
  const p0=camera.position.clone(),c0=controls.target.clone();
  anim=now=>{let k=Math.min(1,(now-t0)/dur);const e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    if(jump){controls.target.lerpVectors(c0,wp[0],e);camera.position.lerpVectors(p0,wp[0].clone().add(off),e)}
    else{const f=e*(wp.length-1),i=Math.floor(f),u=f-i;const p=wp[i].clone().lerp(wp[Math.min(wp.length-1,i+1)],u);controls.target.copy(p);camera.position.copy(p).add(off)}
    if(k>=1){anim=null;tourArrive()}};
}
function tourArrive(){const s=TOUR.stops[TOUR.si];if(s.m&&S[s.m]){if(TOUR.quiz&&S[s.m].kind==='muscle'){const pool=Object.keys(C.MUS).filter(k=>byK[k]&&k!==S[s.m].k&&regOfK(k)===regOfK(S[s.m].k));TOUR.opts=shuffle([S[s.m].k,...pick(pool,3)])}
  ensureShown(S[s.m]);applyVis();flashStruct(s.m,S[s.m].kind==='muscle'?0x1f7a3f:0xd09a00,2600)}renderStudy();queueLabels()}

/* ---------- rendering ---------- */
function chipRow(name,opts,val){return `<div class="filters">${opts.map(([k,t])=>`<button data-${name}="${k}" aria-pressed="${val===k}">${t}</button>`).join('')}</div>`}
function weakList(n){return Object.entries(STATS).filter(([k,s])=>kOK(k)&&s.w>0).map(([k,s])=>({k,acc:s.c/(s.c+s.w),n:s.c+s.w,w:s.w})).sort((a,b)=>a.acc-b.acc||b.w-a.w).slice(0,n)}
function renderStudy(){
  if(DIS.active)return renderDis();if(TOUR.active)return renderTour();
  if(QZ.active)return QZ.summary?renderSummary():renderQ();
  const due=dueKeys().length,learned=Object.keys(SRS).length,nNew=Math.min(10,newKeys(10,SCFG.reg).length),weak=weakList(12),deck=typeof LEC!=='undefined'&&LEC.deck?deckKeys():[];
  const regs=Object.entries(REGIONS).map(([k,[t]])=>[k,t]);
  pane.innerHTML=`<div class="kick">Active recall · spaced repetition</div><h2 class="name">Study</h2>
   <div class="score" style="margin-top:4px"><span>Due today <b>${due}</b></span><span>Learned <b>${learned}</b></span><span>Day streak <b>${dayStreak()}</b></span></div>
   <div class="modes">
    <button class="mode" data-s="review"><strong>Daily review</strong><span>${due?`${due} card${due>1?'s':''} due`:'Nothing due'}${nNew?` + ${nNew} new`:''}. Misses come back tomorrow; things you know fade out to weeks and months.</span></button>
    <button class="mode" data-s="find"><strong>Find-it drill</strong><span>A name (or just its action and nerve) appears — tap it on the model. Bellringer practice, ten at a time.</span></button>
    <button class="mode" data-s="oiai"><strong>OIAI quiz</strong><span>Origin, insertion, action, innervation. Every answer lights up on the model.</span></button>
    <button class="mode" data-s="exam"><strong>Practice exam</strong><span>20 mixed questions in 20 minutes — identify, find and OIAI — with a scored review at the end.</span></button>
    <button class="mode" data-s="lec" ${deck.length?'':'aria-disabled="true"'}><strong>Lecture quiz</strong><span>${deck.length?`${deck.length} structures from the slides you have open in Lecture.`:'Open a slide deck in the Lecture tab first, then quiz yourself on exactly what it covers.'}</span></button>
    <button class="mode" data-s="dis"><strong>Dissect in layers</strong><span>Peel a region superficial → deep, one layer at a time, then nerves & vessels, then bone.</span></button>
    <button class="mode" data-s="tour"><strong>Follow a nerve or vessel</strong><span>Fly along it from start to finish, stopping at each muscle it supplies or each branch.</span></button>
   </div>
   <div class="kick" style="margin-top:16px">Region for drills &amp; new cards</div>${chipRow('sr',regs,SCFG.reg)}
   <div class="kick">Find-it targets</div>${chipRow('sk',[['muscle','Muscles'],['nerve','Nerves'],['vessel','Vessels'],['bone','Bones'],['all','Mixed']],SCFG.kind)}
   <label class="hint" style="display:flex;gap:8px;align-items:center;cursor:pointer"><input type="checkbox" id="sCl" ${SCFG.clue?'checked':''}> Clue mode — give the action &amp; nerve instead of the name (muscles)</label>
   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="sCa" ${SCFG.cad?'checked':''}> Cadaver colouring during Find-it</label>
   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:6px;cursor:pointer"><input type="checkbox" id="sSi" ${SCFG.side?'checked':''}> Ask for a specific side (patient’s left / right)</label>
   <div class="kick" style="margin-top:16px">Weak spots</div>
   ${weak.length?`<div class="links" style="margin-top:6px">${weak.map(w=>`<button class="lnk" data-w="${w.k}">${esc(nameOfK(w.k))} <span class="hint">${Math.round(w.acc*100)}%</span></button>`).join('')}</div>
     ${regBars()}<div class="acts"><button class="btn pri" id="sW">Drill my weak spots</button></div>`:'<p class="hint">Answer a few questions and the structures you miss most will collect here.</p>'}`;
  const sv=()=>LS.set('kl.scfg',SCFG);
  pane.querySelectorAll('[data-sr]').forEach(b=>b.onclick=()=>{SCFG.reg=b.dataset.sr;sv();renderStudy()});
  pane.querySelectorAll('[data-sk]').forEach(b=>b.onclick=()=>{SCFG.kind=b.dataset.sk;sv();renderStudy()});
  $('#sCl').onchange=e=>{SCFG.clue=e.target.checked;sv()};$('#sCa').onchange=e=>{SCFG.cad=e.target.checked;sv()};$('#sSi').onchange=e=>{SCFG.side=e.target.checked;sv()};
  pane.querySelectorAll('[data-w]').forEach(b=>b.onclick=()=>{const id=sameSide(b.dataset.w,'R');setTab('E');select(id,{reveal:true});focus(S[id])});
  const w=$('#sW');if(w)w.onclick=()=>startQuiz('weak',weak.map(x=>x.k),{title:'Weak-spot drill'});
  pane.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>{const m=b.dataset.s;
    if(m==='review'){const ks=[...shuffle(dueKeys()),...newKeys(10,SCFG.reg)];if(!ks.length){toast('All caught up — come back tomorrow');return}startQuiz('review',ks,{srs:true,title:'Daily review'})}
    else if(m==='find'){let ks=poolKeys(SCFG.reg,SCFG.kind==='all'?null:SCFG.kind);if(SCFG.kind==='all')ks=ks.filter(k=>['muscle','nerve','vessel','bone'].includes(kindOfK(k)));
      const items=pick(ks,10).map(k=>({k,types:SCFG.clue&&C.MUS[k]?['findclue']:['find']}));if(!items.length){toast('Nothing to find in that region');return}startQuiz('find',items,{title:'Find-it drill'})}
    else if(m==='oiai'){const ks=pick(poolKeys(SCFG.reg,'muscle').concat(poolKeys(SCFG.reg,'nerve')),10);startQuiz('oiai',ks.map(k=>({k,types:C.MUS[k]?['nerve','action','origin','insertion']:['supplies','whichnerve']})),{title:'OIAI quiz'})}
    else if(m==='exam'){const ks=pick(poolKeys(SCFG.reg,null).filter(k=>['muscle','nerve','vessel','bone'].includes(kindOfK(k))),20);startQuiz('exam',ks.map((k,i)=>({k,types:i%5<2?['find','findclue']:i%5===2?['name']:null})),{limit:20*60000,title:'Practice exam'})}
    else if(m==='lec'){if(!deck.length){toast('Open slides in the Lecture tab first');return}startQuiz('lec',pick(deck,Math.min(15,deck.length)),{title:'Lecture quiz'})}
    else if(m==='dis'){DIS.pick=true;renderDisPick()}
    else if(m==='tour'){renderTourPick()}});
}
function regBars(){const agg={};for(const [k,s] of Object.entries(STATS)){if(!kOK(k))continue;const r=regOfK(k);const a=agg[r]||(agg[r]={c:0,w:0});a.c+=s.c;a.w+=s.w}
  const rows=Object.entries(REGIONS).filter(([k])=>k!=='all'&&agg[k]).map(([k,[t]])=>{const a=agg[k],p=Math.round(a.c/(a.c+a.w)*100);return `<div style="display:grid;grid-template-columns:110px 1fr 38px;gap:8px;align-items:center;font-size:12.5px;margin-top:6px"><span>${t}</span><span style="height:7px;border-radius:4px;background:var(--line);overflow:hidden"><i style="display:block;height:100%;width:${p}%;background:${p<60?'var(--bad)':p<80?'#C99A1E':'var(--ok)'}"></i></span><b style="font:600 12px var(--f-mono)">${p}%</b></div>`});
  return rows.length?`<div style="margin-top:10px">${rows.join('')}</div>`:''}
function renderQ(){
  const q=QZ.q;if(!q)return;const st=S[q.id];const n=QZ.queue.length;
  const head=`<div style="display:flex;justify-content:space-between;align-items:center;gap:10px"><div class="kick">${esc(QZ.title)} · ${QZ.i+1} / ${n}</div><div class="timer" id="qt">${QZ.limit?fmt(Math.max(0,QZ.limit-(performance.now()-QZ.t0))):'0.0s'}</div></div>`;
  let body=`<div class="scen"><div class="kick">${q.click?'Tap it on the model · '+esc(regWord(st)):q.show?'Look at the model':'Question'}</div><p class="q">${esc(q.prompt)}</p></div>`;
  if(q.opts)body+=`<div class="choices">${q.opts.map((o,i)=>`<button class="choice${q.done?(o.ok?' right':(q.pick===i?' wrong':'')):''}" data-o="${i}" ${q.done?'disabled':''}>${esc(o.t)}</button>`).join('')}</div>`;
  if(q.click&&!q.done){body+=`${q.last?`<div class="fb no">That’s the <b>${esc(displayName(q.last))}</b>. ${3-q.tries} tr${3-q.tries===1?'y':'ies'} left.</div>`:''}
    <div class="acts"><button class="btn" id="qP" aria-pressed="${QZ.peel}">${QZ.peel?'Peeling: tap to remove — click to stop':'Peel away a layer'}</button>${q.last?`<button class="btn" id="qD">Dissect away the ${esc(q.last.name.toLowerCase())}</button>`:''}<button class="btn" id="qR">Show me</button></div>
    <p class="hint" style="margin-top:10px">Deep structures may sit under others — peel overlying muscles away like in lab. Anterior view puts the patient’s right on your left.</p>`}
  if(q.done){const ok=q.ok&&q.tries===0;body+=`<div class="fb ${ok?'ok':'no'}"><b>${ok?'Correct':q.ok?'Got there':'Answer'}: ${esc(titleName(st))}</b>${q.alsoK?' · '+esc(nameOfK(q.alsoK)):''}</div>${explainHTML(q.k)}
    <div class="acts"><button class="btn pri" id="qN">${QZ.i+1>=QZ.queue.length?'Finish':'Next →'}</button><button class="btn" id="qF">Zoom to it</button></div>`}
  const right=QZ.res.filter(r=>r.ok).length;
  pane.innerHTML=head+body+`<div class="score"><span>Correct <b>${right}/${QZ.res.length}</b></span>${QZ.srs?`<span>Due left <b>${Math.max(0,QZ.queue.length-QZ.i-1)}</b></span>`:''}</div><div class="acts"><button class="btn" id="qQ">End session</button></div>`;
  const lb=$('#labbar');lb.hidden=false;lb.innerHTML=q.done?`<span>${q.ok&&q.tries===0?'Correct':'Answer'}: ${esc(titleName(st))} — Next below</span>`:`<span class="t" id="lbt"></span><span style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(q.short||q.prompt)}</span>`;
  pane.querySelectorAll('[data-o]').forEach(b=>b.onclick=()=>mcq(+b.dataset.o));
  const on=(id,f)=>{const e=$(id);if(e)e.onclick=f};
  on('#qP',()=>{QZ.peel=!QZ.peel;renderQ()});on('#qD',()=>{ST.hidden.add(q.last.id);q.last=null;applyVis();syncDrawer();renderQ()});
  on('#qR',()=>{q.tries=3;answer(false)});on('#qN',()=>{QZ.i++;QZ.peel=false;nextQ()});on('#qF',()=>focus(st,outwardDir(st)));on('#qQ',()=>{finishQuiz()});
}
function renderSummary(){
  const r=QZ.res,ok=r.filter(x=>x.ok).length,pct=r.length?Math.round(ok/r.length*100):0,miss=r.filter(x=>!x.ok);const secs=(performance.now()-QZ.t0);
  pane.innerHTML=`<div class="kick">${esc(QZ.title)} complete</div><h2 class="name">${ok} / ${r.length}${r.length?` · ${pct}%`:''}</h2><p class="hint">Time ${fmt(secs)}${QZ.mode==='review'?' · misses were rescheduled for today and tomorrow':''}</p>
   ${miss.length?`<div class="kick" style="margin-top:12px">Review these</div><div class="links" style="margin-top:6px">${[...new Set(miss.map(m=>m.k))].map(k=>`<button class="lnk" data-m="${k}">${esc(nameOfK(k))}</button>`).join('')}</div>`:'<div class="fb ok">Clean sweep.</div>'}
   <div class="acts">${miss.length?'<button class="btn pri" id="sR">Drill the misses</button><button class="btn" id="sA">Add misses to daily review</button>':''}<button class="btn" id="sB">Back to Study</button></div>`;
  pane.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{const k=b.dataset.m;const id=sameSide(k,'R');ST.sel=id;ensureShown(S[id]);applyVis();focus(S[id],outwardDir(S[id]));
    const d=document.createElement('div');d.innerHTML=`<div class="note"><b>${esc(nameOfK(k))}</b></div>${explainHTML(k)}`;const old=$('#sumX');if(old)old.remove();d.id='sumX';pane.appendChild(d)});
  const mk=[...new Set(miss.map(m=>m.k))];
  const a=$('#sR');if(a)a.onclick=()=>startQuiz('weak',mk,{title:'Miss drill'});
  const b=$('#sA');if(b)b.onclick=()=>{for(const k of mk){SRS[k]=Object.assign(SRS[k]||{i:0,e:2.5,r:0,l:0},{d:today()})}LS.set('kl.srs',SRS);toast(`${mk.length} added to today’s review`,'ok')};
  $('#sB').onclick=()=>{stopStudy();renderStudy()};
}
function renderDisPick(){
  pane.innerHTML=`<div class="kick">Dissect in layers</div><h2 class="name">Choose a region</h2><p class="hint">The app works out which muscles are visible from the outside, removes them, and repeats — so each step is a real dissection layer for this specimen.</p>
   <div class="modes" style="margin-top:12px">${Object.entries(REGIONS).filter(([k])=>k!=='all').map(([k,[t]])=>`<button class="mode" data-dr="${k}"><strong>${t}</strong></button>`).join('')}</div><div class="acts"><button class="btn" id="sB">Back</button></div>`;
  pane.querySelectorAll('[data-dr]').forEach(b=>b.onclick=()=>startDis(b.dataset.dr));$('#sB').onclick=()=>renderStudy();
}
function renderDis(){
  const steps=disSteps(),cur=steps[DIS.step];
  const shownIds=cur.ids||(cur.nv?ALL.filter(s=>(s.kind==='nerve'||isVes(s.kind))&&inRegion(s)).map(s=>s.id):ALL.filter(s=>(s.kind==='bone')&&inRegion(s)).map(s=>s.id));
  const uniq=[];const seen=new Set();for(const id of shownIds){const s=S[id];if(!seen.has(s.k)){seen.add(s.k);uniq.push(s)}}
  const t=DIS.tap&&S[DIS.tap];
  pane.innerHTML=`<div class="kick">Dissect in layers · ${esc(REGIONS[DIS.reg][0])}</div><h2 class="name">${esc(cur.t)}</h2>
   <p class="hint">Step ${DIS.step+1} of ${steps.length}. ${DIS.step===0?'Nothing removed yet — this is what you see when the skin and fascia come off.':cur.nv?'All muscles reflected: the neurovascular layer.':cur.bone?'Everything removed down to bone.':`The ${DIS.step} layer${DIS.step>1?'s':''} above ${DIS.step>1?'have':'has'} been reflected.`}</p>
   <div style="display:flex;gap:4px;margin:10px 0">${steps.map((s,i)=>`<i style="flex:1;height:5px;border-radius:3px;background:${i<=DIS.step?'var(--accent)':'var(--line)'}"></i>`).join('')}</div>
   <div class="kick" style="margin-top:6px">${cur.ids?'Exposed in this layer':'In view'} — tap to locate</div>
   <div class="links" style="margin-top:6px">${uniq.slice(0,60).map(s=>`<button class="lnk" data-dg="${s.id}">${esc(s.name)}</button>`).join('')}</div>
   ${t?`<div class="note"><b>${esc(titleName(t))}</b></div>${explainHTML(t.k)}`:''}
   <div class="acts"><button class="btn" id="dP" ${DIS.step?'':'disabled'}>← Put back</button><button class="btn pri" id="dN" ${DIS.step<steps.length-1?'':'disabled'}>Peel next layer →</button><button class="btn" id="dQ">Quiz this layer</button><button class="btn" id="dX">Finish</button></div>`;
  pane.querySelectorAll('[data-dg]').forEach(b=>b.onclick=()=>{DIS.tap=b.dataset.dg;ST.sel=DIS.tap;applyVis();flashStruct(DIS.tap,0xd09a00,1500);focus(S[DIS.tap],outwardDir(S[DIS.tap]));renderDis()});
  $('#dP').onclick=()=>{DIS.step--;DIS.tap=null;ST.sel=null;disApply();renderDis()};$('#dN').onclick=()=>{DIS.step++;DIS.tap=null;ST.sel=null;disApply();renderDis()};
  $('#dQ').onclick=()=>{const ks=[...new Set(uniq.map(s=>s.k))].filter(kOK);if(!ks.length)return;const reg=DIS.reg;DIS.active=false;startQuiz('find',pick(ks,Math.min(10,ks.length)).map(k=>({k,types:['find']})),{title:'Layer quiz'})};
  $('#dX').onclick=()=>{stopStudy();renderStudy()};
}
function renderTourPick(){
  const nv=NERV.filter(n=>n.side!=='L').map(n=>n.id),ar=VESS.filter(v=>v.kind==='artery'&&v.side!=='L').map(v=>v.id),ve=VESS.filter(v=>v.kind==='vein'&&v.side!=='L').map(v=>v.id);
  const row=(t,ids)=>`<div class="kick" style="margin-top:14px">${t}</div><div class="links" style="margin-top:6px">${ids.filter(id=>S[id]).sort((a,b)=>S[a].name.localeCompare(S[b].name)).map(id=>`<button class="lnk${S[id].kind==='nerve'?' nv':''}" data-tr="${id}">${esc(S[id].name)}</button>`).join('')}</div>`;
  pane.innerHTML=`<div class="kick">Follow a structure</div><h2 class="name">Pick a nerve or vessel</h2><p class="hint">The camera flies along its course and stops at each muscle it supplies, or at each branch and continuation.</p>
   <label class="hint" style="display:flex;gap:8px;align-items:center;margin-top:10px;cursor:pointer"><input type="checkbox" id="tQz" ${TOUR.quiz?'checked':''}> Quiz me at each muscle before naming it</label>
   ${row('Nerves',nv)}${row('Arteries',ar)}${row('Veins',ve)}<div class="acts"><button class="btn" id="sB">Back</button></div>`;
  $('#tQz').onchange=e=>{TOUR.quiz=e.target.checked};
  pane.querySelectorAll('[data-tr]').forEach(b=>b.onclick=()=>startTour(b.dataset.tr));$('#sB').onclick=()=>renderStudy();
}
function renderTour(){
  const st=S[TOUR.id],s=TOUR.stops[TOUR.si],last=TOUR.si>=TOUR.stops.length-1;const hide=TOUR.opts&&!TOUR.ans;
  pane.innerHTML=`<div class="kick">Following the ${esc(titleName(st).toLowerCase())}</div><h2 class="name">${hide?'Which muscle is lit up?':esc(s.t)}</h2>
   <div style="display:flex;gap:4px;margin:10px 0">${TOUR.stops.map((x,i)=>`<i style="flex:1;height:5px;border-radius:3px;background:${i<=TOUR.si?'var(--c-nerve,#C99A1E)':'var(--line)'}"></i>`).join('')}</div>
   ${hide?`<div class="choices">${TOUR.opts.map(k=>`<button class="choice" data-ta="${k}">${esc(nameOfK(k))}</button>`).join('')}</div>`:
     `${TOUR.ans?`<div class="fb ${TOUR.ans==='ok'?'ok':'no'}">${TOUR.ans==='ok'?'Correct':'It’s the '+esc(s.t.toLowerCase())}</div>`:''}<p style="margin:8px 0 0">${esc(s.txt)}</p>${s.m&&S[s.m]&&MN[S[s.m].k]?`<div class="note"><b>Memory aid</b>${esc(MN[S[s.m].k])}</div>`:''}`}
   ${TOUR.si===0&&MN[st.k]?`<div class="note"><b>Memory aid</b>${esc(MN[st.k])}</div>`:''}
   <div class="acts"><button class="btn" id="tP" ${TOUR.si?'':'disabled'}>← Back</button><button class="btn pri" id="tN" ${last?'disabled':''}>${last?'End of course':'Next stop →'}</button><button class="btn" id="tX">Finish</button></div>
   <p class="hint" style="margin-top:10px">Stop ${TOUR.si+1} of ${TOUR.stops.length}. Drag to look around at any stop.</p>`;
  pane.querySelectorAll('[data-ta]').forEach(b=>b.onclick=()=>{const ok=S[s.m].k===b.dataset.ta;TOUR.ans=ok?'ok':'no';record(S[s.m].k,ok);renderTour()});
  $('#tP').onclick=()=>tourGo(TOUR.si-1);$('#tN').onclick=()=>tourGo(TOUR.si+1);$('#tX').onclick=()=>{stopStudy();renderStudy()};
}
