import binascii
import time
import serial
import threading


class Xbee:
    port = ''
    baudrate = 9600
    comtty = ''
    timeout = 0
    bytesize = 0
    parity = ''
    stopbits = 0
    error = 0
    respuesta = ''
    data = ''
    name = ''
    value = ''
    name_list = []
    value_list = []
    id_name = 0

    def config_port(self, timeout):
        self.port = serial.Serial()
        self.port.port = '/dev/ttyUSB0'
        self.port.baudrate = self.baudrate
        self.port.timeout = timeout
        self.port.bytesize = serial.EIGHTBITS
        self.port.parity = serial.PARITY_NONE
        self.port.stopbits = serial.STOPBITS_ONE

    def __init__(self, names):
        self.name_list = names
        for i in range(0, len(self.name_list)):
            self.value_list.append([])
        self.config_port(1)
        self.port.open()
        lector = threading.Thread(target=self.read_loop)
        lector.start()

    def get_value(self, nombre):
        dato = 0
        id_nombre = (self.name_list.index(nombre))
        div = len(self.value_list[id_nombre])
        suma = 0
        for i in range(0, div):
            suma = suma + self.value_list[id_nombre][i]
            try:
                dato = suma / div
            except:
                print "Divide by 0"
                return 0
        del self.value_list[id_nombre][:]
        return dato

    def read_loop(self):
        while 1:
            self.data = binascii.hexlify(self.port.readline())
            while len(self.data) >= 44:
                dt_num = len(self.data) // 44
                for i in range(0, dt_num):
                    self.name = self.data[len(self.data) - 28: len(self.data) - 20]
                    self.value = self.data[len(self.data) - 6: len(self.data) - 2]
                    self.data = self.data[0: len(self.data) - 44]
                    try:
                        self.id_name = (self.name_list.index(self.name))
                        self.value_list[self.id_name].append(int("0x" + self.value, 0))
                    except StandardError as e:
                        print ("ERROR DE UBICACION DEL NOMBRE" + e.message)
                    time.sleep(0.5)
