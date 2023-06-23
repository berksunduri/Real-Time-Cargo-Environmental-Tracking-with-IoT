import random
import time
import logging
import json
import queue
import zstandard as zstd
import sys
import logging

from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from rx import interval
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops
from flask import jsonify
from threading import Thread
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.util import uuid_from_time
from queue import Full, Empty


app = Flask(__name__)
app.config['SECRET_KEY'] = "arandomstring"
socketio = SocketIO(app, async_mode=None, engineio_logger=True)
# async_mode can be 'threading', None or 'eventlet', hangi serveri kullanicagina bagli


app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

# Create a queue for Kafka data
kafka_data_queue = queue.Queue(maxsize=1000)


consumer = None
last_message = None


def _deserialize(v):
    dctx = zstd.ZstdDecompressor()
    return json.loads(dctx.decompress(v).decode('utf-8'))


def start_kafka_consumer():
    global consumer
    consumer = KafkaConsumer(
        'sensor_data',
        bootstrap_servers=['kafka1:9092'],
        value_deserializer=_deserialize)
    print(f"kafka consumer started successfully")
    for message in consumer:
        while True:
            try:
                kafka_data_queue.put(message.value, timeout=5)  # block until a free slot is available
                break
            except Full:
                continue  # try again if the queue is full


def start_cassandra_writer():
    backoff_time = 1  # start with a 1 second delay
    max_backoff_time = 60  # you might want to cap the delay to a max value
    while True:  # keep trying to connect
        try:
            cluster = Cluster(['cassandra'])  # Cassandra host IP
            cassandra_session = cluster.connect('sensordata')  # Cassandra Keyspace name
            print(f"connection is successful")
            # if we're here, it means the connection was successful
            break  # exit the loop
        except Exception as e:
            print(f"Unable to connect to Cassandra: {e}")
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)  # wait before trying to connect again
            backoff_time *= 2  # increase the wait time for the next possible failure
            if backoff_time > max_backoff_time:
                backoff_time = max_backoff_time  # cap the backoff time
    global last_message
    while True:
        try:
            message = kafka_data_queue.get(timeout=5)  # block until a message is available
        except Empty:
            continue  # try again if the queue is empty

        app.logger.info(f"Processing message: {message}")  # <-- Added this log
        latitude = message['latitude']
        longitude = message['longitude']
        temperature = message['temperature']
        humidity = message['humidity']
        acceleration = message['acceleration']
        gyro = message['gyro']
        current_message = (latitude, longitude, temperature, humidity, acceleration, gyro['x'], gyro['y'], gyro['z'])

        if last_message is None or latitude != last_message[0]:
            insert_latitude_to_cassandra(cassandra_session, latitude)
        if last_message is None or longitude != last_message[1]:
            insert_longitude_to_cassandra(cassandra_session, longitude)
        if last_message is None or temperature != last_message[2]:
            insert_temperature_to_cassandra(cassandra_session, temperature)
        if last_message is None or humidity != last_message[3]:
            insert_humidity_to_cassandra(cassandra_session, humidity)
        if last_message is None or acceleration != last_message[4]:
            insert_acceleration_to_cassandra(cassandra_session, acceleration)
        if last_message is None or (gyro['x'], gyro['y'], gyro['z']) != last_message[5:8]:
            insert_gyro_to_cassandra(cassandra_session, gyro['x'], gyro['y'], gyro['z'])

        if last_message != current_message:
            app.logger.info(f"Data successfully sent to Cassandra")
            last_message = current_message  # update last_message if it has changed
        else:
            app.logger.info(f"No data changed so nothing is sent to Cassandra")


# ana sayfa
@app.route('/')
def index():
    initial_location = kafka_data_queue.get()
    return render_template('index.html', latitude=initial_location['latitude'], longitude=initial_location['longitude'],
                           temperature=initial_location['temperature'], humidity=initial_location['humidity'],
                           acceleration=initial_location['acceleration'], gyro=initial_location['gyro'])


@app.route('/get_sensor_data')
def get_sensor_data():
    try:
        location = kafka_data_queue.get()
    except Empty:
        return jsonify({"error": "No data available in the queue"})
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    temperature = location.get('temperature')
    humidity = location.get('humidity')
    acceleration = location.get('acceleration')
    gyro = location.get('gyro', {})
    gyro_x = gyro.get('x')
    gyro_y = gyro.get('y')
    gyro_z = gyro.get('z')
    data = {'latitude': latitude, 'longitude': longitude, 'temperature': temperature, 'humidity': humidity,
            'acceleration': acceleration, 'gyro': {'x': gyro_x, 'y': gyro_y, 'z': gyro_z}}
    print(data)
    return jsonify(data)


def get_latest_data_from_cassandra(session):
    try:
        rows = session.execute('SELECT * FROM data ORDER BY timestamp DESC LIMIT 1')
        data = rows[0]
        return data.latitude, data.longitude, data.temperature, data.humidity, data.acceleration, data.gyro_x, data.gyro_y, data.gyro_z
    except Exception as e:
        print(f"Exception in get_latest_data_from_cassandra: {e}")
        return None


def insert_latitude_to_cassandra(session, latitude):
    try:
        query = """
        INSERT INTO latitude_data (id, latitude, timestamp)
        VALUES (%s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), latitude, now))
        app.logger.info("Latitude Successfully Sent To Cassandra")
    except Exception as e:
        app.logger.info(f"Exception in insert_latitude_to_cassandra: {e}")


def insert_longitude_to_cassandra(session, longitude):
    try:
        query = """
        INSERT INTO longitude_data (id, longitude, timestamp)
        VALUES (%s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), longitude, now))
        print("Longitude Successfully Sent To Cassandra")
    except Exception as e:
        print(f"Exception in insert_longitude_to_cassandra: {e}")


def insert_temperature_to_cassandra(session, temperature):
    try:
        query = """
        INSERT INTO temperature_data (id, temperature, timestamp)
        VALUES (%s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), temperature, now))
        print("Temperature Successfully Sent To Cassandra")
    except Exception as e:
        print(f"Exception in insert_temperature_to_cassandra: {e}")


def insert_humidity_to_cassandra(session, humidity):
    try:
        query = """
        INSERT INTO humidity_data (id, humidity, timestamp)
        VALUES (%s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), humidity, now))
        print("Humidity Successfully Sent To Cassandra")
    except Exception as e:
        print(f"Exception in insert_humidity_to_cassandra: {e}")


def insert_acceleration_to_cassandra(session, acceleration):
    try:
        query = """
        INSERT INTO acceleration_data (id, acceleration, timestamp)
        VALUES (%s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), acceleration, now))
        print("Acceleration Successfully Sent To Cassandra")
    except Exception as e:
        print(f"Exception in insert_acceleration_to_cassandra: {e}")


def insert_gyro_to_cassandra(session, gyro_x, gyro_y, gyro_z):
    try:
        query = """
        INSERT INTO gyro_data (id, gyro_x, gyro_y, gyro_z, timestamp)
        VALUES (%s, %s, %s, %s, %s);
        """
        now = datetime.now()
        session.execute(query, (uuid_from_time(time.time()), gyro_x, gyro_y, gyro_z, now))
        print("Gyro Successfully Sent To Cassandra")
    except Exception as e:
        print(f"Exception in insert_gyro_to_cassandra: {e}")


# GOOGLE MAPS API
# AIzaSyBwP8UgQnG3wS5nMCQZEmjldj2RaZnrGe0
