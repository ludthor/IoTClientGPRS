class Server:

    def __init__(self):
        self.host = "0.0.0.0"
        self.port = "8080"
        self.services = {"devices": "device/", "sensorData" : "data/", "decisions": "decision/"}
