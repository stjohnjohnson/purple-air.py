#!/usr/bin/env python3

"""Purple-Air Sensor Reader

This script loads the current data (pm2.5, humidity, temperature, 
pressure) from a given PurpleAir sensor and then calculates the 
AQI, Describers (name, color, description), and a color value to
apply to a Inovelli switch.

This expects the sensor ID to be passed as the first value of the 
script.
"""

import urllib.request
import json
import math
import sys
 
if len(sys.argv) != 2:
    print('Usage: ./purple-air.py SENSORID', file=sys.stderr)
    exit(1)

SensorID = sys.argv[1]

AQINames = [
    'Very Hazardous',
    'Hazardous',
    'Very Unhealthy',
    'Unhealthy',
    'Unhealthy for Sensitive Groups',
    'Moderate',
    'Good'
]
AQICalculations = {
    # AQI Range, PM2.5 Range, Color Range, Name, Color, Description
    'Good': {
        'aqi': (0, 50),
        'pm2.5': (0, 12),
        'colorv': (84, 42),
        'name': 'Good',
        'color': 'Green',
        'desc': 'Air quality is considered satisfactory, and air pollution poses little or no risk.'
    },
    'Moderate': {
        'aqi': (51, 100),
        'pm2.5': (12.1, 35.4),
        'colorv': (42, 21),
        'name': 'Moderate',
        'color': 'Yellow',
        'desc': 'Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.'
    },
    'Unhealthy for Sensitive Groups': {
        'aqi': (101, 150),
        'pm2.5': (35.5, 55.4),
        'colorv': (21, 1),
        'name': 'Unhealthy for Sensitive Groups',
        'color': 'Orange',
        'desc': 'Members of sensitive groups may experience health effects. The general public is not likely to be affected.'
    },
    'Unhealthy': {
        'aqi': (151, 200),
        'pm2.5': (55.5, 150.4),
        'colorv': (255, 210),
        'name': 'Unhealthy',
        'color': 'Red',
        'desc': 'Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.'
    },
    'Very Unhealthy': {
        'aqi': (201, 300),
        'pm2.5': (150.5, 250.4),
        'colorv': (210, 189),
        'name': 'Very Unhealthy',
        'color': 'Purple',
        'desc': 'Health warnings of emergency conditions. The entire population is more likely to be affected.'
    },
    'Hazardous': {
        'aqi': (301, 400),
        'pm2.5': (250.5, 350.4),
        'colorv': (189, 189),
        'name': 'Hazardous',
        'color': 'Black',
        'desc': 'Health alert: everyone may experience more serious health effects.'
    },
    'Very Hazardous': {
        'aqi': (401, 500),
        'pm2.5': (350.5, 500),
        'colorv': (189, 189),
        'name': 'Very Hazardous',
        'color': 'Black',
        'desc': 'Health alert: everyone may experience more serious health effects.'
    }
}

def aqiFromPM(pm):
    for name in AQINames:
        if pm > AQICalculations[name]['pm2.5'][0]:
            return calcAvgRange(pm,
                AQICalculations[name]['aqi'][1],
                AQICalculations[name]['aqi'][0],
                AQICalculations[name]['pm2.5'][1],
                AQICalculations[name]['pm2.5'][0]
            )

    return 0

def getColorV(aqi):
    name = getName(aqi)
    return calcAvgRange(aqi,
        AQICalculations[name]['colorv'][1],
        AQICalculations[name]['colorv'][0],
        AQICalculations[name]['aqi'][1],
        AQICalculations[name]['aqi'][0]
    )

def getName(aqi):
    for name in AQINames:
        if aqi > AQICalculations[name]['aqi'][0]:
            return name

    return 'Good'

def getColor(aqi):
    return AQICalculations[getName(aqi)]['color']

def getDesc(aqi):
    return AQICalculations[getName(aqi)]['desc']

# Cp = Current Value
# Ih = High Output
# Il = Low Output
# BPh = Value High
# BPl = Value Low
def calcAvgRange(Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)

    return round((a/b) * c + Il)


with urllib.request.urlopen('https://www.purpleair.com/json?show={}'.format(SensorID)) as url:
    data = json.loads(url.read().decode())

    if len(data['results']) == 0:
        print('Sensor {} not found on PurpleAir servers'.format(SensorID), file=sys.stderr)
        exit(1)

    pm2a = float(data['results'][0]['PM2_5Value'])
    pm2b = float(data['results'][0]['PM2_5Value'])
    pm2 = (pm2a + pm2b) / 2
    aqi = aqiFromPM(pm2)

    output = {
        'pm2.5': pm2,
        'humidity': float(data['results'][0]['humidity']),
        'temp_f': float(data['results'][0]['temp_f']),
        'pressure': float(data['results'][0]['pressure']),
        'aqi': aqi,
        'name': getName(aqi),
        'description': getDesc(aqi),
        'color': getColor(aqi),
        'colorv': getColorV(aqi)
    }
    print(json.dumps(output))
