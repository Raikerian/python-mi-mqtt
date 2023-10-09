# python-mi-mqtt

A service to parse your Xiaomi device metrics and publish them on mqtt broker

One of the personal use cases is to publish temperature and humidity to mqtt so it can be connected to the airconditioner in HomeBridge using [homebridge-broadlink-rm](https://github.com/lprhodes/homebridge-broadlink-rm)

## Quick start

1. Make sure you have docker CLI and Make installed

1. (optional) If you don't have MQTT broker already execute `make run-broker`, this will start MQTT broker instance on your localhost and expose it to port 1883

2. Populate `config.yaml` with your MQTT broker info, device IP address, device token and device type. If you are not sure how to get device token, see this extensive guide [here](https://github.com/merdok/homebridge-miot/blob/main/obtain_token.md)

3. Execute `make build` to build the Docker image locally

4. Execute `make run` to start the application

## Adding more devices

Currently only mi airpurifier is supported, however the code is ready for expansion and adding new devices with any metrics you want should be quite easy. Check DEVICE_TYPE_MAP map in the main python file and add corresponding function returning metrics you need.

## Helpful commands

- `make logs` - to get applicaiton logs

- `make logs-broker` - to get MQTT broker logs if you decided to run it locally

- `make stop` - to stop and cleanup application container

- `make stop-broker` - to stop and cleanup broker container

- `make clean` - to cleanup built docker image
