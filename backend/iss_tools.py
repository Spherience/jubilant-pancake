import datetime as dt
import json
from pathlib import Path
import sys
import io
from orbit_predictor.sources import EtcTLESource
from orbit_predictor.locations import Location
# import requests
import urllib.request

# https://live.ariss.org/iss.txt TLE
urllib.request.urlretrieve("https://live.ariss.org/iss.txt", "iss.tle")
source = EtcTLESource(filename="iss.tle")
# https://live.ariss.org/iss.txt

predictor = source.get_predictor("ISS (ZARYA)")

def printDeltaTime(deltaSeconds = 0):
   t = (dt.datetime.utcnow() + dt.timedelta(seconds = deltaSeconds ))
   return t.strftime('%a %d %b %Y, %I:%M%p')

def getIssLocation(utcTime):
    # Get ISS position
    # issTime = (dt.datetime.utcnow() + dt.timedelta(seconds = issDeltaTime ))
    issTime = utcTime
    position = predictor.get_position(issTime)
    llh_tuple = position.position_llh
    issLat=llh_tuple[0]
    issLng=llh_tuple[1]
    return (issLat, issLng)

def nextPassOver(lat, lng , utcTime):
    location = Location(f"lat:{lat}; lng:{lng}", latitude_deg=float(lat), longitude_deg=float(lng), elevation_m=0.0)
    nextpass = predictor.get_next_pass(location, utcTime)     
    # pass_time = nextpass.aos
    return nextpass

def getTrajectory(start_time, end_time, step):
    result = []
    current = start_time

    while current < end_time:
        result.append(getIssLocation(current))
        current = current + step

    return result