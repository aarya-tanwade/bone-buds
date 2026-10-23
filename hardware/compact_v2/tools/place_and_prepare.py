from pathlib import Path
import pcbnew,json,subprocess,xml.etree.ElementTree as ET,math
R=Path(__file__).resolve().parents[1];mm=pcbnew.FromMM;CLI=r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
def rect(f):
    gs=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer()==pcbnew.F_CrtYd]
    if not gs:gs=[p.GetBoundingBox() for p in f.Pads()]
    return [min(g.GetLeft() for g in gs)/1e6,min(g.GetTop() for g in gs)/1e6,max(g.GetRight() for g in gs)/1e6,max(g.GetBottom() for g in gs)/1e6]
def overlap(a,b):return a[0]<b[2]+.08 and a[2]>b[0]-.08 and a[1]<b[3]+.08 and a[3]>b[1]-.08
for name in ['controller','audio_left','audio_right']:
    d=R/'pcb'/name;p=d/(name+'.kicad_pcb');b=pcbnew.LoadBoard(str(p));data=json.loads((R/'documentation'/(name+'_design.json')).read_text());W,H=data['width'],data['height'];fs=list(b.GetFootprints());placed=[]
    # Place mechanical constraints first, then ICs and passives using closest legal courtyard.
    fs.sort(key=lambda f: (0 if f.GetReference().startswith(('J','SW','H')) else 1 if f.GetReference().startswith(('U','Y','L')) else 2))
    moves=[]
    for f in fs:
        x,y=f.GetPosition().x/1e6,f.GetPosition().y/1e6;box=rect(f);found=False
        candidates=[(0,0)]+sorted([(a*.25,z*.25) for a in range(-48,49) for z in range(-48,49) if a or z],key=lambda a:a[0]*a[0]+a[1]*a[1])
        for dx,dy in candidates:
            bb=[box[0]+dx,box[1]+dy,box[2]+dx,box[3]+dy]
            margin=.1
            # USB shell may project beyond board edge; actual pads must remain inside.
            if min(bb[0],bb[1])<50+margin or bb[2]>50+W-margin or bb[3]>50+H-margin:continue
            if any(overlap(bb,a) for a in placed):continue
            f.SetPosition(pcbnew.VECTOR2I(mm(x+dx),mm(y+dy)));placed.append(bb);moves.append({'reference':f.GetReference(),'x':x+dx,'y':y+dy,'rotation':f.GetOrientationDegrees()});found=True;break
        if not found:raise RuntimeError('No legal position '+name+' '+f.GetReference())
    (R/'documentation'/(name+'_placement.json')).write_text(json.dumps(moves,indent=2))
    # Export native schematic netlist and use its exact NC names too; no parity suppression.
    net=d/(name+'.net');subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(net),str(d/(name+'.kicad_sch'))],check=True)
    netmap={};root=ET.parse(net).getroot()
    for n in root.findall('./nets/net'):
        nn=n.attrib['name'];obj=b.FindNet(nn)
        if not obj or not hasattr(obj,'GetNetCode') or obj.GetNetCode()<0:
            obj=pcbnew.NETINFO_ITEM(b,nn);b.Add(obj)
        for nod in n.findall('node'):netmap[(nod.attrib['ref'],nod.attrib['pin'])]=obj
    for f in fs:
        for pad in f.Pads():
            n=netmap.get((f.GetReference(),pad.GetNumber()))
            if n is not None:pad.SetNet(n)
    # Route outer layers only; restore 4 layers with uninterrupted inner ground planes afterward.
    b.SetCopperLayerCount(2);pcbnew.SaveBoard(str(p),b)
    pro=json.loads((d/(name+'.kicad_pro')).read_text());power=dict(pro['net_settings']['classes'][0]);power.update(name='Power',track_width=.3)
    pro['net_settings']['classes'].append(power);pro['net_settings']['netclass_patterns']=[{'netclass':'Power','pattern':'/'+n} for n in ['VBUS','BAT','SYS','SYS_SW','3V3','BUCK_L1','BUCK_L2','OUT_P','OUT_N','SPK_P','SPK_N']]
    (d/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2));print(name,'legalized',len(fs),'footprints',flush=True)
