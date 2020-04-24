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
            
    GPIO = GPIO_class()
    print(e)

SOLAR_CHARGE_HEADROOM = 200
OVER_USAGE_HEADROOM = 100



ActivityState = {'IDLE':0, "CHARGING":1, "POWERING":2}


class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):
        doCharge = (solar - usage) > SOLAR_CHARGE_HEADROOM
        doPower = (usage - solar) > OVER_USAGE_HEADROOM
        doNothing = not doCharge and not doPower

        if doNothing:
            self._activity_state = ActivityState["IDLE"]

        if doCharge:
            self._activity_state = ActivityState["CHARGING"]

        if doPower:
            self._activity_state = ActivityState["POWERING"]

        print("Solar: {solar}W  Usage: {fish}W".format(solar=solar, fish=usage))


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
        GPIO.setup(11, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(13, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH)
        # Flash the LEDs to say we're up and working
        sleep(0.5)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        sleep(0.5)
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)
        print(self._activity_state)

        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        sleep(0.1)
        GPIO.output(11, GPIO.HIGH if self._activity_state == ActivityState["CHARGING"] else GPIO.LOW) 
        GPIO.output(13, GPIO.HIGH if self._activity_state == ActivityState["IDLE"] else GPIO.LOW) 
        GPIO.output(16, GPIO.HIGH if self._activity_state == ActivityState["POWERING"] else GPIO.LOW) 
