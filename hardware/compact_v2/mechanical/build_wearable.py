"""Editable parametric CAD, millimetres. Run in Python 3.12 with CadQuery + VTK.
Imports real KiCad STEP. Purchased battery, antenna and transducers are labelled fit envelopes.
No physical comfort, acoustic, thermal or RF validation is implied.
"""
from pathlib import Path
import cadquery as cq, math,json
R=Path(__file__).resolve().parents[1];M=R/'mechanical';E=R/'exports';S=M/'step';T=M/'stl'
for p in [E,S,T,R/'pcb'/'models']:p.mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def rounded(x,y,z,w,d,h,r):return cq.Workplane(obj=box(x,y,z,w,d,h)).edges('|Z').fillet(r).val()
def cyl(a,b,r):
    a=cq.Vector(*a);v=cq.Vector(*b)-a;return cq.Solid.makeCylinder(r,v.Length,a,v.normalized())
mic=rounded(-1.5,-2,0,3,4,1.25,.2).cut(cyl((0,.58,1),(0,.58,2),.325))
cq.exporters.export(mic,str(R/'pcb'/'models'/'CMM4030.step'))
if not (S/'controller.step').exists():
    print('Microphone STEP saved; export KiCad boards before building assembly.');raise SystemExit(0)
P={'controller_mm':[50,38,1],'audio_mm':[18,24,1],'crown_housing_mm':[58,46,20], 'pod_housing_mm':[23,34,44], 'battery_envelope_mm':[45,32,6], 'battery_target_mAh':500, 'transducer_envelope_mm':[25,8], 'slider_travel_mm':20, 'headband_inner_radius_mm':82, 'wall_mm':1.8}
(M/'parameters.json').write_text(json.dumps(P,indent=2))
colors={'PA12':(.12,.14,.16),'lid':(.17,.19,.21),'TPU':(.055,.065,.075),'accent':(.12,.48,.43),'steel':(.48,.5,.53),'pcb':(.035,.24,.18),'chip':(.05,.055,.06),'cell':(.55,.57,.59),'wire':(.12,.14,.16)}
items=[];a=cq.Assembly(name='Bone_Buds_Rev_B_EVT')
def add(n,s,mat='PA12',printable=False,exp=(0,0,0),status='Designed geometry'):
    if isinstance(s,cq.Workplane):s=s.val()
    assert s.isValid(),n
    a.add(s,name=n,color=cq.Color(*colors[mat]));items.append(dict(name=n,shape=s,material=mat,explode=exp,status=status))
    if printable:cq.exporters.export(s,str(T/(n+'.stl')),tolerance=.08,angularTolerance=.15);cq.exporters.export(s,str(S/(n+'.step')))
    return s
def pcb(n,s,exp):
    # Actual STEP component shapes retained. Split display colors by height only.
    add(n,s,'pcb',exp=exp,status='Actual exported KiCad assembly geometry')
def arch(ri,ro,width):return cq.Workplane('XZ').circle(ro).circle(ri).extrude(width).translate((0,width/2,0)).val().intersect(box(-100,-20,20,200,40,90))
band=arch(82,86,18)
channel=arch(83.2,85.2,8);band=band.cut(channel)
add('01_PA12_headband_cable_channel',band,'PA12',True,exp=(0,0,12))
add('02_spring_strip_0p5mm',arch(82.7,83.2,6).translate((0,6,0)),'steel',status='Spring temper and preload require mechanical testing')
add('03_TPU_crown_cushion',arch(79,82,14),'TPU',True,exp=(0,0,-12))
add('04_hidden_loom_envelope',arch(83.65,84.75,5),'wire',status='10-wire bundles; bend radius and flex life pending')
# Crown electronics case: battery below PCB, serviceable lid above. No electronics are scaled.
outer=rounded(-29,-23,81,58,46,18.2,6)
outer=cq.Workplane(obj=outer).edges('>Z or <Z').fillet(1.5).val()
inner=rounded(-27.2,-21.2,82.8,54.4,42.4,18,4.2)
base=outer.cut(inner)
board=cq.importers.importStep(str(S/'controller.step')).val().translate((-25,19,92))
placements=json.loads((R/'documentation'/'controller_placement.json').read_text());byref={v['reference']:v for v in placements}
def localpos(ref):p=byref[ref];return (p['x']-75,69-p['y'])
# Exact board-hole centres, raised standoffs. The two holes establish orientation.
for ref in ['H1','H2']:
    x,y=localpos(ref);base=base.fuse(cyl((x,y,82.8),(x,y,91),2.2).cut(cyl((x,y,82),(x,y,94),.8)))
    add('M2_PCB_screw_'+ref,cyl((x,y,89.5),(x,y,93),.95).fuse(cyl((x,y,92),(x,y,93),1.8)),'steel')
