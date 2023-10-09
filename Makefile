# Docker image names
IMAGE_NAME := mi_mqtt_publisher
MQTT_BROKER_IMAGE := eclipse-mosquitto

# Path to the config.yaml on the host system
CONFIG_PATH ?= ./config.yaml

# Check if mosquitto.conf exists, if not, create it
MOSQUITTO_CONF := $(CURDIR)/mosquitto.conf
$(MOSQUITTO_CONF):
	@echo "Creating mosquitto.conf..."
	@echo "listener 1883" > $(MOSQUITTO_CONF)
	@echo "allow_anonymous true" >> $(MOSQUITTO_CONF)
	@echo "persistence true" >> $(MOSQUITTO_CONF)
	@echo "persistence_location /mosquitto/data/" >> $(MOSQUITTO_CONF)

.PHONY: build
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) .

.PHONY: run
run:
	@echo "Running Docker container..."
	docker run -d \
	--add-host host.docker.internal:host-gateway \
	--name $(IMAGE_NAME) \
	--restart unless-stopped \
	-v $(CONFIG_PATH):/app/config.yaml \
	$(IMAGE_NAME)

.PHONY: logs
logs:
	@echo "Fetching logs from Docker container..."
	docker logs -f $(IMAGE_NAME)

.PHONY: stop
stop:
	@echo "Stopping Docker container..."
	docker stop $(IMAGE_NAME)
	docker rm $(IMAGE_NAME)

.PHONY: clean
clean:
	@echo "Removing Docker image..."
	docker rmi $(IMAGE_NAME)

.PHONY: run-broker
run-broker: $(MOSQUITTO_CONF)
	@echo "Running Mosquitto MQTT broker container..."
	mkdir -p $(CURDIR)/data
	docker run -d \
	--name $(MQTT_BROKER_IMAGE) \
	-v $(CURDIR)/data:/mosquitto/data \
	-v $(CURDIR)/mosquitto.conf:/mosquitto/config/mosquitto.conf \
	--network="host" \
	$(MQTT_BROKER_IMAGE)

.PHONY: stop-broker
stop-broker:
	@echo "Stopping Mosquitto MQTT broker container..."
	docker stop $(MQTT_BROKER_IMAGE)
	docker rm $(MQTT_BROKER_IMAGE)

.PHONY: logs-broker
logs-broker:
	@echo "Fetching logs from Docker container..."
	docker logs -f $(MQTT_BROKER_IMAGE)
