from libutil import *
import sys
R=Path(__file__).resolve().parents[1];mm=pcbnew.FromMM
def p(x,y):return pcbnew.VECTOR2I(mm(x),mm(y))
for name in sys.argv[1:] or ['controller','audio_left','audio_right']:
    path=R/'pcb'/name/(name+'.kicad_pcb');b=pcbnew.LoadBoard(str(path));b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(mm(1));fs={f.GetReference():f for f in b.GetFootprints()};g=next(p.GetNet() for f in fs.values() for p in f.Pads() if p.GetNetname()=='/GND')
    # 5mil minimum copper width; verify clearance again after adjusting router neckdowns.
    for t in b.GetTracks():
        if not isinstance(t,pcbnew.PCB_VIA) and t.GetWidth()<mm(.127):t.SetWidth(mm(.127))
    W,H=(50,38) if name=='controller' else (18,24)
    for layer in [pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]:
        z=pcbnew.ZONE(b);z.SetLayer(layer);z.SetNet(g);z.SetLocalClearance(mm(.127));z.SetThermalReliefGap(mm(.15));z.SetThermalReliefSpokeWidth(mm(.15));z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if layer in [pcbnew.In1_Cu,pcbnew.In2_Cu] else pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetMinThickness(mm(.127));o=z.Outline();o.NewOutline()
        for x,y in [(50.3,50.3),(50+W-.3,50.3),(50+W-.3,50+H-.3),(50.3,50+H-.3)]:o.Append(mm(x),mm(y))
        b.Add(z)
    # EP ground stitching, tented 0.20mm drills. Placement screened against both outer layers.
    def segdist(x,y,t):
        a=t.GetStart();e=t.GetEnd();ax=a.x/1e6;ay=a.y/1e6;dx=(e.x-a.x)/1e6;dy=(e.y-a.y)/1e6
        u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
        return math.hypot(x-ax-u*dx,y-ay-u*dy)
    added=[]
    refs=['U1','U4','U6'] if name=='controller' else ['U1']
    for ref in refs:
        f=fs[ref];ep=max([pp for pp in f.Pads() if pp.GetNetname()=='/GND'],key=lambda pp:pp.GetSize().x*pp.GetSize().y);x0=ep.GetPosition().x/1e6;y0=ep.GetPosition().y/1e6
        for dx,dy in [(0,0),(-.6,-.6),(.6,.6),(-.6,.6),(.6,-.6)]:
            x=x0+dx;y=y0+dy
            if abs(dx)+.225>ep.GetSize().x/2e6 or abs(dy)+.225>ep.GetSize().y/2e6:continue
            if any(t.GetNetname()!='/GND' and segdist(x,y,t)<.225+(t.GetWidth(pcbnew.F_Cu) if isinstance(t,pcbnew.PCB_VIA) else t.GetWidth())/2e6+.127 for t in b.GetTracks()):continue
            v=pcbnew.PCB_VIA(b);v.SetPosition(p(x,y));v.SetWidth(mm(.45));v.SetDrill(mm(.2));v.SetViaType(pcbnew.VIATYPE_THROUGH);v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(g);b.Add(v);added.append((x,y))
        ep.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
    text=pcbnew.PCB_TEXT(b);text.SetText('BONE BUDS B' if name=='controller' else ('B-L' if name.endswith('left') else 'B-R'));text.SetLayer(pcbnew.B_SilkS);text.SetMirrored(True);text.SetPosition(p(50+W/2,50+H/2));text.SetTextSize(p(.8,.8));text.SetTextThickness(mm(.12));b.Add(text)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(path),b)
    tree=parse(path.read_text());setup=child(tree,'setup');old=child(setup,'stackup')
    if old:setup.remove(old)
    setup.append(parse('(stackup (layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01)) (layer "F.Cu" (type "copper") (thickness 0.035)) (layer "dielectric 1" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.2) (loss_tangent 0.02)) (layer "In1.Cu" (type "copper") (thickness 0.035)) (layer "dielectric 2" (type "core") (thickness 0.66) (material "FR4") (epsilon_r 4.2) (loss_tangent 0.02)) (layer "In2.Cu" (type "copper") (thickness 0.035)) (layer "dielectric 3" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.2) (loss_tangent 0.02)) (layer "B.Cu" (type "copper") (thickness 0.035)) (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01)) (layer "B.SilkS" (type "Bottom Silk Screen")) (copper_finish "ENIG") (dielectric_constraints yes))'))
    path.write_text(dump(tree));print(name,'4 layers, 1.0mm nominal core stack, inner GND planes, EP vias',added,flush=True)

