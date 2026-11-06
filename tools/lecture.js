/* ---------- lecture mode ---------- */
const LEC={deck:null,i:0,follow:true,an:null,status:'',saved:[]};
function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error('script'));document.head.appendChild(s)})}
const reEsc=t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
/* --- term index: structure names + course vocabulary --- */
const TERMS=[];
function term(p,keys,label,regions){TERMS.push({re:new RegExp('\\b(?:'+p+')\\b','i'),keys:keys||[],label:label||p.split('|')[0].replace(/\\[sb?]|[\\()?:]/g,''),regions:regions||[]})}
for(const k in byK){const st=byK[k][0];let nm=st.name.toLowerCase().replace(/\s*\(.*?\)/g,'').replace(/ & /g,' and ').trim();
  if(nm.length<4)continue;term(reEsc(nm).replace(/\s+/g,'\\s+')+'s?',[k],st.name)}
const AL=[
 ['rotator\\s+cuff|sits muscles',['supraspinatus','infraspinatus','teres-minor','subscapularis'],'Rotator cuff'],
 ['quadriceps(?:\\s+femoris)?|quads',['rectus-femoris','vastus-lateralis','vastus-medialis','vastus-intermedius'],'Quadriceps'],
 ['hamstrings?',['biceps-femoris','semitendinosus','semimembranosus'],'Hamstrings'],
 ['erector\\s+spinae',['iliocostalis','longissimus','spinalis'],'Erector spinae'],
 ['transversospinal(?:is)?',['semispinalis','multifidus','rotatores'],'Transversospinalis'],
 ['triceps\\s+surae|calf\\s+muscles?|plantar\\s*flexors?',['gastrocnemius','soleus','plantaris'],'Calf'],
 ['adductors?|medial\\s+compartment\\s+of\\s+the\\s+thigh|adductor\\s+group',['adductor-longus','adductor-brevis','adductor-magnus','adductor-minimus','gracilis','pectineus','obturator-ext'],'Adductor group'],
 ['glute(?:al|s)|gluteus',['glute-max','glute-med','glute-min','tfl'],'Gluteal muscles'],
 ['lateral\\s+rotators|deep\\s+(?:six|6)|short\\s+lateral\\s+rotators',['piriformis','gemellus-sup','gemellus-inf','obturator-int','obturator-ext','quadratus-femoris'],'Deep lateral rotators'],
 ['iliopsoas|hip\\s+flexors?',['psoas-major','iliacus'],'Iliopsoas'],
 ['scalenes?|scalene\\s+muscles',['scale-ant','scalene-ant','scalene-med','scalene-post'],'Scalenes'],
 ['suprahyoids?',['digastric','mylohyoid','stylohyoid','geniohyoid'],'Suprahyoid'],
 ['infrahyoids?|strap\\s+muscles',['sternohyoid','sternothyroid','thyrohyoid','omohyoid'],'Infrahyoid'],
 ['suboccipital',['rcp-major','rcp-minor','oc-superior','oc-inferior'],'Suboccipital'],
 ['mastication|chewing',['temporalis','masseter','medial-pterygoid','lateral-pterygoid'],'Muscles of mastication'],
 ['facial\\s+expression|muscles\\s+of\\s+the\\s+face',['frontalis','occipitalis','orbicularis-oculi','orbicularis-oris','buccinator','zygomaticus-major','zygomaticus-minor','levator-labii','depressor-anguli','mentalis','nasalis','risorius','corrugator','platysma'],'Facial expression'],
 ['intercostals?',['ext-intercostal','int-intercostal','innermost-intercostal'],'Intercostals'],
 ['anterolateral\\s+abdominal|abdominal\\s+wall|abdominals|\\babs\\b',['rectus-abdominis','ext-oblique','int-oblique','transversus-abdominis','pyramidalis'],'Abdominal wall'],
 ['obliques',['ext-oblique','int-oblique'],'Obliques'],
 ['pelvic\\s+floor|pelvic\\s+diaphragm',['levator-ani','coccygeus'],'Pelvic floor'],
 ['respiration|breathing|muscles\\s+of\\s+inspiration',['diaphragm','ext-intercostal','int-intercostal','scalene-ant','scalene-med','scalene-post'],'Muscles of respiration'],
 ['thenar',['apb','fpb','opponens-pollicis'],'Thenar'],['hypothenar',['adm-hand','fdmb-hand','odm-hand'],'Hypothenar'],
 ['interossei',['dorsal-interossei-hand','palmar-interossei'],'Interossei'],
 ['anterior\\s+(?:compartment\\s+of\\s+the\\s+)?forearm|forearm\\s+flexors|wrist\\s+flexors',['pronator-teres','fcr','palmaris-longus','fcu','fds','fdp','fpl','pronator-quadratus'],'Anterior forearm'],
 ['posterior\\s+(?:compartment\\s+of\\s+the\\s+)?forearm|forearm\\s+extensors|wrist\\s+extensors',['brachioradialis','ecrl','ecrb','ext-digitorum','edm','ecu','supinator','apl','epb','epl','ext-indicis','anconeus'],'Posterior forearm'],
 ['anatomical\\s+snuff\\s*box',['apl','epb','epl','radial-a'],'Anatomical snuffbox'],
 ['rhomboids',['rhomboid-major','rhomboid-minor'],'Rhomboids'],
 ['anterior\\s+compartment\\s+of\\s+the\\s+leg|dorsiflexors?',['tibialis-anterior','ehl','edl','fibularis-tertius'],'Anterior leg'],
 ['lateral\\s+compartment|fibulars|peroneals?|evertors?',['fibularis-longus','fibularis-brevis'],'Lateral leg'],
 ['posterior\\s+compartment\\s+of\\s+the\\s+leg',['gastrocnemius','soleus','plantaris','popliteus','tibialis-posterior','fdl','fhl'],'Posterior leg'],
 ['anterior\\s+compartment\\s+of\\s+the\\s+thigh',['sartorius','rectus-femoris','vastus-lateralis','vastus-medialis','vastus-intermedius'],'Anterior thigh'],
 ['posterior\\s+compartment\\s+of\\s+the\\s+thigh',['biceps-femoris','semitendinosus','semimembranosus'],'Posterior thigh'],
 ['pes\\s+anserinus',['sartorius','gracilis','semitendinosus'],'Pes anserinus'],
 ['plantar\\s+(?:muscles|layers?)|sole\\s+of\\s+the\\s+foot|intrinsic\\s+muscles\\s+of\\s+the\\s+foot',['abductor-hallucis','fdb','adm-foot','quadratus-plantae','lumbricals-foot','fhb','adductor-hallucis','fdmb-foot','plantar-interossei','dorsal-interossei-foot','long-plantar-lig'],'Plantar foot'],
 ['scapular\\s+stabili[sz]ers?',['trapezius','rhomboid-major','rhomboid-minor','levator-scapulae','serratus-anterior','pec-minor'],'Scapular stabilisers'],
 ['femoral\\s+triangle',['sartorius','adductor-longus','iliacus','psoas-major','pectineus','femoral','femoral-a','femoral-v'],'Femoral triangle'],
 ['cubital\\s+fossa',['brachioradialis','pronator-teres','biceps-brachii','brachial-a','median','median-cubital'],'Cubital fossa'],
 ['carpal\\s+tunnel',['flexor-retinaculum','median','fds','fdp','fpl','carpals'],'Carpal tunnel'],
 ['tarsal\\s+tunnel',['tibialis-posterior','fdl','fhl','tibial','post-tibial-a'],'Tarsal tunnel'],
 ['quadrangular\\s+space',['teres-minor','teres-major','triceps','axillary','humerus'],'Quadrangular space'],
 ['brachial\\s+plexus',['brachial-plexus','musculocutaneous','axillary','radial','median','ulnar','long-thoracic','suprascapular','dorsal-scapular','thoracodorsal','subscapular','pectoral'],'Brachial plexus'],
 ['lumbar\\s+plexus',['femoral','obturator'],'Lumbar plexus'],['sacral\\s+plexus',['sciatic','tibial','common-fibular','superior-gluteal','inferior-gluteal','pudendal'],'Sacral plexus'],
 ['common\\s+peroneal|deep\\s+(?:fibular|peroneal)|superficial\\s+(?:fibular|peroneal)',['common-fibular'],'Fibular nerves'],
 ['peroneal\\s+nerve',['common-fibular'],'Common fibular nerve'],
 ['biceps(?!\\s+femoris)',['biceps-brachii'],'Biceps brachii'],['triceps(?!\\s+surae)',['triceps'],'Triceps brachii'],
 ['lats',['lats'],'Latissimus dorsi'],['traps',['trapezius'],'Trapezius'],['pecs',['pec-major','pec-minor'],'Pectorals'],
 ['achilles',['calcaneal-tendon'],'Achilles tendon'],['it\\s+band|iliotibial\\s+band',['it-tract'],'IT band'],
 ['os\\s+coxae|ilium|ischium|pubis|acetabul\\w*|iliac\\s+crest|innominate',['hip-bone'],'Hip bone'],
 ['calcaneus|talus|navicular|cuboid|cuneiforms?|tarsals?',['tarsals'],'Tarsals'],
 ['scaphoid|lunate|triquetr\\w*|pisiform|trapezium|trapezoid|capitate|hamate|carpals?',['carpals'],'Carpals'],
 ['metacarpals?',['metacarpals'],'Metacarpals'],['metatarsals?',['metatarsals'],'Metatarsals'],
 ['vertebral\\s+column|vertebrae|spinal\\s+column|vertebra',['atlas','axis','cervical','thoracic','lumbar','sacrum','discs'],'Vertebral column'],
 ['intervertebral\\s+dis[ck]s?|nucleus\\s+pulposus|annulus\\s+fibrosus',['discs'],'Intervertebral discs'],
 ['sternum',['manubrium','sternum-body','xiphoid'],'Sternum'],['rib\\s+cage|thoracic\\s+cage',['ribs','costal-cart','manubrium','sternum-body','xiphoid'],'Thoracic cage'],
 ['skull|cranium|neurocranium|viscerocranium|cranial\\s+bones',['frontal','parietal','temporal','occipital','sphenoid','ethmoid','zygomatic','maxilla','nasal','lacrimal','palatine','concha','vomer','mandible'],'Skull'],
 ['knee(?:\\s+joint)?',['femur','patella','tibia','fibula','popliteus','patellar-lig','gastrocnemius','biceps-femoris','semimembranosus','semitendinosus','vastus-medialis','vastus-lateralis','rectus-femoris','sartorius','gracilis','it-tract'],'Knee joint'],
 ['elbow(?:\\s+joint)?',['humerus','radius','ulna','brachialis','biceps-brachii','triceps','anconeus','brachioradialis','supinator','pronator-teres'],'Elbow joint'],
 ['glenohumeral|shoulder\\s+joint',['scapula','humerus','clavicle','supraspinatus','infraspinatus','teres-minor','subscapularis','deltoid'],'Shoulder joint'],
 ['hip\\s+joint|coxal\\s+joint',['hip-bone','femur','glute-max','glute-med','glute-min','psoas-major','iliacus','piriformis','obturator-int','quadratus-femoris'],'Hip joint'],
 ['ankle(?:\\s+joint)?|talocrural',['tibia','fibula','tarsals','calcaneal-tendon','tibialis-anterior','tibialis-posterior','fibularis-longus','fibularis-brevis'],'Ankle joint'],
 ['wrist(?:\\s+joint)?|radiocarpal',['radius','ulna','carpals','flexor-retinaculum'],'Wrist joint'],
 ['temporomandibular|\\btmj\\b',['temporal','mandible','lateral-pterygoid','masseter','temporalis'],'TMJ'],
];
for(const [p,k,l] of AL)term(p,k.filter(x=>byK[x]),l);
const RW=[['feet|foot|plantar|toes?|hallux|arch(?:es)?\\s+of\\s+the\\s+foot|pedal',['Foot']],['leg|crural|calf|shin|tibial',['Leg']],['thigh|femoral|femur',['Thigh']],
 ['hip|gluteal|buttocks?|pelvic\\s+girdle',['Hip']],['hand|hands|palm|palmar|fingers?|digits|thumb|manus',['Hand']],['forearm|antebrachi\\w*',['Forearm']],
 ['upper\\s+arm|brachium|brachial|arm',['Arm']],['shoulder|scapular?|pectoral\\s+girdle|axilla\\w*',['Shoulder']],
 ['back|dorsal\\s+region|lumbar|spine|spinal',['Back']],['thorax|thoracic|chest|ribs?|pectoral',['Thorax']],['abdomen|abdominal|inguinal',['Abdomen']],
 ['pelvis|pelvic|perine\\w*',['Pelvis']],['head|face|facial|skull|cranial|scalp',['Head']],['neck|cervical|hyoid|larynx',['Neck']],
 ['upper\\s+limb|upper\\s+extremity',['Shoulder','Arm','Forearm','Hand']],['lower\\s+limb|lower\\s+extremity',['Hip','Thigh','Leg','Foot']],
 ['axial\\s+(?:skeleton|muscles)',['Head','Neck','Back','Thorax','Abdomen','Pelvis']]];
