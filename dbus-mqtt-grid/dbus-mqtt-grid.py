#!/usr/bin/env python

from gi.repository import GLib  # pyright: ignore[reportMissingImports]
import platform
import logging
import sys
import os
from time import sleep, time
import json
import paho.mqtt.client as mqtt
import configparser  # for config/ini file
import _thread

# import Victron Energy packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService


# get values from config.ini file
try:
    config_file = (os.path.dirname(os.path.realpath(__file__))) + "/config.ini"
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if config["MQTT"]["broker_address"] == "IP_ADDR_OR_FQDN":
            print(
                'ERROR:The "config.ini" is using invalid default values like IP_ADDR_OR_FQDN. The driver restarts in 60 seconds.'
            )
            sleep(60)
            sys.exit()
    else:
        print(
            'ERROR:The "'
            + config_file
            + '" is not found. Did you copy or rename the "config.sample.ini" to "config.ini"? The driver restarts in 60 seconds.'
        )
        sleep(60)
        sys.exit()

except Exception:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    file = exception_traceback.tb_frame.f_code.co_filename
    line = exception_traceback.tb_lineno
    print(
        f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
    )
    print("ERROR:The driver restarts in 60 seconds.")
    sleep(60)
    sys.exit()


# Get logging level from config.ini
# ERROR = shows errors only
# WARNING = shows ERROR and warnings
# INFO = shows WARNING and running functions
# DEBUG = shows INFO and data/values
if "DEFAULT" in config and "logging" in config["DEFAULT"]:
    if config["DEFAULT"]["logging"] == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif config["DEFAULT"]["logging"] == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif config["DEFAULT"]["logging"] == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.WARNING)


# get timeout
if "DEFAULT" in config and "timeout" in config["DEFAULT"]:
    timeout = int(config["DEFAULT"]["timeout"])
else:
    timeout = 60


# set variables
connected = 0
last_changed = 0
last_updated = 0

grid_power = -1
grid_current = 0
grid_voltage = 0
grid_forward = 0
grid_reverse = 0

grid_L1_power = None
grid_L1_current = None
grid_L1_voltage = None
grid_L1_frequency = None
grid_L1_forward = None
grid_L1_reverse = None

grid_L2_power = None
grid_L2_current = None
grid_L2_voltage = None
grid_L2_frequency = None
grid_L2_forward = None
grid_L2_reverse = None

grid_L3_power = None
grid_L3_current = None
grid_L3_voltage = None
grid_L3_frequency = None
grid_L3_forward = None
grid_L3_reverse = None


