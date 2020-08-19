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

CHARGER_MAX_POWER = 320
CHARGER_STAY_ON_HEADROOM = 80
SCRIPT_RUNNING_PIN = 18
CHARGER_CONTROL_PIN = 11
ERROR = -1

class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):

        # Find out whether the charge pin is already high (ON)
        self.charging = GPIO.input(CHARGER_CONTROL_PIN) == GPIO.HIGH

        # Calculate current solar excess
        solarExcess = solar - usage

        if solar == ERROR or usage == ERROR:
            self.doCharge = self.charging
        elif self.charging:
            self.doCharge = solarExcess > CHARGER_STAY_ON_HEADROOM
        else:
            self.doCharge = solarExcess > (CHARGER_MAX_POWER + CHARGER_STAY_ON_HEADROOM)

        print(f'Solar: {solar}W  Usage: {usage}W  Charging: {self.charging}  Charge now: {self.doCharge}')


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(SCRIPT_RUNNING_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(CHARGER_CONTROL_PIN, GPIO.OUT)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)

        GPIO.output(CHARGER_CONTROL_PIN, GPIO.HIGH if self.doCharge else GPIO.LOW)
        
        logging.debug(',%s,%s,%s,%s', solar, usage, 1 if self.charging else 0, 1 if self.doCharge else 0)

        sleep(5)
        GPIO.output(SCRIPT_RUNNING_PIN, GPIO.LOW)

