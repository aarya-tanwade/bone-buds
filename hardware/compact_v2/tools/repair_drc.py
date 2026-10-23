from libutil import *
R=Path(__file__).resolve().parents[1];p=R/'pcb'/'controller'/'controller.kicad_pcb';tree=parse(p.read_text())
remove={'24c84de0-3703-4645-99d2-3c42eadf0928','e9be15f5-0a36-4d6e-b96b-5c88d629b382','a031b57d-4565-470a-b3f3-b6941e6a412e','8c07f87e-ba81-49b4-bc24-72a6918330e2'}
tree=[x for x in tree if not(isinstance(x,list) and x[0]=='segment' and val(child(x,'uuid')[1]) in remove)];p.write_text(dump(tree));b=pcbnew.LoadBoard(str(p));fs={f.GetReference():f for f in b.GetFootprints()};mm=pcbnew.FromMM
def vec(x,y):return pcbnew.VECTOR2I(mm(x),mm(y))
def shift_vertex(old,new):
    for t in b.GetTracks():
        if isinstance(t,pcbnew.PCB_VIA):
            if t.GetPosition()==old:t.SetPosition(new)
        else:
            if t.GetStart()==old:t.SetStart(new)
            if t.GetEnd()==old:t.SetEnd(new)
for ref,newx in [('J1',52.4),('C14',55.3)]:
    f=fs[ref];delta=vec(newx-f.GetPosition().x/1e6,0);pairs=[(pp.GetPosition(),pp.GetPosition()+delta) for pp in f.Pads()];f.SetPosition(f.GetPosition()+delta)
    for old,new in pairs:shift_vertex(old,new)
t=next(t for t in b.GetTracks() if t.m_Uuid.AsString()=='944f79d6-007f-4d26-ae01-7dd620ddcd42');ends=[t.GetStart(),t.GetEnd()]
for old in ends:shift_vertex(old,old+vec(-.01,-.01))
net=next(pp.GetNet() for pp in fs['U1'].Pads() if pp.GetNumber()=='26')
for a,z in [((65.8,67.45),(65.8,68.4)),((65.8,68.4),(66.39,68.99)),((66.39,68.99),(66.6,68.99))]:
    t=pcbnew.PCB_TRACK(b);t.SetStart(vec(*a));t.SetEnd(vec(*z));t.SetLayer(pcbnew.F_Cu);t.SetWidth(mm(.15));t.SetNet(net);b.Add(t)
# Remove old continuation from 66.6,68.25 to R7; it is now a dangling stub but no electrical short.
pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(p),b)
(R/'documentation'/'controller_placement.json').write_text(json.dumps([{'reference':r,'x':f.GetPosition().x/1e6,'y':f.GetPosition().y/1e6,'rotation':f.GetOrientationDegrees()} for r,f in fs.items()],indent=2))
