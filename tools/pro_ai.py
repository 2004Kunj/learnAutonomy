"""AI features (Claude via the artifact `sample` capability, on the viewer's own account; everything degrades to the offline app)."""
p = 'site/index.html'; s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

CSS = r"""
/* ---- AI ---- */
.ai{display:none!important}
body.ai-on .ai{display:revert!important}
body.ai-on .tabs .ai{display:block!important}
.aibox{margin-top:12px;border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:linear-gradient(180deg,color-mix(in srgb,var(--accent) 6%,var(--panel)),var(--panel));font-size:14px}
.aibox .kick{display:flex;align-items:center;gap:6px}
.aitext p{margin:6px 0}.aitext ul{margin:6px 0;padding-left:1.2em}.aitext li{margin:2px 0}
.spark{width:14px;height:14px;stroke:var(--accent);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;vertical-align:-2px}
.chat{display:flex;flex-direction:column;gap:10px;margin-top:10px}
.msg{max-width:92%;padding:9px 12px;border-radius:12px;font-size:14px;line-height:1.5}
.msg.u{align-self:flex-end;background:var(--accent);color:var(--accent-ink);border-bottom-right-radius:4px}
.msg.a{align-self:flex-start;background:var(--soft);border:1px solid var(--line);border-bottom-left-radius:4px}
.msg.a .tool{font:500 11px var(--f-mono);color:var(--muted);margin-top:4px}
.composer{display:flex;gap:6px;margin-top:12px;position:sticky;bottom:-28px;background:var(--panel);padding:8px 0 4px}
.composer textarea{flex:1;min-width:0;resize:none;font:14px/1.4 var(--f-body);padding:9px 11px;border-radius:10px;border:1px solid var(--line);background:var(--soft);color:var(--ink);max-height:140px}
.sugg{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.sugg button{border:1px solid var(--line);background:transparent;border-radius:99px;padding:5px 10px;font:500 12.5px var(--f-body);color:var(--ink);cursor:pointer;text-align:left}
.sugg button:hover{border-color:var(--accent)}
"""
rep("/* ---- professional pass ---- */", CSS + "\n/* ---- professional pass ---- */")
SPARK = '<svg class="spark" viewBox="0 0 24 24"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>'

# Tutor tab
rep('''      <button role="tab" id="tS" aria-selected="false">Study</button>''',
    '''      <button role="tab" id="tS" aria-selected="false">Study</button>
      <button role="tab" id="tA" aria-selected="false" class="ai">Tutor</button>''')
rep("for(const [k,id] of [['E','tE'],['I','tI'],['L','tL'],['C','tC'],['S','tS']])", "for(const [k,id] of [['E','tE'],['I','tI'],['L','tL'],['C','tC'],['S','tS'],['A','tA']])")
rep("$('#tS').onclick=()=>setTab('S');", "$('#tS').onclick=()=>setTab('S');$('#tA').onclick=()=>setTab('A');")
rep("else if(ST.tab==='S')renderStudy();else renderLab()}", "else if(ST.tab==='S')renderStudy();else if(ST.tab==='A')renderTutor();else renderLab()}")

