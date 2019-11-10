import asyncio
import re

from aiohttp import ClientSession, ClientError

URL_INFO = "http://{}/general/information.html"
URL_STATUS = "http://{}/general/status.html"

MAX_IMAGE_HEIGHT = 56

REGEX_STATUS = r"<dd>.*>(\w+\s?\w+)\s+<.*</dd>"
REGEX_RES_BLACK = r"alt=\"Black\" class=\"tonerremain\" height=\"(\d+)\""
REGEX_MODEL = r"<div id=\"modelName\"><h1>(.+)\sseries<\/h1"
REGEX_SERIAL_NO = r"<dt>Serial&#32;no.<\/dt><dd>(\w+)<\/dd>"
REGEX_FIRMWARE_VER = r"<dt>Main&#32;Firmware&#32;Version<\/dt><dd>(\d+\.\d+)<\/dd>"
REGEX_PAGE_COUNT = r"<dt>Page&#32;Counter<\/dt><dd>(\d+)<\/dd>"
REGEX_DRUM_COUNT = r"<dt>Drum&#32;Count<\/dt><dd>(\d+)<\/dd>"
REGEX_DRUM_USAGE = r"<dt>\(%&#32;of&#32;Life&#32;Remaining\)<\/dt><dd>\((\d+)\.\d+%\)<\/dd>"

HOST = "brother.bieniu.lan"

async def main():
    url = URL_INFO.format(HOST)
    print(f"URL: {url}")
    try:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
    except ClientError as error:
        print(f"Error: {error}")
    info_page = data

    model = re.findall(REGEX_MODEL, info_page)[0]
    serial_no = re.findall(REGEX_SERIAL_NO, info_page)[0]
    firmware_ver = re.findall(REGEX_FIRMWARE_VER, info_page)[0]
    page_count = int(re.findall(REGEX_PAGE_COUNT, info_page)[0])
    drum_count = int(re.findall(REGEX_DRUM_COUNT, info_page)[0])
    drum_usage = 100 - int(re.findall(REGEX_DRUM_USAGE, info_page)[0])
    print(f"model: {model}, serial: {serial_no}, firmware version: {firmware_ver}, page counter: {page_count}, drum counter: {drum_count}, drum usage: {drum_usage}%")

    url = URL_STATUS.format(HOST)
    print(f"URL: {url}")
    try:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
    except ClientError as error:
        print(f"Error: {error}")
    status_page = data

    status = re.findall(REGEX_STATUS, status_page)[0].lower()
    black = round(int(re.findall(REGEX_RES_BLACK, status_page)[0]) / MAX_IMAGE_HEIGHT * 100)

    print(f"Status: {status}, black toner: {black}%")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()