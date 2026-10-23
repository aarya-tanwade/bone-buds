"""Bone Buds Rev B native KiCad source generator. KiCad 10 Python required.
Engineering prototype: RF matching, USB SI, thermal and purchased pack qualification pending.
"""
from libutil import *
import copy
ROOT=Path(__file__).resolve().parents[1]
CUSTOM=ROOT/'pcb'/'BoneBuds.pretty'; CUSTOM.mkdir(exist_ok=True)
micpins=[('1','GND','power_in'),('2','NC','no_connect'),('3','WS','input'),('4','CHIPEN','input'),('5','LR','input'),('6','SCK','input'),('7','SD','tri_state'),('8','VDD','power_in')]
def mic_symbol():
    s='(symbol "CMM4030" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27)))) (property "Value" "CMM-4030D-261-I2S-TR" (at 0 0 0) (effects (font (size 1.27 1.27)))) (symbol "CMM4030_0_1" (rectangle (start -7.62 12.7) (end 7.62 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "CMM4030_1_1" '
    for i,(num,name,typ) in enumerate(micpins):
        x=-12.7 if i<4 else 12.7;y=7.62-(i%4)*5.08;a=0 if i<4 else 180
        s+=f'(pin {typ} line (at {x} {y} {a}) (length 5.08) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))'
    return parse(s+'))')
# Datasheet bottom view mirrored to PCB top view. Pads enlarged 0.1 mm for assembly.
fp='(footprint "CMM4030" (version 20241229) (generator pcbnew) (layer "F.Cu") (attr smd) (fp_rect (start -1.5 -2) (end 1.5 2) (stroke (width 0.12) (type default)) (fill none) (layer "F.Fab")) (fp_rect (start -1.8 -2.3) (end 1.8 2.3) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))'
for num in range(1,9):
    x=.95 if num<5 else -.95;y=1.5-(num-1) if num<5 else -1.5+(num-5)
    fp+=f'(pad "{num}" smd rect (at {x} {y}) (size 1.0 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))'
fp+='(fp_circle (center 0 -0.58) (end 0.325 -0.58) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab")) (model "${KIPRJMOD}/../models/CMM4030.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))))'
(CUSTOM/'CMM4030.kicad_mod').write_text(fp)
mic=mic_symbol();(ROOT/'pcb'/'BoneBuds.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator kicad_symbol_editor) '+dump(mic)+')')
parts=[]
def add(ref,value,sym,fp,nets,xy,rot=0,side='F'):
    parts.append(dict(ref=ref,value=value,sym=sym,fp=fp,nets={str(i+1):n for i,n in enumerate(nets)} if isinstance(nets,list) else {str(k):v for k,v in nets.items()},xy=xy,rot=rot,side=side,uuid=uid()))
def r(ref,value,a,b,xy,rot=0):add(ref,value,'Device:R','Resistor_SMD:R_0402_1005Metric',[a,b],xy,rot)
def c(ref,value,a,xy,sz='0402_1005Metric',b='GND',rot=0):add(ref,value,'Device:C','Capacitor_SMD:C_'+sz,[a,b],xy,rot)
def ic(ref,sym,nets,xy,value=None,rot=0):
    s=symbol(*sym.split(':'));fp=val(next(p[2] for p in children(s,'property') if val(p[1])=='Footprint'));add(ref,value or sym.split(':')[1],sym,fp,nets,xy,rot)
def conn(ref,nets,xy,rot=0):
    n=len(nets);add(ref,'JST SH '+str(n)+'P','Connector_Generic:Conn_01x%02d'%n,f'Connector_JST:JST_SH_BM{n:02d}B-SRSS-TB_1x{n:02d}-1MP_P1.00mm_Vertical',nets,xy,rot)
