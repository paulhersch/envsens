
#plus rot in 41board
# minus in gnd

from machine import Pin, deepsleep
from time import sleep
from machine import SoftI2C, I2C
# Messung Temperatur, Luftdruck, Luftfeuchte
import BME280
# Messung CO2-Konzentration in der Luft
import MHZ19C
# Messung ob es regnet oder nicht
import DeboSenRain
# Messung Feinstaubgehalt in der Luft
import HM3301
# stellt Verbindung zum Netzwerk her und sendet Daten an Server
import Wifi

# Relais, welches für das Ausschalten der 5V Betriebsspannung dient
# soll beim Start angeschalten werden
# Relais an GPIO 34 
relay = Pin(25, Pin.OUT)
# Relay An
relay.off()

# Hauptprogramm für die Messungen
while True:
    # Relais erneut anzuschalten ist nicht nötig
    # das Aufwachen aus dem deepsleep erledigt dies bereits 
    # relay.off()
    
    # Anzeige fürs Aufwachen
    print('             ')
    print('wakeywakey my little sunshine')
    print('             ')
    
    # Ansprechen Pins für I2C
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)

    '''
        HM3301
        - für die Bestimmung der Feinstaubbelastung in der Luft in Mikrogramm/m³
        - der Sensor braucht nach der Initialisierung 30s zum Warmlaufen
    '''
    
    # zunächst Erstellung eines Objektes vom Typ HM3301
    hm = HM3301.HM3301Sensor()
    
    # auslesen der Feinstaubbelastung
    feinstaub = hm.measure(i2c)

    '''
        MHZ19C
        - für die Bestimmung des CO2 Gehalts in der Luft in ppm(parts per million)       
    '''
    
    # zunächst Erstellung eines Objektes vom Typ MHZ19C
    mh = MHZ19C.MHZ19CSensor(tx_pin=17, rx_pin=16)
    
    # auslesen des CO2 Gehalts und anschließende Ausgabe
    co2 = mh.measure()
    print('Co2: ', co2,'ppm')
    print(type(co2))
    
    '''
        BME280
        - für die Temperatur in °C
        - Luftfeuchte in %
        - Luftdruck in Pa
    '''
    
    # zunächst Erstellung eines Objektes vom Typ BME280
    bme = BME280.BME280(i2c=i2c)
    
    # Auslesen der Temperatur aus dem BME
    temp = bme.temperature
    
    # Auslesen der Luftfeuchtigkeit aus dem BME
    hum = bme.humidity
    
    # Auslesen des Limport Regenuftdrucks aus dem BME
    pres = bme.pressure
    
    # Temperatur in Fahrenheit
    # temp = (bme.read_temperature()/100) * (9/5) + 32
    # temp = str(round(temp, 2)) + 'F'
    
    # Ausgabe der einzelnen Werte
    print('Temperatur: ', temp, '°C')
    print(type(temp))
    print('Luftfeuchtigkeit: ', hum, '%')
    print(type(hum))
    print('Luftdruck: ', pres, 'hPa')
    print(type(pres))
    
    '''
        DeboSenRain
        - boolean Wert für Regen
    '''
    
    # zunächst Erstellung eines Objektes vom Typ DeboSenRain
    dbs = DeboSenRain.DeboSenRainSensor()
    
    # Auslesen und Ausgabe des Regenzustands
    rain = dbs.measure()
    print('Regnet es? ',rain)
    print(type(rain))
    
    '''
        Verbindungsaufbau zum Netzwerk.
        Senden der Daten, an den Server.
    '''
    
    wifi = Wifi.WiFi()
    wifi.conn_Net()
    wifi.send_Data(co2,rain,temp,pres,hum)
    wifi.end_Net()
    
    sleep(1)
    
    '''
        Deepsleep
        - ESP32 und alle Sensoren sollen nur für einen kurzen Zeitraum messen
        - danach werden sie, bis sie wieder benötigt werden ausgeschaltet
        - diente ursprünglich zum Schonen des Akkus
    '''
    # Relais Aus, unnötig durch deepsleep()
    #relay.on()
    
    # Deninitialisierung
    i2c = None
    #hm = None
    
    # Messung/Ausgabe der Werte ist abgeschlossen
    # Vorbereitung des deepsleep
    # dieser erhält einen Wert in ms
    print('             ')
    print('it is time to sleep you little ...')
    print('             ')
    deepsleep(60000)
