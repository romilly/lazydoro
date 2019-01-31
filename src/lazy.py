import time

import board
import busio

import adafruit_vl53l0x

import neopixel

led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.3

RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
YELLOW = (127, 127, 0)
BLUE   = (0, 0, 255)


def colour_for(range):
    if range > 1000: return BLUE
    if range >  300: return GREEN
    if range >  150: return YELLOW
    return RED


def show(range):
    led[0] = colour_for(range)


# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)


vl53.measurement_timing_budget = 200000
# Main loop will read the range and print it every second.


while True:
    show(vl53.range)
    time.sleep(1.0)