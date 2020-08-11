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

CHARGER_MAX_POWER = 600
SCRIPT_RUNNING_PIN = 18
CHARGER_CONTROL_PIN = 11
OTHER_PIN_1 = 13
OTHER_PIN_2 = 15

class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):

        # Find out whether the charge pin is already high (ON)
        self.charging = GPIO.input(CHARGER_CONTROL_PIN) == GPIO.HIGH

        correctedUsage = usage

        # Remove assumed charger usage from usage
        if self.charging:
            correctedUsage -= CHARGER_MAX_POWER

        self.doCharge = (solar - correctedUsage) > CHARGER_MAX_POWER

        print(f'Solar: {solar}W  Usage: {usage}W  Usage without charger: {correctedUsage}W')


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(SCRIPT_RUNNING_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(CHARGER_CONTROL_PIN, GPIO.OUT)
        GPIO.setup(OTHER_PIN_1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(OTHER_PIN_2, GPIO.OUT, initial=GPIO.HIGH)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)
        print(f'Charging now: {self.charging}')
        print(f'Charge next: {self.doCharge}')

        GPIO.output(CHARGER_CONTROL_PIN, GPIO.HIGH if self.doCharge else GPIO.LOW)
        sleep(5)
        GPIO.output(SCRIPT_RUNNING_PIN, GPIO.LOW)