const RTERMS=RW.map(([p,r])=>({re:new RegExp('\\b(?:'+p+')\\b','i'),regions:r,label:p.split('|')[0].replace(/\\\\s\+/g,' ')}));
const LIMB=new Set(['Shoulder','Arm','Forearm','Hand','Hip','Thigh','Leg','Foot']);
function analyze(raw){
  const text=' '+String(raw||'').replace(/-\s*\n\s*/g,'').replace(/[‐-―]/g,'-').replace(/\s+/g,' ')+' ';
  const keys=new Set(),labels=[],regions=new Set();
  for(const t of TERMS){if(t.re.test(text)){let added=false;for(const k of t.keys)if(byK[k]&&!keys.has(k)){keys.add(k);added=true}if(added)labels.push(t.label)}}
  for(const t of RTERMS)if(t.re.test(text))for(const r of t.regions)regions.add(r);
  const low=text.toLowerCase();
  const sys={nerve:/\bnerves?\b|plexus|innervat|\bneuro|spinal\s+cord/.test(low)||[...keys].some(k=>byK[k][0].kind==='nerve'),
    vessel:/arter|\bveins?\b|venous|blood\s+supply|vascular|circulat/.test(low)||[...keys].some(k=>isVes(byK[k][0].kind)),
    bone:/\bbones?\b|osteolog|skelet|joint|articulat|ligament|landmark/.test(low),muscle:/muscle|muscular|\boian\b|origin|insertion/.test(low)};
  return {keys,labels,regions,sys};
}
const NEAR={Head:['Skull'],Neck:['Neck','Vertebral column','Skull'],Back:['Vertebral column','Thorax'],Thorax:['Thorax','Vertebral column'],Abdomen:['Vertebral column','Hip'],Pelvis:['Hip','Vertebral column'],
 Shoulder:['Shoulder','Arm','Thorax'],Arm:['Arm','Shoulder','Forearm'],Forearm:['Forearm','Arm','Hand'],Hand:['Hand','Forearm'],Hip:['Hip','Thigh','Vertebral column'],Thigh:['Thigh','Hip','Leg'],Leg:['Leg','Thigh','Foot'],Foot:['Foot','Leg'],
 Skull:['Skull'],'Vertebral column':['Vertebral column']};
