"""
@title: bleak-pymb1
@brief A rewrite of the pymb1 library that uses bleak instead of bluepy.
@author SantX27
@license GPLv3
@version 0.0.1
"""

#Import standard python modules
import asyncio

#Import third party modules
from bleak import BleakClient, BleakScanner

class MiBand():
    def __init__(self, gender, age, height, weight, alias, which_hand, keep_data):
        """
        @param {MiBand} self
        @param {integer} gender (0=female, 1=man, 2=other)
        @param {integer} age
        @param {integer} height in cm (e.g.: 175)
        @param {integer} weight in kg (e.g.: 75)
        @param {string} alias user name (ex: "jbegood")
        @param {integer} which_hand (left=0, right=1)
        @param {boolean} keep_data inside the MiBand ?
        @return None
        """

        # Some initializations
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.alias = alias
        self.which_hand = which_hand
        self.keep_data = keep_data
    
    async def scan_and_connect(self, timeout, bluetooth_address, rssi_threshold):
        """
        @param {MiBand} self
        @param {integer} timeout in seconds
        @param {string} bluetooth_address (ex: "88:0f:10:ed:aa:bd")
        @param {integer} rssi_threshold in dBm
        @return {boolean} True if the connection was successful, False otherwise
        """
        # Scan for MiBand
        print("Scanning for MiBand...")
        scanner = BleakScanner()
        devices = await scanner.discover(timeout=timeout)
        for device in devices:
            print(device.address, device.rssi, device.name)
            if device.address.casefold() == bluetooth_address.casefold() and device.rssi > rssi_threshold:
                print(f"Found MiBand ({bluetooth_address})")
                break
        else:
            print("Could not find MiBand.")
            return False
        
        # Connect to MiBand
        print("Connecting to MiBand...")
        self.client = BleakClient(device.address)
        await self.client.connect()
        if self.client.is_connected:
            print("Connection was successful.")
            return True
        else:
            print("Connection failed.")
            return False

    def get_services_and_characteristics(self):
        """
        List of all methods used by the MiBand.
        @param {MiBand1A} self
        @return None
        """
        # Get useful services
        #print(self.device.getState())
        #self.mili_service =  self.device.getServiceByUUID("0000fee0-0000-1000-8000-00805f9b34fb")
        #self.alert_service = self.device.getServiceByUUID("00001802-0000-1000-8000-00805f9b34fb")

        # Get useful characteristics
        self.device_info_characteristic =    "0000ff01-0000-1000-8000-00805f9b34fb"
        self.device_name_characteristic =    "0000ff02-0000-1000-8000-00805f9b34fb"
        self.notification_characteristic =   "0000ff03-0000-1000-8000-00805f9b34fb"
        self.user_info_characteristic =      "0000ff04-0000-1000-8000-00805f9b34fb"
        self.control_point_characteristic =  "0000ff05-0000-1000-8000-00805f9b34fb"
        self.realtime_steps_characteristic = "0000ff06-0000-1000-8000-00805f9b34fb"
        self.activity_data_characteristic =  "0000ff07-0000-1000-8000-00805f9b34fb"
        self.firmware_data_characteristic =  "0000ff08-0000-1000-8000-00805f9b34fb"
        self.le_params_characteristic =      "0000ff09-0000-1000-8000-00805f9b34fb"
        self.date_time_characteristic =      "0000ff0a-0000-1000-8000-00805f9b34fb"
        self.statistics_characteristic =     "0000ff0b-0000-1000-8000-00805f9b34fb"
        self.battery_characteristic =        "0000ff0c-0000-1000-8000-00805f9b34fb"
        self.test_characteristic =           "0000ff0d-0000-1000-8000-00805f9b34fb"
        self.sensor_data_characteristic =    "0000ff0e-0000-1000-8000-00805f9b34fb"
        self.pair_characteristic =           "0000ff0f-0000-1000-8000-00805f9b34fb"
        self.vibrate_characteristic =        "00002a06-0000-1000-8000-00805f9b34fb"

    async def subscribe_to_notifications(self):
        """Method to subscribe to all interesting notification characteristics
        @param {MiBand1A} self
        @return None
        """
        subscribe_command = bytes([0x01, 0x00])

        #await self.client.write_gatt_char(self.notification_characteristic, subscribe_command)

        #await self.client.write_gatt_char(self.activity_data_characteristic, subscribe_command)

        await self.client.write_gatt_char(self.sensor_data_characteristic, subscribe_command)

    async def read_battery_data(self):
        """Method to read battery informations
        @param {MiBand1A} self
        @return {dict} battery_informations
        """
        data = await self.client.read_gatt_char(self.battery_characteristic)
        #print("DEBUG => ", data)
        # Analyse and decode bytes
        battery_data = {}
        if len(data) == 10:
            level = data[0]
            year = data[1] + 2000
            month = data[2] + 1
            day = data[3]
            hour = data[4]
            minute = data[5]
            second = data[6]
            cycles = 0xffff & (0xff & data[7] | (0xff & data[8]) << 8)
            status = data[9]

            # Package all as a dictionary
            battery_data = {"level": level, "year":year, "month": month, "day": day, "hour": hour, "minute": minute, "second":second, "cycles": cycles, "status": status}

        return battery_data
    
    async def vibrate(self, duration, led):
        # Types of vibration
        # 0x00: Stop vibration
        # 0x01: Short vibration (2 Beeps) + LED
        # 0x02: Long vibration (10 Beeps) + LED (Breaks with short duration)
        # 0x03: Seems the same as 0x01
        # 0x04: Short vibration (2 Beeps) with no LED
        if led is True:
            led_command = bytes([0x01])
        else:
            led_command = bytes([0x04])
        await self.client.write_gatt_char(self.vibrate_characteristic, led_command)
        await asyncio.sleep(duration)
        await self.client.write_gatt_char(self.vibrate_characteristic, bytes([0x00]))

    # async def test_mode(self):
    # Can't get it to work
    #     await self.client.write_gatt_char(self.test_characteristic, bytes([0x02]))

    async def read_name(self):
        name_data = await self.client.read_gatt_char(self.device_name_characteristic)
        return name_data
