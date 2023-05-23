# Integration der Bibliothek
# https://randomnerdtutorials.com/esp32-useful-wi-fi-functions-arduino/
# https://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html
# Server: #http://141.48.16.175:8888/docs#/default/show_data__get
'''
    Datei für den Aufbau einer Netzwerkverbindung und
    das Senden der gemessenen und vorverarbeiteten Daten
    an eine Datenbank.
'''
import socket
import urequests
import network

#sta_if = network.WLAN(network.STA_IF)
#print(sta_if.active())
#sta_if.active(True)
#print(sta_if.active())
#sta_if.active(False)
#sta_if.connect('<dlink-CBA8>', '<xglri80143>')

class WiFi:
    def __init__(self):
        # Station-Modus
        self.sta_if = network.WLAN(network.STA_IF)
        # in Kommandozeile für Test, ob Interface aktiv
        # sta_if.active()

    def conn_Net(self):
        # Nochmals ausschalten
        self.sta_if.active(False)
        # Anschalten
        self.sta_if.active(True)
        # sta_if.connect(SSID, password)
        self.sta_if.connect('<dlink-CBA8>', '<xglri80143>')       

    def send_Data(self,co2, rain, temp, press, humid):
        if self.sta_if.isconnected == False:
            print('Keine Verbindung zum Senden')
            return
        else:
            # Setze IP Addresse und Port Nummer vom Remote Server
            SERVER_IP = '141.48.16.175'
            SERVER_PORT = 8888

            # Socket Objekt erzeugen
            #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Server verbinden
            #sock.connect((SERVER_IP, SERVER_PORT))
            data = {
                      "co2": co2,
                      "rain": rain,
                      "temp": temp,
                      "press": press,
                      "humid": humid
                    }
            
            response = urequests.post("http://141.48.16.175:8888/docs", data = data)
            #sock.send(data)
            
    def end_Net(self):
        # Ausschalten
        self.sta_if.active(False)
            

# Test ob verbunden
# sta_if.isconnected()

# Setze IP Addresse und Port Nummer vom Remote Server
# SERVER_IP = '192.168.22.1'
# SERVER_PORT = 8080

# Socket Objekt erzeugen
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server verbinden
# sock.connect((SERVER_IP, SERVER_PORT))

# Daten an Web-Server senden
# data = b'Hello, world!'
# sock.send(data)

# Schließe den Socket
#sock.close()

# Test
#url = 'http://192.168.0.171'
#http://141.48.16.175:8888/docs#/default/show_data__get
#response = urequests.get(url)
#print(response.json())

# Ausschalten
#sta_if.active(False)