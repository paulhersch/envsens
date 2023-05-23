'''
    Datei für die Feststellung, ob es regnet oder nicht.
    Gibt True oder False zurück.
    Datenblatt: 
    Originalbibliothek: "bitte eingeben"
'''
import machine

# Setze den Regensensor-Pin am ESP32
regensensor_pin = machine.ADC(machine.Pin(33))

class DeboSenRainSensor:
    def __init__(self):
        return

    def measure(self):
        # lesen des Wertes
        regensensor_wert = regensensor_pin.read()
        
        # zurückgegebenen Wert überprüfen
        # für Werte größer als 2000 regnet es nicht
        if regensensor_wert > 2000:
            #return "Es regnet nicht."
            return False
        #return "Es regnet."
        return True