def tp(ref,n,xy):add(ref,n,'Connector:TestPoint','TestPoint:TestPoint_Pad_D1.0mm',[n],xy)
def flag(net):
    add('#FLG'+str(len(parts)),'PWR_FLAG','power:PWR_FLAG','',{'1':net},(0,0))
bus=['SYS_SW','GND','3V3','AMP_BCLK','AMP_WS','AMP_DIN','MIC_BCLK','MIC_WS','MIC_SD','AUDIO_EN']

def main():
    global parts;parts=[]
    ic('U1','MCU_Espressif:ESP32-S3',{1:'RF_CHIP',2:'3V3_RF',3:'3V3_RF',4:'CHIP_EN',5:'BOOT',6:'BAT_ADC',9:'AMP_BCLK_SRC',10:'AMP_WS_SRC',11:'AMP_DIN_SRC',12:'MIC_BCLK_SRC',13:'MIC_WS_SRC',14:'MIC_SD',15:'AUDIO_GPIO',16:'USB_500_EN',17:'USER_KEY',20:'3V3',25:'USB_DN',26:'USB_DP',29:'VDD_SPI',30:'SPI_HD',31:'SPI_WP',32:'SPI_CS',33:'SPI_CLK',34:'SPI_Q',35:'SPI_D',46:'3V3',49:'UART_TX',50:'UART_RX',51:'STRAP45',52:'STRAP46',53:'XTAL_N',54:'XTAL_P',55:'3V3_RF',56:'3V3_RF',57:'GND'},(64,64),'ESP32-S3R8')
    ic('U2','Memory_Flash:W25Q128JVP',{1:'SPI_CS',2:'SPI_Q',3:'SPI_WP',4:'GND',5:'SPI_D',6:'SPI_CLK_FLASH',7:'SPI_HD',8:'VDD_SPI',9:'GND'},(77,64),'W25Q128JVPIQ / 16 MB')
    r('R1','33R','SPI_CLK','SPI_CLK_FLASH',(71.5,64));c('C1','100n','VDD_SPI',(72.5,61));c('C2','1u','VDD_SPI',(72.5,59.5))
    add('Y1','40MHz 10ppm CL8pF','Device:Crystal_GND24','Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm',{1:'XTAL_DRIVE',2:'GND',3:'XTAL_N',4:'GND'},(64,56))
    add('L1','24nH RF tuning','Device:L','Inductor_SMD:L_0402_1005Metric',['XTAL_P','XTAL_DRIVE'],(63,58))
    c('C3','12p C0G tune','XTAL_DRIVE',(62,55));c('C4','12p C0G tune','XTAL_N',(66,55))
    r('R2','10k','3V3','CHIP_EN',(59,59));c('C5','1u','CHIP_EN',(57,59))
    r('R3','10k','3V3','BOOT',(57,63));r('R4','100k','USB_500_EN','GND',(83,70))
    # Reset and boot are production test pads, short to GND for service.
    tp('TP1','BOOT',(53,63));tp('TP2','CHIP_EN',(53,66));tp('TP3','GND',(53,69));tp('TP4','UART_TX',(72,70));tp('TP5','UART_RX',(74,70))
    for i,(xy,n) in enumerate([((59,62),'3V3_RF'),((59,66),'3V3'),((64,69),'3V3'),((68,59),'3V3_RF'),((66,69),'VDD_SPI')],6):c('C'+str(i),'100n',n,xy)
    c('C11','10u','3V3_RF',(55,59),'0603_1608Metric');c('C12','22u','3V3',(68,72),'0805_2012Metric')
    add('FB1','BLM18AG601SN1 600R','Device:FerriteBead','Inductor_SMD:L_0603_1608Metric',['3V3','3V3_RF'],(57,56))
    # CLC RF matching seed, to be tuned on assembled hardware.
    c('C13','1.5p RF tune','RF_CHIP',(58,53));add('L2','2.4nH RF tune','Device:L','Inductor_SMD:L_0402_1005Metric',['RF_CHIP','RF_50'],(55.5,53));c('C14','1.5p RF tune','RF_50',(53.5,54.5))
    add('J1','U.FL 2.4GHz antenna','Connector:Conn_Coaxial','Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical',{1:'RF_50',2:'GND'},(52.5,52.5))
    usb={p:'GND' for p in ['A1','A12','B1','B12','SH']};usb.update({p:'VBUS' for p in ['A4','A9','B4','B9']});usb.update({'A5':'CC1','B5':'CC2','A6':'DP_ESD','B6':'DP_ESD','A7':'DN_ESD','B7':'DN_ESD'})
    add('J2','GCT USB4105-GF-A','Connector:USB_C_Receptacle_USB2.0_16P','Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',usb,(92,53),180)
    r('R5','5.1k 1%','CC1','GND',(86,53));r('R6','5.1k 1%','CC2','GND',(86,55))
    ic('U3','Power_Protection:USBLC6-2SC6',{1:'DP_ESD',2:'GND',3:'DN_ESD',4:'DN_ESD',5:'VBUS',6:'DP_ESD'},(89,60))
    r('R7','22R','DP_ESD','USB_DP',(84,62));r('R8','22R','DN_ESD','USB_DN',(84,64))
    ic('U4','Battery_Management:BQ24074RGT',{1:'BAT_NTC',2:'BAT',3:'BAT',4:'GND',5:'GND',6:'USB_500_EN',7:'PGOOD',8:'GND',9:'CHG',10:'SYS',11:'SYS',12:'ILIM',13:'VBUS',16:'ISET',17:'GND'},(90,75))
    r('R9','3.57k 1% 249mA','ISET','GND',(87,73));r('R10','3.48k 1%','ILIM','GND',(87,76))
    c('C15','4.7u 10V','VBUS',(94,72),'0603_1608Metric');c('C16','4.7u 10V','BAT',(94,75),'0603_1608Metric');c('C17','10u 10V','SYS',(90,79),'0805_2012Metric')
    conn('J3',['BAT','GND','BAT_NTC'],(94,84));tp('TP6','BAT',(97,78));tp('TP7','SYS',(97,80))
    ic('U5','Power_Management:TPS22917DBV',{1:'SYS',2:'GND',3:'PWR_ON',4:'CT',5:'QOD',6:'SYS_SW'},(81,79))
    c('C18','1n','CT',(78,79));c('C19','10u','SYS_SW',(82,74),'0805_2012Metric');r('R11','100k','PWR_ON','GND',(78,81))
    add('SW1','POWER','Switch:SW_SPDT','Button_Switch_SMD:SW_SPDT_PCM12',{1:'SYS',2:'PWR_ON',3:'GND'},(86,85))
    ic('U6','Regulator_Switching:TPS63031DSK',{1:'3V3',2:'BUCK_L2',3:'GND',4:'BUCK_L1',5:'SYS_SW',6:'SYS_SW',7:'SYS_SW',8:'SYS_SW',9:'GND',10:'3V3',11:'GND'},(74,78))
    add('L3','1.5uH >=2A DCR<100m','Device:L','Inductor_SMD:L_Wuerth_MAPI-3015',['BUCK_L1','BUCK_L2'],(74,82))
    c('C20','10u','SYS_SW',(77.5,75),'0805_2012Metric');c('C21','100n','SYS_SW',(76,77));c('C22','10u','3V3',(71,77),'0805_2012Metric');c('C23','10u','3V3',(71,80),'0805_2012Metric')
    ic('U7','Power_Supervisor:TPS3839DBZ',{1:'GND',2:'RESET_SUP',3:'3V3'},(59,72),'TPS3839K33DBZR / 3.08V')
    # Supervisor push-pull isolated from service reset by diode, active low can discharge CHIP_EN.
    add('D1','BAT54H','Device:D_Schottky','Diode_SMD:D_SOD-323',{1:'RESET_SUP',2:'CHIP_EN'},(59,69))
    r('R12','1M','BAT','BAT_ADC',(84,67));r('R13','330k','BAT_ADC','GND',(84,69));c('C24','100n','BAT_ADC',(86,68))
    for i,(a,b,xy) in enumerate([('AMP_BCLK_SRC','AMP_BCLK',(68,65)),('AMP_WS_SRC','AMP_WS',(68,63.5)),('AMP_DIN_SRC','AMP_DIN',(68,62)),('MIC_BCLK_SRC','MIC_BCLK',(59,64)),('MIC_WS_SRC','MIC_WS',(59,67.5))],14):r('R'+str(i),'33R',a,b,xy)
    r('R19','100k','MIC_SD','GND',(62,72));r('R20','100k','AUDIO_GPIO','GND',(64,73))
    add('SW2','MUTE / PLAY','Switch:SW_SPDT','Button_Switch_SMD:SW_SPDT_PCM12',{1:'AUDIO_GPIO',2:'AUDIO_EN',3:'GND'},(54,74),90)
    conn('J4',bus,(59,83));conn('J5',bus,(79,53),180)
    conn('J6',['USER_KEY','GND'],(97,66));r('R21','10k','USER_KEY','3V3',(94,65))
    tp('TP8','3V3',(69,83));tp('TP9','CHG',(92,68));tp('TP10','PGOOD',(94,68))
    r('R22','10k','STRAP45','GND',(70,58));r('R23','10k','STRAP46','GND',(70,56));r('R24','100R','QOD','SYS_SW',(81,82))
    for n in ['GND','VBUS','VDD_SPI','3V3_RF']:flag(n)
    save('controller',50,38,[(52,81),(97,86)])

