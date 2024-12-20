# dbus-mqtt-grid - Emulates a physical Grid/Genset/AC Load Meter from MQTT data

<small>GitHub repository: [mr-manuel/venus-os_dbus-mqtt-grid](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid)</small>

## Index

1. [Disclaimer](#disclaimer)
1. [Supporting/Sponsoring this project](#supportingsponsoring-this-project)
1. [Purpose](#purpose)
1. [Config](#config)
1. [JSON structure](#json-structure)
    - [Generic device](#generic-device)
    - [Home Assistant](#home-assistant)
    - [Shelly Gen2+](#shelly-gen-2)
    - [Tasmota](#tasmota)
1. [Install / Update](#install--update)
1. [Uninstall](#uninstall)
1. [Restart](#restart)
1. [Debugging](#debugging)
1. [Compatibility](#compatibility)
1. [Screenshots](#screenshots)


## Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.


## Supporting/Sponsoring this project

You like the project and you want to support me?

[<img src="https://github.md0.eu/uploads/donate-button.svg" height="50">](https://www.paypal.com/donate/?hosted_button_id=3NEVZBDM5KABW)


## Purpose

The script emulates a physical Grid/Genset/AC Load Meter in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service `com.victronenergy.grid.mqtt_grid`, `com.victronenergy.genset.mqtt_genset` or `com.victronenergy.acload.mqtt_acload` with the VRM instance `31`.

It also supports the Tasmota-SmartMeter format.


## Config

Copy or rename the `config.sample.ini` to `config.ini` in the `dbus-mqtt-grid` folder and change it as you need it.

## JSON structure

### Generic device

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
            "power_factor": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0
        },
        "L2": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "frequency": 0.0000,
            "power_factor": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0
        },
        "L3": {
            "power": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "frequency": 0.0000,
            "power_factor": 0.0,
            "energy_forward": 0.0,
            "energy_reverse": 0.0
        }
    }
}
```
</details>

Alternatively you can use the JSON structure produced by Tasmota-EnergyMeter (see section [Tasmota](#Tasmota))


### Home Assistant

This is only a simple example that can be reduced expanded to match the minimum or full requirements shown above.

```yml
alias: mqtt publish sensor grid power
description: ""
trigger:
  - platform: state
    entity_id: sensor.YOUR_GRID_POWER_ENTITY
condition: []
action:
  - service: mqtt.publish
    data_template:
      payload: |
        {
          "grid": {
            "power": {{ (states('sensor.YOUR_GRID_POWER_ENTITY') | float(0)) }},
            "L1": {
                "power": {{ (states('sensor.YOUR_GRID_L1_POWER_ENTITY') | float(0)) }}
            },
            "L2": {
                "power": {{ (states('sensor.YOUR_GRID_L2_POWER_ENTITY') | float(0)) }}
            },
            "L3": {
                "power": {{ (states('sensor.YOUR_GRID_L3_POWER_ENTITY') | float(0)) }}
            }
          }
        }
      topic: homeassistant/energy/grid
```

In the `config.ini` of `dbus-mqtt-grid` set the MQTT broker to the Home Assistant hostname/IP and the topic to the same as in your Home Assistant config (like above).

See also this [comment](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid/issues/10#issuecomment-1826763558).


### Shelly (Gen 2+)

```json
 {
    "apower": 0.0,
    "voltage": 0.0,
    "freq": 0,
    "current": 0.000,
    "pf": 0,
    "aenergy": {
        "total": 0.000
    },
    "ret_aenergy": {
        "total": 0.000
    }
}
```

Ensure your Shelly device uses the same topic as configured in `config.ini`. Enable MQTT on your Shelly device and set the host, port, and topic correctly.


### Tasmota

Setting up tasmota as Tasmota-SmartMeter is not part of this documentation. See https://tasmota.github.io/docs/Smart-Meter-Interface/#meter-metrics
or https://homeitems.de/smartmeter-mit-tasmota-auslesen/# (German) for detailed information on how to set up Tasmota-EnergyMeter.

In order to get dbus-mqtt-grid working with the Tasmota-SmartMeter, the script on tasmota has to be configured in a specific way.

Depending on your individual Smart Meter, the first part of the script looks like this:
```
>D
>B
=>sensor53 r
>M 1
+1,3,s,0,9600,grid
```
Important for dbus-mqtt-grid is, that the `<jsonPrefix>` of the [meter definition](https://tasmota.github.io/docs/Smart-Meter-Interface/#meter-definition) is called `grid`.

Following is an example of the [meter metrics](https://tasmota.github.io/docs/Smart-Meter-Interface/#meter-metrics):
```
1,77070100100700ff@1,Current Consumption,W,power,16
1,77070100240700ff@1,Current Consumption P1,W,power_L1,16
1,77070100380700ff@1,Current Consumption P2,W,power_L2,16
1,770701004c0700ff@1,Current Consumption P3,W,power_L3,16
```

Important are the 2 last parts of each line.
- The last number (`16`) lets tasmota transmit this reading via mqtt immediately. This is necessary to get updates of the current power consumption as fast as possible.
- The second last entry needs to be named exactly like this: L1: `power_L1`, L2: `power_L2`, L3: `power_L3`, total grid power: `power`. These are the keywords that are expected by dbus-mqtt-grid.

The MQTT messages sent from tasmota should then look like this:
```
21:57:13.103 RSL: SENSOR = {"Time":"2023-11-22T21:57:13","grid":{"power":413}}
21:57:13.124 RSL: SENSOR = {"Time":"2023-11-22T21:57:13","grid":{"power_L1":94}}
```

Sending the total energy (kWh consumed and delivered) is also possible.
Since those values are not changing much, it is sufficient to transmit them only every [TelePeriod](https://tasmota.github.io/docs/Commands/#teleperiod) seconds.
<br>Again, the important parts are the last two of each line, where `3` in this case means that you will get a precision of 3 digits (see  [meter metrics/precision](https://tasmota.github.io/docs/Smart-Meter-Interface/#meter-metrics)).
```
1,77070100010800ff@1000,Total Consumed,KWh,energy_forward,3
1,77070100020800ff@1000,Total Delivered,KWh,energy_reverse,3
```

It is possible to directly use the ip address of your venusOS installation as MQTT host in tasmota.
For this to work, set the MQTT part of `config.ini` to `localhost` and enable the MQTT server on your venusOS: https://github.com/victronenergy/dbus-mqtt#set-up


The topic in tasmota has to fit together with the config.ini. For example:
```
Tasmota Topic: SML
Tasmota Full Topic: %topic%/
config.ini topic = SML/SENSOR
```

Additional information can be found in this [issue](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid/issues/13#issue-2045377392).


## Install / Update

1. Login to your Venus OS device via SSH. See [Venus OS:Root Access](https://www.victronenergy.com/live/ccgx:root_access#root_access) for more details.

2. Execute this commands to download and copy the files:

    ```bash
    wget -O /tmp/download_dbus-mqtt-grid.sh https://raw.githubusercontent.com/mr-manuel/venus-os_dbus-mqtt-grid/master/download.sh

    bash /tmp/download_dbus-mqtt-grid.sh
    ```

3. Select the version you want to install.

4. Press enter for a single instance. For multiple instances, enter a number and press enter.

    Example:

    - Pressing enter or entering `1` will install the driver to `/data/etc/dbus-mqtt-grid`.
    - Entering `2` will install the driver to `/data/etc/dbus-mqtt-grid-2`.

### Extra steps for your first installation

5. Edit the config file to fit your needs. The correct command for your installation is shown after the installation.

    - If you pressed enter or entered `1` during installation:
    ```bash
    nano /data/etc/dbus-mqtt-grid/config.ini
    ```

    - If you entered `2` during installation:
    ```bash
    nano /data/etc/dbus-mqtt-grid-2/config.ini
    ```

6. Install the driver as a service. The correct command for your installation is shown after the installation.

    - If you pressed enter or entered `1` during installation:
    ```bash
    bash /data/etc/dbus-mqtt-grid/install.sh
    ```

    - If you entered `2` during installation:
    ```bash
    bash /data/etc/dbus-mqtt-grid-2/install.sh
    ```

    The daemon-tools should start this service automatically within seconds.

## Uninstall

⚠️ If you have multiple instances, ensure you choose the correct one. For example:

- To uninstall the default instance:
    ```bash
    bash /data/etc/dbus-mqtt-grid/uninstall.sh
    ```

- To uninstall the second instance:
    ```bash
    bash /data/etc/dbus-mqtt-grid-2/uninstall.sh
    ```

## Restart

⚠️ If you have multiple instances, ensure you choose the correct one. For example:

- To restart the default instance:
    ```bash
    bash /data/etc/dbus-mqtt-grid/restart.sh
    ```

- To restart the second instance:
    ```bash
    bash /data/etc/dbus-mqtt-grid-2/restart.sh
    ```

## Debugging

⚠️ If you have multiple instances, ensure you choose the correct one.

- To check the logs of the default instance:
    ```bash
    tail -n 100 -F /data/log/dbus-mqtt-grid/current | tai64nlocal
    ```

- To check the logs of the second instance:
    ```bash
    tail -n 100 -F /data/log/dbus-mqtt-grid-2/current | tai64nlocal
    ```

The service status can be checked with svstat `svstat /service/dbus-mqtt-grid`

This will output somethink like `/service/dbus-mqtt-grid: up (pid 5845) 185 seconds`

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in `/data/etc/dbus-mqtt-grid/dbus-mqtt-grid.py` by changing `level=logging.WARNING` to `level=logging.INFO` or `level=logging.DEBUG`

If the script stops with the message `dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid.mqtt_grid"` it means that the service is still running or another service is using that bus name.

## Compatibility

This software supports the latest three stable versions of Venus OS. It may also work on older versions, but this is not guaranteed.

## Screenshots

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
