import os
import time
import yaml
import miio
import threading
import logging
from paho.mqtt import client as mqtt_client

# Setup logging with time
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load configuration from YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# MQTT details
BROKER = config['mqtt']['broker']
PORT = config['mqtt']['port']
CLIENT_NAME = config['mqtt']['client_name']
POLL_INTERVAL = config.get('poll_interval', 60)  # Use a default value if not provided
mqtt_client_instance = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error(f"Failed to connect to MQTT Broker with return code {rc}")

def connect_to_mqtt():
    global mqtt_client_instance
    mqtt_client_instance = mqtt_client.Client(CLIENT_NAME)
    mqtt_client_instance.on_connect = on_connect
    mqtt_client_instance.connect(BROKER, PORT)
    mqtt_client_instance.loop_start()

def publish_to_mqtt(room, device, metric, value):
    try:
        topic = f"/{room}/{device}/{metric}"
        mqtt_client_instance.publish(topic, value)
        logger.info(f"Published {metric} = {value} to {topic}")
    except Exception as e:
        logger.error(f"Error publishing to MQTT: {e}")

def fetch_data_airpurifier(device_config):
    XIAOMI_IP = device_config['ip']
    air_purifier = miio.AirPurifier(XIAOMI_IP, device_config['token'])
    logger.info(f"Connecting to Xiaomi Air Purifier at {XIAOMI_IP}")
    status = air_purifier.status()
    return {
        "temperature": status.temperature,
        "humidity": status.humidity,
        "aqi": status.aqi
    }

DEVICE_TYPE_MAP = {
    "airpurifier": fetch_data_airpurifier,
    # Add more device types to the map as needed
}

def fetch_and_publish(device_config):
    device_type = device_config['type']
    fetch_func = DEVICE_TYPE_MAP.get(device_type)
    if not fetch_func:
        logger.error(f"Unsupported device type: {device_type}")
        return

    while True:
        try:
            data = fetch_func(device_config)
            room_name = device_config['room']
            for metric, value in data.items():
                publish_to_mqtt(room_name, device_type, metric, str(value))
        except Exception as e:
            logger.error(f"Error fetching data from {device_type} device: {e}")
        # Sleep for the specified interval before fetching data again
        time.sleep(POLL_INTERVAL)

def main():
    connect_to_mqtt()
    threads = []
    for device_config in config['devices']:
        t = threading.Thread(target=fetch_and_publish, args=(device_config,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
