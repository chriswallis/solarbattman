import json
from time import sleep 
from urllib.request import urlopen

SOLAR_SENSOR_SID = "793983"
USAGE_SENSOR_SID = "833355"
SOLAR_CORRECTION = -48

while True:
    with urlopen('http://www.energyhive.com/mobile_proxy/getCurrentValuesSummary?token=3TAoBW0SidCO90NH3K8rDKP1FVJmhWQB') as response:
        sensorJson = response.read()

    sensors = json.loads(sensorJson)

    for s in sensors:
        dataElement = s["data"][0]
        for key in dataElement.keys():
            if s["sid"] == SOLAR_SENSOR_SID:
                solarNow = dataElement[key] + SOLAR_CORRECTION
            elif s["sid"] == USAGE_SENSOR_SID:
                usageNow = dataElement[key]

    solarExcess = solarNow - usageNow
    print(
        "Solar: " + str(solarNow) + 
        "W  Usage: " + str(usageNow) + 
        "W  Solar Excess: " + str(solarExcess) + "W")
    
    sleep(10)