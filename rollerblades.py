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
PRIDEMONTH = int(os.getenv('PRIDEMONTH', 1))
DECEMBER = int(os.getenv('DECEMBER', 1))
OCTOBER = int(os.getenv('OCTOBER', 1))
NOVEMBER = int(os.getenv('NOVEMBER', 1))
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

        if current_month == "06" and PRIDEMONTH == 1:
            # If it's June and you're supportive, use the pride month preroll
            new_preroll = my_prerolls['SPECIAL_MONTHS']['June']
        elif current_month == "12" and DECEMBER == 1:
            # If it's December celebrate Christmas
            new_preroll = my_prerolls['SPECIAL_MONTHS']['December']
        elif current_month == "11" and NOVEMBER == 1:
            # If it's November celebrate Thanksgiving
            new_preroll = my_prerolls['SPECIAL_MONTHS']['November']
        elif current_month == "10" and OCTOBER == 1:
            # If it's December celebrate Christmas
            new_preroll = my_prerolls['SPECIAL_MONTHS']['October']    
        elif my_prerolls['HOLIDAYS'].get(todays_date) is not None:
            # If match on a holiday in the list of holidays, use that
            new_preroll = my_prerolls['HOLIDAYS'].get(todays_date)
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
