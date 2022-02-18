class Controller:
    def __init__(self , power = False , intensity = 1):
            self.power = power
            self.intensity = intensity
    def turn_on(self):
            self.power = True
    def turn_off(self):
            self.power = False
    def status(self):
            return self.intensity
    def adjust(self , intensity):
            self.intensity = intensity

class Device_1(Controller):
    def __init__(self):
            Controller.__init__(self , power = False , intensity = 1)
            self.consumption = [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 19.3 , 24.5 , 26.2]#1 - 12
    def get_consumption(self):  
            if self.power == 0:
                return 0
            return self.consumption[self.intensity]
class Device_3(Controller):
    def __init__(self):
            Controller.__init__(self , power = False , intensity = 1)
            self.consumption = [i*12.3 + 1200 if i != 0 else 0 for i in range(1 , 5)]#1 , 2 , 3
    def get_consumption(self):  
            if self.power == 0:
                return 0
            return self.consumption[self.intensity]
class Device_2(Controller):
    def __init__(self):
            Controller.__init__(self , power = False , intensity = 1)
            self.consumption = [0 , 0 , 47]#1 , 2
    def get_consumption(self):  
            if self.power == 0:
                return 0
            return self.consumption[self.intensity]


def Simulate(power, intensity , device):
    if power == 1:
        device.turn_on()
    else:
        device.turn_off()
    device.adjust(intensity)
    return device.get_consumption()