def audio(side):
    global parts;parts=[]
    conn('J1',bus,(59,53),180)
    ic('U1','Audio:MAX98357A',{1:'AMP_DIN',2:'GAIN',3:'GND',4:'SD_MODE',7:'SYS_SW',8:'SYS_SW',9:'OUT_P',10:'OUT_N',11:'GND',14:'AMP_WS',15:'GND',16:'AMP_BCLK',17:'GND'},(57,61))
    add('U2','CMM-4030D-261-I2S-TR','BoneBuds:CMM4030','BoneBuds:CMM4030',{1:'GND',3:'MIC_WS',4:'3V3',5:'GND' if side=='left' else '3V3',6:'MIC_BCLK',7:'MIC_SD',8:'3V3'},(64,67))
    r('R1','2k' if side=='left' else '210k 1%','AUDIO_EN','SD_MODE',(53.5,61));r('R2','100k / 3dB','SYS_SW','GAIN',(53.5,63))
    c('C1','100n','SYS_SW',(59,58.5));c('C2','22u 10V','SYS_SW',(62,59),'0805_2012Metric');c('C3','100n','3V3',(61,65));c('C4','10u','3V3',(61,67),'0603_1608Metric')
    # Ferrite output EMC filter for the short BTL pair; no output is grounded.
    add('FB1','BLM18PG121SN1','Device:FerriteBead','Inductor_SMD:L_0603_1608Metric',['OUT_P','SPK_P'],(55,65))
    add('FB2','BLM18PG121SN1','Device:FerriteBead','Inductor_SMD:L_0603_1608Metric',['OUT_N','SPK_N'],(57.5,65))
    c('C5','1n C0G','SPK_P',(53,67));c('C6','1n C0G','SPK_N',(56,67));conn('J2',['SPK_P','SPK_N'],(55,70))
    tp('TP1','GND',(65,59));tp('TP2','SD_MODE',(65,61))
    for n in ['GND','SYS_SW','3V3']:flag(n)
    save('audio_'+side,18,24,[(52,57),(66,72)])

