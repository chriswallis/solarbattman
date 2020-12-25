import logging
from time import sleep
from datetime import datetime, time

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

INVERTER_IS_ON = 0

if INVERTER_IS_ON:
    BT_USAGE_HEADROOM = 50
    EV_USAGE_HEADROOM = 5
else:
    BT_USAGE_HEADROOM = -200
    EV_USAGE_HEADROOM = -1000

EV_MAX_POWER = 2350
BT_MAX_POWER = 650

NIGHT_ON_AT = '00:30:00'
NIGHT_OFF_AT = '04:30:00'

SCRIPT_RUNNING_PIN = 18
EV_CONTROL_PIN = 13
BT_CONTROL_PIN = 11

ERROR = -1

class Output:
    
    def __init__(self, name):
        self.name = name


    def set_sensor_values(self, solar, usage):
        
        def time_is_between(startIsoTime, endIsoTime):
            now = datetime.now().time()
            start = time.fromisoformat(startIsoTime)
            end = time.fromisoformat(endIsoTime)
            if start <= end:
                return start <= now < end
            else: # over midnight e.g., 23:30-04:15
                return start <= now or now < end

        # Find out whether the charge pin is already high (ON)
        self.evCharging = GPIO.input(EV_CONTROL_PIN) == GPIO.HIGH 
        self.btCharging = GPIO.input(BT_CONTROL_PIN) == GPIO.HIGH
        
        evPowerRequired = EV_MAX_POWER + EV_USAGE_HEADROOM
        btPowerRequired = BT_MAX_POWER + BT_USAGE_HEADROOM
        allInPowerRequired = EV_MAX_POWER + BT_MAX_POWER + BT_USAGE_HEADROOM

        # Calculate current solar excess
        solarExcess = solar - usage

        if time_is_between(NIGHT_ON_AT, NIGHT_OFF_AT):
            self.doEvCharge = 1
            self.doBtCharge = 1

        # Something went wrong getting power values - continue as was
        elif solar == ERROR or usage == ERROR:
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
            self.doBtCharge = 1 if self.doEvCharge else solarExcess > BT_USAGE_HEADROOM

        # EV is charging
        elif self.evCharging and not self.btCharging:
            # If we're switching off EV, switch on BT
            self.doEvCharge = solarExcess > EV_USAGE_HEADROOM
            self.doBtCharge = 1 if not self.doEvCharge else (solarExcess > btPowerRequired)

        # EV is charging and battery is charging
        elif self.evCharging and self.btCharging:
            # Only check batt charge.  Switch this off first
            self.doBtCharge = solarExcess > BT_USAGE_HEADROOM
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

