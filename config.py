import json, time
import sys
from termcolor import cprint
from datetime import date, datetime
import datetime as date_timestamp
import math
import random
import asyncio, aiohttp
from loguru import logger
from setting import *

logger.remove()
logger.add(sys.stderr,
           format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level>| <level>{message}</level>")
logger.add("results/outputXlogfile.log", rotation="1 day")

outfile = ''
with open(f"{outfile}data/wallets.txt", "r") as f:
    WALLETS = [row.strip() for row in f]

with open(f"{outfile}data/proxies.txt", "r") as f:
    PROXIES = [row.strip() for row in f]
