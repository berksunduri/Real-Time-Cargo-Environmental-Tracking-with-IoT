#!/usr/bin/env bash

until printf "" 2>>/dev/null >>/dev/tcp/cassandra/9042; do
    sleep 5;
    echo "Waiting for cassandra...";
done

echo "Creating keyspace and tables..."
cqlsh cassandra -u cassandra -p cassandra -e "CREATE KEYSPACE IF NOT EXISTS sensordata WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};"
cqlsh cassandra -u cassandra -p cassandra -e "USE sensordata;
CREATE TABLE IF NOT EXISTS latitude_data (
    id UUID,
    timestamp TIMESTAMP,
    latitude DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS longitude_data (
    id UUID,
    timestamp TIMESTAMP,
    longitude DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS temperature_data (
    id UUID,
    timestamp TIMESTAMP,
    temperature DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS acceleration_data (
    id UUID,
    timestamp TIMESTAMP,
    acceleration DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS humidity_data (
    id UUID,
    timestamp TIMESTAMP,
    humidity DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS gyro_data (
    id UUID,
    timestamp TIMESTAMP,
    gyro_x DECIMAL,
    gyro_y DECIMAL,
    gyro_z DECIMAL,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);"






