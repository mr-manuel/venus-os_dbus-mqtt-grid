# dbus-mqtt-grid - Emulates a physical Grid Meter from MQTT data

<small>GitHub repository: [mr-manuel/venus-os_dbus-mqtt-grid](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid)</small>

### Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.


## Supporting/Sponsoring this project

You like the project and you want to support me?

[<img src="https://github.md0.eu/uploads/donate-button.svg" height="50">](https://www.paypal.com/donate/?hosted_button_id=3NEVZBDM5KABW)


### Purpose

The script emulates a physical Grid Meter in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service `com.victronenergy.grid.mqtt_grid` with the VRM instance `31`.

It also supports the Tasmota-SmartMeter format.


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
            "frequency": 0.0000,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        },
        "L2": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "frequency": 0.0000,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        },
        "L3": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "frequency": 0.0000,
            "energy_forward": 0.0,
            "energy_reverse": 0.0,
        }
    }
}
```
</details>

Alternatively you can use the json structure produced by Tasmota-EnergyMeter (see section [tasmota](#Tasmota))

#### Tasmota

Setting up tasmota as Tasmota-SmartMeter is not part of this documentation. See https://tasmota.github.io/docs/Smart-Meter-Interface/#meter-metrics 
or https://homeitems.de/smartmeter-mit-tasmota-auslesen/# (German) for detailed information on how to set up Tasmota-EnergyMeter.

In order to get dbus-mqtt-grid working with the Tasmota-SmartMeter, the script on tasmota has to be configured in a specific way, e.g.:

```
1,77070100100700ff@1,Current Consumption,W,power,16
1,77070100240700ff@1,Current Consumption P1,W,power_L1,16
1,77070100380700ff@1,Current Consumption P2,W,power_L2,16
1,770701004c0700ff@1,Current Consumption P3,W,power_L3,16
```

Important are the 2 last parts of each line.
- The last number (`16`) lets tasmota transmit this reading via mqtt immediately.
- The second last entry needs to be named exactly like this: L1: `power_L1`, L2: `power_L2`, L3: `power_L3`, total grid power: `power`

The MQTT messages sent from tasmota should then look like this:
```
21:57:13.103 RSL: SENSOR = {"Time":"2023-11-22T21:57:13","grid":{"power":413}}
21:57:13.124 RSL: SENSOR = {"Time":"2023-11-22T21:57:13","grid":{"power_L1":94}}
```

It is possible to directly use the ip address of your venusOS installation as MQTT host in tasmota.
For this to work, set the MQTT part of `config.ini` to `localhost` and enable the MQTT server on your venusOS: https://github.com/victronenergy/dbus-mqtt#set-up


### Install

1. Copy the `dbus-mqtt-grid` folder to `/data/etc` on your Venus OS device

2. Run `bash /data/etc/dbus-mqtt-grid/install.sh` as root

   The daemon-tools should start this service automatically within seconds.

### Uninstall

Run `/data/etc/dbus-mqtt-grid/uninstall.sh`

### Restart

Run `/data/etc/dbus-mqtt-grid/restart.sh`

### Debugging

The logs can be checked with `tail -n 100 -F /data/log/dbus-mqtt-grid/current | tai64nlocal`

The service status can be checked with svstat `svstat /service/dbus-mqtt-grid`

This will output somethink like `/service/dbus-mqtt-grid: up (pid 5845) 185 seconds`

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in `/data/etc/dbus-mqtt-grid/dbus-mqtt-grid.py` by changing `level=logging.WARNING` to `level=logging.INFO` or `level=logging.DEBUG`

If the script stops with the message `dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid.mqtt_grid"` it means that the service is still running or another service is using that bus name.

### Multiple instances

It's possible to have multiple instances, but it's not automated. Follow these steps to achieve this:

1. Save the new name to a variable `driverclone=dbus-mqtt-grid-2`

2. Copy current folder `cp -r /data/etc/dbus-mqtt-grid/ /data/etc/$driverclone/`

3. Rename the main script `mv /data/etc/$driverclone/dbus-mqtt-grid.py /data/etc/$driverclone/$driverclone.py`

4. Fix the script references for service and log
    ```
    sed -i 's:dbus-mqtt-grid:'$driverclone':g' /data/etc/$driverclone/service/run
    sed -i 's:dbus-mqtt-grid:'$driverclone':g' /data/etc/$driverclone/service/log/run
    ```

5. Change the `device_name` and increase the `device_instance` in the `config.ini`

Now you can install and run the cloned driver. Should you need another instance just increase the number in step 1 and repeat all steps.

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
