import logging
from time import sleep

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as e:
    class GPIO_class(object):
        def __init__(self):
            self.BOARD = 1
            self.OUT = 69 #LAMO
            self.LOW = 0
            self.HIGH = 1
            
        def setwarnings(self, something):
            print(something)
        def setmode(self, mode):
            print(f'setmode {mode}')
        def setup(self, pin, direction, initial):
            print(f'setup {pin}, {direction}, {initial}')
        def output(self, pin, level):
            print(f'output {pin}, {level}')
        def input(self, pin):
            print(f'input {pin}')

    GPIO = GPIO_class()
    print(e)

SCRIPT_RUNNING_PIN = 18
EV_CONTROL_PIN = 13
CHARGER_CONTROL_PIN = 11

EV_MAX_POWER = 2000
CHARGER_MAX_POWER = 650
USAGE_HEADROOM = 50

ERROR = -1

class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):

        solar = 3701
        usage = 1000

        # Find out whether the charge pin is already high (ON)
        self.charging = GPIO.input(CHARGER_CONTROL_PIN) == GPIO.HIGH
        self.evCharging = GPIO.input(EV_CONTROL_PIN) == GPIO.HIGH
  
        # Calculate current solar excess
        solarExcess = solar - usage
        
        realSolarExcess = solarExcess
        if self.evCharging:
            realSolarExcess += EV_MAX_POWER

        if self.charging:
            realSolarExcess += CHARGER_MAX_POWER

        # Something went wrong getting power values - continue as was
        if solar == ERROR or usage == ERROR:
            self.doEvCharge = self.evCharging
            self.doCharge = self.charging
        else:
            self.doEvCharge = realSolarExcess > (EV_MAX_POWER + USAGE_HEADROOM)
            if self.doEvCharge:
                self.doCharge = realSolarExcess > (EV_MAX_POWER + CHARGER_MAX_POWER + USAGE_HEADROOM)
            else:
                self.doCharge = realSolarExcess > (CHARGER_MAX_POWER + USAGE_HEADROOM)

        print(f'Solar: {solar}W  Usage: {usage}W  EV Charging: {self.evCharging}  Do EV Charge: {self.doEvCharge} Charging: {self.charging}  Do charge: {self.doCharge}')


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(SCRIPT_RUNNING_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(CHARGER_CONTROL_PIN, GPIO.OUT)
        GPIO.setup(EV_CONTROL_PIN, GPIO.OUT)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)

        #GPIO.output(CHARGER_CONTROL_PIN, GPIO.HIGH if self.doCharge else GPIO.LOW)
        #GPIO.output(EV_CONTROL_PIN, GPIO.HIGH if self.doEvCharge else GPIO.LOW)

        logging.debug(',%s,%s,%s,%s,%s,%s', solar, usage, 1 if self.charging else 0, 1 if self.doCharge else 0, 1 if self.evCharging else 0, 1 if self.doEvCharge else 0)

        sleep(1)
        GPIO.output(SCRIPT_RUNNING_PIN, GPIO.LOW)

