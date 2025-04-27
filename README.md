# dbus-mqtt-grid - Emulates a physical Grid/Genset/AC Load Meter from MQTT data

<small>GitHub repository: [mr-manuel/venus-os_dbus-mqtt-grid](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid)</small>

## Index

1. [Disclaimer](#disclaimer)
1. [Supporting/Sponsoring this project](#supportingsponsoring-this-project)
1. [Purpose](#purpose)
1. [Config](#config)
1. [JSON structure](#json-structure)
    - [Generic device](#generic-device)
    - [ESPHome](#esphome)
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
        "power": 0.0                 <-- watts
    }
}
```
</details>

<details><summary>Minimum required with L1</summary>

```json
{
    "grid": {
        "power": 0.0,                <-- watts
        "L1": {
            "power": 0.0             <-- watts
        }
    }
}
```
</details>

<details><summary>Minimum required with L1, L2</summary>

```json
{
    "grid": {
        "power": 0.0,                <-- watts
        "L1": {
            "power": 0.0             <-- watts
        },
        "L2": {
            "power": 0.0             <-- watts
        }
    }
}
```
</details>

<details><summary>Minimum required with L1, L2, L3</summary>

```json
{
    "grid": {
        "power": 0.0,                <-- watts
        "L1": {
            "power": 0.0             <-- watts
        },
        "L2": {
            "power": 0.0             <-- watts
        },
        "L3": {
            "power": 0.0             <-- watts
        }
    }
}
```
</details>

<details><summary>Full</summary>

```json
{
    "grid": {
        "power": 0.0,                <-- watts
        "voltage": 0.0,              <-- volts
        "current": 0.0,              <-- amps
        "energy_forward": 0.0,       <-- imported/bought energy (lifetime), positive value in kWh
        "energy_reverse": 0.0,       <-- exported/sold energy (lifetime), positive value in kWh
        "L1": {
            "power": 0.0,            <-- watts
            "voltage": 0.0,          <-- volts
            "current": 0.0,          <-- amps
            "frequency": 0.0000,     <-- Hz
            "power_factor": 0.0,
            "energy_forward": 0.0,   <-- imported/bought energy (lifetime), positive value in kWh
            "energy_reverse": 0.0    <-- exported/sold energy (lifetime), positive value in kWh
        },
        "L2": {
            "power": 0.0,            <-- watts
            "voltage": 0.0,          <-- volts
            "current": 0.0,          <-- amps
            "frequency": 0.0000,     <-- Hz
            "power_factor": 0.0,
            "energy_forward": 0.0,   <-- imported/bought energy (lifetime), positive value in kWh
            "energy_reverse": 0.0    <-- exported/sold energy (lifetime), positive value in kWh
        },
        "L3": {
            "power": 0.0,            <-- watts
            "voltage": 0.0,          <-- volts
            "current": 0.0,          <-- amps
            "frequency": 0.0000,     <-- Hz
            "power_factor": 0.0,
            "energy_forward": 0.0,   <-- imported/bought energy (lifetime), positive value in kWh
            "energy_reverse": 0.0    <-- exported/sold energy (lifetime), positive value in kWh
        }
    }
}
```
</details>

Alternatively you can use the JSON structure produced by Tasmota-EnergyMeter (see section [Tasmota](#Tasmota))


### ESPHome

With this ESPHome-code, you can directly send the grid-usage to the GX device, to configure zero feed-in, without the need to modify the payload.

See also [esphome configuration to directly send from MBus-Grid-Smartmeter to Victron](https://github.com/mr-manuel/venus-os_dbus-mqtt-grid/issues/41).

<details><summary>ESPHome config</summary>

```yml
esphome:
  name: "smartmeter"
  area: Keller

esp8266:
  board: nodemcuv2
logger:        #level: DEBUG #INFO   #  level: DEBUG #WARN #DEBUG NONE
  level: WARN
  baud_rate: 0
  esp8266_store_log_strings_in_flash: false


wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  reboot_timeout: 5min
  fast_connect: true

external_components:
  - source: github://pr#8009   # see https://github.com/esphome/esphome/pull/8009
    components: [ dlms_meter ]

web_server:
  port: 80
  version: 2

mqtt:
  broker: x.local #ip to venusos
  id: mqtt_broker
  discovery: false
  enable_on_boot: false


# Enable Home Assistant API
api:
  encryption:
    key: ""
  reboot_timeout: 5 min

ota:
  - platform: esphome
    password: ""


uart:
  tx_pin: RX
  rx_pin: TX
  baud_rate: 2400
  rx_buffer_size: 1024 # Needed to receive the large packets send by the smart meter
  id: mbus

dlms_meter:
  decryption_key: "kexFromEVN"


binary_sensor:
  - platform: template
    name: "L1 Overcurrent Alarm"
    lambda: |-
      if (id(meter01_current_l1).state > 25) {
        return true;
      } else {
        return false;
      }
  - platform: template
    name: "L2 Overcurrent Alarm"
    lambda: |-
      if (id(meter01_current_l2).state > 25) {
        return true;
      } else {
        return false;
      }
  - platform: template
    name: "L3 Overcurrent Alarm"
    lambda: |-
      if (id(meter01_current_l3).state > 25) {
        return true;
      } else {
        return false;
      }

sensor:

  - platform: dlms_meter
    voltage_l1:
      name: "smartmeter_voltage_l1"
      id: meter01_voltage_l1
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    voltage_l2:
      name: "smartmeter_voltage_l2"
      id: meter01_voltage_l2
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    voltage_l3:
      name: "smartmeter_voltage_l3"
      id: meter01_voltage_l3
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    current_l1:
      name: "smartmeter_current_l1"
      id: meter01_current_l1
      device_class: "current"
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    current_l2:
      name: "smartmeter_current_l2"
      id: meter01_current_l2
      device_class: "current"
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    current_l3:
      name: "smartmeter_current_l3"
      id: meter01_current_l3
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0

    active_power_plus:
      name: "smartmeter_active_power_plus"
      id: active_power_plus
      # filters:
      # - filter_out:
      #     - 0
      on_value:
        then:
          - lambda: |-
              id(smartmeter_active_power).publish_state(id(active_power_plus).state-0);

    active_power_minus:
      name: "smartmeter_active_power_minus"
      id: active_power_minus
      on_value:
        then:
          - lambda: |-
              if (id(active_power_minus).state != 0) {
                id(smartmeter_active_power).publish_state(0 - id(active_power_minus).state);
              }
    active_energy_plus:
      name: "smartmeter_active_energy_plus"
      id: active_energy_plus
    active_energy_minus:
      name: "smartmeter_active_energy_minus"
      id: active_energy_minus
    reactive_energy_plus:
      name: "smartmeter_reactive_energy_plus"
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0
    reactive_energy_minus:
      name: "smartmeter_reactive_energy_minus"
      disabled_by_default: true
      entity_category: diagnostic
      filters:
        - or:
          - throttle: 10s
          - delta: 2.0

    # # EVN
    # power_factor:
    #   name: "Power Factor"

  - platform: template
    id: smartmeter_active_power
    name: meter01_active_power
    unit_of_measurement: W
    accuracy_decimals: 0
    device_class: "power"
    state_class: "measurement"
    update_interval: never
    on_value:
          - if:
              condition:
                switch.is_on: switch_on_off
              then:
                - mqtt.publish_json:
                    topic: "external/nodered/shrdzm-to-victron/grid"
                    payload: |-
                      root["grid"]["power"]          = (float)id(smartmeter_active_power).state;
                      root["grid"]["voltage"]        = (float)id(meter01_voltage_l1).state;
                      root["grid"]["energy_forward"] = (float)id(smartmeter_zaehlerstand_bezug).state*0.001;
                      root["grid"]["energy_reverse"] = (float)id(smartmeter_zaehlerstand_einspeisung).state*0.001;
                      root["grid"]["L1"]["voltage"] = (float)id(meter01_voltage_l1).state;
                      root["grid"]["L2"]["voltage"] = (float)id(meter01_voltage_l2).state;
                      root["grid"]["L3"]["voltage"] = (float)id(meter01_voltage_l3).state;
                      root["grid"]["L1"]["power"]   = (float)id(meter01_voltage_l1).state*id(meter01_current_l1).state;
                      root["grid"]["L2"]["power"]   = (float)id(meter01_voltage_l2).state*id(meter01_current_l2).state;
                      root["grid"]["L3"]["power"]   = (float)id(meter01_voltage_l3).state*id(meter01_current_l3).state;
                      root["grid"]["L1"]["current"] = (float)id(meter01_current_l1).state;
                      root["grid"]["L2"]["current"] = (float)id(meter01_current_l2).state;
                      root["grid"]["L3"]["current"] = (float)id(meter01_current_l3).state;


  - platform: template
    id: smartmeter_zaehlerstand_bezug
    name: smartmeter_zaehlerstand_bezug
    unit_of_measurement: kWh
    accuracy_decimals: 0
    device_class: "energy"
    state_class: "total_increasing"
    update_interval: 120s
    lambda: |-
         return id(active_energy_plus).state;
    filters:
     - multiply: 0.001

  - platform: template
    id: smartmeter_zaehlerstand_einspeisung
    name: smartmeter_zaehlerstand_einspeisung
    unit_of_measurement: kWh
    accuracy_decimals: 0
    device_class: "energy"
    state_class: "total_increasing"
    update_interval: 120s
    lambda: |-
         return id(active_energy_minus).state;
    filters:
     - multiply: 0.001


switch:
  - platform: template
    name: Nutze Smartmeter direkt in Victron
    id: switch_on_off
    restore_mode: RESTORE_DEFAULT_OFF
    # lambda: |-
    #   if (id(switch_on_off).state) {
    #     return true;
    #   } else {
    #     return false;
    #   }
    optimistic: true
    turn_on_action:
      - mqtt.enable:
    #   - delay: 500ms
    #   - switch.turn_on: switch_on_off
    turn_off_action:
      - mqtt.publish_json:
          topic: "external/nodered/shrdzm-to-victron/grid"
          payload: |-
            root["grid"] = "";
      - mqtt.disable:

text_sensor:
  - platform: dlms_meter
    timestamp:
      name: "smartmeter_timestamp"
      disabled_by_default: true
    # # EVN
    # meternumber:
    #   name: "meterNumber"
```
</details>


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
