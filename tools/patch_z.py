p='site/index.html';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:80],s.count(a)); s=s.replace(a,b)
i=s.index("function tubeStruct(n,kind,region){"); j=s.index("for(const n of NERV)tubeStruct")
new=r"""/* merged tube geometry for one structure: every path in one mesh, radius per point (Z-Anatomy) or constant (traced) */
function tubeGeo(n,rf,radial,every){
  const pos=[],nor=[],idx=[];let base=0;const T=new THREE.Vector3(),N=new THREE.Vector3(),B=new THREE.Vector3();
  n.paths.forEach((P0,pi)=>{let P=P0,R=n.rads?n.rads[pi]:null;
    if(!R){const c=new THREE.CatmullRomCurve3(P.map(q=>new THREE.Vector3(q[0],q[1],q[2])),false,'centripetal');P=c.getSpacedPoints(Math.max(8,Math.round(c.getLength()/4))).map(v=>[v.x,v.y,v.z])}
    if(every>1&&P.length>every*2){const Q=[],RR=[];for(let i=0;i<P.length;i+=every){Q.push(P[i]);if(R)RR.push(R[i])}if((P.length-1)%every){Q.push(P[P.length-1]);if(R)RR.push(R[R.length-1])}P=Q;if(R)R=RR}
    const m=P.length;if(m<2)return;
    for(let i=0;i<m;i++){const a=P[Math.max(0,i-1)],b=P[Math.min(m-1,i+1)];T.set(b[0]-a[0],b[1]-a[1],b[2]-a[2]);if(T.lengthSq()<1e-9)T.set(0,0,1);T.normalize();
      if(i===0){N.crossVectors(T,Math.abs(T.x)<.9?new THREE.Vector3(1,0,0):new THREE.Vector3(0,1,0)).normalize()}else{N.addScaledVector(T,-N.dot(T));if(N.lengthSq()<1e-9)N.crossVectors(T,new THREE.Vector3(0,0,1));N.normalize()}
      B.crossVectors(T,N);const r=rf(R?R[i]:n.r);
      for(let j=0;j<radial;j++){const t=j/radial*Math.PI*2,c=Math.cos(t),s2=Math.sin(t),nx=N.x*c+B.x*s2,ny=N.y*c+B.y*s2,nz=N.z*c+B.z*s2;pos.push(P[i][0]+nx*r,P[i][1]+ny*r,P[i][2]+nz*r);nor.push(nx,ny,nz)}}
    for(let i=0;i<m-1;i++)for(let j=0;j<radial;j++){const a=base+i*radial+j,b=base+i*radial+(j+1)%radial;idx.push(a,b,a+radial,b,b+radial,a+radial)}
    base+=m*radial});
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(nor,3));
  g.setIndex(base>65535?new THREE.Uint32BufferAttribute(idx,1):new THREE.Uint16BufferAttribute(idx,1));g.computeBoundingSphere();g.computeBoundingBox();return g}
function tubeStruct(n,kind,region){
  const st=S[n.id]={id:n.id,k:n.k,name:n.name,kind,region,side:n.side,meshes:[],ghosts:[],hits:[],partNames:[],src:n.src||'traced'};
  const p0=n.paths[0];const q=p0[Math.floor(p0.length/2)];st.anchor=new THREE.Vector3(q[0],q[1],q[2]);
  const g=tubeGeo(n,r=>r,8,1);g.setAttribute('aux',new THREE.BufferAttribute(new Uint8Array(g.attributes.position.count*2),2,true));
  const mat=tissueMat(kind,[0,0,1]);mat.userData.j=1;
  const mesh=new THREE.Mesh(g,mat);mesh.castShadow=mesh.receiveShadow=true;mesh.userData={sid:n.id,part:''};body.add(mesh);st.meshes.push(mesh);pickables.push(mesh);
  const gm=new THREE.Mesh(tubeGeo(n,r=>Math.max(r*1.7,2.4),6,1),new THREE.MeshBasicMaterial({transparent:true,opacity:.85,depthTest:false,depthWrite:false}));
  gm.renderOrder=10;gm.userData={sid:n.id};body.add(gm);st.ghosts.push(gm);
  const hm=new THREE.Mesh(tubeGeo(n,r=>Math.max(5,r*3),5,3),new THREE.MeshBasicMaterial({visible:false}));hm.userData={sid:n.id,part:'',hit:true};body.add(hm);st.hits.push(hm);nerveHit.push(hm);
}
"""
s=s[:i]+new+s[j:]
rep("for(const n of NERV)tubeStruct(n,'nerve',NREG[n.k]||'Back');","for(const n of NERV)tubeStruct(n,'nerve',n.region||NREG[n.k]||'Back');")
# content fallbacks for structures that only Z-Anatomy has
rep("  }else if(kind==='nerve'){const n=C.NER[st.k];","  }else if(kind==='nerve'){const n=C.NER[st.k]||zInfo(st,'nerve');")
rep("<p class=\"hint\" style=\"margin-top:10px\">Nerve courses are traced along this specimen’s real bones and muscles; diameters are enlarged so you can see them.</p>`;",
    "<p class=\"hint\" style=\"margin-top:10px\">${st.src==='z'?'Nerve model: Z-Anatomy (CC BY-SA 4.0), true diameter shown (minimum 0.8 mm).':'Nerve course traced along this specimen’s bones and muscles; diameter enlarged so you can see it.'}</p>`;")
