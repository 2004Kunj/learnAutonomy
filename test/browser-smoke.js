const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1300,height:820}});const logs=[];p.on('console',m=>{if(m.type()==='error'||m.type()==='warning')logs.push(m.type()+': '+m.text())});p.on('pageerror',e=>logs.push('PAGEERR '+e.message));
await p.goto('http://localhost:8766/index.html?lite=1');
await p.waitForFunction(()=>document.getElementById('loading').hidden,null,{timeout:400000});console.log('loaded');
await p.waitForTimeout(6000);await p.screenshot({path:'app1.png',timeout:300000});console.log('shot1');
for(const step of JSON.parse(process.argv[2]||'[]')){await p.evaluate(step[0]);await p.waitForTimeout(step[2]||6000);await p.screenshot({path:step[1],timeout:300000});console.log(step[1])}
console.log(logs.filter(l=>!/TUNNEL|fonts|ReadPixels|GPU stall/.test(l)).slice(0,15).join('\n'));await b.close()})();
