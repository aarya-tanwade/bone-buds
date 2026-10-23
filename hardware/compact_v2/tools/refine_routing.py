from libutil import *
import sys,subprocess
R=Path(__file__).resolve().parents[1];mm=pcbnew.FromMM
def pos(x,y):return pcbnew.VECTOR2I(mm(x),mm(y))
name='controller';path=R/'pcb'/name/(name+'.kicad_pcb');tree=parse(path.read_text()); tree=[n for n in tree if not (isinstance(n,list) and n[0] in ['segment','via'])]; path.write_text(dump(tree)); b=pcbnew.LoadBoard(str(path));fs={f.GetReference():f for f in b.GetFootprints()}
fixed={'U1':(64,64,0),'J1':(53,61.4,180),'C13':(58.5,60.92,90),'L2':(56.9,61.4,180),'C14':(55.8,60.92,90),'R8':(65.4,69.5,90),'R7':(66.6,69.5,90)}
for ref,(x,y,rot) in fixed.items():fs[ref].SetPosition(pos(x,y));fs[ref].SetOrientationDegrees(rot)
def rect(f):
    gs=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer()==pcbnew.F_CrtYd]
    if not gs:gs=[p.GetBoundingBox() for p in f.Pads()]
    return [min(g.GetLeft() for g in gs)/1e6,min(g.GetTop() for g in gs)/1e6,max(g.GetRight() for g in gs)/1e6,max(g.GetBottom() for g in gs)/1e6]
def overlaps(a,z):return a[0]<z[2]+.05 and a[2]>z[0]-.05 and a[1]<z[3]+.05 and a[3]>z[1]-.05
placed=[rect(fs[r]) for r in fixed]
for f in sorted([f for r,f in fs.items() if r not in fixed],key=lambda f:0 if f.GetReference().startswith(('U','J','SW','H','Y','L')) else 1):
    x,y=f.GetPosition().x/1e6,f.GetPosition().y/1e6;bb=rect(f)
    candidates=[(0,0)]+sorted([(a*.25,c*.25) for a in range(-40,41) for c in range(-40,41) if a or c],key=lambda z:z[0]**2+z[1]**2)
    for dx,dy in candidates:
        v=[bb[0]+dx,bb[1]+dy,bb[2]+dx,bb[3]+dy]
        if min(v[:2])<50.1 or v[2]>99.9 or v[3]>87.9 or any(overlaps(v,z) for z in placed):continue
        f.SetPosition(pos(x+dx,y+dy));placed.append(v);break
    else:raise RuntimeError('No space '+f.GetReference())
def pad(r,n):return next(p for p in fs[r].Pads() if p.GetNumber()==str(n))
def track(p1,p2,net,width=.18):
    t=pcbnew.PCB_TRACK(b);t.SetStart(pos(*p1));t.SetEnd(pos(*p2));t.SetWidth(mm(width));t.SetLayer(pcbnew.F_Cu);t.SetNet(pad('U1',1).GetNet() if net=='RF_CHIP' else b.FindNet('/'+net));t.SetLocked(True);b.Add(t)
def xy(p):return(p.GetPosition().x/1e6,p.GetPosition().y/1e6)
# No vias on the LNA matching path. Nominal 50 ohm width uses 0.1mm FR4 separation;
# fabricator must solve final impedance, CLC needs conducted RF tuning.
for r,n,r2,n2 in [('U1',1,'C13',1),('C13',1,'L2',1),('L2',2,'C14',1),('C14',1,'J1',1)]:
    p=pad(r,n);track(xy(p),xy(pad(r2,n2)),p.GetNetname().strip('/'))
track(xy(pad('U1',25)),xy(pad('R8',2)),'USB_DN',.15)
track(xy(pad('U1',26)),(66.6,68.25),'USB_DP',.15);track((66.6,68.25),xy(pad('R7',2)),'USB_DP',.15)
pcbnew.SaveBoard(str(path),b)
(R/'documentation'/'controller_placement.json').write_text(json.dumps([{'reference':r,'x':f.GetPosition().x/1e6,'y':f.GetPosition().y/1e6,'rotation':f.GetOrientationDegrees()} for r,f in fs.items()],indent=2))
pcbnew.ExportSpecctraDSN(b,str(path.with_suffix('.dsn')))
print('Critical RF and USB fanout manually placed/routed; remaining nets exported.',flush=True)

