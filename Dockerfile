FROM python:3-slim

# Set working directory
WORKDIR /app

# Install necessary build tools and libraries
RUN apt-get update \
      && apt-get install -y  build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        cargo \
      && apt-get clean

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install required Python packages from requirements.txt
RUN pip install -r requirements.txt

# Copy the script to the container
COPY mi_mqtt.py /app/

# Command to run the script
CMD ["python", "/app/mi_mqtt.py"]
