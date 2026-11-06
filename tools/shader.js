const NOISE=`
uniform vec3 uAxis; uniform float uKind; uniform float uBump; uniform float uTint; uniform float uCad;
uniform vec3 uFascia; uniform vec3 uTendon; uniform vec3 uFat; varying vec3 vObj; varying vec2 vAux;
float th(vec3 p){p=fract(p*0.3183099+.1);p*=17.0;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
float vn(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);
 return mix(mix(mix(th(i),th(i+vec3(1,0,0)),f.x),mix(th(i+vec3(0,1,0)),th(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(th(i+vec3(0,0,1)),th(i+vec3(1,0,1)),f.x),mix(th(i+vec3(0,1,1)),th(i+vec3(1,1,1)),f.x),f.y),f.z);}
float ridge(vec3 p){return 1.-abs(2.*vn(p)-1.);}
vec3 frame(out vec3 u,out vec3 v){vec3 a=normalize(uAxis);u=normalize(cross(a,abs(a.z)<.9?vec3(0,0,1):vec3(1,0,0)));v=cross(a,u);return a;}
/* fibres along the muscle axis (fascicles + fine fibres) */
float fibres(vec3 p,out float aa){vec3 u,v;vec3 a=frame(u,v);vec3 q=vec3(dot(p,u),dot(p,v),dot(p,a));
 vec3 s=q*vec3(1.6,1.6,.08);aa=clamp(1.25-length(fwidth(s))*1.5,0.,1.);
 return vn(s)*.45+vn(q*vec3(.42,.42,.035))*.4+vn(q*vec3(3.2,3.2,.2))*.15*aa;}
/* crinkled fascia / aponeurosis / vessel wall: ridged, wrinkly film */
float crinkle(vec3 p,out float aa){vec3 s=p*.55;aa=clamp(1.3-length(fwidth(s))*1.2,0.,1.);
 return ridge(s)*.5+ridge(p*.19+3.)*.35+vn(p*1.7)*.15*aa;}
/* bone: fine porosity + coarse irregularity */
float bone(vec3 p,out float aa){vec3 s=p*1.4;aa=clamp(1.2-length(fwidth(s))*1.4,0.,1.);return vn(p*.25)*.55+vn(s)*.45;}`;
function tissueMat(kind,axis){
  const m=new THREE.MeshPhysicalMaterial({roughness:.6,metalness:0,envMapIntensity:.55,clearcoat:0,clearcoatRoughness:.22});m.extensions={derivatives:true};
  m.userData.u={uAxis:{value:new THREE.Vector3(...axis)},uKind:{value:kind==='muscle'?0:kind==='bone'||kind==='disc'?1:2},
    uBump:{value:kind==='muscle'?1.0:kind==='bone'?.55:.45},uTint:{value:kind==='muscle'?.9:.5},uCad:{value:0},
    uFascia:{value:new THREE.Color(0xC9BCA6).convertSRGBToLinear()},uTendon:{value:new THREE.Color(0xDCCDAD).convertSRGBToLinear()},uFat:{value:new THREE.Color(0xD6B26A).convertSRGBToLinear()}};
  m.userData.b0=m.userData.u.uBump.value;
  m.onBeforeCompile=sh=>{
    Object.assign(sh.uniforms,m.userData.u);
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vObj; attribute vec2 aux; varying vec2 vAux;').replace('#include <begin_vertex>','#include <begin_vertex>\nvObj=position; vAux=aux;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\n'+NOISE)
     .replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
      float crev=smoothstep(.3,1.,vAux.x), tnd=uKind<.5?vAux.y:(uKind>1.5?1.:0.);
      if(uCad>.5){ roughnessFactor=clamp(roughnessFactor+(vn(vObj*.05)-.5)*.5-tnd*.22+crev*.15,.12,1.); }`)
     .replace('#include <normal_fragment_maps>',`#include <normal_fragment_maps>
      float aa,a2; float h; float wr=crinkle(vObj,a2);
      if(uKind<.5) h=fibres(vObj,aa); else if(uKind<1.5) h=bone(vObj,aa); else {h=wr;aa=a2;}
      float film=uCad*(uKind<.5?(.18+.82*tnd):(uKind>1.5?.7:.0));
      float hb=mix(h,wr,film*.85);
      { vec3 vp=-vViewPosition; vec3 dpx=dFdx(vp),dpy=dFdy(vp); float hx=dFdx(hb),hy=dFdy(hb);
        vec3 r1=cross(dpy,normal),r2=cross(normal,dpx); float det=dot(dpx,r1);
        vec3 gr=sign(det)*(hx*r1+hy*r2); normal=normalize(abs(det)*normal-gr*uBump*mix(aa,a2,film)); }
      diffuseColor.rgb*=mix(1.0,.72+.52*h,uTint*aa*(1.-film*.6));
      if(uCad>.5){
        float big=vn(vObj*.022+7.3)*.6+vn(vObj*.07)*.4;
        diffuseColor.rgb*=.86+.24*big;                                   /* uneven fixation */
        if(uKind<.5){ float t=smoothstep(.15,.75,clamp(tnd*(.8+.4*vn(vObj*.21)),0.,1.));
          diffuseColor.rgb=mix(diffuseColor.rgb,uTendon*(.9+.2*vn(vObj*.5)),t*.95);
          diffuseColor.rgb=mix(diffuseColor.rgb,uFascia,smoothstep(.62,.9,vn(vObj*.04))*.16); }
        float lump=vn(vObj*.11+3.1)*.7+vn(vObj*.37)*.3;
        float fatAmt=crev*smoothstep(.4,.7,lump)*((uKind<.5||uKind>1.5)?.85:0.);
        diffuseColor.rgb=mix(diffuseColor.rgb,uFat*(.82+.36*lump),fatAmt);
        diffuseColor.rgb*=1.-crev*.5*(1.-fatAmt);
        diffuseColor.rgb*=.94+.08*vn(vObj*2.6);                          /* fine speckle */
      } else diffuseColor.rgb*=1.-crev*.3;`)
     .replace('#include <lights_physical_fragment>',`#include <lights_physical_fragment>
      #ifdef USE_CLEARCOAT
      if(uCad>.5){ material.clearcoat=clamp(material.clearcoat*(.6+.8*tnd+.3*vn(vObj*.08)-crev*.4),0.,1.); }
      #endif`);
  };
  m.customProgramCacheKey=()=>'tissue5';
  return m;
}