# core AI module, placed before the graphics-quality section
AI = r"""/* ---------- AI: Claude on the viewer's own account (optional — the app works fully without it) ---------- */
const AI={sample:null,limits:null,off:false,chat:LS.get('kl.chat',[]),ctl:null,busy:false};
const SPARK='""" + SPARK + r"""';
(async()=>{try{if(!window.claude||typeof claude.use!=='function')return;const sm=await claude.use('sample');if(!sm)return;
  AI.sample=sm;AI.limits=await sm.limits().catch(()=>null);document.body.classList.add('ai-on');
  if(ST.tab==='E'||ST.tab==='S'||ST.tab==='C')renderPane()}catch(e){}})();
function aiErr(e){const c=e&&e.code;
  if(['not_granted','sampling_disabled','not_declared','capability_disabled','capability_removed'].includes(c)){AI.off=true;document.body.classList.remove('ai-on');if(ST.tab==='A')setTab('E');return 'AI isn’t available on this account or was not allowed. Everything else still works.'}
  if(c==='rate_limited')return 'Too many AI requests right now — wait a minute and try again.';if(c==='session_expired')return 'Sign in to Claude again to use the AI features.';
  if(c==='refused')return 'Claude couldn’t answer that. Try rephrasing.';if(c==='prompt_too_large')return 'That was too long — ask about less at once.';if(c==='invalid_json')return 'The AI reply was malformed — try again.';
  if(c==='cancelled')return '';return 'The AI request failed — try again.'}
function aiOK(){return AI.sample&&!AI.off}
/* tiny safe markdown: paragraphs, bullets, bold */
function md(t){const out=[];let list=null;for(const raw of String(t).split('\n')){const l=raw.trimEnd();const b=l.match(/^\s*[-*•]\s+(.*)/)||l.match(/^\s*\d+[.)]\s+(.*)/);
  const fmt=x=>esc(x).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/(^|\W)\*(?!\s)(.+?)\*(?=\W|$)/g,'$1<em>$2</em>').replace(/^#{1,4}\s*/,'');
  if(b){if(!list){list=[];out.push(list)}list.push('<li>'+fmt(b[1])+'</li>')}else{list=null;if(l.trim())out.push('<p>'+fmt(l)+'</p>')}}
  return out.map(x=>Array.isArray(x)?'<ul>'+x.join('')+'</ul>':x).join('')}
/* facts the app already holds about a structure, so Claude works from the course notes */
function factsFor(k){const st=byK[k]&&byK[k][0];if(!st)return '';const L=[`${st.name} (${KINDW[st.kind]||st.kind}, ${st.region})`];
  const m=C.MUS[k];if(m)L.push(`Origin: ${m[0]}. Insertion: ${m[1]}. Action: ${m[2]}. Innervation: ${m[3]}. Note: ${m[5]||''}`);
  const n=C.NER[k];if(n){L.push(`Roots: ${n[0]}. Course: ${n[1]}. Motor: ${n[2]}. Clinical: ${n[3]}`);const sup=(SUPPLIES[k]||[]).filter(x=>byK[x]).map(nameOfK);if(sup.length)L.push('Supplies: '+sup.join(', '))}
  const v=C.VES[k];if(v)L.push(`Begins: ${v[0]}. Ends: ${v[1]}. Supplies/drains: ${v[2]}. Clinical: ${v[3]}`);
  const g=LIG[k];if(g)L.push(`Joint: ${g[0]}. Attaches: ${g[1]}. Function: ${g[2]}. ${g[3]}`);
  if(C.BON[k])L.push(C.BON[k].join(' '));if(C.TEN[k])L.push(C.TEN[k].join(' '));if(MN[k])L.push('Mnemonic: '+MN[k]);
  if(DEFS&&DEFS[k])L.push('Reference: '+firstSentences(DEFS[k][0],3,500));return L.join('\n')}
function resolveName(nm){nm=String(nm||'').trim();if(!nm)return null;const low=nm.toLowerCase().replace(/^(the\s+)?(left|right)\s+/,'');
  const side=/\bleft\b/i.test(nm)?'L':/\bright\b/i.test(nm)?'R':'R';
  let st=ALL.find(s=>s.name.toLowerCase()===low)||ALL.find(s=>s.name.toLowerCase().replace(/ (muscle|nerve|artery|vein|ligament)$/,'')===low.replace(/ (muscle|nerve|artery|vein|ligament)$/,''));
  if(!st){const it=palItems(low)[0];st=it&&it.st}
  if(!st)return null;return S[sameSide(st.k,side)]||st}
/* Explore: "Explain with AI" */
function aiExplain(st){const box=$('#aiExplain');if(!box||!aiOK())return;box.hidden=false;const out=box.querySelector('.aitext');out.innerHTML='<p class="hint">Thinking…</p>';
  const prompt=`You are an anatomy tutor for a university kinesiology course (KNES 259, Human Anatomy & Physiology I). Explain the structure below to a student preparing for a cadaver lab practical.
Use the course facts given; do not contradict them. Write at most 170 words in short Markdown: one sentence on what it is, then bullets for
- how to find and identify it on a cadaver (landmarks, neighbours, depth, fibre direction),
- what it does in movement,
- one clinical or injury link,
- one memory trick.
FACTS:\n${factsFor(st.k)}`;
  AI.sample(prompt,{onText:({text})=>{out.innerHTML=md(text)},cache:{gcTime:6*3600e3}}).catch(e=>{out.innerHTML=`<p class="hint">${esc(e.text?'':aiErr(e))}</p>`+(e.text?md(e.text):'')})}
/* Study: explain an answer */
function aiWhy(q){const box=$('#aiWhy');if(!box||!aiOK())return;box.hidden=false;const out=box.querySelector('.aitext');out.innerHTML='<p class="hint">Thinking…</p>';
  const picked=q.opts&&q.pick!=null?q.opts[q.pick].t:(q.last?q.last.name:'');
  const prompt=`A kinesiology anatomy student answered a quiz question. Explain in at most 110 words why the correct answer is right${picked&&!q.ok?' and why their answer was wrong':''}, and give one tip to remember it. Plain short Markdown.
Question: ${q.prompt}
Correct answer: ${nameOfK(q.k)}${q.opts?' — '+(q.opts.find(o=>o.ok)||{}).t:''}
${picked&&!q.ok?'Student answered: '+picked:''}
Facts:\n${factsFor(q.k)}`;
  AI.sample(prompt,{onText:({text})=>{out.innerHTML=md(text)},cache:{gcTime:3600e3}}).catch(e=>{out.innerHTML=`<p class="hint">${esc(aiErr(e))}</p>`})}
/* Study: AI clinical cases → tap the answer on the model */
async function aiCases(btn){if(!aiOK())return;const pool=poolKeys(SCFG.reg,null).filter(k=>['muscle','nerve','vessel','ligament'].includes(kindOfK(k)));
  if(pool.length<4){toast('Pick a larger region first');return}
  const list=shuffle(pool).slice(0,60);btn.disabled=true;const old=btn.innerHTML;btn.innerHTML='<strong>Writing cases…</strong><span>Claude is writing five clinical scenarios for you.</span>';
  try{const r=await AI.sample.json(`Write 5 short clinical bellringer cases for a kinesiology anatomy cadaver lab. Each case describes a patient (mechanism of injury, signs, what they cannot do) whose problem points to ONE structure from the list, and ends with a question like "Find the injured muscle." Do not name the structure. Vary the structures.
Reply with only a JSON array of 5 objects: {"key": one key from the list, "case": the scenario (2-3 sentences), "hint": a region hint, "why": one sentence explaining the answer}.
LIST (key: name — facts):\n`+list.map(k=>`${k}: ${nameOfK(k)} — ${factsFor(k).split('\n').slice(1,2).join(' ').slice(0,160)}`).join('\n'),{cache:false});
    const items=(Array.isArray(r)?r:[]).filter(x=>x&&byK[x.key]&&x.case).slice(0,5);
    if(!items.length){toast('The AI didn’t return usable cases — try again','bad');return}
    startQuiz('find',items.map(x=>{const q=mkQ(x.key,'find',{});q.prompt=String(x.case);q.short='Find the structure in the case';q.aiWhy=String(x.why||'');q.hint=String(x.hint||'');return {k:x.key,q}}),{title:'AI clinical cases'})}
  catch(e){const m=aiErr(e);if(m)toast(m,'bad')}finally{btn.disabled=false;btn.innerHTML=old}}
/* Lecture: read the slide picture with Claude */
async function aiReadSlide(btn){const d=LEC.deck;if(!d||!aiOK())return;const i=LEC.i;
  if(!(AI.limits&&AI.limits.images)){toast('Image reading isn’t available here','bad');return}
  let blob;try{blob=await d.imageBlob(i)}catch(e){}const blobs=(Array.isArray(blob)?blob:(blob?[blob]:[])).slice(0,AI.limits.images.maxCount||3);
  if(!blobs.length){toast('This slide has no picture to read');return}
  btn.disabled=true;visStatus('Claude is reading the slide picture…');
  try{const r=await AI.sample.json(`This is a slide from an anatomy lecture. List every anatomical structure that is labelled or clearly named in the picture (muscles, bones, ligaments, nerves, arteries, veins), using full standard English names (expand abbreviations like "a." = artery, "n." = nerve, "m." = muscle). Also say which view it shows if obvious.
Reply with only JSON: {"structures": ["name", ...], "view": "anterior"|"posterior"|"lateral"|"medial"|"superior"|"inferior"|null}.
Slide text for context:\n${(d.texts[i]||'').slice(0,1500)}`,{images:blobs,cache:{gcTime:24*3600e3}});
    const names=(r&&Array.isArray(r.structures)?r.structures:[]).map(String).slice(0,80);
    if(LEC.i!==i)return;const before=new Set(LEC.an.keys);const an=analyze((d.texts[i]||'')+'\n'+(OCR.cache.get(d.name+'#'+i)||'')+'\n'+names.join('\n')+(r&&r.view?'\n'+r.view+' view':''));
    for(const it of an.items)if(it.keys.length&&!it.keys.some(k=>before.has(k)))it.src='ai';
    const extra=an.items.filter(it=>it.src==='ai').length;LEC.an=an;
    visStatus(`Claude read ${names.length} label${names.length===1?'':'s'} — ${extra} new structure${extra===1?'':'s'} added to the checklist.`);
    if(LEC.follow){applyAnalysis(LEC.an);renderMatch(true)}else renderMatch(false)}
  catch(e){visStatus(aiErr(e)||'Stopped.')}finally{btn.disabled=false}}
/* Tutor chat with tools that drive the 3D model */
const TUTOR_RULES=()=>`You are the built-in anatomy tutor of "Anatomy Lab", a 3D study app for the university course KNES 259 (Human Anatomy & Physiology I, kinesiology). The student sees a 3D human model beside this chat.
- Teach clearly and accurately at undergraduate level; be concise (usually under 160 words) and use short Markdown (bullets, **bold** key terms).
- Use the tools to SHOW structures on the model whenever you mention specific ones, and to read the app's course notes (prefer those facts).
- Quiz the student when they ask to practise: ask one question at a time and wait for their answer.
- Never invent structures; if unsure, say so. This is a study aid, not medical advice.
Current app state:
${ST.sel&&S[ST.sel]?'Selected structure: '+titleName(S[ST.sel])+'\n'+factsFor(S[ST.sel].k):'Nothing selected.'}
${LEC.deck?'Lecture slide '+(LEC.i+1)+' of '+LEC.deck.n+' text: '+(LEC.deck.texts[LEC.i]||'').slice(0,1200):''}
${(()=>{const w=weakList(6);return w.length?'Student’s weakest structures: '+w.map(x=>nameOfK(x.k)).join(', '):''})()}`;
const TUTOR_TOOLS=()=>[
 {name:'show_on_model',description:'Highlight structures on the 3D model. Pass exact or common names; mode "isolate" shows only them, "select" highlights the first and zooms to it. Returns which names were found.',
  inputSchema:{type:'object',properties:{names:{type:'array',items:{type:'string'}},mode:{type:'string',enum:['select','isolate']}},required:['names']},
  execute:({names,mode})=>{const found=[],missing=[];for(const n of [].concat(names||[]).slice(0,20)){const st=resolveName(n);st?found.push(st):missing.push(String(n))}
    if(!found.length)throw new Error('none of these are in the model: '+missing.join(', '));
    if(found.some(s=>s.kind==='nerve'||isVes(s.kind))){ST.xray=true;for(const s of found)ST.ly[layerOf(s)]=true}
    if(mode==='isolate'&&found.length>1){isolate=new Set(found.map(s=>s.id));ST.sel=found[0].id;applyVis();syncDrawer();view(lastViewName())}
    else{for(const s of found)ensureShown(s);ST.sel=found[0].id;applyVis();focus(found[0])}
    return {shown:found.map(s=>titleName(s)),notFound:missing}}},
 {name:'get_course_notes',description:'Read the app’s course notes for one structure (origin, insertion, action, innervation, clinical notes, mnemonic). Returns text.',
  inputSchema:{type:'object',properties:{name:{type:'string'}},required:['name']},
  execute:({name})=>{const st=resolveName(name);if(!st)throw new Error('not in the model: '+name);return factsFor(st.k)}}];
function renderTutor(){
  if(!aiOK()){pane.innerHTML='<div class="kick">Tutor</div><h2 class="name">AI tutor unavailable</h2><p class="hint">The tutor uses Claude on your own account. It isn’t available in this view.</p>';return}
  const sel=ST.sel&&S[ST.sel];const sg=[sel?`Quiz me on the ${sel.name.toLowerCase()}`:'Quiz me on the rotator cuff',sel?`How do I find the ${sel.name.toLowerCase()} on a cadaver?`:'How do I tell the median, ulnar and radial nerves apart?',
    'Show me the muscles of the anterior forearm','What’s the difference between the brachial plexus cords?',...(LEC.deck?['Explain this lecture slide']:[]),...(weakList(3).length?['Help me with my weak spots']:[])];
  pane.innerHTML=`<div class="kick">${SPARK} AI tutor · Claude</div><h2 class="name">Ask anything</h2>
   <p class="hint" style="margin:2px 0 0">It can point to structures on the model and quiz you. Uses your Claude account; check answers against your course notes.</p>
   <div class="chat" id="chat">${AI.chat.map(m=>`<div class="msg ${m.role==='user'?'u':'a'}">${m.role==='user'?esc(m.content):md(m.content)}</div>`).join('')}</div>
   ${AI.chat.length?'':`<div class="sugg">${sg.map(t=>`<button data-sg="${esc(t)}">${esc(t)}</button>`).join('')}</div>`}
   <div class="composer"><textarea id="chatIn" rows="1" placeholder="Ask about any muscle, nerve, vessel or ligament…" aria-label="Message"></textarea><button class="btn pri" id="chatGo">${AI.busy?'Stop':'Send'}</button></div>
   ${AI.chat.length?'<div class="acts" style="margin-top:4px"><button class="btn" id="chatClear">New conversation</button></div>':''}`;
  const inp=$('#chatIn');inp.oninput=()=>{inp.style.height='auto';inp.style.height=Math.min(140,inp.scrollHeight)+'px'};
  inp.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendTutor(inp.value)}};
  $('#chatGo').onclick=()=>{if(AI.busy){AI.ctl&&AI.ctl.abort()}else sendTutor(inp.value)};
  pane.querySelectorAll('[data-sg]').forEach(b=>b.onclick=()=>sendTutor(b.dataset.sg));
  const c=$('#chatClear');if(c)c.onclick=()=>{AI.chat=[];LS.set('kl.chat',[]);renderTutor()};
  pane.scrollTop=pane.scrollHeight}
async function sendTutor(text){text=String(text||'').trim();if(!text||AI.busy||!aiOK())return;
  AI.chat.push({role:'user',content:text});AI.busy=true;renderTutor();
  const chat=$('#chat');const bub=document.createElement('div');bub.className='msg a';bub.innerHTML='<p class="hint">Thinking…</p>';chat.appendChild(bub);pane.scrollTop=pane.scrollHeight;
  const tools=AI.limits&&AI.limits.tools?TUTOR_TOOLS().map(t=>({...t,execute:(a)=>{const r=t.execute(a||{});const n=document.createElement('div');n.className='tool';n.textContent=t.name==='show_on_model'?'↳ showing on the model':'↳ reading course notes';bub.appendChild(n);return r}})):undefined;
  AI.ctl=new AbortController();const turns=AI.chat.slice(-12);
  try{const {text:ans}=await AI.sample([{role:'user',content:TUTOR_RULES()},...turns],{cache:false,signal:AI.ctl.signal,tools,onText:({text})=>{bub.innerHTML=md(text);pane.scrollTop=pane.scrollHeight}});
    AI.chat.push({role:'assistant',content:ans})}
  catch(e){const m=aiErr(e);if(e.text)AI.chat.push({role:'assistant',content:e.text+(m?'\n\n_'+m+'_':'')});else if(m)AI.chat.push({role:'assistant',content:'_'+m+'_'});if(!AI.chat.length||AI.chat[AI.chat.length-1].role==='user')AI.chat.pop()}
  finally{AI.busy=false;AI.chat=AI.chat.slice(-30);LS.set('kl.chat',AI.chat);if(ST.tab==='A')renderTutor()}}

/* ---------- graphics quality ---------- */"""
rep("/* ---------- graphics quality ---------- */", AI)