# USB aperture and plug approach volume calculated from the actual placement.
ux,uy=localpos('J2');base=base.cut(box(ux-5.3,19.5,91.7,10.6,5,4.8))
# Power and mute actuators have separate access windows; mechanisms are on the actual PCB.
sx,sy=localpos('SW1');base=base.cut(box(sx-4,-24,91.2,10,6,4.8))
mx,my=localpos('SW2');base=base.cut(box(-30,my-5,91.2,5,11,4.8))
for x in [-25,25]:base=base.cut(cyl((x,-25,95),(x,-18,95),2.3))
# Lid fixing columns in sidewall corners; test printed pilot fit for M2 screws.
lid=rounded(-29,-23,99.2,58,46,1.8,6)
lid=cq.Workplane(obj=lid).edges('>Z').fillet(.8).val()
for x,y in [(-25,-18),(25,-18),(-25,18),(25,18)]:
    # Narrow bosses extend from walls, clear PCB perimeter by placing above PCB plane.
    base=base.fuse(cyl((x,y,95),(x,y,99.2),2).cut(cyl((x,y,94),(x,y,101),.8)))
    lid=lid.cut(cyl((x,y,98),(x,y,102),1.1))
    add('M2_lid_screw_'+str(x)+'_'+str(y),cyl((x,y,97),(x,y,101),.95),'steel',exp=(0,0,32))
