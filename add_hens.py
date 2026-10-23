import json,base64,math,numpy as np,trimesh,sys
D='/workspace/armadillo/gallinero_tractor/ar_app/'
def ico(s,t,sub=1):
    m=trimesh.creation.icosphere(subdivisions=sub);m.apply_scale(s);m.apply_translation(t);return m
def cone(r,h,t,rot):
    m=trimesh.creation.cone(r,h,sections=6);m.apply_transform(rot);m.apply_translation(t);return m
Ry=lambda a:trimesh.transformations.rotation_matrix(a,[0,1,0])
Rz=lambda a:trimesh.transformations.rotation_matrix(a,[0,0,1])
body=ico([.17,.13,.11],[0,.25,0]); tail=ico([.06,.09,.05],[-.15,.34,0],0); body=trimesh.util.concatenate([body,tail])
head=ico([.065,.07,.06],[0,0,0])
comb=trimesh.util.concatenate([ico([.045,.03,.012],[-.005,.075,0],0),ico([.02,.025,.01],[.045,-.04,0],0)])  # cresta + barbilla
beak=cone(.022,.05,[.055,0,0],Rz(-math.pi/2))
legs=trimesh.util.concatenate([trimesh.creation.box([.02,.15,.02],trimesh.transformations.translation_matrix([0,.075,z])) for z in(-.04,.04)])
g=json.load(open(sys.argv[1])); sep=len(sys.argv)>3
blob=bytearray(); bvs=[];accs=[]
def addacc(arr,typ,target=None,minmax=False):
    arr=np.ascontiguousarray(arr);off=len(blob);blob.extend(arr.tobytes())
    while len(blob)%4:blob.append(0)
    bv={'buffer':len(g['buffers']),'byteOffset':off,'byteLength':arr.nbytes}
    if target:bv['target']=target
    g['bufferViews'].append(bv)
    a={'bufferView':len(g['bufferViews'])-1,'componentType':5126 if arr.dtype==np.float32 else 5125,'count':len(arr),'type':typ}
    if minmax:a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist()
    g['accessors'].append(a);return len(g['accessors'])-1
def mat(n,rgb):
    g['materials'].append({'name':'Gallinas__'+n,'pbrMetallicRoughness':{'baseColorFactor':rgb+[1],'metallicFactor':0,'roughnessFactor':.9}});return len(g['materials'])-1
def prim(m,mi):
    m=m.copy();m.merge_vertices()
    return {'attributes':{'POSITION':addacc(m.vertices.astype(np.float32),'VEC3',34962,True),'NORMAL':addacc(m.vertex_normals.astype(np.float32),'VEC3',34962)},'indices':addacc(m.faces.astype(np.uint32).ravel(),'SCALAR',34963),'material':mi}
cols={'cafe':[.55,.3,.13],'blanca':[.93,.92,.88],'negra':[.08,.08,.09]}
mr=mat('cresta_roja',[.8,.08,.06]);my=mat('pico_amarillo',[.95,.7,.1]);mo=mat('patas_naranja',[.9,.5,.1])
pb,ph={},{}
pc=prim(comb,mr);pk=prim(beak,my)
for k,c in cols.items():
    mi=mat(k,c);pb[k]=prim(body,mi);ph[k]=prim(head,mi)
def mesh(n,prims):
    g['meshes'].append({'name':n,'primitives':prims});return len(g['meshes'])-1
MB={k:mesh('gallina_cuerpo_'+k,[v]) for k,v in pb.items()}
MH={k:mesh('gallina_cabeza_'+k,[ph[k],pc,pk]) for k in cols}
ML=mesh('gallina_patas',[prim(legs,mo)])
T=8.0;N=33;ts=np.linspace(0,T,N).astype(np.float32);tacc=addacc(ts,'SCALAR');g['accessors'][tacc]['min']=[0];g['accessors'][tacc]['max']=[T]
def P(x,y,z):  # cm Z-up -> m Y-up (mismo origen que build_glb.py)
    return [x/100-3,z/100,-(y/100-.6)]
