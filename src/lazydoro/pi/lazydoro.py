# Simple demo of the VL53L0X distance sensor.
# Will print the sensed range/distance every second.
from time import sleep
import board
import busio

import adafruit_vl53l0x
import RPi.GPIO as GPIO



def average(values):
    return sum(values)/len(values)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
buzzer = GPIO.PWM(18, 400)


def beep(seconds, freq):
    buzzer.ChangeFrequency(freq)
    buzzer.start(50)
    sleep(seconds)
    buzzer.stop()



WAITING = 'waiting'
WORKING = 'working'
RESTING = 'resting'
DURATION =  60*25 # 25 mins
BREAK = 60*5
RANGE_LIMIT = 400 # if range is closer than that, I'm at my desk


i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
current_state = WAITING
time_now = 0
ranges = 5*[2 * RANGE_LIMIT]


def at_desk():
    global ranges
    range = vl53.range
    while range == 0:
        range = vl53.range
    ranges = ranges[1:]+[range]
    return average(ranges) < RANGE_LIMIT


def check_waiting(time):
    if at_desk():
        return (0,  WORKING)
    else:
        return(time+1, WAITING)


def check_working(time):
    time += 1
    if time > DURATION:
        if not at_desk():
            print('resting')
            return 0, RESTING
        else:
            beep(1, 400)
            return time, WORKING
    if at_desk():
        return time, WORKING
    else:
        return 0, WAITING


def check_resting(time):
    if at_desk():
        return 0, WORKING
    time += 1
    if time > BREAK:
            beep(1, 200)
            beep(1, 400)
            beep(1, 200)
    return time, RESTING


def tick(time, state):
    if state == WAITING:
        return check_waiting(time)
    if state == WORKING:
        return check_working(time)
    if state == RESTING:
        return check_resting(time)
    raise Exception('invalid state %s' % state)

count = 0
while True:
    sleep(1)
    time_now, current_state = tick(time_now, current_state)
    # count += 1
    # if count == 10:
    #     print(ranges, time_now, current_state)
    #     count = 0