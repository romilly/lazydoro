import board
import busio

import adafruit_vl53l0x

from lazydoro.pi.lazy_oo import ToFSensor


class VL53L0XToF(ToFSensor):
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def distance(self):
        distance = self.vl53.range
        if distance == 0:
            distance = 8190
        return distance

