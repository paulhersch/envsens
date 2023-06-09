'''
    Datei für das Messen und Umwandeln der Rohwerte in
    - °C für die Temperatur
    - % für die Luftfeuchtigkeit
    - hPascal für den Luftdruck
    Datenblatt: 
    Originalbibliothek: "bitte eingeben"
'''
from machine import I2C
import time

# Standardardesse des BME280
BME280_I2CADDR = 0x76

# Operating Modi
BME280_OSAMPLE_1 = 1
BME280_OSAMPLE_2 = 2
BME280_OSAMPLE_4 = 3
BME280_OSAMPLE_8 = 4
BME280_OSAMPLE_16 = 5

# BME280 Register
# Temperaturregister
BME280_REGISTER_DIG_T1 = 0x88  
BME280_REGISTER_DIG_T2 = 0x8A
BME280_REGISTER_DIG_T3 = 0x8C

# Druckregister
BME280_REGISTER_DIG_P1 = 0x8E
BME280_REGISTER_DIG_P2 = 0x90
BME280_REGISTER_DIG_P3 = 0x92
BME280_REGISTER_DIG_P4 = 0x94
BME280_REGISTER_DIG_P5 = 0x96
BME280_REGISTER_DIG_P6 = 0x98
BME280_REGISTER_DIG_P7 = 0x9A
BME280_REGISTER_DIG_P8 = 0x9C
BME280_REGISTER_DIG_P9 = 0x9E

# Feuchtigkeitsregister
BME280_REGISTER_DIG_H1 = 0xA1
BME280_REGISTER_DIG_H2 = 0xE1
BME280_REGISTER_DIG_H3 = 0xE3
BME280_REGISTER_DIG_H4 = 0xE4
BME280_REGISTER_DIG_H5 = 0xE5
BME280_REGISTER_DIG_H6 = 0xE6
BME280_REGISTER_DIG_H7 = 0xE7

BME280_REGISTER_CHIPID = 0xD0
BME280_REGISTER_VERSION = 0xD1
BME280_REGISTER_SOFTRESET = 0xE0

BME280_REGISTER_CONTROL_HUM = 0xF2
BME280_REGISTER_CONTROL = 0xF4
BME280_REGISTER_CONFIG = 0xF5
BME280_REGISTER_PRESSURE_DATA = 0xF7
BME280_REGISTER_TEMP_DATA = 0xFA
BME280_REGISTER_HUMIDITY_DATA = 0xFD


class Device:
    '''
        Klasse für Kommunikation mit I2C Gerät.
        Schreibt/Liest 8-/16-bit und Byte-Werte in die Register.
    '''

    def __init__(self, address, i2c):
        '''
            Erzeuge eien Instanz vom I2C Gerät mit übergebener Adresse
        '''
        self._address = address
        self._i2c = i2c

    def writeRaw8(self, value):
        '''
            Schreibe einen 8-bit Wert auf den Bus (ohne Register).
        '''
        value = value & 0xFF
        self._i2c.writeto(self._address, value)

    def write8(self, register, value):
        '''
            Schreibe einen 8-bit Wert in das übergebene Register.
        '''
        b=bytearray(1)
        b[0]=value & 0xFF
        self._i2c.writeto_mem(self._address, register, b)

    def write16(self, register, value):
        '''
            Schreibe einen 16-bit Wert in das übergebene Register.
        '''
        value = value & 0xFFFF
        b=bytearray(2)
        b[0]= value & 0xFF
        b[1]= (value>>8) & 0xFF
        self.i2c.writeto_mem(self._address, register, value)

    def readRaw8(self):
        '''
            Lies einen 8-bit Wert auf dem Bus (ohne Register)
        '''
        return int.from_bytes(self._i2c.readfrom(self._address, 1),'little') & 0xFF

    def readU8(self, register):
        '''
            Lies einen vorzeichenloses Byte vom übergebenen Register.
        '''
        return int.from_bytes(
            self._i2c.readfrom_mem(self._address, register, 1),'little') & 0xFF

    def readS8(self, register):
        '''
            Lies ein vorzeichenbehfatets Byte vom übergebenen Register.
        '''
        result = self.readU8(register)
        if result > 127:
          result -= 256
        return result

    def readU16(self, register, little_endian=True):
        '''
            Lies einen vorzeichenlosen 16 Bit-Wert aus dem übergebenen Register,
            mit dem übergebenen endian(kleinster Stellenwert zuerst).
        '''
        result = int.from_bytes(
            self._i2c.readfrom_mem(self._address, register, 2),'little') & 0xFFFF
        if not little_endian:
          result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        '''
            Lies einen vorzeichenbehafteten 16 Bit-Wert aus dem übergebenen Register,
            mit dem übergebenen endian(kleinster Stellenwert zuerst).
        '''
        result = self.readU16(register, little_endian)
        if result > 32767:
          result -= 65536
        return result

    def readU16LE(self, register):
        '''
            Lies einen vorzeichenlosen 16 Bit-Wert aus dem übergebenen Register,
            mit der little_endian(kleinster Stellenwert zuerst) Reihenfolge.
        '''
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        '''
            Lies einen vorzeichenlosen 16 Bit-Wert aus dem übergebenen Register,
            mit der big_endian(größter Stellenwert zuerst) Reihenfolge.
        '''
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        '''
            Lies einen vorzeichenbehafteten 16 Bit-Wert aus dem übergebenen Register,
            mit der little_endian(kleinster Stellenwert zuerst) Reihenfolge.
        '''
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        '''
            Lies einen vorzeichenbehafteten 16 Bit-Wert aus dem übergebenen Register,
            mit der big_endian(größter Stellenwert zuerst) Reihenfolge.
        '''
        return self.readS16(register, little_endian=False)


