import random
import math


class SensorData:
    def __init__(self):
        # gauss(mu, sigma) where mu=mean and sigma=standard deviation
        self.latitude = random.gauss(0, 1)
        self.longitude = random.gauss(0, 1)
        self.temperature = random.gauss(25, 5)  # Tempin %5 sapma ile 25 derecede oldugunu varsayarak
        self.humidity = random.gauss(30, 10)  # Humiditynin %10 sapma ile 30da oldugunu varsayarak
        self.acceleration = random.gauss(0, 0.1)
        self.gyro = {"x": random.gauss(0, 0.1), "y": random.gauss(0, 0.1), "z": random.gauss(0, 0.1)}

    def update_data(self):
        # %70 sansla degisicek
        if random.random() < 0.7:
            self.latitude += random.gauss(0.1, 0.01)
            self.longitude += random.gauss(0.01, 0.003)

        # all sensors will change with 20% probability
        if random.random() < 0.2:
            self.temperature += random.gauss(2, 3.0)

        if random.random() < 0.2:
            self.humidity += random.gauss(2, 3)

        if random.random() < 0.2:
            self.acceleration += random.gauss(0, 0.05)

        if random.random() < 0.2:
            self.gyro["x"] += random.gauss(0, 0.05)
            self.gyro["y"] += random.gauss(0, 0.05)
            self.gyro["z"] += random.gauss(0, 0.05)