# Explore: Explain with AI
rep('''   <div class="acts"><button class="btn pri" id="aF">Zoom to it</button>''',
    '''   <button class="btn ai" id="aAI" style="margin-top:14px">${SPARK} Explain with AI</button><div class="aibox" id="aiExplain" hidden><div class="kick">${SPARK} Claude explains</div><div class="aitext"></div></div>
   <div class="acts"><button class="btn pri" id="aF">Zoom to it</button>''')
rep("  $('#aF').onclick=()=>focus(st);", "  $('#aF').onclick=()=>focus(st);{const b=$('#aAI');if(b)b.onclick=()=>aiExplain(st)}")

# Study: AI cases + explain answer
rep('''    <button class="mode" data-s="tour"><strong>Follow a nerve or vessel</strong>''',
    '''    <button class="mode ai" data-s="aicase"><strong>${SPARK} AI clinical cases</strong><span>Claude writes fresh bellringer scenarios from the region you choose below; you find the answer on the model.</span></button>
    <button class="mode" data-s="tour"><strong>Follow a nerve or vessel</strong>''')
rep("    else if(m==='tour'){renderTourPick()}});", "    else if(m==='tour'){renderTourPick()}\n    else if(m==='aicase'){aiCases(b)}});")
rep('''    <div class="acts"><button class="btn pri" id="qN">${QZ.i+1>=QZ.queue.length?'Finish':'Next →'}</button><button class="btn" id="qF">Zoom to it</button></div>`}''',
    '''    ${q.aiWhy?`<div class="note"><b>Why</b>${esc(q.aiWhy)}</div>`:''}
    <div class="aibox" id="aiWhy" hidden><div class="kick">${SPARK} Claude explains</div><div class="aitext"></div></div>
    <div class="acts"><button class="btn pri" id="qN">${QZ.i+1>=QZ.queue.length?'Finish':'Next →'}</button><button class="btn" id="qF">Zoom to it</button><button class="btn ai" id="qW">${SPARK} Why?</button></div>`}''')
rep("on('#qR',()=>{q.tries=3;answer(false)});", "on('#qR',()=>{q.tries=3;answer(false)});on('#qW',()=>aiWhy(q));")

# Lecture: read slide picture with Claude
rep('''   <div class="hint" id="visStat" style="margin:2px 0 0 24px">''', '''   <button class="btn ai" id="visAI" style="margin:8px 0 0 24px">${SPARK} Read this slide’s labels with AI</button>
   <div class="hint" id="visStat" style="margin:2px 0 0 24px">''')
rep("  const cb=$('#visOn');if(cb)cb.onchange=", "  const va=$('#visAI');if(va)va.onclick=()=>aiReadSlide(va);\n  const cb=$('#visOn');if(cb)cb.onchange=")
open(p, 'w').write(s); print('ai ok')