class BME280:
    def __init__(self, mode=BME280_OSAMPLE_1, address=BME280_I2CADDR, i2c=None, **kwargs):
        # Überprüfung, ob Modus korrekt
        if mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                        BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unerwarteter Modus {0}. Setze diesen stattdessen '
                'BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or '
                'BME280_ULTRAHIGHRES'.format(mode))
        self._mode = mode
        # Erzeuge I2C Gerät
        if i2c is None:
          raise ValueError('Ein I2C Objekt wird benötigt.')
        self._device = Device(address, i2c)
        # lade Kalibrierung
        self._load_calibration()
        self._device.write8(BME280_REGISTER_CONTROL, 0x3F)
        self.t_fine = 0

    def _load_calibration(self):

        self.dig_T1 = self._device.readU16LE(BME280_REGISTER_DIG_T1)
        self.dig_T2 = self._device.readS16LE(BME280_REGISTER_DIG_T2)
        self.dig_T3 = self._device.readS16LE(BME280_REGISTER_DIG_T3)

        self.dig_P1 = self._device.readU16LE(BME280_REGISTER_DIG_P1)
        self.dig_P2 = self._device.readS16LE(BME280_REGISTER_DIG_P2)
        self.dig_P3 = self._device.readS16LE(BME280_REGISTER_DIG_P3)
        self.dig_P4 = self._device.readS16LE(BME280_REGISTER_DIG_P4)
        self.dig_P5 = self._device.readS16LE(BME280_REGISTER_DIG_P5)
        self.dig_P6 = self._device.readS16LE(BME280_REGISTER_DIG_P6)
        self.dig_P7 = self._device.readS16LE(BME280_REGISTER_DIG_P7)
        self.dig_P8 = self._device.readS16LE(BME280_REGISTER_DIG_P8)
        self.dig_P9 = self._device.readS16LE(BME280_REGISTER_DIG_P9)

        self.dig_H1 = self._device.readU8(BME280_REGISTER_DIG_H1)
        self.dig_H2 = self._device.readS16LE(BME280_REGISTER_DIG_H2)
        self.dig_H3 = self._device.readU8(BME280_REGISTER_DIG_H3)
        self.dig_H6 = self._device.readS8(BME280_REGISTER_DIG_H7)

        h4 = self._device.readS8(BME280_REGISTER_DIG_H4)
        h4 = (h4 << 24) >> 20
        self.dig_H4 = h4 | (self._device.readU8(BME280_REGISTER_DIG_H5) & 0x0F)

        h5 = self._device.readS8(BME280_REGISTER_DIG_H6)
        h5 = (h5 << 24) >> 20
        self.dig_H5 = h5 | (
            self._device.readU8(BME280_REGISTER_DIG_H5) >> 4 & 0x0F)

    def read_raw_temp(self):
        '''
            Lies die Rohtemperatur vom Sensor.
        '''
        meas = self._mode
        self._device.write8(BME280_REGISTER_CONTROL_HUM, meas)
        meas = self._mode << 5 | self._mode << 2 | 1
        self._device.write8(BME280_REGISTER_CONTROL, meas)
        sleep_time = 1250 + 2300 * (1 << self._mode)

        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        time.sleep_us(sleep_time)  # Wait the required time
        msb = self._device.readU8(BME280_REGISTER_TEMP_DATA)
        lsb = self._device.readU8(BME280_REGISTER_TEMP_DATA + 1)
        xlsb = self._device.readU8(BME280_REGISTER_TEMP_DATA + 2)
        raw = ((msb << 16) | (lsb << 8) | xlsb) >> 4
        return raw

    def read_raw_pressure(self):
        '''
            Nimm an, dass die Temperatur bereits gelesen wurde (genügend deleay).
            Lies den Rohdruck vom Sensor.
        '''
        msb = self._device.readU8(BME280_REGISTER_PRESSURE_DATA)
        lsb = self._device.readU8(BME280_REGISTER_PRESSURE_DATA + 1)
        xlsb = self._device.readU8(BME280_REGISTER_PRESSURE_DATA + 2)
        raw = ((msb << 16) | (lsb << 8) | xlsb) >> 4
        return raw

    def read_raw_humidity(self):
        '''
            Nimm an, dass die Temperatur bereits gelesen wurde (genügend deleay).
            Lies den Rohluftfeuchte vom Sensor.
        '''
        msb = self._device.readU8(BME280_REGISTER_HUMIDITY_DATA)
        lsb = self._device.readU8(BME280_REGISTER_HUMIDITY_DATA + 1)
        raw = (msb << 8) | lsb
        return raw

    def read_temperature(self):
        '''
            Gib die korrigierte Temperatur mit einer Genauigkeit von 0,01°C an.
        '''
        adc = self.read_raw_temp()
        var1 = ((adc >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = ((
            (((adc >> 4) - self.dig_T1) * ((adc >> 4) - self.dig_T1)) >> 12) *
            self.dig_T3) >> 14
        self.t_fine = var1 + var2
        return (self.t_fine * 5 + 128) >> 8

    def read_pressure(self):
        '''
            Gib den korrigierten Druck in Pascal zurück.
        '''
        adc = self.read_raw_pressure()
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) >> 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
          return 0
        p = 1048576 - adc
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        return ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

    def read_humidity(self):
        '''
            Gib die korrigierte Luftfeuchte zurück.
        '''
        adc = self.read_raw_humidity()
        # print 'Raw humidity = {0:d}'.format (adc)
        h = self.t_fine - 76800
        h = (((((adc << 14) - (self.dig_H4 << 20) - (self.dig_H5 * h)) +
             16384) >> 15) * (((((((h * self.dig_H6) >> 10) * (((h *
                              self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) *
                              self.dig_H2 + 8192) >> 14))
        h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
        h = 0 if h < 0 else h
        h = 419430400 if h > 419430400 else h
        return h >> 12

    @property
    def temperature(self):
        '''
            Temperatur in °C
        '''
        t = self.read_temperature()
        ti = t // 100
        td = t - ti * 100
        #return "{}.{:02d}C".format(ti, td)
        return ti

    @property
    def pressure(self):
        '''
            Druck in hPa.
        '''
        p = self.read_pressure() // 256
        pi = p // 100
        pd = p - pi * 100
        #return "{}.{:02d}hPa".format(pi, pd)
        return pi

    @property
    def humidity(self):
        '''
            Luftfeuchte in %
        '''
        h = self.read_humidity()
        hi = h // 1024
        hd = h * 100 // 1024 - hi * 100
        #return "{}.{:02d}%".format(hi, hd)
        return hi