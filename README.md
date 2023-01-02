# dbus-mqtt-grid - Emulates a physical Grid Meter from MQTT data

<small>GitHub repository: [mr-manuel/venus-os_dbus-mqtt-grid](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid)</small>

### Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.


### Purpose

The script emulates a physical Grid Meter in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service `com.victronenergy.grid.mqtt_grid` with the VRM instance `31`.


### Config

Copy or rename the `config.sample.ini` to `config.ini` in the `dbus-mqtt-grid` folder and change it as you need it.


### JSON structure

<details><summary>Minimum required</summary>

```json
{
    "grid": {
        "power": 0.0
    }
}
```
</details>

<details><summary>Minimum required with L1</summary>

```json
{
    "grid": {
        "power": 0.0,
        "L1": {
            "power": 0.0
        }
    }
}
```
</details>

<details><summary>Minimum required with L1, L2</summary>

```json
{
    "grid": {
        "power": 0.0,
        "L1": {
            "power": 0.0
        },
        "L2": {
            "power": 0.0
        }
    }
}
```
</details>

<details><summary>Minimum required with L1, L2, L3</summary>

```json
{
    "grid": {
        "power": 0.0,
        "L1": {
            "power": 0.0
        },
        "L2": {
            "power": 0.0
        },
        "L3": {
            "power": 0.0
        }
    }
}
```
</details>

<details><summary>Full</summary>

```json
{
    "grid": {
        "power": 0.0,
        "voltage": 0.0,
        "current": 0.0,
        "energy_forward": 0.0,
        "energy_reverse": 0.0,
        "L1": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        },
        "L2": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        },
        "L3": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        }
    }
}
```
</details>


### Install

1. Copy the `dbus-mqtt-grid` folder to `/data/etc` on your Venus OS device

2. Run `bash /data/etc/dbus-mqtt-grid/install.sh` as root

   The daemon-tools should start this service automatically within seconds.

### Uninstall

Run `/data/etc/dbus-mqtt-grid/uninstall.sh`

### Restart

Run `/data/etc/dbus-mqtt-grid/restart.sh`

### Debugging

The logs can be checked with `tail -n 100 -f /data/log/dbus-mqtt-grid/current | tai64nlocal`

The service status can be checked with svstat `svstat /service/dbus-mqtt-grid`

This will output somethink like `/service/dbus-mqtt-grid: up (pid 5845) 185 seconds`

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in `/data/etc/dbus-mqtt-grid/dbus-mqtt-grid.py` by changing `level=logging.WARNING` to `level=logging.INFO` or `level=logging.DEBUG`

If the script stops with the message `dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid.mqtt_grid"` it means that the service is still running or another service is using that bus name.

### Compatibility

It was tested on Venus OS Large `v2.92` on the following devices:

* RaspberryPi 4b
* MultiPlus II (GX Version)

### Screenshots

<details><summary>Power and/or L1</summary>

![Grid power L1 - pages](/screenshots/grid_power_L1_pages.png)
![Grid power L1 - device list](/screenshots/grid_power_L1_device-list.png)
![Grid power L1 - device list - mqtt grid 1](/screenshots/grid_power_L1_device-list_mqtt-grid-1.png)
![Grid power L1 - device list - mqtt grid 2](/screenshots/grid_power_L1_device-list_mqtt-grid-2.png)

</details>

<details><summary>Power, L1 and L2</summary>

![Grid power L1, L2 - pages](/screenshots/grid_power_L2_L1_pages.png)
![Grid power L1, L2 - device list](/screenshots/grid_power_L2_L1_device-list.png)
![Grid power L1, L2 - device list - mqtt grid 1](/screenshots/grid_power_L2_L1_device-list_mqtt-grid-1.png)
![Grid power L1, L2 - device list - mqtt grid 2](/screenshots/grid_power_L2_L1_device-list_mqtt-grid-2.png)

</details>

<details><summary>Power, L1, L2 and L3</summary>

![Grid power L1, L2, L3 - pages](/screenshots/grid_power_L3_L2_L1_pages.png)
![Grid power L1, L2, L3 - device list](/screenshots/grid_power_L3_L2_L1_device-list.png)
![Grid power L1, L2, L3 - device list - mqtt grid 1](/screenshots/grid_power_L3_L2_L1_device-list_mqtt-grid-1.png)
![Grid power L1, L2, L3 - device list - mqtt grid 2](/screenshots/grid_power_L3_L2_L1_device-list_mqtt-grid-2.png)

</details>