case=add('05_PA12_controller_lower_shell',base,'PA12',True,exp=(0,0,-12))
add('06_PA12_controller_service_lid',lid,'lid',True,exp=(0,0,30))
pcb('07_ACTUAL_KICAD_CONTROLLER',board,(0,0,13))
cell=rounded(-22.5,-16,83.4,45,32,6,1.5)
add('08_PROTECTED_1S_500mAh_PACK_ENVELOPE',cell,'cell',exp=(0,-50,0),status='Provisional purchased-pack envelope, includes protection allowance; 10k NTC required')
add('09_TPU_battery_cradle',rounded(-23.3,-16.8,83,46.6,33.6,.4,1.9),'TPU',True,exp=(0,-50,-4))
add('10_TPU_battery_retaining_strap',box(-3,-17,89.4,6,34,.6),'TPU',True,exp=(0,-50,8))
badge=cq.Workplane('XY').text('BONE BUDS',3.2,.15,font='Arial',halign='center',valign='center').val().translate((0,0,101))
add('11_recessed_brand_mark',badge,'accent',exp=(0,0,30))
add('12_FPC_ANTENNA_ENVELOPE',rounded(-12,-5,97.7,24,10,.2,1),'accent',status='Provisional FPC antenna envelope; final antenna and ground clearance require RF selection')
add('13_USB_port_TPU_bezel',rounded(ux-6,21,91,12,2.4,6,1).cut(box(ux-5.3,20,91.7,10.6,5,4.8)),'TPU',True)
# Bilateral mastoid pods. Anatomical contact position is adjustable, not clinically validated.
pod_checks={}
for side in ['right','left']:
    sign=1 if side=='right' else -1
    def mirror(s):return s if sign==1 else s.mirror('YZ')
    def put(n,s,mat='PA12',pr=False,exp=(0,0,0),status='Designed geometry'):
        return add(side+'_'+n,mirror(s),mat,pr,tuple([sign*exp[0],exp[1],exp[2]]),status)
    # Make rounded pod by rotating a rounded extrusion so the service lid faces outward.
    def podshape(x,thick,margin=0):
        s=rounded(-17+margin,-29+margin,0,34-2*margin,44-2*margin,thick,10-margin)
        return s.rotate((0,0,0),(0,1,0),90).rotate((0,0,0),(1,0,0),90).translate((x,0,0))
    # Simpler explicit YZ extrusion gives predictable assembly axes.
    def capsule(x,t,m=0):
        s=cq.Workplane('YZ').center(0,-7).rect(34-2*m,44-2*m).extrude(t).edges('|X').fillet(9-m).val().translate((x,0,0));return s
    sh=capsule(73,21.2).cut(capsule(74.8,23,1.8))
    sh=sh.cut(cyl((71,0,-10),(78,0,-10),12.65))
    pd=cq.importers.importStep(str(S/('audio_'+side+'.step'))).val().rotate((0,0,0),(0,1,0),90).translate((85,12,5))
    pl=json.loads((R/'documentation'/('audio_'+side+'_placement.json')).read_text());pdrefs={v['reference']:v for v in pl}
    # Mic is top-port; physical tube follows actual mic centre (including 0.58mm offset).
    mp=pdrefs['U2'];my=12-(mp['y']-50)+.58;mz=5-(mp['x']-50)
    lid2=capsule(94.2,1.8).cut(cyl((92,my,mz),(98,my,mz),.8))
    # Support plate bridges both sidewalls behind the board; window saves mass.
    plate=box(82.8,-15.3,-15,2.2,30.6,23).cut(box(82,-6,-10,4,12,10))
    # Two mounting posts derived from board holes; no invented module holes.
    for ref in ['H1','H2']:
        hp=pdrefs[ref];yy=12-(hp['y']-50);zz=5-(hp['x']-50)
        sh=sh.fuse(cyl((84,yy,zz),(85,yy,zz),2).cut(cyl((83,yy,zz),(88,yy,zz),1.1)))
        # Bracket reaches from shell edge to post outside the active transducer face.
        sh=sh.fuse(box(83,yy-2,zz-2,2,4,4).cut(cyl((82,yy,zz),(88,yy,zz),1.1)))
        plate=plate.cut(cyl((82,yy,zz),(87,yy,zz),.85))
    sh=sh.fuse(plate)
    for yy,zz in [(-11,-22),(11,-22),(-11,7),(11,7)]:
        sh=sh.fuse(cyl((90,yy,zz),(94.2,yy,zz),2).cut(cyl((89,yy,zz),(98,yy,zz),.8)))
        lid2=lid2.cut(cyl((93,yy,zz),(98,yy,zz),1.1))
        put('M2_service_screw_'+str(yy)+'_'+str(zz),cyl((92,yy,zz),(96,yy,zz),.95),'steel',exp=(24,0,0))
    sh=sh.cut(cyl((84,0,11),(84,0,18),2.4))
    shell=put('PA12_pod_shell',sh,'PA12',True)
    put('PA12_service_lid',lid2,'lid',True,(24,0,0))
    pcb(side+'_ACTUAL_KICAD_AUDIO',mirror(pd),(sign*12,0,0))
    trans=cyl((72.6,0,-10),(80.6,0,-10),12.5)
    put('TRANSDUCER_25x8_ENVELOPE',trans,'steel',exp=(-16,0,0),status='Provisional 8ohm transducer; flange, impedance and drive limits must be confirmed')
    # Rigid rear annulus couples force, TPU surrounds the perimeter, active metal face remains exposed.
    ring=cyl((80.6,0,-10),(82.4,0,-10),13.7).cut(cyl((80,0,-10),(83,0,-10),10.2))
    for yy in [-13.5,13.5]:
        ring=ring.fuse(cyl((80.6,yy,-10),(82.8,yy,-10),1.8)).cut(cyl((80,yy,-10),(84,yy,-10),1.1))
        put('M2_retainer_screw_'+str(yy),cyl((80.7,yy,-10),(84.7,yy,-10),.95),'steel')
    put('PA12_rigid_transducer_retainer',ring,'PA12',True,(8,0,0))
    pad=cyl((72.5,0,-10),(74.8,0,-10),15).cut(cyl((71,0,-10),(76,0,-10),12.7))
    put('TPU_skin_contact_surround',pad,'TPU',True,(-20,0,0))
    # Locate the port surface from imported solids, including real PCB thickness.
    near=[]
    for sol in pd.Solids():
        bb=sol.BoundingBox()
        if bb.ymin<my<bb.ymax and bb.zmin<mz<bb.zmax and bb.xlen<3 and bb.ylen<6 and bb.zlen<6:near.append(bb.xmax)
    port_x=max(near) if near else 88
    duct=cyl((port_x+.03,my,mz),(94.2,my,mz),1.7).cut(cyl((port_x-.1,my,mz),(96,my,mz),.8))
    put('TPU_mic_acoustic_duct',duct,'TPU',True,(12,0,0))
    put('TPU_cable_strain_relief',cyl((84,0,12),(84,0,21),3).cut(cyl((84,0,11),(84,0,22),2)),'TPU',True)
    # 20mm captive slide; rail has indexed holes, clamp screw through outer collar.
    rail=rounded(82.7,-4,9,1.2,8,32,.4)
    for z in [15,20,25,30,35]:rail=rail.cut(cyl((82,0,z),(85,0,z),1))
    put('steel_adjustment_rail',rail,'steel',True,(0,0,20),status='1.2mm stainless rail; cut/drill/deburr, clamp fit pending')
    collar=rounded(80.5,-6,9,5.6,12,20,1).cut(box(82.5,-4.2,8,1.6,8.4,22)).cut(cyl((80,0,22),(88,0,22),1.1))
    put('PA12_slide_collar',collar,'PA12',True)
    put('M2_fit_clamp',cyl((80,0,22),(86.5,0,22),.95),'steel')
    put('TPU_tactile_LR_marker',cyl((96,8,2),(96.5,8,2),2.2),'accent')
    pod_checks[side]={'pcb_shell_mm3':mirror(pd).intersect(shell).Volume(),'pcb_transducer_mm3':pd.intersect(trans).Volume(),'pcb_retainer_mm3':pd.intersect(ring).Volume(),'mic_duct_pcb_mm3':pd.intersect(duct).Volume()}
