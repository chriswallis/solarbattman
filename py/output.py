import RPi.GPIO as GPIO
from enum import Enum

SOLAR_CHARGE_HEADROOM = 200
OVER_USAGE_HEADROOM = 100

class ActivityState(Enum):
     IDLE = 0
     CHARGING = 1
     POWERING = 2


class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):
        doCharge = (solar - usage) > SOLAR_CHARGE_HEADROOM
        doPower = (usage - solar) > OVER_USAGE_HEADROOM
        doNothing = not doCharge and not doPower

        if doNothing:
            self._activity_state = ActivityState.IDLE

        if doCharge:
            self._activity_state = ActivityState.CHARGING

        if doPower:
            self._activity_state = ActivityState.POWERING

        print("Solar: {0}W  Usage: {1}W".format(solar, usage))


class ConsoleOutput(Output):
    
    def __init__(self):
        super(ConsoleOutput, self).__init__("Console Output")
        print(self.name)


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)
        GPIO.output(11, GPIO.HIGH if self._activity_state == ActivityState.CHARGING else GPIO.LOW) 
        GPIO.output(13, GPIO.HIGH if self._activity_state == ActivityState.POWERING else GPIO.LOW) 
        GPIO.output(16, GPIO.HIGH if self._activity_state == ActivityState.IDLE else GPIO.LOW) 
