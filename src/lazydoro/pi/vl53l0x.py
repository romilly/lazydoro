import board
import busio

import adafruit_vl53l0x

from lazydoro.pi.lazy_oo import ToFSensor


def average(values):
    return sum(values)/len(values)


class VL53L0XToF(ToFSensor):
    def __init__(self, threshold=400):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)
        self.threshold = threshold
        self.ranges = 5*[1.1 * threshold]

    def is_someone_there(self):
        distance = self.vl53.range
        while distance == 0:
            distance = self.vl53.range
        self.ranges = self.ranges[1:] + [distance]
        return average(self.ranges) < self.threshold
