import output   
import json
from time import sleep 
from urllib.request import urlopen

MONITOR_URL = "http://www.energyhive.com/mobile_proxy/getCurrentValuesSummary?token=3TAoBW0SidCO90NH3K8rDKP1FVJmhWQB"
SOLAR_SENSOR_SID = "793983"
USAGE_SENSOR_SID = "833355"
SOLAR_CORRECTION = -48

c = output.GpioOutput()

try:
    print('Getting energy values ...')
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
except:
    print('Getting energy values failed,')
    solarNow = -1
    usageNow = -1

c.set_sensor_values(solarNow, usageNow)
