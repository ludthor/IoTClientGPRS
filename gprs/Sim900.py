import serial
import time
import datetime
import RPi.GPIO as GPIO  # Libreria Python GPIO
import json

GPIO.setmode(GPIO.BCM)  # Establecemos el sisetma de numeracion de pins BCM
GPIO.setup(4, GPIO.OUT)  # Ponemos el Pin GPIO4 como salida
GPIO.output(4, GPIO.LOW)  # Asignamos el valor 0 a la salida GPIO4


class Sim900:
    port = ''
    baudrate = 19200
    comtty = ''
    timeout = 0
    bytesize = 0
    parity = ''
    stopbits = 0
    error = 0
    respuesta = ''

    def show_serial_data(self):
        dato = self.port.readall()
        print dato
        return dato

    def config_port(self, timeout):
        self.port = serial.Serial()
        self.port.port = '/dev/ttyAMA0'
        self.port.baudrate = self.baudrate
        self.port.timeout = timeout
        self.port.bytesize = serial.EIGHTBITS
        self.port.parity = serial.PARITY_NONE
        self.port.stopbits = serial.STOPBITS_ONE

    def send_command(self, command, respuesta):
        self.port.open()
        if self.port.isOpen():
            for i in range(0, 3):
                self.port.readall()
                self.port.write(command)
                time.sleep(0.5)
                for j in range(0, 3):
                    self.respuesta = self.port.readline()[:-2]
                    if self.respuesta == respuesta:
                        self.error = 0
                        print command, '\r\n', "Comando exitoso"
                        self.port.close()
                        return
                    elif self.respuesta == 'ERROR':
                        self.error = 2
                        print command, '\r\n', "Comando fallido"
                    else:
                        self.error = 3
        self.port.close()

    def module_restart(self):
        self.error = 0
        GPIO.output(4, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(4, GPIO.LOW)
        time.sleep(1)
        self.send_command("AT\r", 'OK')
        if self.error == 0:
            print "Modulo GPRS Encendido"
        elif self.error == 2:
            print "Modulo no responde"
        elif self.error == 3:
            print "Fallo al encender el modulo"
        if self.error == 0:
            self.send_command("AT+CGATT=1\r", 'OK')
            if self.error == 0:
                self.send_command('AT+CSTT=' + self.APN + '\r', 'OK')
            if self.error == 0:
                self.send_command('AT+CIICR\r', 'OK')
            if self.error == 0:
                self.port.open()
            if self.port.isOpen():
                self.port.write('AT+CIFSR\r')
                print self.port.readall()
                self.port.close()

    def send_val(self, host, port, address, datos):
        num = 0
        le = ''
        var = ''
        var = datos
        var = json.dumps(var)
        num = len(var)
        le = str(num)
        self.send_command('AT+CIPSTART=\"tcp\",\"' + host + '\",\"' + port + '\"\r', 'CONNECT OK')
        time.sleep(1)
        self.send_command('AT+CIPSEND\r', '')
        time.sleep(3)
        self.port.open()
        self.ShowSerialData()
        self.port.write(address)
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Content-Type:application/json\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Content-Length: " + le + '\r\n')
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Host: " + host + "\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write('\r\n')
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write(var + '\r\n')
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write('\r\n')
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write('\x1a')
        time.sleep(7)
        self.port.write('\r')
        time.sleep(3)
        result = self.port.readall()
        if '201 CREATED' in result:
            result = 'Valor Archivado'
            self.error = 0
            self.port.close()
        self.send_command("AT+CIPCLOSE\r", 'OK')  # //close the communication
        return result

    def send_val_http(self, host, puerto, token, direccion, datos):

        json_datos = json.dumps(datos)
        _len = str(len(json_datos))

        self.send_command('AT+HTTPINIT')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPPARA="CID",1')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPPARA="URL","' + host + '"')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPPARA="CONTENT","application/json"')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command(
            'AT+HTTPPARA="USERDATA","Content-length:"' + _len + '\\r\\n Authorization:' + token + '\\r\\n Host:' + host + '\\r\\n')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPPARA?')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPDATA=' + _len + ', 12000,5000')
        time.sleep(0.1)
        self.ShowSerialData()

        self.send_command('[' + json_datos + ']')
        time.sleep(1)
        self.ShowSerialData()

        # self.send_command('AT+HTTPDATA='+json_datos)
        # time.sleep(1)
        # self.ShowSerialData()

        self.send_command('AT+HTTPACTION=1')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPREAD')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPTERM')
        time.sleep(1)
        self.ShowSerialData()

        self.send_command('AT+HTTPACTION=1')
        time.sleep(1)
        self.ShowSerialData()

    def recive_val(self, host, puerto, direccion):
        self.send_command('AT+CIPSTART=\"tcp\",\"' + host + '\",\"' + puerto + '\"\r',
                          'CONNECT OK')  # //start up the connection
        time.sleep(3)
        self.ShowSerialData()
        time.sleep(3)
        self.ShowSerialData()
        self.port.write("AT+CIPSEND\r")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write(direccion)
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Host: " + host + "\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Connection: Keep-Alive\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Accept: */*\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write("Accept-Language: en-us\r\n")
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write('\r\n')
        time.sleep(0.1)
        self.ShowSerialData()
        self.port.write('\x1a')
        time.sleep(7)
        self.port.write('\r')
        entrega = self.ShowSerialData()
        self.port.write("AT+CIPCLOSE\r")  # //close the communication
        time.sleep(1)
        self.ShowSerialData()
        start = entrega.find("city") + len("city") + 3
        end = entrega.find("\"", start)
        city = entrega[start:end]
        start = entrega.find("precip_1hr_metric") + len("precip_1hr_metric") + 3
        end = entrega.find("\"", start)
        precip = entrega[start:end]
        start = entrega.find("pop") + len("pop") + 4
        end = entrega.find("\"", start)
        pop = entrega[start:end]
        start = entrega.find("temp_c") + len("temp_c") + 2
        end = entrega.find(",", start)
        temp = entrega[start:end]
        start = entrega.find("relative_humidity") + len("relative_humidity") + 3
        end = entrega.find("\"", start)
        rel_hum = entrega[start:end]
        # print "--------------------------------------------------------------------"
        # print "\r\n\r\n\r\n"
        # print "RESULTADOS"
        # print "\r\n\r\n\r\n"
        # print "CITY : ", city
        # print "PRECIPITACION : ", precip
        # print "PROABILIDAD DE LLUVIA : ", pop
        # print "TEMPERATURA : ", temp
        # print "HUMEDAD RELATIVA : ", rel_hum
        # print "--------------------------------------------------------------------"
        resultados = [city, precip, pop, temp, rel_hum]
        return resultados

    # -------------------------------------------#
    #		Inicializacion de la clase-objeto	#
    # -------------------------------------------#
    def __init__(self, APN):
        self.error = 0
        self.APN = APN
        self.config_port(1)
        self.module_restart()