# MQTT requests
def on_disconnect(client, userdata, rc):
    global connected
    logging.warning("MQTT client: Got disconnected")
    if rc != 0:
        logging.warning(
            "MQTT client: Unexpected MQTT disconnection. Will auto-reconnect"
        )
    else:
        logging.warning("MQTT client: rc value:" + str(rc))

    while connected == 0:
        try:
            logging.warning("MQTT client: Trying to reconnect")
            client.connect(config["MQTT"]["broker_address"])
            connected = 1
        except Exception as err:
            logging.error(
                f"MQTT client: Error in retrying to connect with broker ({config['MQTT']['broker_address']}:{config['MQTT']['broker_port']}): {err}"
            )
            logging.error("MQTT client: Retrying in 15 seconds")
            connected = 0
            sleep(15)


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        logging.info("MQTT client: Connected to MQTT broker!")
        connected = 1
        client.subscribe(config["MQTT"]["topic"])
    else:
        logging.error("MQTT client: Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:
        global last_changed, grid_power, grid_current, grid_voltage, grid_forward, grid_reverse, \
            grid_L1_power, grid_L1_current, grid_L1_voltage, grid_L1_frequency, grid_L1_forward, grid_L1_reverse, \
            grid_L2_power, grid_L2_current, grid_L2_voltage, grid_L2_frequency, grid_L2_forward, grid_L2_reverse, \
            grid_L3_power, grid_L3_current, grid_L3_voltage, grid_L3_frequency, grid_L3_forward, grid_L3_reverse

        # get JSON from topic
        if msg.topic == config["MQTT"]["topic"]:
            if msg.payload != "" and msg.payload != b"":
                jsonpayload = json.loads(msg.payload)

                last_changed = int(time())

                if "grid" in jsonpayload:
                    if isinstance(jsonpayload["grid"], dict):
                        if "power" in jsonpayload["grid"]:
                            grid_power = float(jsonpayload["grid"]["power"])
                            grid_voltage = (
                                float(jsonpayload["grid"]["voltage"])
                                if "voltage" in jsonpayload["grid"]
                                else float(config["DEFAULT"]["voltage"])
                            )
                            grid_current = (
                                float(jsonpayload["grid"]["current"])
                                if "current" in jsonpayload["grid"]
                                else (
                                    grid_power / grid_voltage
                                    if grid_voltage != 0
                                    else 0
                                )
                            )
                            grid_forward = (
                                float(jsonpayload["grid"]["energy_forward"])
                                if "energy_forward" in jsonpayload["grid"]
                                else None
                            )
                            grid_reverse = (
                                float(jsonpayload["grid"]["energy_reverse"])
                                if "energy_reverse" in jsonpayload["grid"]
                                else None
                            )

                            # check if L1 and L1 -> power exists
                            if (
                                "L1" in jsonpayload["grid"]
                                and "power" in jsonpayload["grid"]["L1"]
                            ):
                                grid_L1_power = float(jsonpayload["grid"]["L1"]["power"])
                                grid_L1_voltage = (
                                    float(jsonpayload["grid"]["L1"]["voltage"])
                                    if "voltage" in jsonpayload["grid"]["L1"]
                                    else float(config["DEFAULT"]["voltage"])
                                )
                                grid_L1_current = (
                                    float(jsonpayload["grid"]["L1"]["current"])
                                    if "current" in jsonpayload["grid"]["L1"]
                                    else (
                                        grid_L1_power / grid_L1_voltage
                                        if grid_L1_voltage != 0
                                        else 0

                                    )
                                )
                                grid_L1_frequency = (
                                    float(jsonpayload["grid"]["L1"]["frequency"])
                                    if "frequency" in jsonpayload["grid"]["L1"]
                                    else None
                                )
                                grid_L1_forward = (
                                    float(jsonpayload["grid"]["L1"]["energy_forward"])
                                    if "energy_forward" in jsonpayload["grid"]["L1"]
                                    else 0
                                )
                                grid_L1_reverse = (
                                    float(jsonpayload["grid"]["L1"]["energy_reverse"])
                                    if "energy_reverse" in jsonpayload["grid"]["L1"]
                                    else 0
                                )

                            # check if L2 and L2 -> power exists
                            if (
                                "L2" in jsonpayload["grid"]
                                and "power" in jsonpayload["grid"]["L2"]
                            ):
                                grid_L2_power = float(jsonpayload["grid"]["L2"]["power"])
                                grid_L2_voltage = (
                                    float(jsonpayload["grid"]["L2"]["voltage"])
                                    if "voltage" in jsonpayload["grid"]["L2"]
                                    else float(config["DEFAULT"]["voltage"])
                                )
                                grid_L2_current = (
                                    float(jsonpayload["grid"]["L2"]["current"])
                                    if "current" in jsonpayload["grid"]["L2"]
                                    else (
                                        grid_L2_power / grid_L2_voltage
                                        if grid_L2_voltage != 0
                                        else 0
                                    )
                                )
                                grid_L2_frequency = (
                                    float(jsonpayload["grid"]["L2"]["frequency"])
                                    if "frequency" in jsonpayload["grid"]["L2"]
                                    else None
                                )
                                grid_L2_forward = (
                                    float(jsonpayload["grid"]["L2"]["energy_forward"])
                                    if "energy_forward" in jsonpayload["grid"]["L2"]
                                    else 0
                                )
                                grid_L2_reverse = (
                                    float(jsonpayload["grid"]["L2"]["energy_reverse"])
                                    if "energy_reverse" in jsonpayload["grid"]["L2"]
                                    else 0
                                )

                            # check if L3 and L3 -> power exists
                            if (
                                "L3" in jsonpayload["grid"]
                                and "power" in jsonpayload["grid"]["L3"]
                            ):
                                grid_L3_power = float(jsonpayload["grid"]["L3"]["power"])
                                grid_L3_voltage = (
                                    float(jsonpayload["grid"]["L3"]["voltage"])
                                    if "voltage" in jsonpayload["grid"]["L3"]
                                    else float(config["DEFAULT"]["voltage"])
                                )
                                grid_L3_current = (
                                    float(jsonpayload["grid"]["L3"]["current"])
                                    if "current" in jsonpayload["grid"]["L3"]
                                    else (
                                        grid_L3_power / grid_L3_voltage
                                        if grid_L3_voltage != 0
                                        else 0

                                    )
                                )
                                grid_L3_frequency = (
                                    float(jsonpayload["grid"]["L3"]["frequency"])
                                    if "frequency" in jsonpayload["grid"]["L3"]
                                    else None
                                )
                                grid_L3_forward = (
                                    float(jsonpayload["grid"]["L3"]["energy_forward"])
                                    if "energy_forward" in jsonpayload["grid"]["L3"]
                                    else 0
                                )
                                grid_L3_reverse = (
                                    float(jsonpayload["grid"]["L3"]["energy_reverse"])
                                    if "energy_reverse" in jsonpayload["grid"]["L3"]
                                    else 0
                                )
                        # for Tasmota support
                        # the power and power_L1-3 values have to be sent within the same second or
                        # power as last one, else on startup the phases are not correctly recognized
                        elif "power_L1" in jsonpayload["grid"]:
                            grid_L1_power = float(jsonpayload["grid"]["power_L1"])
                            grid_L1_voltage = float(config["DEFAULT"]["voltage"])
                            grid_L1_current = grid_L1_power / float(config["DEFAULT"]["voltage"])
                            grid_L1_frequency = None
                            grid_L1_forward = 0
                            grid_L1_reverse = 0
                        elif "power_L2" in jsonpayload["grid"]:
                            grid_L2_power = float(jsonpayload["grid"]["power_L2"])
                            grid_L2_voltage = float(config["DEFAULT"]["voltage"])
                            grid_L2_current = grid_L2_power / float(config["DEFAULT"]["voltage"])
                            grid_L2_frequency = None
                            grid_L2_forward = 0
                            grid_L2_reverse = 0
                        elif "power_L3" in jsonpayload["grid"]:
                            grid_L3_power = float(jsonpayload["grid"]["power_L3"])
                            grid_L3_voltage = float(config["DEFAULT"]["voltage"])
                            grid_L3_current = grid_L3_power / float(config["DEFAULT"]["voltage"])
                            grid_L3_frequency = None
                            grid_L3_forward = 0
                            grid_L3_reverse = 0
                        else:
                            logging.error(
                                'Received JSON MQTT message does not include a power object in the grid object. Expected at least: {"grid": {"power": 0.0}"}'
                            )
                            logging.debug("MQTT payload: " + str(msg.payload)[1:])
                    else:
                        logging.error(
                            'Received JSON MQTT message grid object is not of type dictionary. Expected at least: {"grid": {"power": 0.0}"}'
                        )
                        logging.debug("MQTT payload: " + str(msg.payload)[1:])
                else:
                    logging.error(
                        'Received JSON MQTT message does not include a grid object. Expected at least: {"grid": {"power": 0.0}"}'
                    )
                    logging.debug("MQTT payload: " + str(msg.payload)[1:])

            else:
                logging.warning(
                    "Received JSON MQTT message was empty and therefore it was ignored"
                )
                logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except ValueError as e:
        logging.error("Received message is not a valid JSON. %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except Exception:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        file = exception_traceback.tb_frame.f_code.co_filename
        line = exception_traceback.tb_lineno
        print(
            f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
        )
        logging.debug("MQTT payload: " + str(msg.payload)[1:])


class DbusMqttGridService:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Grid",
        customname="MQTT Grid",
        connection="MQTT Grid service",
    ):
        self._dbusservice = VeDbusService(servicename)
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.1.5 (20231219)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Latency", None)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed, last_updated

        now = int(time())

        try:

            if last_changed != last_updated:
                self._dbusservice["/Ac/Power"] = (
                    round(grid_power, 2) if grid_power is not None else None
                )  # positive: consumption, negative: feed into grid
                self._dbusservice["/Ac/Current"] = (
                    round(grid_current, 2) if grid_current is not None else None
                )
                self._dbusservice["/Ac/Voltage"] = (
                    round(grid_voltage, 2) if grid_voltage is not None else None
                )
                if grid_forward is not None:
                    self._dbusservice["/Ac/Energy/Forward"] = (
                        round(grid_forward, 2)
                    )
                if grid_reverse is not None:
                    self._dbusservice["/Ac/Energy/Reverse"] = (
                        round(grid_reverse, 2)
                    )

                if grid_L1_power is not None:
                    self._dbusservice["/Ac/L1/Power"] = (
                        round(grid_L1_power, 2) if grid_L1_power is not None else None
                    )
                    self._dbusservice["/Ac/L1/Current"] = (
                        round(grid_L1_current, 2) if grid_L1_current is not None else None
                    )
                    self._dbusservice["/Ac/L1/Voltage"] = (
                        round(grid_L1_voltage, 2) if grid_L1_voltage is not None else None
                    )
                    self._dbusservice["/Ac/L1/Frequency"] = (
                        round(grid_L1_frequency, 2)
                        if grid_L1_frequency is not None
                        else None
                    )
                    self._dbusservice["/Ac/L1/Energy/Forward"] = (
                        round(grid_L1_forward, 2) if grid_L1_forward is not None else None
                    )
                    self._dbusservice["/Ac/L1/Energy/Reverse"] = (
                        round(grid_L1_reverse, 2) if grid_L1_reverse is not None else None
                    )
                else:
                    self._dbusservice["/Ac/L1/Power"] = (
                        round(grid_power, 2) if grid_power is not None else None
                    )
                    self._dbusservice["/Ac/L1/Current"] = (
                        round(grid_current, 2) if grid_current is not None else None
                    )
                    self._dbusservice["/Ac/L1/Voltage"] = (
                        round(grid_voltage, 2) if grid_voltage is not None else None
                    )
                    self._dbusservice["/Ac/L1/Frequency"] = None
                    self._dbusservice["/Ac/L1/Energy/Forward"] = (
                        round(grid_forward, 2) if grid_forward is not None else None
                    )
                    self._dbusservice["/Ac/L1/Energy/Reverse"] = (
                        round(grid_reverse, 2) if grid_reverse is not None else None
                    )

                if grid_L2_power is not None:
                    self._dbusservice["/Ac/L2/Power"] = (
                        round(grid_L2_power, 2) if grid_L2_power is not None else None
                    )
                    self._dbusservice["/Ac/L2/Current"] = (
                        round(grid_L2_current, 2) if grid_L2_current is not None else None
                    )
                    self._dbusservice["/Ac/L2/Voltage"] = (
                        round(grid_L2_voltage, 2) if grid_L2_voltage is not None else None
                    )
                    self._dbusservice["/Ac/L2/Frequency"] = (
                        round(grid_L2_frequency, 2)
                        if grid_L2_frequency is not None
                        else None
                    )
                    self._dbusservice["/Ac/L2/Energy/Forward"] = (
                        round(grid_L2_forward, 2) if grid_L2_forward is not None else None
                    )
                    self._dbusservice["/Ac/L2/Energy/Reverse"] = (
                        round(grid_L2_reverse, 2) if grid_L2_reverse is not None else None
                    )

                if grid_L3_power is not None:
                    self._dbusservice["/Ac/L3/Power"] = (
                        round(grid_L3_power, 2) if grid_L3_power is not None else None
                    )
                    self._dbusservice["/Ac/L3/Current"] = (
                        round(grid_L3_current, 2) if grid_L3_current is not None else None
                    )
                    self._dbusservice["/Ac/L3/Voltage"] = (
                        round(grid_L3_voltage, 2) if grid_L3_voltage is not None else None
                    )
                    self._dbusservice["/Ac/L3/Frequency"] = (
                        round(grid_L3_frequency, 2)
                        if grid_L3_frequency is not None
                        else None
                    )
                    self._dbusservice["/Ac/L3/Energy/Forward"] = (
                        round(grid_L3_forward, 2) if grid_L3_forward is not None else None
                    )
                    self._dbusservice["/Ac/L3/Energy/Reverse"] = (
                        round(grid_L3_reverse, 2) if grid_L3_reverse is not None else None
                    )

                logging.debug(
                    "Grid: {:.1f} W - {:.1f} V - {:.1f} A".format(
                        grid_power, grid_voltage, grid_current
                    )
                )
                if grid_L1_power:
                    logging.debug(
                        "|- L1: {:.1f} W - {:.1f} V - {:.1f} A".format(
                            grid_L1_power, grid_L1_voltage, grid_L1_current
                        )
                    )
                if grid_L2_power:
                    logging.debug(
                        "|- L2: {:.1f} W - {:.1f} V - {:.1f} A".format(
                            grid_L2_power, grid_L2_voltage, grid_L2_current
                        )
                    )
                if grid_L3_power:
                    logging.debug(
                        "|- L3: {:.1f} W - {:.1f} V - {:.1f} A".format(
                            grid_L3_power, grid_L3_voltage, grid_L3_current
                        )
                    )

                last_updated = last_changed

        except KeyError:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            file = exception_traceback.tb_frame.f_code.co_filename
            line = exception_traceback.tb_lineno
            if "/Ac/L" in repr(exception_object):
                logging.error(
                    f"Exception occurred: {repr(exception_object)}. You have to send all phase power values at the same time at startup."
                )
            else:
                logging.error(
                    f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
                )
            logging.error("ERROR:The driver restarts now.")
            sys.exit()

        except Exception:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            file = exception_traceback.tb_frame.f_code.co_filename
            line = exception_traceback.tb_lineno
            logging.error(
                f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
            )
            logging.error("ERROR:The driver restarts now.")
            sys.exit()

        # quit driver if timeout is exceeded
        if timeout != 0 and (now - last_changed) > timeout:
            logging.error(
                "Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time."
                % timeout
            )
            sys.exit()

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


def main():
    _thread.daemon = True  # allow the program to quit

    from dbus.mainloop.glib import (
        DBusGMainLoop,
    )  # pyright: ignore[reportMissingImports]

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    # MQTT setup
    client = mqtt.Client("MqttGrid_" + str(config["MQTT"]["device_instance"]))
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    # check tls and use settings, if provided
    if "tls_enabled" in config["MQTT"] and config["MQTT"]["tls_enabled"] == "1":
        logging.info("MQTT client: TLS is enabled")

        if (
            "tls_path_to_ca" in config["MQTT"]
            and config["MQTT"]["tls_path_to_ca"] != ""
        ):
            logging.info(
                'MQTT client: TLS: custom ca "%s" used'
                % config["MQTT"]["tls_path_to_ca"]
            )
            client.tls_set(config["MQTT"]["tls_path_to_ca"], tls_version=2)
        else:
            client.tls_set(tls_version=2)

        if "tls_insecure" in config["MQTT"] and config["MQTT"]["tls_insecure"] != "":
            logging.info(
                "MQTT client: TLS certificate server hostname verification disabled"
            )
            client.tls_insecure_set(True)

    # check if username and password are set
    if (
        "username" in config["MQTT"]
        and "password" in config["MQTT"]
        and config["MQTT"]["username"] != ""
        and config["MQTT"]["password"] != ""
    ):
        logging.info(
            'MQTT client: Using username "%s" and password to connect'
            % config["MQTT"]["username"]
        )
        client.username_pw_set(
            username=config["MQTT"]["username"], password=config["MQTT"]["password"]
        )

    # connect to broker
    logging.info(
        f"MQTT client: Connecting to broker {config['MQTT']['broker_address']} on port {config['MQTT']['broker_port']}"
    )
    client.connect(
        host=config["MQTT"]["broker_address"], port=int(config["MQTT"]["broker_port"])
    )
    client.loop_start()

    # wait to receive first data, else the JSON is empty and phase setup won't work
    i = 0
    while grid_power == -1:
        if i % 12 != 0 or i == 0:
            logging.info("Waiting 5 seconds for receiving first data...")
        else:
            logging.warning(
                "Waiting since %s seconds for receiving first data..." % str(i * 5)
            )

        # check if timeout was exceeded
        if timeout <= (i * 5):
            logging.error(
                "Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time."
                % timeout
            )
            sys.exit()

        sleep(5)
        i += 1

    # formatting
    def _kwh(p, v):
        return str("%.2f" % v) + "kWh"

    def _a(p, v):
        return str("%.1f" % v) + "A"

    def _w(p, v):
        return str("%i" % v) + "W"

    def _v(p, v):
        return str("%.2f" % v) + "V"

    def _hz(p, v):
        return str("%.4f" % v) + "Hz"

    def _n(p, v):
        return str("%i" % v)

    paths_dbus = {
        "/Ac/Power": {"initial": 0, "textformat": _w},
        "/Ac/Current": {"initial": 0, "textformat": _a},
        "/Ac/Voltage": {"initial": 0, "textformat": _v},
        "/Ac/Energy/Forward": {
            "initial": None,
            "textformat": _kwh,
        },  # energy bought from the grid
        "/Ac/Energy/Reverse": {
            "initial": None,
            "textformat": _kwh,
        },  # energy sold to the grid
        "/Ac/L1/Power": {"initial": 0, "textformat": _w},
        "/Ac/L1/Current": {"initial": 0, "textformat": _a},
        "/Ac/L1/Voltage": {"initial": 0, "textformat": _v},
        "/Ac/L1/Frequency": {"initial": None, "textformat": _hz},
        "/Ac/L1/Energy/Forward": {"initial": None, "textformat": _kwh},
        "/Ac/L1/Energy/Reverse": {"initial": None, "textformat": _kwh},
        "/UpdateIndex": {"initial": 0, "textformat": _n},
    }

    if grid_L2_power is not None:
        paths_dbus.update(
            {
                "/Ac/L2/Power": {"initial": 0, "textformat": _w},
                "/Ac/L2/Current": {"initial": 0, "textformat": _a},
                "/Ac/L2/Voltage": {"initial": 0, "textformat": _v},
                "/Ac/L2/Frequency": {"initial": None, "textformat": _hz},
                "/Ac/L2/Energy/Forward": {"initial": None, "textformat": _kwh},
                "/Ac/L2/Energy/Reverse": {"initial": None, "textformat": _kwh},
            }
        )

    if grid_L3_power is not None:
        paths_dbus.update(
            {
                "/Ac/L3/Power": {"initial": 0, "textformat": _w},
                "/Ac/L3/Current": {"initial": 0, "textformat": _a},
                "/Ac/L3/Voltage": {"initial": 0, "textformat": _v},
                "/Ac/L3/Frequency": {"initial": None, "textformat": _hz},
                "/Ac/L3/Energy/Forward": {"initial": None, "textformat": _kwh},
                "/Ac/L3/Energy/Reverse": {"initial": None, "textformat": _kwh},
            }
        )

    DbusMqttGridService(
        servicename="com.victronenergy.grid.mqtt_grid_"
        + str(config["MQTT"]["device_instance"]),
        deviceinstance=int(config["MQTT"]["device_instance"]),
        customname=config["MQTT"]["device_name"],
        paths=paths_dbus,
    )

    logging.info(
        "Connected to dbus and switching over to GLib.MainLoop() (= event based)"
    )
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
