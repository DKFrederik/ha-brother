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

    for key, value in data.items():
        print(f"{key}: {value}")

    print(f"model: {data[OIDS_TEXT['model']]}")
    print(f"serial no: {data[OIDS_TEXT['serial_no']]}")
    print("status:", data[OIDS_TEXT['status']])
    print(f"firmware version: {data[OIDS_TEXT['firmware_ver']]}")
    print(f"printer counter: {int(data[OIDS_HEX['brInfoCounter']][0][-8:], 16)}")
    print(f"drum status: {int(data[OIDS_HEX['brInfoMaintenance']][0][-8:], 16)}")
    print(f"drum counter: {int(data[OIDS_HEX['brInfoMaintenance']][1][-8:], 16)}")
    print(f"drum remaining life: {int(data[OIDS_HEX['brInfoMaintenance']][2][-8:], 16) / 100}%")
    print(f"drum remaining pages: {int(data[OIDS_HEX['brInfoNextCare']][0][-8:], 16)}")
    print(f"toner status: {int(data[OIDS_HEX['brInfoMaintenance']][3][-8:], 16)}")
    print(f"black toner: {int(data[OIDS_HEX['brInfoMaintenance']][5][-8:], 16)}%")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()