import threading
import app

from multiprocessing import Process
from esp32_simulator import Esp32Simulator


def run_app():
    # Start the Kafka consumer and Cassandra writer in separate threads at the beginning of the program
    consumer_thread = threading.Thread(target=app.start_kafka_consumer)
    consumer_thread.start()
    print("kafka consumer started")

    cassandra_thread = threading.Thread(target=app.start_cassandra_writer)
    cassandra_thread.start()
    print("cassandra writer started")

    app.socketio.run(app.app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)


def run_simulator():
    simulator = Esp32Simulator()
    simulator.start()


if __name__ == '__main__':
    app_process = Process(target=run_app)
    simulator_process = Process(target=run_simulator)

    app_process.start()
    simulator_process.start()

    app_process.join()
    simulator_process.join()
