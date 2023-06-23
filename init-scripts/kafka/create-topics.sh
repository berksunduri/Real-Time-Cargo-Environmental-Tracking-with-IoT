#!/bin/bash

# Wait for Kafka to become available
until $(nc -zv kafka1 9092); do
    echo "Waiting for Kafka to start..."
    sleep 5
done

# Create the 'sensor_data' topic
/usr/bin/kafka-topics --create --topic sensor_data --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1