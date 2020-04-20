import RPi.GPIO as GPIO
import json
from time import sleep 
from urllib2 import urlopen

MONITOR_URL = "http://www.energyhive.com/mobile_proxy/getCurrentValuesSummary?token=3TAoBW0SidCO90NH3K8rDKP1FVJmhWQB"
SOLAR_SENSOR_SID = "793983"
USAGE_SENSOR_SID = "833355"
SOLAR_CORRECTION = -48
SOLAR_CHARGE_HEADROOM = 200
OVER_USAGE_HEADROOM = 100

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)

while True:
    sensorJson = urlopen(MONITOR_URL).read()
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
    
    doCharge = (solarNow - usageNow) > SOLAR_CHARGE_HEADROOM
    doPower = (usageNow - solarNow) > OVER_USAGE_HEADROOM
    doNothing = not doCharge and  not doPower

    if doCharge:
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW) 

    if doPower:
        GPIO.output(11, GPIO.LOW) 
        GPIO.output(13, GPIO.LOW)  # Turn on yellow
        GPIO.output(15, GPIO.HIGH)

    if doNothing:
        GPIO.output(11, GPIO.LOW) 
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(15, GPIO.LOW)  # Turn on red

    sleep(10)
