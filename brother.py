import asyncio
import pysnmp.hlapi.asyncio as hlapi
import sys
from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    UsmUserData,
    getCmd,
)

OIDS_TEXT = {
    "serial_no": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0",
    "status": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.4.5.2.0",
    "model": "1.3.6.1.4.1.2435.2.4.3.2435.5.13.3.0",
    "firmware_ver": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.17.0",
}

OIDS_HEX = {
    "brInfoCounter": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.10.0",
    "brInfoMaintenance": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.8.0",
    "brInfoNextCare": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.11.0",
    "brInfoReplaceCount": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.20.0",
    "brInfoJamCount": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.21.0",
    "brInfoCoverage": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.18.0",
}


async def main():

    if not sys.argv:
        print("No host address!")
        return

    host = sys.argv[1]

    data = {}

    oids = (
        ObjectType(ObjectIdentity(OIDS_TEXT["serial_no"])),
        ObjectType(ObjectIdentity(OIDS_TEXT["status"])),
        ObjectType(ObjectIdentity(OIDS_TEXT["model"])),
        ObjectType(ObjectIdentity(OIDS_TEXT["firmware_ver"])),
    )

    request_args = [
        SnmpEngine(),
        CommunityData("public", mpModel=0),
        UdpTransportTarget((host, 161)),
        ContextData(),
    ]

    errindication, errstatus, errindex, restable = await getCmd(*request_args, *oids)

    if errindication:
        print(f"SNMP error: {errindication}")
    elif errstatus:
        print(f"SNMP error: {errstatus}, {errindex}")
    else:
        for resrow in restable:
            data[str(resrow[0])] = str(resrow[-1])

    oids = (
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoCounter"])),
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoMaintenance"])),
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoNextCare"])),
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoReplaceCount"])),
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoJamCount"])),
        ObjectType(ObjectIdentity(OIDS_HEX["brInfoCoverage"])),
    )

    errindication, errstatus, errindex, restable = await getCmd(*request_args, *oids)

    if errindication:
        print(f"SNMP error: {errindication}")
    elif errstatus:
        print(f"SNMP error: {errstatus}, {errindex}")
    else:
        for resrow in restable:
            temp = resrow[-1].asOctets()
            temp = ''.join(['%.2x' % x for x in temp])[0:-2]
            temp = [temp[ind:ind+14] for ind in range(0, len(temp), 14)]
            data[str(resrow[0])] = temp
    print("----------RAW DATA------------")
    for key, value in data.items():
        print(f"{key}: {value}")
    print("----------PARSED DATA---------")
    print(f"model: {data[OIDS_TEXT['model']]}")
    print(f"serial no: {data[OIDS_TEXT['serial_no']]}")
    print(f"status: {data[OIDS_TEXT['status']]}")
    print(f"firmware version: {data[OIDS_TEXT['firmware_ver']]}")
    for word in data[OIDS_HEX['brInfoMaintenance']]:
        if word[:2] == "11":
            print(f"drum counter: {int(word[-8:], 16)}")
        elif word[:2] == "63":
            print(f"drum status: {int(word[-8:], 16)}")
        elif word[:2] == "41":
            print(f"drum remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "31":
            print(f"toner status: {int(word[-8:], 16)}")
        elif word[:2] == "69":
            print(f"belt unit remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "6a":
            print(f"fuser remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "6b":
            print(f"laser remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "6c":
            print(f"pf kit mp remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "6d":
            print(f"pf kit 1 remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "6f":
            print(f"toner remaining life: {round(int(word[-8:], 16) / 100)}%")
        elif word[:2] == "81":
            print(f"black toner: {int(word[-8:], 16)}%")
        elif word[:2] == "82":
            print(f"cyan toner: {int(word[-8:], 16)}%")
        elif word[:2] == "83":
            print(f"magenta toner: {int(word[-8:], 16)}%")
        elif word[:2] == "84":
            print(f"yellow toner: {int(word[-8:], 16)}%")

    for word in data[OIDS_HEX['brInfoNextCare']]:
        if word[:2] == "82":
            print(f"drum remaining pages: {int(word[-8:], 16)}")
        elif word[:2] == "88":
            print(f"belt unit remaining pages: {int(word[-8:], 16)}")
        elif word[:2] == "89":
            print(f"fuser unit remaining pages: {int(word[-8:], 16)}")
        elif word[:2] == "73":
            print(f"laser unit remaining pages: {int(word[-8:], 16)}")
        elif word[:2] == "86":
            print(f"pf kit mp remaining pages: {int(word[-8:], 16)}")
        elif word[:2] == "77":
            print(f"pf kit 1 remaining pages: {int(word[-8:], 16)}")

    for word in data[OIDS_HEX['brInfoCounter']]:
        if word[:2] == "00":
            print(f"printer counter: {int(word[-8:], 16)}")
        elif word[:2] == "01":
            print(f"b/w page counter: {int(word[-8:], 16)}")
        elif word[:2] == "02":
            print(f"color page counter: {int(word[-8:], 16)}")
        elif word[:2] == "12":
            print(f"black counter: {int(word[-8:], 16)}")
        elif word[:2] == "13":
            print(f"cyan counter: {int(word[-8:], 16)}")
        elif word[:2] == "14":
            print(f"magenta counter: {int(word[-8:], 16)}")
        elif word[:2] == "15":
            print(f"yellow counter: {int(word[-8:], 16)}")
        elif word[:2] == "16":
            print(f"image counter: {int(word[-8:], 16)}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()