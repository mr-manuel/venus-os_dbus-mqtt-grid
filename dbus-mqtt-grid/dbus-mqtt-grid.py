#!/usr/bin/env python

from gi.repository import GLib
import platform
import logging
import sys
import os
import time
import json
import paho.mqtt.client as mqtt
import configparser # for config/ini file
import _thread

# import Victron Energy packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'ext', 'velib_python'))
from vedbus import VeDbusService

# use WARNING for default, INFO for displaying actual steps and values, DEBUG for debugging
logging.basicConfig(level=logging.WARNING)

# get values from config.ini file
try:
    config = configparser.ConfigParser()
    config.read("%s/config.ini" % (os.path.dirname(os.path.realpath(__file__))))
    if (config['MQTT']['broker_address'] == "IP_ADDR_OR_FQDN"):
        logging.error("config.ini file using invalid default values.")
        raise
except:
    logging.error("config.ini file not found. Copy or rename the config.sample.ini to config.ini")
    sys.exit()

# set variables
connected = 0

grid_power = 0
grid_current = 0
grid_voltage = 0
grid_forward = 0
grid_reverse = 0

grid_L1_power = None
grid_L1_current = None
grid_L1_voltage = None
grid_L1_forward = None
grid_L1_reverse = None

grid_L2_power = None
grid_L2_current = None
grid_L2_voltage = None
grid_L2_forward = None
grid_L2_reverse = None

grid_L3_power = None
grid_L3_current = None
grid_L3_voltage = None
grid_L3_forward = None
grid_L3_reverse = None


# MQTT requests
def on_disconnect(client, userdata, rc):
    global connected
    logging.warning("MQTT client: Got disconnected")
    if rc != 0:
        logging.debug('MQTT client: Unexpected MQTT disconnection. Will auto-reconnect')
    else:
        logging.debug('MQTT client: rc value:' + str(rc))

    try:
        logging.info("MQTT client: Trying to reconnect")
        client.connect(config['MQTT']['broker_address'])
        connected = 1
    except Exception as e:
        logging.error("MQTT client: Error in retrying to connect with broker: %s" % e)
        connected = 0

