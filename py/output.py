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
BT_CONTROL_PIN = 11

EV_MAX_POWER = 2400
BT_MAX_POWER = 650
USAGE_HEADROOM = 50

ERROR = -1

class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):

        # Find out whether the charge pin is already high (ON)
        self.evCharging = GPIO.input(EV_CONTROL_PIN) == GPIO.HIGH 
        self.btCharging = GPIO.input(BT_CONTROL_PIN) == GPIO.HIGH
        
        evPowerRequired = EV_MAX_POWER + USAGE_HEADROOM
        btPowerRequired = BT_MAX_POWER + USAGE_HEADROOM
        allInPowerRequired = EV_MAX_POWER + BT_MAX_POWER + USAGE_HEADROOM

        # Calculate current solar excess
        solarExcess = solar - usage

        # Something went wrong getting power values - continue as was
        if solar == ERROR or usage == ERROR:
            self.doEvCharge = self.evCharging
            self.doBtCharge = 0

        # Nothing is charging
        elif not self.evCharging and not self.btCharging:
            self.doEvCharge = solarExcess > evPowerRequired
            if self.doEvCharge:
               self.doBtCharge = solarExcess > allInPowerRequired
            else:
               self.doBtCharge = solarExcess > btPowerRequired
            
        # Battery is charging
        elif not self.evCharging and self.btCharging:
            self.doEvCharge = (solarExcess + BT_MAX_POWER) > evPowerRequired
            self.doBtCharge = 1 if self.doEvCharge else solarExcess > USAGE_HEADROOM

        # EV is charging
        elif self.evCharging and not self.btCharging:
            # If we're switching off EV, switch on BT
            self.doEvCharge = solarExcess > USAGE_HEADROOM
            self.doBtCharge = 1 if not self.doEvCharge else (solarExcess > btPowerRequired)

        # EV is charging and battery is charging
        elif self.evCharging and self.btCharging:
            # Only check batt charge.  Switch this off first
            self.doBtCharge = solarExcess > USAGE_HEADROOM
            self.doEvCharge = 1

        print(f'Solar: {solar}W  Usage: {usage}W  EV Charging: {self.evCharging}  Do EV Charge: {self.doEvCharge} Charging: {self.btCharging}  Do charge: {self.doBtCharge}')


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(SCRIPT_RUNNING_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(BT_CONTROL_PIN, GPIO.OUT)
        GPIO.setup(EV_CONTROL_PIN, GPIO.OUT)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)

        GPIO.output(BT_CONTROL_PIN, GPIO.HIGH if self.doBtCharge else GPIO.LOW)
        GPIO.output(EV_CONTROL_PIN, GPIO.HIGH if self.doEvCharge else GPIO.LOW)

        logging.debug(',%s,%s,%s,%s,%s,%s', solar, usage, 1 if self.evCharging else 0, 1 if self.doEvCharge else 0, 1 if self.btCharging else 0, 1 if self.doBtCharge else 0)

        sleep(1)
        GPIO.output(SCRIPT_RUNNING_PIN, GPIO.LOW)

