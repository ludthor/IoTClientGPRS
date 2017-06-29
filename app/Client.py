import threading
import datetime
import json
from Server import Server
from gprs.Sim900 import Sim900
from xbee.Xbee import Xbee
from Model import SensorData


class Client:

    def __init__(self):

        self.apn_movistar = {"apn": "internet.movistar.com.co", "user": "movistar", "pass": "movistar"}
        self.apn_comcel = {"apn": "internet.comcel.com.co", "user": "comcel", "pass": "comcel"}

        self.deviceName = "RaspberryTest"
        self.sensors = ['41046b6f','41046b5d']
        self.sensor_num = len(self.sensors)
        self.interval = 10 # Minutes

        self.server = Server()
        self.gprs = Sim900(self.apn_comcel["apn"])
        self.xbee = Xbee(self.sensors)

    def loop(self):

        for i in range(0, len(self.sensors)):
            error = False
            try:
                data = SensorData(self.sensors[i], self.xbee.get_value(self.sensors[i], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%s.%f")))
                send_data = json.dumps(data)
            except StandardError as e:
                error = True
                print ("Error retrieving errors from XBee. " + e.message)
            if not error:
                try:
                    self.gprs.send_val(self.server.host, self.server.port, '', send_data)
                except StandardError as e:
                    error = True
                    print ("Error sending value to the server. " + e.message)

        t = threading.Timer(1*60*self.interval, self.loop)  # 1*60*10 para 10 minutos
        t.daemon = True
        t.start()

