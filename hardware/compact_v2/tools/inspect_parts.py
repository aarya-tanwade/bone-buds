from libutil import *
items=['MCU_Espressif:ESP32-S3','Audio:MAX98357A','Battery_Management:BQ24074RGT','Regulator_Switching:TPS63031DSK','Memory_Flash:W25Q128JVE','Sensor_Audio:ICS-43434','Power_Protection:USBLC6-2SC6','Power_Management:TPS22917DBV','Connector:USB_C_Receptacle_USB2.0_16P']
for item in items:
 lib,name=item.split(':');s=symbol(lib,name)
 props={val(p[1]):val(p[2]) for p in children(s,'property')}
 pins=[(val(child(p,'number')[1]),val(child(p,'name')[1]),p[1]) for sub in children(s,'symbol') for p in children(sub,'pin')]
 print(item,props.get('Footprint'),pins)
