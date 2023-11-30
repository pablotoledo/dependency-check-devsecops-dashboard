# https://github.com/jeremylong/DependencyCheck
#docker build --build-arg NVD_API_KEY=$NVD_API_KEY -t dpcheck .
FROM artifactory.vodafone.com/docker-vfes-digital-local/vf-dependency-check:latest

# Install Python 3.8 and pip
# Actualizar el índice de paquetes
RUN apt-get update

# Instalar Python 3 y pip
RUN apt-get install -y python3 python3-pip

# Create a workspace directory
WORKDIR /workspace

# Copy the start.sh script into the workspace directory
COPY start.sh /workspace/start.sh
RUN chmod +x /workspace/start.sh

COPY requirements.txt /workspace/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy feed_mongo.py into the workspace directory
COPY feed_influx.py /workspace/feed_influx.py

RUN cat feed_influx.py

# Command to run the start.sh script
CMD ["/workspace/start.sh"]