function applyAnalysis(an,fly=true){
  if(!an.keys.size&&!an.regions.size)return false;
  ST.sel=null;ST.hidden.clear();
  const sts=[];for(const k of an.keys)for(const st of byK[k])sts.push(st);
  const regs=new Set(an.regions);for(const st of sts)regs.add(st.region);
  const limbOnly=[...regs].every(r=>LIMB.has(r)||r==='Hip');
  const sideOK=st=>!limbOnly||!st.side||st.side==='R';
  ST.side='both';
  if(sts.length){
    const near=new Set();for(const r of regs)for(const n of (NEAR[r]||[r]))near.add(n);
    const ctx=ALL.filter(st=>(st.kind==='bone'||st.kind==='disc')&&near.has(st.region));
    isolate=new Set([...sts,...ctx].filter(sideOK).map(st=>st.id));
    if(an.sys.nerve)for(const st of ALL)if(st.kind==='nerve'&&regs.has(st.region)&&sideOK(st)&&!an.keys.size)isolate.add(st.id);
  }else{
    isolate=null;ST.region='custom';ST.cregions=[...new Set([...regs].flatMap(r=>[r,...(NEAR[r]||[]).filter(n=>['Skull','Vertebral column'].includes(n))]))];
    if(limbOnly)ST.side='R';
    ST.ly.bone=true;ST.ly.muscle=an.sys.muscle||!an.sys.bone;ST.ly.tendon=ST.ly.muscle;ST.ly.nerve=an.sys.nerve;ST.ly.vessel=an.sys.vessel;
  }
  ST.xray=an.sys.nerve||an.sys.vessel||sts.some(s=>s.kind==='nerve'||isVes(s.kind));
  ST.opacity=sts.some(s=>s.kind==='nerve'||isVes(s.kind))&&sts.some(s=>s.kind==='muscle')?.7:1;
  applyVis();syncDrawer();
  if(fly){
    const bb=new THREE.Box3();for(const st of ALL)if(st.meshes[0]&&st.meshes[0].visible)for(const m of st.meshes)bb.expandByObject(m);
    if(!bb.isEmpty()){const c=bb.getCenter(new THREE.Vector3()),r=bb.getSize(new THREE.Vector3()).length()/2;
      const mus=sts.filter(s=>s.kind==='muscle'&&s.ex&&s.ex.length()>1);let d=new THREE.Vector3();
      for(const s of mus)d.add(s.ex.clone().normalize());if(d.length()<.35*Math.max(1,mus.length))d.set(0,-1,0);else d.normalize();
      if(Math.abs(d.z)>.8)d.set(0,-.4,d.z>0?1:-1).normalize();
      flyTo(c,dirToWorld(d),Math.max(200,r/Math.tan(camera.fov*Math.PI/360)*1.05));}
  }
  return true;
}
/* --- decks --- */
async function openPdf(file){
  if(!window.pdfjsLib){await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js');await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js')}
  pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  const doc=await pdfjsLib.getDocument({data:new Uint8Array(await file.arrayBuffer()),isEvalSupported:false}).promise;
  const texts=[];
  for(let p=1;p<=doc.numPages;p++){const pg=await doc.getPage(p);const tc=await pg.getTextContent();texts.push(tc.items.map(i=>i.str+(i.hasEOL?'\n':' ')).join(''));if(p%5===0){lecStatus(`Reading slide ${p} of ${doc.numPages}…`)}}
  return {name:file.name,n:doc.numPages,texts,async render(i,box){
    const pg=await doc.getPage(i+1);const v1=pg.getViewport({scale:1});const w=Math.max(320,box.clientWidth||600);const dpr=Math.min(2,window.devicePixelRatio||1);
    const vp=pg.getViewport({scale:w*dpr/v1.width});const c=document.createElement('canvas');c.width=Math.round(vp.width);c.height=Math.round(vp.height);c.style.width='100%';c.style.height='auto';
    box.style.aspectRatio=v1.width+' / '+v1.height;box.innerHTML='';box.appendChild(c);await pg.render({canvasContext:c.getContext('2d'),viewport:vp}).promise}};
}
async function openPptx(file){
  if(!window.JSZip)await loadScript('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js');
  const zip=await JSZip.loadAsync(file);const XP=new DOMParser();const xml=async p=>{const f=zip.file(p);return f?XP.parseFromString(await f.async('text'),'application/xml'):null};
  const RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
  const rels=p=>xml(p).then(d=>{const o={};if(d)for(const r of d.getElementsByTagName('Relationship'))o[r.getAttribute('Id')]=r.getAttribute('Target');return o});
  const pres=await xml('ppt/presentation.xml');const prel=await rels('ppt/_rels/presentation.xml.rels');
  const ids=[...pres.getElementsByTagNameNS('*','sldId')].map(e=>e.getAttributeNS(RNS,'id'));
  const slides=[];
  for(const id of ids){const path='ppt/'+prel[id].replace(/^\.?\/?(ppt\/)?/,'');const d=await xml(path);if(!d)continue;
    const base=path.replace(/[^/]+$/,''),fn=path.split('/').pop();const srel=await rels(base+'_rels/'+fn+'.rels');
    let title='';const bullets=[];
    for(const sp of d.getElementsByTagNameNS('*','sp')){const ph=sp.getElementsByTagNameNS('*','ph')[0];const isT=ph&&/title/i.test(ph.getAttribute('type')||'');
      for(const p of sp.getElementsByTagNameNS('*','p')){const t=[...p.getElementsByTagNameNS('*','t')].map(x=>x.textContent).join('').trim();if(!t)continue;if(isT&&!title)title=t;else bullets.push(t)}}
    const imgs=[];for(const b of d.getElementsByTagNameNS('*','blip')){const r=b.getAttributeNS(RNS,'embed');const tg=srel[r];if(!tg)continue;
      const ip=tg.startsWith('/')?tg.slice(1):(base+tg).split('/').reduce((a,x)=>{x==='..'?a.pop():a.push(x);return a},[]).join('/');const f=zip.file(ip);
      if(f&&/\.(png|jpe?g|gif|webp|svg)$/i.test(ip)&&imgs.length<2)imgs.push(URL.createObjectURL(await f.async('blob')))}
    slides.push({title,bullets,imgs});
  }
  return {name:file.name,n:slides.length,texts:slides.map(s=>s.title+'\n'+s.bullets.join('\n')),render:(i,box)=>cardSlide(slides[i],box)};
}
function cardSlide(s,box){box.style.aspectRatio='16 / 9';box.innerHTML=`<div class="pp">${s.imgs&&s.imgs.length?s.imgs.map(u=>`<img src="${u}" alt="">`).join(''):''}<h4>${esc(s.title||'Untitled slide')}</h4><ul>${s.bullets.slice(0,12).map(b=>`<li>${esc(b)}</li>`).join('')}</ul></div>`}
async function openImage(file){const u=URL.createObjectURL(file);return {name:file.name,n:1,texts:[file.name.replace(/\.[^.]+$/,'').replace(/[_-]+/g,' ')],render:(i,box)=>{box.style.aspectRatio='';box.innerHTML=`<img src="${u}" alt="Slide" style="width:100%;display:block">`}}}
const SAMPLE={name:'Sample — KNES 259 week 7',n:6,slides:[
 {title:'The foot: plantar muscles in four layers',bullets:['Layer 1: abductor hallucis, flexor digitorum brevis, abductor digiti minimi','Layer 2: quadratus plantae and the lumbricals','Layer 3: flexor hallucis brevis, adductor hallucis','Layer 4: plantar and dorsal interossei','All supplied by the medial and lateral plantar nerves (tibial nerve)'],imgs:[]},
 {title:'Rotator cuff (SITS)',bullets:['Stabilises the glenohumeral joint','Supraspinatus initiates abduction','Infraspinatus and teres minor laterally rotate','Subscapularis medially rotates'],imgs:[]},
 {title:'Brachial plexus — terminal branches',bullets:['Roots C5–T1 → trunks → divisions → cords','Musculocutaneous, axillary, radial, median and ulnar nerves','Know one motor test for each'],imgs:[]},
 {title:'Knee joint',bullets:['Modified hinge synovial joint','Femur, tibia and patella articulate','Popliteus unlocks the knee'],imgs:[]},
 {title:'Posterior compartment of the thigh',bullets:['The hamstrings flex the knee and extend the hip','Innervated by the sciatic nerve'],imgs:[]},
 {title:'Action potentials',bullets:['Resting membrane potential about −70 mV','Voltage-gated Na⁺ channels open → depolarisation','K⁺ efflux → repolarisation'],imgs:[]}]};
