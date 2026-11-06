import json, numpy as np, os
SITE=os.environ.get('SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','site')
M=json.load(open(os.path.join(SITE,'manifest.json')))
segR={'spine':[(0,-55,880),(0,-70,1480)],'head':[(0,-95,1480),(0,-100,1600)],
 'arm':[(-163,-72,1330),(-210,-62,1055)],'fore':[(-210,-62,1055),(-255,-115,810)],'hand':[(-255,-115,810),(-272,-165,690)],
 'thigh':[(-95,-82,850),(-77,-65,410)],'leg':[(-77,-65,410),(-75,-62,60)],'foot':[(-75,-70,40),(-82,-170,10)]}
allow={'Head':['head'],'Neck':['spine','head'],'Back':['spine'],'Thorax':['spine'],'Abdomen':['spine'],'Pelvis':['spine'],'Vertebral column':['spine'],
 'Shoulder':['spine','arm'],'Arm':['arm'],'Forearm':['fore','arm'],'Hand':['hand','fore'],'Hip':['thigh','spine'],'Thigh':['thigh'],'Leg':['leg'],'Foot':['foot','leg']}
def closest(p,a,b):
    a,b=np.array(a,float),np.array(b,float);ab=b-a;t=np.clip((p-a)@ab/(ab@ab),0,1);return a+ab*t
info={s['id']:s for s in M['structures']}
for m in M['meshes']:
    s=info[m[0]]
    if s['kind'] not in ('muscle','tendon'): 
        if len(m)>8: m[8]=[0,0,0]
        else: m.append([0,0,0])
        continue
    c=np.array(m[6],float);best=None
    for seg in allow.get(s['region'],['spine']):
        a,b=segR[seg]
        if seg not in ('spine','head') and c[0]>0: a=(-a[0],a[1],a[2]);b=(-b[0],b[1],b[2])
        q=closest(c,a,b);d=np.linalg.norm(c-q)
        if best is None or d<best[0]: best=(d,c-q)
    o=best[1]
    # midline structures in the trunk spread mostly forward/back, limbs radially
    m8=[round(float(x),1) for x in o]
    if len(m)>8: m[8]=m8
    else: m.append(m8)
json.dump(M,open(os.path.join(SITE,'manifest.json'),'w'),separators=(',',':'))
print('done', len(M['meshes']))