def q(yaw,pitch=0):  # yaw sobre Y, pitch sobre Z local
    qy=np.array([0,math.sin(yaw/2),0,math.cos(yaw/2)]);qz=np.array([0,0,math.sin(pitch/2),math.cos(pitch/2)])
    x1,y1,z1,w1=qy;x2,y2,z2,w2=qz
    return [w1*x2+x1*w2+y1*z2-z1*y2,w1*y2-x1*z2+y1*w2+z1*x2,w1*z2+x1*y2-y1*x2+z1*w2,w1*w2-x1*x2-y1*y2-z1*z2]
chans=[];samps=[];newnodes=[]
def anim(node,path,vals):
    o=addacc(np.array(vals,np.float32),'VEC4' if path=='rotation' else 'VEC3');samps.append({'input':tacc,'output':o,'interpolation':'LINEAR'})
    chans.append({'sampler':len(samps)-1,'target':{'node':node,'path':path}})
def node(d):g['nodes'].append(d);return len(g['nodes'])-1
def hen(name,col,root_tr,root_rot,head_rot,corral):
    dx=1.5 if (sep and corral) else 0
    h=node({'name':name+'_cabeza','mesh':MH[col],'translation':[.15,.4,0]})
    b=node({'name':name+'_cuerpo','mesh':MB[col],'children':[h]})
    l=node({'name':name+'_patas','mesh':ML})
    r=node({'name':name,'children':[b,l]});newnodes.append(r)
    tr=[[p[0]+dx,p[1],p[2]] for p in root_tr]
    anim(r,'translation',tr);anim(r,'rotation',root_rot);anim(h,'rotation',head_rot)
idle=lambda ph:[q(.4*math.sin(2*math.pi*(t/T*2+ph))) for t in ts]
def walker(name,col,cx,cy,rx,ry,ph,d=1):
    a=[d*2*math.pi*t/T+ph for t in ts]
    pos=[P(cx+rx*math.cos(t),cy+ry*math.sin(t),0) for t in a]
    pos=[[p[0],p[1]+.015*abs(math.sin(i*math.pi/2)),p[2]] for i,p in enumerate(pos)]
    rot=[q(math.atan2(d*ry*math.cos(t),-d*rx*math.sin(t))) for t in a]
    hen(name,col,pos,rot,[q(0,.15*math.sin(i*math.pi/2)) for i in range(N)],True)
def static(name,col,x,y,z,yaw,peck,corral):
    pos=[P(x,y,z)]*N;rot=[q(yaw+.15*math.sin(2*math.pi*t/T))for t in ts]
    hr=[q(0,-1.1*max(0,math.sin(2*math.pi*(t/T*4)+peck))**2) for t in ts] if peck is not None else idle(x)
    hen(name,col,pos,rot,hr,corral)
walker('Gallina_01','cafe',340,60,90,35,0)
walker('Gallina_02','blanca',470,55,80,30,2,-1)
walker('Gallina_03','negra',520,70,50,30,4)
walker('Gallina_04','cafe',420,60,150,40,3.5)
static('Gallina_05','blanca',275,70,0,math.pi/2,0,True)      # bebedero flotador
static('Gallina_06','negra',310,98,0,math.pi,1.5,True)
static('Gallina_07','cafe',100,28,45,-math.pi/2,0.7,False)    # comedero lado y=0
static('Gallina_08','blanca',100,92,45,math.pi/2,2.2,False)   # comedero lado y=W
static('Gallina_09','negra',77,45,122,math.pi/2,None,False)   # percha 2
static('Gallina_10','cafe',122,80,107,-math.pi/2,None,False)  # percha 3
pos=[P(78,-17,38)]*N;hen('Gallina_11','blanca',pos,[q(math.pi/2)]*N,idle(.3),False)  # echada en nido
g['scenes'][0]['nodes']+=newnodes
g['animations']=[{'name':'Gallinas','channels':chans,'samplers':samps}]
g['buffers'].append({'byteLength':len(blob),'uri':'data:application/octet-stream;base64,'+base64.b64encode(bytes(blob)).decode()})
json.dump(g,open(sys.argv[2],'w'),separators=(',',':'))
print(sys.argv[2],len(blob))
