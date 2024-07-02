# Changelog

## v0.1.5
* Added: Error handling
* Changed: Fixed problems when timeout was set to `0`.
* Changed: Handling when voltage=0 is provided and no current

## v0.1.4
* Added: Tasmota support with https://github.com/mr-manuel/venus-os_dbus-mqtt-grid/pull/8 by @randomname32
* Added: Timeout on driver startup. Prevents problems, if the MQTT broker is not reachable on driver startup

## v0.1.3
* Changed: Fix crash when rounding none value
* Changed: Fixed a typo

## v0.1.2
* Added: Frequency
* Added: Show to which broker and port the connection was made when logging is set to INFO
* Added: Try to reconnect every 15 seconds to MQTT broker, if connection is closed abnormally
* Changed: Improved error handling and output

## v0.1.1
* Added: Timeout in order to disconnect the grid meter, if no new MQTT message is received after x seconds (configurable in `config.ini`)

## v0.1.0
* Added: Device name can be changed in the `config.ini`
* Added: Device instance can be changed in the `config.ini`
* Added: How to create multiple instances in `README.md`
* Changed: Topic variable name in `config.ini`

## v0.0.2
* Added: Set logging level in `config.default.ini`
* Changed: Logging levels of different messages for clearer output
* Changed: Optimized log output for faster troubleshooting

## v0.0.1
Initial release
