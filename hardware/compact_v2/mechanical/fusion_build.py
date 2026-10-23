"""Run through official Fusion MCP. Native sketches/extrusions/fillets + real PCB STEP imports.
All coordinates mm here; converted to Fusion centimetres at the API boundary.
"""
import adsk.core as C, adsk.fusion as F, math,json,pathlib
R=pathlib.Path(r'C:\Users\Aarya Tanwade\Desktop\Projects\Hardware\Bone Conduction\Repo\bone-buds\hardware\compact_v2')
OUT=R/'mechanical'/'fusion';OUT.mkdir(exist_ok=True)
def run(_context: str):
 app=C.Application.get();doc=app.documents.add(C.DocumentTypes.FusionDesignDocumentType);doc.name='Bone Buds Rev B - Native Fusion EVT'
 d=F.Design.cast(app.activeProduct);d.designType=F.DesignTypes.ParametricDesignType;d.unitsManager.defaultLengthUnits='mm';root=d.rootComponent
 params={'CrownWidth':62,'CrownLength':50,'CrownHeight':18.2,'Wall':1.8,'CrownRadius':9,'BandInner':82,'BandThickness':4,'BandWidth':18,'PadThickness':3,'PodWidth':34,'PodHeight':44,'PodDepth':21.2,'PodRadius':9,'SliderTravel':20,'BatteryWidth':45,'BatteryLength':32,'BatteryHeight':6}
 for n,v in params.items():d.userParameters.add(n,C.ValueInput.createByString(str(v)+' mm'),'mm','Bone Buds EVT design dimension')
 occs={};meta=[];new=F.FeatureOperations.NewBodyFeatureOperation;cut=F.FeatureOperations.CutFeatureOperation;join=F.FeatureOperations.JoinFeatureOperation
 lib=app.materialLibraries.itemByName('Fusion Appearance Library');apps={}
 for key,src in [('PA12','Plastic - Matte (Gray)'),('TPU','Rubber - Soft'),('steel','Stainless Steel - Satin'),('accent','Plastic - Matte (Green)'),('lid','Plastic - Matte (Black)')]:
  apps[key]=d.appearances.addByCopy(lib.appearances.itemByName(src),'Bone Buds '+key)
  color=apps[key].appearanceProperties.itemById('generic_diffuse')
  if color and key in ['PA12','lid','accent']:color.value=C.Color.create(*({'PA12':(40,46,51,255),'lid':(52,58,64,255),'accent':(45,111,105,255)}[key]))
 def comp(n,mat='PA12',explode=(0,0,0)):
  o=root.occurrences.addNewComponent(C.Matrix3D.create());o.component.name=n;occs[n]=o;o.component.attributes.add('BoneBuds','material',mat);o.component.attributes.add('BoneBuds','exploded_offset_mm',json.dumps(explode));meta.append({'name':n,'material':mat,'explode':explode});return o.component
 def finish(c,mat):
  for b in c.bRepBodies:b.appearance=apps[mat]
  for s in c.sketches:s.isVisible=False
  for p in c.constructionPlanes:p.isVisible=False
 def vi(v):return C.ValueInput.createByString(str(v)+' mm' if isinstance(v,(int,float)) else v)
 def num(v):return float(v) if isinstance(v,(int,float)) else d.unitsManager.evaluateExpression(v,'mm')*10
 def pt(x,y,z=0):return C.Point3D.create(x/10,y/10,z/10)
 def plane(c,axis,offset):
  base={'XY':c.xYConstructionPlane,'YZ':c.yZConstructionPlane,'XZ':c.xZConstructionPlane}[axis]
  if abs(offset)<1e-9:return base
  pi=c.constructionPlanes.createInput();pi.setByOffset(base,vi(offset));return c.constructionPlanes.add(pi)
 def rect(c,n,axis,offset,cx,cy,w,h,depth,rad=0,op=None):
  op=new if op is None else op;s=c.sketches.add(plane(c,axis,offset));s.name=n+' profile';ww,hh=num(w),num(h)
  lines=s.sketchCurves.sketchLines.addTwoPointRectangle(pt(cx-ww/2,cy-hh/2),pt(cx+ww/2,cy+hh/2))
  for ln,orient,expr in [(lines.item(0),F.DimensionOrientations.HorizontalDimensionOrientation,w),(lines.item(1),F.DimensionOrientations.VerticalDimensionOrientation,h)]:
   dim=s.sketchDimensions.addDistanceDimension(ln.startSketchPoint,ln.endSketchPoint,orient,pt(cx+ww,cy+hh));dim.parameter.expression=str(expr)+' mm' if isinstance(expr,(int,float)) else expr
  e=c.features.extrudeFeatures.addSimple(s.profiles.item(0),vi(depth),op);e.name=n
  if num(rad)>0:
   edges=C.ObjectCollection.create();seen=set()
   for b in e.bodies:
    for ed in b.edges:
     if not ed.startVertex or not ed.endVertex:continue
     a=s.modelToSketchSpace(ed.startVertex.geometry);z=s.modelToSketchSpace(ed.endVertex.geometry)
     if abs(a.x-z.x)<1e-6 and abs(a.y-z.y)<1e-6 and abs(a.z-z.z)>1e-4 and abs(abs(a.x*10-cx)-ww/2)<.001 and abs(abs(a.y*10-cy)-hh/2)<.001:
      tok=ed.entityToken
      if tok not in seen:edges.add(ed);seen.add(tok)
   if edges.count:
    fi=c.features.filletFeatures.createInput();fi.edgeSetInputs.addConstantRadiusEdgeSet(edges,vi(rad),False);c.features.filletFeatures.add(fi).name=n+' corner radii'
  return e
 def disk(c,n,axis,off,cx,cy,r,depth,inner=0,op=None):
  s=c.sketches.add(plane(c,axis,off));s.name=n+' profile';circ=s.sketchCurves.sketchCircles.addByCenterRadius(pt(cx,cy),num(r)/10);s.sketchDimensions.addRadialDimension(circ,pt(cx+num(r)+2,cy)).parameter.expression=str(r)+' mm' if isinstance(r,(int,float)) else r
  if inner:s.sketchCurves.sketchCircles.addByCenterRadius(pt(cx,cy),inner/10)
  prof=min([s.profiles.item(i) for i in range(s.profiles.count)],key=lambda p:p.areaProperties().area) if inner else s.profiles.item(0)
  e=c.features.extrudeFeatures.addSimple(prof,vi(depth),new if op is None else op);e.name=n;return e
 def arch(c,n,ri,ro,width,y=0):
  s=c.sketches.add(plane(c,'XZ',-(y+width/2)));s.name=n+' profile';z=20;xo=math.sqrt(ro*ro-z*z);xi=math.sqrt(ri*ri-z*z)
  # World-to-sketch conversion avoids assumptions about XZ plane orientation.
  def ap(x,z):return s.modelToSketchSpace(pt(x,y+width/2,z))
  s.sketchCurves.sketchArcs.addByThreePoints(ap(-xo,z),ap(0,ro),ap(xo,z));s.sketchCurves.sketchLines.addByTwoPoints(ap(xo,z),ap(xi,z));s.sketchCurves.sketchArcs.addByThreePoints(ap(xi,z),ap(0,ri),ap(-xi,z));s.sketchCurves.sketchLines.addByTwoPoints(ap(-xi,z),ap(-xo,z))
  e=c.features.extrudeFeatures.addSimple(s.profiles.item(0),vi(width),new);e.name=n;return e
 def save():
  assert d.exportManager.execute(d.exportManager.createFusionArchiveExportOptions(str(OUT/'Bone_Buds_RevB.f3d')))
  (OUT/'component_manifest.json').write_text(json.dumps(meta,indent=2));print('Checkpoint: native Fusion archive saved,',root.occurrences.count,'components')
 c=comp('01 PA12 structural headband',explode=(0,0,12));arch(c,'Overhead arc',82,86,18);finish(c,'PA12')
 c=comp('02 TPU head-contact cushion', 'TPU',(0,0,-10));arch(c,'Replaceable comfort arc',79,82,14);finish(c,'TPU')
 c=comp('03 Stainless reinforcement','steel');arch(c,'Spring strip',82.7,83.2,6,6);finish(c,'steel')
 # Headband cable conduits are small separate rigid covers with internal bore.
 c=comp('04 Protected cable loom envelope','TPU');arch(c,'Loom envelope',84,85.2,5);finish(c,'TPU')
 c=comp('05 Crown lower shell',explode=(0,0,-12));rect(c,'Crown outer','XY',81,0,0,'CrownWidth','CrownLength','CrownHeight','CrownRadius');rect(c,'Battery and PCB cavity','XY',82.8,0,0,'CrownWidth-2*Wall','CrownLength-2*Wall',20,'CrownRadius-Wall',cut)
 placements=json.loads((R/'documentation'/'controller_placement.json').read_text());br={v['reference']:v for v in placements}
 for ref in ['H1','H2']:
  x,y=br[ref]['x']-75,69-br[ref]['y'];disk(c,ref+' PCB boss','XY',82.8,x,y,2.2,8.2,op=join);disk(c,ref+' M2 pilot','XY',82,x,y,.85,12,op=cut)
 # Connector windows use native board coordinates. Front USB plug travels along Y.
 ux,uy=br['J2']['x']-75,69-br['J2']['y'];rect(c,'USB-C plug passage','XZ',-26,ux,94.2,11,5,8,1,cut)
 sx=br['SW1']['x']-75;rect(c,'Power slider access','XZ',18,sx,94,10,5,9,.7,cut)
 my=69-br['SW2']['y'];rect(c,'Mute slider access','YZ',-33,my,94,11,5,8,.7,cut)
 for x in [-25,25]:disk(c,'Loom exit '+str(x),'XZ',18,x,96,2.2,9,op=cut)
 for x,y in [(-27,-19),(27,-19),(-27,19),(27,19)]:disk(c,'Lid screw boss','XY',95,x,y,2,4.2,op=join);disk(c,'M2 lid pilot','XY',94,x,y,.85,7,op=cut)
 finish(c,'PA12')
 c=comp('06 Crown sculpted service lid','lid',(0,0,32));rect(c,'Rounded lid','XY',99.2,0,0,'CrownWidth','CrownLength',1.8,'CrownRadius')
 for x,y in [(-27,-19),(27,-19),(-27,19),(27,19)]:disk(c,'M2 lid clearance','XY',99,x,y,1.1,3,op=cut)
 finish(c,'lid')
 c=comp('07 Protected LiPo PACK - provisional 500mAh','steel',(0,-45,0));rect(c,'Protected pack envelope','XY',83.4,0,0,'BatteryWidth','BatteryLength','BatteryHeight',1.5);finish(c,'steel')
 c=comp('08 TPU battery cradle','TPU',(0,-45,-5));rect(c,'Battery cushion','XY',83,0,0,46.6,33.6,.4,1.9);finish(c,'TPU')
 c=comp('09 TPU battery retaining strap','TPU',(0,-45,9));rect(c,'Retention strap','XY',89.4,0,0,6,34,.6,.2);finish(c,'TPU')
 save()
 # Import actual KiCad electronics into independent components, no scaling.
 def importpcb(name,file,side=0):
  c=comp(name,'steel',(0,0,14) if not side else (side*15,0,0));opts=app.importManager.createSTEPImportOptions(str(R/'mechanical'/'step'/file));assert app.importManager.importToTarget(opts,c)
  m=C.Matrix3D.create()
  if not side:m.translation=C.Vector3D.create(-2.5,1.9,9.2)
  else:
   m.setWithCoordinateSystem(pt(side*85,side*12,5),C.Vector3D.create(0,0,-1),C.Vector3D.create(0,side,0),C.Vector3D.create(side,0,0))
  occs[name].transform2=m;c.attributes.add('BoneBuds','geometry_provenance','Unscaled KiCad STEP '+file);return c
 importpcb('10 ACTUAL KiCad controller 50x38','controller.step')
 for side,sg in [('right',1),('left',-1)]:
  importpcb(side+' ACTUAL KiCad audio 18x24','audio_'+side+'.step',sg)
  pl={v['reference']:v for v in json.loads((R/'documentation'/('audio_'+side+'_placement.json')).read_text())};mp=pl['U2'];mic_y=sg*(12-(mp['y']-50)+.58);mic_z=5-(mp['x']-50)
  c=comp(side+' PA12 acoustic pod',explode=(0,0,0));rect(c,'Organic pod outer','YZ',sg*73,0,-7,'PodWidth','PodHeight',sg*21.2,'PodRadius');rect(c,'Pod cavity','YZ',sg*74.8,0,-7,'PodWidth-2*Wall','PodHeight-2*Wall',sg*24,'PodRadius-Wall',cut);disk(c,'Transducer face opening','YZ',sg*71,0,-10,12.65,sg*8,op=cut)
  rect(c,'Integrated PCB support plate','YZ',sg*82.8,0,-3.5,30.6,23,sg*2.2,0,join);rect(c,'Support plate lightening','YZ',sg*82,0,-5,12,10,sg*5,1,cut)
  for ref in ['H1','H2']:
   p=pl[ref];yy=sg*(12-(p['y']-50));zz=5-(p['x']-50);disk(c,ref+' M2 PCB pilot','YZ',sg*82,yy,zz,.85,sg*6,op=cut)
  for yy,zz in [(-11,-22),(11,-22),(-11,7),(11,7)]:disk(c,'Service boss','YZ',sg*90,yy,zz,2,sg*4.2,op=join);disk(c,'M2 service pilot','YZ',sg*89,yy,zz,.85,sg*8,op=cut)
  # Top loom entry; vertical Z axis, not the transducer coupling axis.
  disk(c,'Protected loom entry','XY',11,sg*84,0,2.4,8,op=cut);finish(c,'PA12')
  c=comp(side+' PA12 service lid','lid',(sg*25,0,0));rect(c,'Rounded pod lid','YZ',sg*94.2,0,-7,'PodWidth','PodHeight',sg*1.8,'PodRadius');disk(c,'Microphone acoustic port','YZ',sg*93,mic_y,mic_z,.8,sg*5,op=cut)
  for yy,zz in [(-11,-22),(11,-22),(-11,7),(11,7)]:disk(c,'M2 clearance','YZ',sg*93,yy,zz,1.1,sg*5,op=cut)
  finish(c,'lid')
  c=comp(side+' Transducer 25x8 ENVELOPE','steel',(-sg*16,0,0));disk(c,'Rigid vibration contact','YZ',sg*72.6,0,-10,12.5,sg*8);finish(c,'steel')
  c=comp(side+' Rigid transducer retaining ring','PA12',(sg*9,0,0));disk(c,'Rear force-coupling ring','YZ',sg*80.6,0,-10,13.7,sg*1.8,10.2);finish(c,'PA12')
  c=comp(side+' TPU skin surround','TPU',(-sg*20,0,0));disk(c,'Compliant perimeter - active face exposed','YZ',sg*72.5,0,-10,15,sg*2.3,12.7);finish(c,'TPU')
  c=comp(side+' TPU microphone duct','TPU',(sg*12,0,0));disk(c,'Acoustic duct','YZ',sg*88.4,mic_y,mic_z,1.7,sg*5.8,.8);finish(c,'TPU')
  c=comp(side+' TPU strain relief','TPU');disk(c,'Loom strain relief','XY',12,sg*84,0,3,9,2);finish(c,'TPU')
  c=comp(side+' Stainless fit rail','steel',(0,0,20));rect(c,'Indexed adjustment rail','YZ',sg*82.7,0,25,8,32,sg*1.2,.6)
  for z in [15,20,25,30,35]:disk(c,'Fit indexing hole','YZ',sg*82,0,z,1,sg*4,op=cut)
  finish(c,'steel')
  c=comp(side+' PA12 slide collar');rect(c,'Rail guide','YZ',sg*80.5,0,19,12,20,sg*5.6,2);rect(c,'Captive rail slot','YZ',sg*82.5,0,19,8.4,22,sg*1.6,0,cut);disk(c,'Clamp screw','YZ',sg*80,0,22,1.1,sg*8,op=cut);finish(c,'PA12')
  c=comp(side+' Tactile L-R accent','accent');disk(c,'Accent medallion','YZ',sg*96,8,2,2.2,sg*.4);finish(c,'accent')
  save()
 app.activeViewport.fit();app.activeViewport.refresh();save()
 print('Native Fusion assembly complete:',root.occurrences.count,'components;',d.timeline.count,'timeline features')
