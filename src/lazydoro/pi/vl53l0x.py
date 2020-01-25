import board
import busio

import adafruit_vl53l0x

from lazydoro.pi.lazy_oo import ToFSensor


def average(values):
    return sum(values)/len(values)


class VL53L0XToF(ToFSensor):
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def distance(self):
        distance = self.vl53.range
        while distance == 0:
            distance = self.vl53.range
        return distance