def save(name,w,h,holes):
    dest=ROOT/'pcb'/name;rootid=uid();libs={};inst=[]
    import sys
    if '--schematic-only' in sys.argv:
        old=pcbnew.LoadBoard(str(dest/(name+'.kicad_pcb')));refs={f.GetReference():f for f in old.GetFootprints()}
        for p in parts:
            if p['ref'] in refs:
                path=refs[p['ref']].GetPath().AsString().strip('/').split('/');rootid=path[0];p['uuid']=path[-1]
    # Native labelled schematic. ICs occupy the large first row; passives subsequent rows.
    ordered=sorted(parts,key=lambda p:0 if p['ref'].startswith('U') else 1)
    for i,p in enumerate(ordered):
        lib,sn=p['sym'].split(':');s=copy.deepcopy(mic) if lib=='BoneBuds' else symbol(lib,sn);s[1]=q(p['sym']);libs[p['sym']]=s
        pins=[pin for u in children(s,'symbol') for pin in children(u,'pin')]
        x=50.8+(i%8)*139.7;y=91.44+(i//8)*68.58
        out=f'(symbol (lib_id {q(p["sym"])}) (at {x} {y} 0) (unit 1) (in_bom {"yes" if p["fp"] else "no"}) (on_board {"yes" if p["fp"] else "no"}) (dnp no) (uuid {p["uuid"]})'
        for key,txt,dy in [('Reference',p['ref'],-43.18),('Value',p['value'],-40.64),('Footprint',p['fp'],0)]:out+=f'(property {q(key)} {q(txt)} (at {x-25.4} {y+dy} 0) (effects (font (size 1.27 1.27)) (justify left) {"(hide yes)" if key=="Footprint" else ""}))'
        for pin in pins:out+=f'(pin {child(pin,"number")[1]} (uuid {uid()}))'
        out+=f'(instances (project {q(name)} (path "/{rootid}" (reference {q(p["ref"])}) (unit 1)))))';inst.append(out)
        for pin in pins:
            num=val(child(pin,'number')[1]);at=child(pin,'at');px,py,a=map(float,at[1:]);sx=round(x+px,4);sy=round(y-py,4);net=p['nets'].get(num)
            if not net:inst.append(f'(no_connect (at {sx} {sy}) (uuid {uid()}))');continue
            # Horizontal labels on horizontal pins; stagger vertical pin labels to avoid overlaps.
            ex=round(sx-math.cos(math.radians(a))*7.62,4);ey=round(sy+math.sin(math.radians(a))*7.62,4)
            inst.append(f'(wire (pts (xy {sx} {sy}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid()}))')
            la=90 if a in [90,270] else 0
            inst.append(f'(label {q(net)} (at {ex} {ey} {la}) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid {uid()}))')
    notes=[f'BONE BUDS REV B | {name.upper()} | BARE IC ENGINEERING PROTOTYPE',
      'RF matching, impedance, USB signal integrity, acoustic performance and cell safety require engineering qualification.',
      'Controller requires protected 1S 4.2V LiPo pack + 10k NTC. USB defaults 100mA; firmware may select 500mA ONLY after enumeration.',
      'Audio: 64 clocks per stereo frame. Separate microphone input and amplifier output I2S buses. BTL speaker terminals must never be grounded.']
    for j,t in enumerate(notes):inst.append(f'(text {q(t)} (at 15.24 {12.7+j*5.08} 0) (effects (font (size 1.6 1.6)) (justify left)) (uuid {uid()}))')
    sch=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {rootid}) (paper "A0") (title_block (title "Bone Buds Rev B - {name}") (date "2026-10-23") (rev "B EVT / qualification pending")) (lib_symbols '+''.join(dump(s) for s in libs.values())+')'+''.join(inst)+')'
    (dest/(name+'.kicad_sch')).write_text(sch,encoding='utf8')
    (dest/'sym-lib-table').write_text('(sym_lib_table (version 7)'+''.join(f'(lib (name "{l}") (type "KiCad") (uri "${{KICAD10_SYMBOL_DIR}}/{l}.kicad_sym") (options "") (descr ""))' for l in sorted({p['sym'].split(':')[0] for p in parts if not p['sym'].startswith('BoneBuds')}))+'(lib (name "BoneBuds") (type "KiCad") (uri "${KIPRJMOD}/../BoneBuds.kicad_sym") (options "") (descr "Manufacturer drawing derived")))')
    (dest/'fp-lib-table').write_text('(fp_lib_table (version 7)(lib (name "BoneBuds") (type "KiCad") (uri "${KIPRJMOD}/../BoneBuds.pretty") (options "") (descr "Manufacturer drawing derived")))')
    if '--schematic-only' in sys.argv:return
    b=pcbnew.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.0));nets={}
    for n in sorted({n for p in parts for n in p['nets'].values()}):ni=pcbnew.NETINFO_ITEM(b,'/'+n);b.Add(ni);nets[n]=ni
    for p in parts:
        if not p['fp']:continue
        lib,fn=p['fp'].split(':');f=pcbnew.FootprintLoad(str(CUSTOM if lib=='BoneBuds' else LIB/'footprints'/(lib+'.pretty')),fn)
        if not f:raise RuntimeError(p['fp'])
        f.SetReference(p['ref']);f.SetValue(p['value']);f.SetFPID(pcbnew.LIB_ID(lib,fn));f.SetPath(pcbnew.KIID_PATH('/'+rootid+'/'+p['uuid']));b.Add(f);f.SetPosition(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in p['xy']]));f.SetOrientationDegrees(p['rot'])
        f.SetAttributes(f.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
        for pad in f.Pads():
            n=p['nets'].get(pad.GetNumber());
            if n:pad.SetNet(nets[n])
        f.Value().SetVisible(False);f.Reference().SetVisible(False)
    for i,(x,y) in enumerate(holes,1):
        f=pcbnew.FootprintLoad(str(LIB/'footprints'/'MountingHole.pretty'),'MountingHole_2.2mm_M2');f.SetReference('H'+str(i));f.SetAttributes(f.GetAttributes()|pcbnew.FP_BOARD_ONLY);b.Add(f);f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)));f.Reference().SetVisible(False);f.Value().SetVisible(False)
    for a,z in [((50,50),(50+w,50)),((50+w,50),(50+w,50+h)),((50+w,50+h),(50,50+h)),((50,50+h),(50,50))]:
        d=pcbnew.PCB_SHAPE();d.SetShape(pcbnew.SHAPE_T_SEGMENT);d.SetStart(pcbnew.VECTOR2I(*[pcbnew.FromMM(t) for t in a]));d.SetEnd(pcbnew.VECTOR2I(*[pcbnew.FromMM(t) for t in z]));d.SetLayer(pcbnew.Edge_Cuts);d.SetWidth(pcbnew.FromMM(.05));b.Add(d)
    pcbnew.SaveBoard(str(dest/(name+'.kicad_pcb')),b)
    pro=json.loads((dest/(name+'.kicad_pro')).read_text())
    pro['net_settings']={'classes':[{'name':'Default','clearance':.127,'track_width':.15,'via_diameter':.45,'via_drill':.2,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.15,'diff_pair_gap':.15,'diff_pair_via_gap':.25}], 'netclass_assignments':{},'netclass_patterns':[]}
    pro.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{}).update({'min_clearance':.127,'min_track_width':.127,'min_via_diameter':.45,'min_through_hole_diameter':.2,'min_hole_to_hole':.25,'min_copper_edge_clearance':.25})
    (dest/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2));(ROOT/'documentation'/(name+'_design.json')).write_text(json.dumps({'name':name,'width':w,'height':h,'holes':holes,'parts':parts},indent=2))
    print(name,len(parts),'symbols',w,h)
if __name__=='__main__':main();audio('left');audio('right')



