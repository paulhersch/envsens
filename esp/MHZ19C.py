'''
    Datei für das Messen, Überprüfen mithilfe der im Datenblatt gegebenen Prüfsumme
    und der Rückgabe des korrekten CO2 Wertes im Bereich von 400-5000 ppm.
    Datenblatt: https://cdn-reichelt.de/documents/datenblatt/C150/MH-Z19CDATENBLATT.pdf
    Originalbibliothek: bitte einfügen
    
'''
from machine import UART,Pin
import utime
import time
class MHZ19CSensor:
    # Initialisierung des Sensors
    def __init__(self, tx_pin, rx_pin):
        self.uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=int(tx_pin), rx=int(rx_pin))

    # Messung CO2
    def measure(self):
        while True:
            # Befehl an den Sensor schicken zum Messen
            # siehe Datenblatt
            # x86 = schreiben
            self.uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')

            # kurz warten für Messung und Sendung des Wertes
            time.sleep(1)  # in seconds

            # lesen und überprüfen
            buf = self.uart.read(9)
            if self.is_valid(buf):
                break

        # CO2 -Konzentration = HIGH (buf[2]) * 256 + LOW (buf[3])
        co2 = buf[2] * 256 + buf[3]

        return co2

    def is_valid(self, buf):
        '''
        Erstellung der Prüfsumme nach
        checksum = - (byte[0]%256 + ... byte[7]%256)) + 1
        '''
        if buf is None or buf[0] != 0xFF or buf[1] != 0x86:
            return False
        
        # Prüfsumme wird in buf[8] gespeichert und ist zu beginn 0
        checksum = 0x00
        
        i = 1
        while i < 8:
            checksum += buf[i] % 256
            i += 1
        checksum = ~checksum & 0xFF
        checksum += 1
        return checksum == buf[8]
