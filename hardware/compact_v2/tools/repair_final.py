from libutil import *
p=ROOT/'pcb'/'controller'/'controller.kicad_pcb';a=parse(p.read_text());ids={'00b0101d-7933-4839-b99b-5e85fafea111','23332414-bd77-41c5-bfe3-4a44c0ba9a66','19b18233-4616-438f-aee4-d073709656db','1cf44419-9a8f-456a-902c-259893304c12','d63f6de2-fee3-4977-88a2-98bb12a52f7d'};a=[x for x in a if not(isinstance(x,list) and x[0]=='segment' and val(child(x,'uuid')[1]) in ids)];p.write_text(dump(a));b=pcbnew.LoadBoard(str(p));fs={f.GetReference():f for f in b.GetFootprints()}
for ref,dx in [('C14',.2),('L2',.1)]:
 f=fs[ref];dv=pcbnew.VECTOR2I(pcbnew.FromMM(dx),0);old=[(pp.GetPosition(),pp.GetPosition()+dv) for pp in f.Pads()];f.SetPosition(f.GetPosition()+dv)
 for a,z in old:
  for t in b.GetTracks():
   if not isinstance(t,pcbnew.PCB_VIA):
    if t.GetStart()==a:t.SetStart(z)
    if t.GetEnd()==a:t.SetEnd(z)
for pp in fs['C6'].Pads():
 if pp.GetNumber()=='2':pp.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(p),b)
(ROOT/'documentation'/'controller_placement.json').write_text(json.dumps([{'reference':r,'x':f.GetPosition().x/1e6,'y':f.GetPosition().y/1e6,'rotation':f.GetOrientationDegrees()} for r,f in fs.items()],indent=2))
