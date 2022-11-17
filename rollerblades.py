#!/usr/bin/env python3

import logging
import os
import json
import requests
import urllib3
import xml.etree.ElementTree as ET
from time import strftime, sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # noqa E501

# --- To be passed in to container ---
# Required Vars
SCHEME = os.getenv('SCHEME', 'https')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT', '32400')
TOKEN = os.getenv('TOKEN')
INTERVAL = int(os.getenv('INTERVAL', 3600))
PREROLLS = os.getenv('PREROLLS', '/config/prerolls.json')
JANUARY = int(os.getenv('JANUARY', 1))
FEBRUARY = int(os.getenv('FEBRUARY', 1))
MARCH = int(os.getenv('MARCH', 1))
APRIL = int(os.getenv('APRIL', 1))
MAY = int(os.getenv('MAY', 1))
JUNE = int(os.getenv('JUNE', 1))
JULY = int(os.getenv('JULY', 1))
AUGUST = int(os.getenv('AUGUST', 1))
SEPTEMBER = int(os.getenv('SEPTEMBER', 1))
OCTOBER = int(os.getenv('OCTOBER', 1))
NOVEMBER = int(os.getenv('NOVEMBER', 1))
DECEMBER = int(os.getenv('DECEMBER', 1))
DEBUG = int(os.getenv('DEBUG', 0))

# --- Globals ---
VER = '0.5'
USER_AGENT = f"rollerblades.py/{VER}"
KEY = 'CinemaTrailersPrerollID'

HEADERS = {
    "User-Agent": USER_AGENT
}

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def load_prerolls(file: str) -> dict:
    with open(file, "r") as f:
        prerolls = json.load(f)
    return prerolls


def get_current_preroll(scheme: str, host: str, port: str, token: str) -> str:
    url = f"{scheme}://{host}:{port}/:/prefs?X-Plex-Token={token}"
    r = requests.get(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"HTTP status code: {r.status_code}.")
    root = ET.fromstring(r.content)
    return root.findall(".//*[@id='CinemaTrailersPrerollID']")[0].attrib['value']  # noqa E501


def update_preroll(scheme: str, host: str, port: str, token: str, key: str, preroll: str) -> int:  # noqa E501
    url = f"{scheme}://{host}:{port}/:/prefs?{key}={preroll}&X-Plex-Token={token}"  # noqa E501
    r = requests.put(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"Update HTTP status code: {r.status_code}.")
    return r.status_code


def main() -> None:
    logger.info(f"Startup {USER_AGENT}.")
    my_prerolls = load_prerolls(PREROLLS)
    logger.info(f"Loaded in prerolls data from {PREROLLS}.")
    while True:
        current_preroll = get_current_preroll(SCHEME, HOST, PORT, TOKEN)
        logger.info(f"Current preroll is: {current_preroll}.")
        current_month = strftime("%m")
        todays_date = strftime("%m%d")

        if my_prerolls['HOLIDAYS'].get(todays_date) is not None:
            # If match on a holiday in the list of holidays, use that
            new_preroll = my_prerolls['HOLIDAYS'].get(todays_date)
        elif current_month == "01" and JANUARY == 1:
            # If it's January
            new_preroll = my_prerolls['SPECIAL_MONTHS']['January']
        elif current_month == "02" and FEBRUARY == 1:
            # If it's February
            new_preroll = my_prerolls['SPECIAL_MONTHS']['February']
        elif current_month == "03" and MARCH == 1:
            # If it's March
            new_preroll = my_prerolls['SPECIAL_MONTHS']['March']
        elif current_month == "04" and APRIL == 1:
            # If it's April
            new_preroll = my_prerolls['SPECIAL_MONTHS']['April']         
        elif current_month == "05" and MAY == 1:
            # If it's May
            new_preroll = my_prerolls['SPECIAL_MONTHS']['May']
        elif current_month == "06" and JUNE == 1:
            # If it's June
            new_preroll = my_prerolls['SPECIAL_MONTHS']['June']
        elif current_month == "07" and JULY == 1:
            # If it's July
            new_preroll = my_prerolls['SPECIAL_MONTHS']['July']
        elif current_month == "08" and AUGUST == 1:
            # If it's August
            new_preroll = my_prerolls['SPECIAL_MONTHS']['August'] 
        elif current_month == "09" and SEPTEMBER == 1:
            # If it's September
            new_preroll = my_prerolls['SPECIAL_MONTHS']['September']                    
        elif current_month == "10" and OCTOBER == 1 and my_prerolls['SPECIAL_MONTHS']['October'] is not None:
            # If it's October
            new_preroll = my_prerolls['SPECIAL_MONTHS']['October'] 
        elif current_month == "11" and NOVEMBER == 1 and my_prerolls['SPECIAL_MONTHS'] is not None:
            # If it's November
            new_preroll = my_prerolls['SPECIAL_MONTHS']['November']            
        elif current_month == "12" and DECEMBER == 1:
            # If it's December
            new_preroll = my_prerolls['SPECIAL_MONTHS']['December']
        else:
            # otherwise use the day of the week
            new_preroll = f'{my_prerolls["DAILYPATH"]}'  # noqa E501

        # If there's a change from the current preroll, update Plex
        if new_preroll != current_preroll:
            logger.info(f"Change {current_preroll} to {new_preroll}.")
            update_preroll(SCHEME, HOST, PORT, TOKEN, KEY, new_preroll)

        # take a nap for an hour and do it again
        sleep(INTERVAL)


if __name__ == "__main__":
    main()
