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
CHARGER_CONTROL_PIN = 11


class Output:
    
    def __init__(self, name):
        self.name = name

    def set_sensor_values(self, solar, usage):

        # Find out whether the charge pin is already low (ON)
        self.charging = GPIO.input(CHARGER_CONTROL_PIN) == GPIO.LOW

        correctedUsage = usage

        # Remove assumed charger usage from usage
        if self.charging:
            correctedUsage -= CHARGER_MAX_POWER

        self.doCharge = (solar - correctedUsage) > CHARGER_MAX_POWER

        print(f'Solar: {solar}W  Usage: {usage}W  Corrected Usage: {correctedUsage}W')


class GpioOutput(Output):

    def __init__(self):
        super(GpioOutput, self).__init__("GPIO Output")
        print(self.name)
        print("Setup GPIO ...")
        GPIO.setwarnings(False)  # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(CHARGER_CONTROL_PIN, GPIO.OUT)

    def set_sensor_values(self, solar, usage):
        super().set_sensor_values(solar, usage)
        print(f'Charging now: {self.charging}')
        print(f'Charge next: {self.doCharge}')

        GPIO.output(CHARGER_CONTROL_PIN, GPIO.LOW if self.doCharge else GPIO.HIGH) 