def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        logging.info("MQTT client: Connected to MQTT broker!")
        connected = 1
        client.subscribe(config['MQTT']['topic_meters'])
    else:
        logging.error("MQTT client: Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    try:

        global grid_power, grid_current, grid_voltage, grid_forward, grid_reverse, grid_L1_power, grid_L1_current, grid_L1_voltage, grid_L1_forward, grid_L1_reverse, grid_L2_power, grid_L2_current, grid_L2_voltage, grid_L2_forward, grid_L2_reverse, grid_L3_power, grid_L3_current, grid_L3_voltage, grid_L3_forward, grid_L3_reverse
        # get JSON from topic
        if msg.topic == config['MQTT']['topic_meters']:
            if msg.payload != '{"value": null}' and msg.payload != b'{"value": null}':
                jsonpayload = json.loads(msg.payload)
                grid_power   = float(jsonpayload['grid']['power'])
                grid_current = float(jsonpayload['grid']['current']) if 'current' in jsonpayload['grid'] else grid_power/float(config['DEFAULT']['voltage'])
                grid_voltage = float(jsonpayload['grid']['voltage']) if 'voltage' in jsonpayload['grid'] else float(config['DEFAULT']['voltage'])
                grid_forward = float(jsonpayload['grid']['energy_forward']) if 'energy_forward' in jsonpayload['grid'] else 0
                grid_reverse = float(jsonpayload['grid']['energy_reverse']) if 'energy_reverse' in jsonpayload['grid'] else 0

                # check if L1 and L1 -> power exists
                if 'L1' in jsonpayload['grid'] and 'power' in jsonpayload['grid']['L1']:
                    grid_L1_power   = float(jsonpayload['grid']['L1']['power'])
                    grid_L1_current = float(jsonpayload['grid']['L1']['current']) if 'current' in jsonpayload['grid']['L1'] else grid_L1_power/float(config['DEFAULT']['voltage'])
                    grid_L1_voltage = float(jsonpayload['grid']['L1']['voltage']) if 'voltage' in jsonpayload['grid']['L1'] else float(config['DEFAULT']['voltage'])
                    grid_L1_forward = float(jsonpayload['grid']['L1']['energy_forward']) if 'energy_forward' in jsonpayload['grid']['L1'] else 0
                    grid_L1_reverse = float(jsonpayload['grid']['L1']['energy_reverse']) if 'energy_reverse' in jsonpayload['grid']['L1'] else 0

                # check if L2 and L2 -> power exists
                if 'L2' in jsonpayload['grid'] and 'power' in jsonpayload['grid']['L2']:
                    grid_L2_power   = float(jsonpayload['grid']['L2']['power'])
                    grid_L2_current = float(jsonpayload['grid']['L2']['current']) if 'current' in jsonpayload['grid']['L2'] else grid_L2_power/float(config['DEFAULT']['voltage'])
                    grid_L2_voltage = float(jsonpayload['grid']['L2']['voltage']) if 'voltage' in jsonpayload['grid']['L2'] else float(config['DEFAULT']['voltage'])
                    grid_L2_forward = float(jsonpayload['grid']['L2']['energy_forward']) if 'energy_forward' in jsonpayload['grid']['L2'] else 0
                    grid_L2_reverse = float(jsonpayload['grid']['L2']['energy_reverse']) if 'energy_reverse' in jsonpayload['grid']['L2'] else 0

                # check if L3 and L3 -> power exists
                if 'L3' in jsonpayload['grid'] and 'power' in jsonpayload['grid']['L3']:
                    grid_L3_power   = float(jsonpayload['grid']['L3']['power'])
                    grid_L3_current = float(jsonpayload['grid']['L3']['current']) if 'current' in jsonpayload['grid']['L3'] else grid_L3_power/float(config['DEFAULT']['voltage'])
                    grid_L3_voltage = float(jsonpayload['grid']['L3']['voltage']) if 'voltage' in jsonpayload['grid']['L3'] else float(config['DEFAULT']['voltage'])
                    grid_L3_forward = float(jsonpayload['grid']['L3']['energy_forward']) if 'energy_forward' in jsonpayload['grid']['L3'] else 0
                    grid_L3_reverse = float(jsonpayload['grid']['L3']['energy_reverse']) if 'energy_reverse' in jsonpayload['grid']['L3'] else 0

            else:
                logging.info("Answer from MQTT was NULL and therefore it was ignored")

    except Exception as e:
        logging.error("The programm MQTTtoMeter is crashed. (on message function)")
        print(e)
        print("In the MQTTtoMeter programm something went wrong during the reading of the messages")



class DbusMqttGridService:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname='MQTT Grid',
        connection='MQTT Grid service'
    ):

        self._dbusservice = VeDbusService(servicename)
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        self._dbusservice.add_path('/ProductId', 0xFFFF)
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/CustomName', productname)
        self._dbusservice.add_path('/FirmwareVersion', '0.0.1')
        self._dbusservice.add_path('/HardwareVersion', '0.0.1')
        self._dbusservice.add_path('/Connected', 1)

        self._dbusservice.add_path('/Latency', None)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path, settings['initial'], gettextcallback=settings['textformat'], writeable=True, onchangecallback=self._handlechangedvalue
                )

        GLib.timeout_add(1000, self._update) # pause 1000ms before the next request


    def _update(self):
        self._dbusservice['/Ac/Power'] =  round(grid_power, 2) # positive: consumption, negative: feed into grid
        self._dbusservice['/Ac/Current'] = round(grid_current, 2)
        self._dbusservice['/Ac/Voltage'] = round(grid_voltage, 2)
        self._dbusservice['/Ac/Energy/Forward'] = round(grid_forward, 2)
        self._dbusservice['/Ac/Energy/Reverse'] = round(grid_reverse, 2)

        if grid_L1_power != None:
            self._dbusservice['/Ac/L1/Power'] = round(grid_L1_power, 2)
            self._dbusservice['/Ac/L1/Current'] = round(grid_L1_current, 2)
            self._dbusservice['/Ac/L1/Voltage'] = round(grid_L1_voltage, 2)
            self._dbusservice['/Ac/L1/Energy/Forward'] = round(grid_L1_forward, 2)
            self._dbusservice['/Ac/L1/Energy/Reverse'] = round(grid_L1_reverse, 2)
        else:
            self._dbusservice['/Ac/L1/Power'] = round(grid_power, 2)
            self._dbusservice['/Ac/L1/Current'] = round(grid_current, 2)
            self._dbusservice['/Ac/L1/Voltage'] = round(grid_voltage, 2)
            self._dbusservice['/Ac/L1/Energy/Forward'] = round(grid_forward, 2)
            self._dbusservice['/Ac/L1/Energy/Reverse'] = round(grid_reverse, 2)

        if grid_L2_power != None:
            self._dbusservice['/Ac/L2/Power'] = round(grid_L2_power, 2)
            self._dbusservice['/Ac/L2/Current'] = round(grid_L2_current, 2)
            self._dbusservice['/Ac/L2/Voltage'] = round(grid_L2_voltage, 2)
            self._dbusservice['/Ac/L2/Energy/Forward'] = round(grid_L2_forward, 2)
            self._dbusservice['/Ac/L2/Energy/Reverse'] = round(grid_L2_reverse, 2)

        if grid_L3_power != None:
            self._dbusservice['/Ac/L3/Power'] = round(grid_L3_power, 2)
            self._dbusservice['/Ac/L3/Current'] = round(grid_L3_current, 2)
            self._dbusservice['/Ac/L3/Voltage'] = round(grid_L3_voltage, 2)
            self._dbusservice['/Ac/L3/Energy/Forward'] = round(grid_L3_forward, 2)
            self._dbusservice['/Ac/L3/Energy/Reverse'] = round(grid_L3_reverse, 2)

        logging.info("Grid: {:.1f} W - {:.1f} V - {:.1f} A".format(grid_power, grid_voltage, grid_current))
        if grid_L1_power:
            logging.info("|- L1: {:.1f} W - {:.1f} V - {:.1f} A".format(grid_L1_power, grid_L1_voltage, grid_L1_current))
        if grid_L2_power:
            logging.info("|- L2: {:.1f} W - {:.1f} V - {:.1f} A".format(grid_L2_power, grid_L2_voltage, grid_L2_current))
        if grid_L3_power:
            logging.info("|- L3: {:.1f} W - {:.1f} V - {:.1f} A".format(grid_L3_power, grid_L3_voltage, grid_L3_current))


        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice['/UpdateIndex'] + 1  # increment index
        if index > 255:   # maximum value of the index
            index = 0       # overflow from 255 to 0
        self._dbusservice['/UpdateIndex'] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True # accept the change



