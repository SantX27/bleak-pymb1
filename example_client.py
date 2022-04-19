# This is an example client for the bleak_pymb1.py module.
# Change the MAC address to the one of your MiBand or specify it in the argument.

import sys
import asyncio

import bleak_pymb1

MAC_ADDR = "88:0F:10:XX:XX:XX"

#Main
async def main():
    print("Creating MiBand data object...")
    mi_band = bleak_pymb1.MiBand(gender=2, age=25, height=175, weight=70, alias="Test", which_hand=0, keep_data=True)
    print(f"Try connecting to MiBand ({MAC_ADDR})...")
    if await mi_band.scan_and_connect(5.0, MAC_ADDR, -80) == True:
        print("Getting services...")
        mi_band.get_services_and_characteristics()
        print("Subscribing to notifications...")
        await mi_band.subscribe_to_notifications()
        print("Reading name...")
        print(await mi_band.read_name())
        print("Reading battery level...")
        battery_data = await mi_band.read_battery_data()
        print(f"Battery level: {battery_data['level']}%")
        while True:
            print("Vibrate MiBand with LEDs on...")
            await mi_band.vibrate(3.0, True)
            print("Vibrate MiBand with LEDs off...")
            await mi_band.vibrate(3.0, False)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else MAC_ADDR))