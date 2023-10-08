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
BROKER = os.environ.get('MQTT_BROKER', "localhost")
PORT = 1883
mqtt_client_instance = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error(f"Failed to connect to MQTT Broker with return code {rc}")

def connect_to_mqtt():
    global mqtt_client_instance
    mqtt_client_instance = mqtt_client.Client("XiaomiPublisher")
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
    XIAOMI_TOKEN = device_config['token']
    ROOM_NAME = device_config['room']

    # Connect to Xiaomi device
    try:
        air_purifier = miio.AirPurifier(XIAOMI_IP, XIAOMI_TOKEN)
        logger.info(f"Connected to Xiaomi device at {XIAOMI_IP}")

        while True:
            # Fetch data
            status = air_purifier.status()
            data = {
                "temperature": status.temperature,
                "humidity": status.humidity,
                "aqi": status.aqi,
            }

            # Publish data to MQTT
            for metric, value in data.items():
                publish_to_mqtt(ROOM_NAME, "airpurifier", metric, str(value))

            # Sleep for a specified interval (e.g., 60 seconds) before fetching data again
            time.sleep(60)
    except Exception as e:
        logger.error(f"Error fetching data from Xiaomi device: {e}")

def main():
    connect_to_mqtt()
    threads = []
    for device_config in config['devices']:
        t = threading.Thread(target=fetch_data_airpurifier, args=(device_config,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
