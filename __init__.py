import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('0.0.0.0', 11719))


def sendMsg(msg):
    s.sednto(bytes("t: "+msg, "utf-8"), ("255.255.255.255", 11719))

def getMsg():
    msg = s.recv(128)
    msg = msg.decode('utf-8')
    if not msg.startswith("r: "):
        return getMsg()
    else:
        return msg[3:]


class Station():
    def __init__(self):
        self.connection = False
        self.power = False
        self.pipes = []
        self.sensors = []
        self.heaters = []

    def checkConnection(self):
        error = "Connect the model before performing any actions"
        assert self.connection == True, error

    def connect(self):
        sendMsg("ping")
        getMsg()
        self.connection = True

    def setPower(self, pwr):
        self.checkConnection()
        power = int(pwr)
        if power == 1 or power == 0:
            self.power = pwr
            sendMsg("set On={}".format(power))
        else:
            raise ValueError("Model power must be a boolean value")

    def getEnergy(self):
        self.checkConnection()
        sendMsg("get E")
        return int(getMsg())


class Pipe():
    def __init__(self, station, pin):
        assert type(station) is Station, "Wrong argument type: {}".format(str(type(station)))
        station.checkConnection()
        station.pipes.append(self)
        self.pin = pin
        self.power = None

    def setPower(self, val):
        error = "Wrong value {}: must be between 0 and 100"
        assert val <= 100 and val>=0, error
        sendMsg("set P{}={}".format(self.pin, val))


class Sensor():
    def __init__(self, station, pin):
        assert type(station) is Station, "Wrong argument type: {}".format(str(type(station)))
        station.checkConnection()
        station.sensors.append(self)
        self.pin = pin
        self.temperature = None

    def getValue(self):
        sendMsg("get S{}".format(self.pin))
        return int(getMsg())


class Heater():
    def __init__(self, station, num):
        assert type(station) is Station, "Wrong argument type: {}".format(str(type(station)))
        station.checkConnection()
        self.num = num
        self.checkAvailible(station)

    def checkAvailible(self, station):
        error1 = "Heater not availible"
        error2 = "Heater already exists"
        assert self.num == 0 or self.num == 1, error1
        for heater in station.heaters:
            assert self.num != heater.num, error2

    def setPower(self, val):
        error = "Wrong value: {}, must be between 0 and 100".format(val)
        assert val <= 100 and val >= 0,
        sendMsg("set H{}={}".format(self.num, val))