def main():
    _thread.daemon = True # allow the program to quit

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)


    # MQTT setup
    client = mqtt.Client("MqttGrid")
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    # check tls and use settings, if provided
    if 'tls_enabled' in config['MQTT'] and config['MQTT']['tls_enabled'] == '1':
        logging.debug("MQTT client: TLS is enabled")

        if 'tls_path_to_ca' in config['MQTT'] and config['MQTT']['tls_path_to_ca'] != '':
            logging.debug("MQTT client: TLS: custom ca \"%s\" used" % config['MQTT']['tls_path_to_ca'])
            client.tls_set(config['MQTT']['tls_path_to_ca'], tls_version=2)
        else:
            client.tls_set(tls_version=2)

        if 'tls_insecure' in config['MQTT'] and config['MQTT']['tls_insecure'] != '':
            logging.debug("MQTT client: TLS certificate server hostname verification disabled")
            client.tls_insecure_set(True)

    # check if username and password are set
    if 'username' in config['MQTT'] and 'password' in config['MQTT'] and config['MQTT']['username'] != '' and config['MQTT']['password'] != '':
        logging.debug("MQTT client: Using username \"%s\" and password to connect" % config['MQTT']['username'])
        client.username_pw_set(username=config['MQTT']['username'], password=config['MQTT']['password'])

     # connect to broker
    client.connect(
        host=config['MQTT']['broker_address'],
        port=int(config['MQTT']['broker_port'])
    )
    client.loop_start()

    # wait to receive first data, else the JSON is empty and phase setup won't work
    while grid_power == 0:
        logging.info("Waiting 5 seconds for receiving first data...")
        time.sleep(5)


    #formatting
    _kwh = lambda p, v: (str(round(v, 2)) + 'kWh')
    _a = lambda p, v: (str(round(v, 2)) + 'A')
    _w = lambda p, v: (str(round(v, 2)) + 'W')
    _v = lambda p, v: (str(round(v, 2)) + 'V')
    _n = lambda p, v: (str(round(v, 0)))

    paths_dbus = {
        '/Ac/Power': {'initial': 0, 'textformat': _w},
        '/Ac/Current': {'initial': 0, 'textformat': _a},
        '/Ac/Voltage': {'initial': 0, 'textformat': _v},
        '/Ac/Energy/Forward': {'initial': None, 'textformat': _kwh}, # energy bought from the grid
        '/Ac/Energy/Reverse': {'initial': None, 'textformat': _kwh}, # energy sold to the grid

        '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
        '/Ac/L1/Current': {'initial': 0, 'textformat': _a},
        '/Ac/L1/Voltage': {'initial': 0, 'textformat': _v},
        '/Ac/L1/Energy/Forward': {'initial': None, 'textformat': _kwh},
        '/Ac/L1/Energy/Reverse': {'initial': None, 'textformat': _kwh},

        '/UpdateIndex': {'initial': 0, 'textformat': _n},
    }

    if grid_L2_power != None:
        paths_dbus.update({
            '/Ac/L2/Power': {'initial': 0, 'textformat': _w},
            '/Ac/L2/Current': {'initial': 0, 'textformat': _a},
            '/Ac/L2/Voltage': {'initial': 0, 'textformat': _v},
            '/Ac/L2/Energy/Forward': {'initial': None, 'textformat': _kwh},
            '/Ac/L2/Energy/Reverse': {'initial': None, 'textformat': _kwh},
        })

    if grid_L3_power != None:
        paths_dbus.update({
            '/Ac/L3/Power': {'initial': 0, 'textformat': _w},
            '/Ac/L3/Current': {'initial': 0, 'textformat': _a},
            '/Ac/L3/Voltage': {'initial': 0, 'textformat': _v},
            '/Ac/L3/Energy/Forward': {'initial': None, 'textformat': _kwh},
            '/Ac/L3/Energy/Reverse': {'initial': None, 'textformat': _kwh},
        })


    pvac_output = DbusMqttGridService(
        servicename='com.victronenergy.grid.mqtt_grid',
        deviceinstance=31,
        paths=paths_dbus
        )

    logging.info('Connected to dbus and switching over to GLib.MainLoop() (= event based)')
    mainloop = GLib.MainLoop()
    mainloop.run()



if __name__ == "__main__":
  main()
