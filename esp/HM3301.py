'''
    Datei für das Messen und Umwandeln der Rohwerte vom Feinstaub.
    Dies ist möglich in den Größen 2,5; 5 und 10 Mikrometer.
    Zurückgegebener Wert ist ug/m^3
    Datenblatt: 
    Originalbibliothek: "bitte eingeben"
'''
import time
from machine import Pin, SoftI2C

# HM3301 I2C Addresse
HM3301_ADDR = 0x40

# Befehl zum 'aktiv' setzen
HM3301_CMD_ACTIVE = bytearray([0x01, 0x02])

# Befehl zum Lesen
HM3301_CMD_READ_PARTICLES = bytearray([0x05, 0x03, 0x00, 0x00])

# Initialisieren des I2C Bus
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# 'aktiv' setzen des Sensors, überflüssig?
#i2c.writeto(HM3301_ADDR, HM3301_CMD_ACTIVE)

class HM3301Sensor:
    def __init__(self):        
        # 30s warm laufen lassen
        time.sleep(30)

    def measure(self, i2c):    
        # Auslesen der Daten vom HM3301
        i2c.writeto(HM3301_ADDR, HM3301_CMD_READ_PARTICLES)
        data = i2c.readfrom(HM3301_ADDR, 29)

        # Rohdaten in Konzentrationen umwandeln
        # pm1p0_cf1 = data[4] * 256 + data[5]
        # gemessen werden nur Partikel der Größe 5 Mikrometer
        pm2p5_cf1 = data[6] * 256 + data[7]
        # pm10_cf1 = data[8] * 256 + data[9]

        #print("PM1.0 (CF=1): {} ug/m^3".format(pm1p0_cf1))
        #print("PM2.5 (CF=1): {} ug/m^3".format(pm2p5_cf1)) von uns beachteter Wert
        #print("PM10 (CF=1): {} ug/m^3".format(pm10_cf1))
        
        return pm2p5_cf1
        