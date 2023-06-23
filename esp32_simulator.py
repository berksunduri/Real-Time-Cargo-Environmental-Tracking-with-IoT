import time
import json
import copy
import zstandard as zstd

from kafka import KafkaProducer
from SensorData import SensorData


class Esp32Simulator:
    def _serialize(self, v):
        cctx = zstd.ZstdCompressor()
        return cctx.compress(json.dumps(v).encode('utf-8'))

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='kafka1:9092',
                                      value_serializer=self._serialize)
        print(f"Kafka producer started successfully")
        self.sensor_data = SensorData()
        self.sensor_data.latitude = 42.217699
        self.sensor_data.longitude = 20.729430
        self.prev_data = copy.deepcopy(self.sensor_data.__dict__)

    def insert_data_to_kafka(self, sensor_data):
        self.producer.send('sensor_data', sensor_data)
        self.producer.flush()

    def start(self):
        tolerances = {
            "latitude": 0.00001,
            "longitude": 0.00001,
            "temperature": 0.1,  # daha gercekci yaklasim icin degistirilebilir
            "humidity": 1,
            "acceleration": 0.01,
            "gyro": {"x": 0.01, "y": 0.01, "z": 0.01}
        }

        while True:
            self.sensor_data.update_data()
            current_data = self.sensor_data.__dict__
            data_changed = False

            for key in current_data.keys():
                if isinstance(current_data[key], dict):
                    print(f"Processing {key} which is a dictionary.")
                    if key == "gyro":
                        for axis in current_data[key].keys():
                            if abs(self.prev_data[key][axis] - current_data[key][axis]) >= tolerances[key][axis]:
                                data_changed = True
                                break
                else:
                    print(f"Processing {key} which is not a dictionary.")
                    if abs(self.prev_data[key] - current_data[key]) >= tolerances[key]:
                        data_changed = True

            if data_changed:
                self.insert_data_to_kafka(current_data)
                self.prev_data = copy.deepcopy(current_data)

            time.sleep(8)  # check every 8 seconds