rep("const v=C.VES[st.k]||['','','',''];","const v=C.VES[st.k]||zInfo(st,kind);")
rep("${VREG[st.k]?'<p class=\"hint\" style=\"margin-top:10px\">Traced along this specimen; the scan itself only includes the trunk vessels.</p>':''}`",
    "${st.src==='z'?'<p class=\"hint\" style=\"margin-top:10px\">Vessel model: Z-Anatomy (CC BY-SA 4.0), true calibre.</p>':st.src==='traced'?'<p class=\"hint\" style=\"margin-top:10px\">Traced along this specimen (not in the source models).</p>':''}`")
rep("function credit(){","""function zInfo(st,kind){const nm=st.name;const m=nm.match(/(?:branch(?:es)?|division|root|trunk|cord) of (?:the )?(.+)$/i);const parent=m?m[1]:'';
  const where=(st.side?SIDEW[st.side].toLowerCase()+' ':'')+st.region.toLowerCase()+' region';
  if(kind==='nerve')return ['—',parent?`Part of the ${parent}, in the ${where}.`:`Runs in the ${where}.`,parent?`See the ${parent}.`:'Tap nearby muscles to see what they are supplied by.',''];
  return [parent?`From the ${parent}`:'—','—',`Structures of the ${where}`,'']}
function credit(){""")
rep("3D anatomy: BodyParts3D, © The Database Center for Life Science, licensed under","3D anatomy: <a href=\"https://www.z-anatomy.com\" target=\"_blank\" rel=\"noopener\">Z-Anatomy</a> (CC BY-SA 4.0) — muscles, bones, ligaments, nerves and vessels — built on BodyParts3D, © The Database Center for Life Science,")
rep(" Ligaments, capsules, menisci and retinacula: <a href=\"https://www.z-anatomy.com\" target=\"_blank\" rel=\"noopener\">Z-Anatomy</a>, CC BY-SA 4.0. Nerve paths traced for this app."," A few nerves and vessels Z-Anatomy lacks are traced for this app.")
rep("const total=14192560;","const total=15496316;")
rep("(about 48 MB)","(about 52 MB)"); rep("HD downloads about 48 MB","HD downloads about 52 MB"); rep("HD anatomy loaded — 5.3 million triangles","HD anatomy loaded — 5.5 million triangles")
# tour picker: only structures with study content (the full list is in the Index)
rep("const nv=NERV.filter(n=>n.side!=='L').map(n=>n.id),ar=VESS.filter(v=>v.kind==='artery'&&v.side!=='L').map(v=>v.id),ve=VESS.filter(v=>v.kind==='vein'&&v.side!=='L').map(v=>v.id);",
    "const nv=NERV.filter(n=>n.side!=='L'&&C.NER[n.k]).map(n=>n.id),ar=VESS.filter(v=>v.kind==='artery'&&v.side!=='L'&&C.VES[v.k]).map(v=>v.id),ve=VESS.filter(v=>v.kind==='vein'&&v.side!=='L'&&C.VES[v.k]).map(v=>v.id);")
open(p,'w').write(s);print('ok')
