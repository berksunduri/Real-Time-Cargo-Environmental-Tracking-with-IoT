CREATE KEYSPACE IF NOT EXISTS sensordata WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

USE sensordata;

CREATE TABLE IF NOT EXISTS data (
    id UUID,
    acceleration DECIMAL,
    gyro_x DECIMAL,
    gyro_y DECIMAL,
    gyro_z DECIMAL,
    humidity DECIMAL,
    latitude DECIMAL,
    longitude DECIMAL,
    temperature DECIMAL,
    timestamp TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);