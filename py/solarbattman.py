import logging
import output   
import json
from time import sleep 
from urllib.request import urlopen

MONITOR_URL = "http://192.168.86.107/feed/list.json?apikey=8c91f09904345ca35bcb84bac461980b"

logging.basicConfig(filename='output.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

c = output.GpioOutput()

try:
    print('Getting energy values ...')
    with urlopen(MONITOR_URL) as response:
        sensorJson = response.read()

#    print(sensorJson)
    feeds = json.loads(sensorJson)

    for f in feeds:
#        print(f)
        if f["name"] == "solar":
            solarNow = f["value"]
        elif f["name"] == "use":
            usageNow = f["value"]

except Exception as e:
    print('Getting energy values failed,')
    print(str(e))
    solarNow = -1
    usageNow = -1

c.set_sensor_values(solarNow, usageNow)
