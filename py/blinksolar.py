import RPi.GPIO as GPIO
import json
from time import sleep 
from urllib.request import urlopen

MONITOR_URL = "http://www.energyhive.com/mobile_proxy/getCurrentValuesSummary?token=3TAoBW0SidCO90NH3K8rDKP1FVJmhWQB"
SOLAR_SENSOR_SID = "793983"
USAGE_SENSOR_SID = "833355"
SOLAR_CORRECTION = -48

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)

while True:
    with urlopen(MONITOR_URL) as response:
        sensorJson = response.read()

    sensors = json.loads(sensorJson)

    for s in sensors:
        dataElement = s["data"][0]
        for key in dataElement:
            if s["sid"] == SOLAR_SENSOR_SID:
                solarNow = dataElement[key] + SOLAR_CORRECTION
            elif s["sid"] == USAGE_SENSOR_SID:
                usageNow = dataElement[key]

    solarExcess = solarNow - usageNow
    print("Solar: {0}W  Usage: {1}W  Solar Excess: {2}W".format(solarNow, usageNow, solarExcess))
    
    if solarNow > usageNow:
        GPIO.output(11, GPIO.HIGH)  # Turn on green
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW) 

    if solarNow == usageNow:
        GPIO.output(11, GPIO.LOW) 
        GPIO.output(13, GPIO.HIGH)  # Turn on yellow
        GPIO.output(15, GPIO.LOW)

        if solarNow < usageNow:
        GPIO.output(11, GPIO.LOW) 
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)  # Turn on red

    sleep(10)