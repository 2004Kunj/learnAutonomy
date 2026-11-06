p='site/index.html';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
old="  if(nm.length<4)continue;term(reEsc(nm).replace(/\\s+/g,'\\\\s+')+'s?',[k],st.name)}"
new="  if(nm.length<4)continue;term(reEsc(nm).replace(/\\s+/g,'\\\\s+')+'s?'+(st.kind==='ligament'?'':'(?!\\\\s+lig)'),[k],st.name);\n  const lw=st.kind==='ligament'&&nm.match(/^([a-z-]{8,}) ligament$/);if(lw)term(reEsc(lw[1]),[k],st.name)}"
rep(old,new)
rep("term('labrum',","term('(?<!glenoid\\\\s)(?<!acetabular\\\\s)labrum',")
open(p,'w').write(s);print('ok')