function sampleDeck(){return {name:SAMPLE.name,n:SAMPLE.n,texts:SAMPLE.slides.map(s=>s.title+'\n'+s.bullets.join('\n')),render:(i,box)=>cardSlide(SAMPLE.slides[i],box),sample:true}}
/* saved lectures (this browser only) */
function idb(){return new Promise((res,rej)=>{const r=indexedDB.open('kl-lectures',1);r.onupgradeneeded=()=>r.result.createObjectStore('decks',{keyPath:'name'});r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
async function saveDeck(file){try{const db=await idb();db.transaction('decks','readwrite').objectStore('decks').put({name:file.name,file,added:Date.now()})}catch(e){}}
async function listDecks(){try{const db=await idb();return await new Promise(res=>{const q=db.transaction('decks').objectStore('decks').getAll();q.onsuccess=()=>res((q.result||[]).sort((a,b)=>b.added-a.added));q.onerror=()=>res([])})}catch(e){return []}}
async function delDeck(name){try{const db=await idb();db.transaction('decks','readwrite').objectStore('decks').delete(name)}catch(e){}}
async function openFile(file,save=true){
  const ext=(file.name.split('.').pop()||'').toLowerCase();lecStatus('Opening '+file.name+'…');
  try{let d;
    if(ext==='pdf')d=await openPdf(file);else if(ext==='pptx')d=await openPptx(file);else if(/^(png|jpe?g|webp|gif)$/.test(ext))d=await openImage(file);
    else{lecStatus('That file type isn’t supported yet. Upload a PDF, a PowerPoint (.pptx) or a slide image. Older .ppt files: save them as PDF first.');return}
    if(!d.n){lecStatus('No slides were found in that file.');return}
    if(save)saveDeck(file);LEC.deck=d;LEC.i=0;LEC.status='';enterLecture();
  }catch(e){lecStatus('That file could not be read. If it’s password-protected or very large, export it to PDF and try again.')}
}
function lecStatus(t){LEC.status=t;const el=$('#lecStatus');if(el)el.textContent=t}
function enterLecture(){$('.app').classList.add('lecture');setLook('atlas');setExplode(0);ST.labels=true;$('#bLabels').setAttribute('aria-pressed',true);renderLecture();showSlide(LEC.i)}
function setLook(l){ST.look=l;$('#bLook').setAttribute('aria-pressed',l==='cadaver');applyLook()}
async function showSlide(i){
  const d=LEC.deck;if(!d)return;LEC.i=Math.max(0,Math.min(d.n-1,i));
  const box=$('#slideBox');$('#slideN').textContent=`Slide ${LEC.i+1} of ${d.n}`;$('#sPrev').disabled=LEC.i===0;$('#sNext').disabled=LEC.i===d.n-1;
  try{await d.render(LEC.i,box)}catch(e){box.innerHTML='<p class="hint" style="padding:16px">This slide couldn’t be drawn.</p>'}
  LEC.an=analyze(d.texts[LEC.i]||'');
  const applied=LEC.follow?applyAnalysis(LEC.an):false;renderMatch(applied);
}
function renderMatch(applied){
  const an=LEC.an,el=$('#lecMatch');if(!el)return;
  const sts=[...an.keys].map(k=>byK[k][0]);
  if(!an.keys.size&&!an.regions.size){el.innerHTML=`<div class="note" style="border-left-color:var(--line)"><b style="color:var(--muted)">Nothing to show</b>No anatomy terms on this slide, so the model stays as it was. Type a focus below if you want something specific.</div>`;return}
  el.innerHTML=`<div class="kick" style="margin-bottom:6px">${applied?'Model is showing':'Found on this slide'}${an.regions.size?' · '+[...an.regions].join(', '):''}</div>
   <div class="links">${sts.slice(0,40).map(s=>`<button class="lnk${s.kind==='nerve'?' nv':''}" data-lk="${s.k}">${esc(s.name)}</button>`).join('')||'<span class="hint">Whole region shown</span>'}</div>
   ${an.labels.length?`<p class="hint" style="margin:8px 0 0">Matched: ${an.labels.slice(0,10).map(esc).join(' · ')}</p>`:''}
   ${!applied?'<div class="acts"><button class="btn pri" id="lecApply">Show this on the model</button></div>':''}`;
  el.querySelectorAll('[data-lk]').forEach(b=>b.onclick=()=>{const st=byK[b.dataset.lk].find(s=>s.side!=='L')||byK[b.dataset.lk][0];if(isolate)isolate.add(st.id);select(st.id,{reveal:!isolate});focus(st)});
  const ap=$('#lecApply');if(ap)ap.onclick=()=>{applyAnalysis(LEC.an);renderMatch(true)};
}
function updateLecSel(){const el=$('#lecSel');if(!el)return;const st=S[ST.sel];if(!st){el.innerHTML='';return}
  let line='';if(st.kind==='muscle'){const m=C.MUS[st.k];line=`<b>Action:</b> ${esc(m[2])}<br><b>Nerve:</b> ${esc(m[3])}`}else if(st.kind==='nerve')line=esc(C.NER[st.k][2]);else if(isVes(st.kind))line=esc((C.VES[st.k]||[])[2]||'');else if(C.BON[st.k])line=esc(C.BON[st.k][0]);else if(C.TEN[st.k])line=esc(C.TEN[st.k][0]);
  el.innerHTML=`<div class="scen" style="margin-top:12px"><div class="kick">Selected · ${esc(KINDW[st.kind])}</div><div style="font:700 1.15rem var(--f-display);margin:2px 0 6px">${esc(displayName(st))}</div><div style="font-size:14px">${line}</div><div class="acts" style="margin-top:8px"><button class="btn" id="lsF">Full details</button></div></div>`;
  $('#lsF').onclick=()=>setTab('E');
}
async function renderLecture(){
  const d=LEC.deck;
  if(!d){
    pane.innerHTML=`<div class="kick">Side-by-side with your slides</div><h2 class="name">Lecture mode</h2>
    <p class="hint" style="margin:4px 0 12px">Upload your instructor’s slides. As you move through them, the model rebuilds itself for each slide — a slide about the foot shows the foot bones, plantar muscles, nerves and vessels; the next slide moves the model on.</p>
    <label class="drop" id="drop" for="lecFile"><strong>Choose a lecture file</strong><span>PDF, PowerPoint (.pptx) or a slide image · or drop it here</span></label>
    <input type="file" id="lecFile" accept=".pdf,.pptx,image/*" hidden>
    <p class="hint" id="lecStatus" style="margin:10px 0 0" aria-live="polite">${esc(LEC.status)}</p>
    <div class="acts"><button class="btn" id="lecSample">Try a sample lecture</button></div>
    <div id="lecSaved"></div>
    <p class="hint" style="margin-top:14px">Files are read inside your browser and saved only on this device so you can reopen them. Nothing is uploaded anywhere.</p>`;
    const inp=$('#lecFile');inp.onchange=()=>{if(inp.files[0])openFile(inp.files[0])};
    const dr=$('#drop');dr.ondragover=e=>{e.preventDefault();dr.classList.add('over')};dr.ondragleave=()=>dr.classList.remove('over');dr.ondrop=e=>{e.preventDefault();dr.classList.remove('over');const f=e.dataTransfer.files[0];if(f)openFile(f)};
    $('#lecSample').onclick=()=>{LEC.deck=sampleDeck();LEC.i=0;enterLecture()};
    const saved=await listDecks();const sv=$('#lecSaved');
    if(sv&&saved.length){sv.innerHTML=`<div class="kick" style="margin:16px 0 4px">Your lectures on this device</div>${saved.map((x,i)=>`<div class="it" style="cursor:default"><button class="lnk" data-op="${i}" style="border:0;background:transparent;padding:0;text-align:left">${esc(x.name)}</button><button class="lnk" data-del="${i}">Remove</button></div>`).join('')}`;
      sv.querySelectorAll('[data-op]').forEach(b=>b.onclick=()=>openFile(saved[+b.dataset.op].file,false));
      sv.querySelectorAll('[data-del]').forEach(b=>b.onclick=async()=>{await delDeck(saved[+b.dataset.del].name);renderLecture()});}
    return;
  }
  pane.innerHTML=`<div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><div class="kick" style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(d.name)}</div><button class="lnk" id="lecClose">Close lecture</button></div>
   <div class="slide" id="slideBox"></div>
   <div class="snav"><button class="btn" id="sPrev" aria-label="Previous slide">← Prev</button><span class="n" id="slideN"></span><button class="btn pri" id="sNext" aria-label="Next slide">Next →</button></div>
   <label class="hint" style="display:flex;gap:8px;align-items:center;cursor:pointer"><input type="checkbox" id="lecFollow" ${LEC.follow?'checked':''}> Model follows the slides</label>
   <div id="lecMatch" class="match"></div>
   <form id="lecFocus" class="acts" style="flex-wrap:nowrap"><input class="search" id="lecQ" placeholder="Focus the model on… e.g. ankle, rotator cuff" autocomplete="off"><button class="btn" type="submit">Show</button></form>
   <div id="lecSel"></div>`;
  $('#sPrev').onclick=()=>showSlide(LEC.i-1);$('#sNext').onclick=()=>showSlide(LEC.i+1);
  $('#lecFollow').onchange=e=>{LEC.follow=e.target.checked;if(LEC.follow)showSlide(LEC.i);else renderMatch(false)};
  $('#lecClose').onclick=()=>{LEC.deck=null;isolate=null;ST.region='all';ST.side='both';applyVis();syncDrawer();$('.app').classList.remove('lecture');renderLecture();view('front')};
  $('#lecFocus').onsubmit=e=>{e.preventDefault();const q=$('#lecQ').value;const an=analyze(q);if(applyAnalysis(an)){LEC.an=an;renderMatch(true)}else toast('No anatomy recognised in “'+q+'”')};
  updateLecSel();
}
document.addEventListener('keydown',e=>{if(ST.tab!=='C'||!LEC.deck)return;const t=e.target.tagName;if(t==='INPUT'||t==='TEXTAREA')return;
  if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();showSlide(LEC.i+1)}else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();showSlide(LEC.i-1)}});