# Main verification is exact solids; fitted interfaces intentionally share contact surfaces.
report={'all_shapes_valid':all(i['shape'].isValid() for i in items),'objects':len(items),'controller_shell_intersection_mm3':board.intersect(case).Volume(),'controller_battery_intersection_mm3':board.intersect(cell).Volume(),'pods':pod_checks,'status':'EVT geometry only; no wear, pressure, RF, electrical, drop, thermal or acoustic testing performed'}
(R/'documentation'/'cad_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
a.export(str(S/'bone_buds_revb_assembly.step'));a.export(str(M/'bone_buds_revb.xml'))
manifest=[]
for i in items:
    bb=i['shape'].BoundingBox();manifest.append({k:v for k,v in i.items() if k!='shape'}|{'bbox_mm':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]})
(R/'documentation'/'assembly_manifest.json').write_text(json.dumps(manifest,indent=2))
# Geometry-derived studio views, no generative image editing.
import vtk
def actor(shape,color):
    vs,fs=shape.tessellate(.1,.15);pts=vtk.vtkPoints();cells=vtk.vtkCellArray()
    for v in vs:pts.InsertNextPoint(v.x,v.y,v.z)
    for f in fs:
        cells.InsertNextCell(3)
        for j in f:cells.InsertCellPoint(j)
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells);norm=vtk.vtkPolyDataNormals();norm.SetInputData(poly);norm.SetFeatureAngle(50);norm.Update();mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort());ac=vtk.vtkActor();ac.SetMapper(mapper);p=ac.GetProperty();p.SetColor(*color);p.SetInterpolationToPBR();p.SetRoughness(.45);p.SetMetallic(.15);return ac
actors={i['name']:actor(i['shape'],colors[i['material']]) for i in items}
def render(n,pos,target=(0,0,35),select=lambda n:True,explode=False,scale=None):
    ren=vtk.vtkRenderer();ren.SetBackground(.87,.89,.91);ren.SetBackground2(.98,.98,.98);ren.GradientBackgroundOn()
    for i in items:
        ac=actors[i['name']];ac.SetPosition(*(i['explode'] if explode else (0,0,0)))
        if select(i['name']):ren.AddActor(ac)
    for xyz,inten in [((180,-220,300),1.3),((-180,-50,150),.8),((0,200,250),1)]:
        light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*xyz);light.SetFocalPoint(*target);light.SetIntensity(inten);ren.AddLight(light)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(2200,1700);win.SetMultiSamples(8);win.AddRenderer(ren)
    cam=ren.GetActiveCamera();cam.SetPosition(*pos);cam.SetFocalPoint(*target);cam.SetViewUp(0,0,1) if n!='top' else cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(.9)
    if scale:cam.SetParallelScale(scale)
    ren.ResetCameraClippingRange();win.Render();grab=vtk.vtkWindowToImageFilter();grab.SetInput(win);grab.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(E/(n+'.png')));writer.SetInputConnection(grab.GetOutputPort());writer.Write();win.Finalize();print('render',n,flush=True)
render('hero',(240,-330,180))
render('front',(0,-500,35))
render('side',(500,0,35))
render('top',(0,0,600))
render('exploded',(250,-350,220),explode=True)
render('electronics',(240,-300,250),select=lambda n:'ACTUAL' in n or 'PACK' in n or 'shell' in n or 'ANTENNA' in n or 'hidden_loom' in n)
render('contact_detail',(40,-120,20),target=(84,0,-7),select=lambda n:n.startswith('right_') and not 'service_lid' in n and not 'service_screw' in n,explode=True)
print('Complete parametric CAD, STEP/STL, assembly XML and seven true geometry renders.',flush=True)
