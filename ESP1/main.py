from machine import Pin, ADC
from time import sleep
import umqtt_robust2 as mqtt
import tm1637
from micropyGPS import MicropyGPS
from machine import UART
import gps_funktion
import math

analog_pin = ADC(Pin(34))
analog_pin.atten(ADC.ATTN_11DB)
analog_pin.width(ADC.WIDTH_12BIT)

tm = tm1637.TM1637(clk=Pin(2), dio=Pin(0))
tm.write([0x00, 0x00, 0x00, 0x00])

vibe = Pin(5, Pin.OUT, value = 0)

def vibestarter():
        vibe.value(1)
        sleep(0.3)
        vibe.value(0)
        sleep(0.3)
        vibe.value(1)
        sleep(0.3)
        vibe.value(0)
        sleep(0.3)
        vibe.value(1)
        sleep(0.3)
        vibe.value(0)



GC_x = 55.706276
GC_y = 12.539559


R = 0.0003

while True:
    try:
# Jeres kode skal starte her

#Her sender vi data fra GPS'en til adafruit via mqtt.web_printet. Data sendes til et feed oprettet i Adafruit.
        sleep(3)
        # Denne variabel vil have GPS data når den har fået kontakt til sattellitterne ellers vil den være None
        gps_data = gps_funktion.gps_to_adafruit
        print(f"\ngps_data er: {gps_data}")
        
        #For at sende beskeder til andre feeds kan det gøres sådan:
        #Indsæt eget username og feednavn til så det svarer til dit eget username og feed du har oprettet
        #mqtt.web_print(gps_data, 'Tomtsi/feeds/iot_feed')
        
        #For at vise lokationsdata på adafruit dashboard skal det sendes til feed med /csv til sidst
        #For at sende til GPS lokationsdata til et feed kaldet mapfeed kan det gøres således:
        mqtt.web_print(gps_data, 'Tomtsi/feeds/mapfeed/csv')        
        sleep(3) # vent mere end 3 sekunder mellem hver besked der sendes til adafruit
        
        #mqtt.web_print("test1") # Hvis der ikke angives et 2. argument vil default feed være det fra credentials filen      
        sleep(3)  # vent mere end 3 sekunder mellem hver besked der sendes til adafruit
        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
        print(".", end = '') # printer et punktum til shell, uden et enter 

#Her sender vi batteridata til adafruit. Husk at vi gange med 5 eftersom at spændingsdeleren nedsætter spændingen med 1/5.

        if gps_data == None:
            print("Geofence loading...")
        else:
            raw_data = gps_data.split(",")
            COOR_x = float(raw_data[1])
            COOR_y = float(raw_data[2])
        
            print(COOR_x)
            a = GC_x - COOR_x
            b = GC_y - COOR_y
        
            a = abs(a)
            b = abs(b)
        
            c = math.sqrt((b**2) + (a**2))
            print(c)
        
            if c >= R:
                print("Out of bounds")
                vibestarter()
                mqtt.web_print("ude_for_zone")
            if c < R:
                print("Inbounds")
                mqtt.web_print("inde_for_zone")
        sleep(3)
               
        analog_val = analog_pin.read()
        m_spaending = analog_val/4095*3.3 #4095 er BAUD max værdien for ESP analog måling, og 3.3 er spændingen på ESP analog 3.3Vpin. m_spaending = målt spænding.
        print("Analog maalt vaerdi: ", m_spaending)
        spaending = m_spaending * 5
        print("Input spaending: ", spaending)
        battery_percentage = spaending/7.9 *100  #7,9 er vores max spænding for alle batterier tilsammen i serie (2 LiPo Batterier)fratrukket -0,5 fra dioden.
        battery_percentage = int(battery_percentage)
        print("the battery percentage is:", battery_percentage, "%")
        tm.show(str(battery_percentage))
        mqtt.web_print(battery_percentage)
        sleep(3)
        
        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
        print(".", end = '') # printer et punktum til shell, uden et enter        
    # Stopper programmet når der trykkes Ctrl + c
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()
        

