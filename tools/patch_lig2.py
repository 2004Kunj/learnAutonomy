p='site/index.html';s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
rep("&&(reg==='all'||regOfK(k)===reg)&&!(kindOfK(k)==='muscle'&&PIN_SKIP.has(k)","&&(reg==='all'||regOfK(k)===reg)&&(kindOfK(k)!=='ligament'||!!LIG[k][1])&&!(kindOfK(k)==='muscle'&&PIN_SKIP.has(k)")
anchor="  if(nm.length<4)continue;term(reEsc(nm).replace(/\\s+/g,'\\\\s+')+'s?',[k],st.name)}"
assert s.count(anchor)==1, anchor
L=lambda x:'lig-'+x
aliases=[
 (r"acl|anterior\\s+cruciate(?:\\s+lig\\w*)?",[L('anterior-cruciate-ligament')],'ACL'),
 (r"pcl|posterior\\s+cruciate(?:\\s+lig\\w*)?",[L('posterior-cruciate-ligament')],'PCL'),
 (r"mcl|medial\\s+collateral\\s+lig\\w*(?:\\s+of\\s+(?:the\\s+)?knee)?|tibial\\s+collateral(?:\\s+lig\\w*)?",[L('superficial-part-of-tibial-collateral-ligament'),L('deep-part-of-tibial-collateral-ligament')],'MCL'),
 (r"lcl|lateral\\s+collateral\\s+lig\\w*\\s+of\\s+(?:the\\s+)?knee|fibular\\s+collateral(?:\\s+lig\\w*)?",[L('fibular-collateral-ligament')],'LCL'),
 (r"atfl|anterior\\s+talofibular(?:\\s+lig\\w*)?",[L('anterior-talofibular-ligament')],'ATFL'),
 (r"cfl|calcaneofibular(?:\\s+lig\\w*)?",[L('calcaneofibular-ligament')],'CFL'),
 (r"ptfl|posterior\\s+talofibular(?:\\s+lig\\w*)?",[L('posterior-talofibular-ligament')],'PTFL'),
 (r"lateral\\s+(?:collateral\\s+)?lig\\w*\\s+of\\s+(?:the\\s+)?ankle|lateral\\s+ankle\\s+lig\\w*",[L('anterior-talofibular-ligament'),L('calcaneofibular-ligament'),L('posterior-talofibular-ligament')],'Lateral ankle ligaments'),
 (r"deltoid\\s+lig\\w*|medial\\s+(?:collateral\\s+)?lig\\w*\\s+of\\s+(?:the\\s+)?ankle",[L('tibiocalcaneal-ligament'),L('tibionavicular-ligament'),L('posterior-tibiotalar-ligament')],'Deltoid ligament'),
 (r"spring\\s+lig\\w*|plantar\\s+calcaneonavicular(?:\\s+lig\\w*)?",[L('plantar-calcaneonavicular-ligament')],'Spring ligament'),
 (r"bifurcate\\s+lig\\w*",[L('calcaneocuboid-ligament'),L('calcaneonavicular-ligament')],'Bifurcate ligament'),
 (r"short\\s+plantar\\s+lig\\w*",[L('plantar-calcaneocuboid-ligament')],'Short plantar ligament'),
 (r"coracoclavicular(?:\\s+lig\\w*)?",[L('conoid-ligament'),L('trapezoid-ligament')],'Coracoclavicular ligament'),
 (r"iliofemoral(?:\\s+lig\\w*)?|y[-\\s]lig\\w*",[L('transverse-part-of-iliofemoral-ligament'),L('descending-part-of-iliofemoral-ligament')],'Iliofemoral ligament'),
 (r"glenohumeral\\s+lig\\w*",[L('superior-glenohumeral-ligament'),L('middle-glenohumeral-ligament'),L('inferior-glenohumeral-ligament')],'Glenohumeral ligaments'),
 (r"(?:shoulder|glenohumeral)\\s+(?:joint\\s+)?capsule",[L('articular-capsule-of-glenohumeral-joint')],'Shoulder capsule'),
 (r"(?:knee)\\s+(?:joint\\s+)?capsule",[L('articular-capsule-of-knee-joint')],'Knee capsule'),
 (r"(?:hip)\\s+(?:joint\\s+)?capsule",[L('articular-capsule-of-hip-joint')],'Hip capsule'),
 (r"menisc(?:us|i)",[L('medial-meniscus'),L('lateral-meniscus')],'Menisci'),
 (r"ucl|ulnar\\s+collateral(?:\\s+lig\\w*)?",[L('ulnar-collateral-ligament')],'UCL'),
 (r"rcl|radial\\s+collateral(?:\\s+lig\\w*)?",[L('radial-collateral-ligament')],'RCL'),
 (r"annular\\s+lig\\w*",[L('annular-ligament-of-radius')],'Annular ligament'),
 (r"tfcc|triangular\\s+fibrocartilage",[L('articular-disc-of-distal-radio-ulnar-joint')],'TFCC'),
 (r"ligamentum\\s+flavum|ligamenta\\s+flava",[L('ligamenta-flava')],'Ligamentum flavum'),
 (r"ligamentum\\s+nuchae|nuchal\\s+lig\\w*",[L('nuchal-ligament')],'Ligamentum nuchae'),
 (r"all|anterior\\s+longitudinal(?:\\s+lig\\w*)?",[L('anterior-longitudinal-ligament')],'ALL'),
 (r"pll|posterior\\s+longitudinal(?:\\s+lig\\w*)?",[L('posterior-longitudinal-ligament')],'PLL'),
 (r"thoracolumbar\\s+fascia",[L('posterior-layer-of-thoracolumbar-fascia')],'Thoracolumbar fascia'),
 (r"patellar\\s+(?:lig\\w*|tendon)",[L('patellar-ligament')],'Patellar ligament'),
 (r"plantar\\s+fascia|plantar\\s+aponeurosis",[L('plantar-aponeurosis')],'Plantar aponeurosis'),
 (r"labrum",[L('glenoid-labrum'),L('acetabular-labrum')],'Labrum'),
]
code="\n".join("term('%s',%s,'%s');"%(p_,repr(k).replace("'",'"'),lab) for p_,k,lab in aliases)
# 'all' alone would match the English word; require the abbreviation in caps context -> drop bare 'all'
code=code.replace("term('all|anterior","term('anterior")
s=s.replace(anchor,anchor+"\n/* ligament aliases */\n"+code)
open(p,'w').write(s);print('ok')
