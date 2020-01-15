# Simple demo of the VL53L0X distance sensor.
# Will print the sensed range/distance every second.
from time import sleep
import board
import busio

import adafruit_vl53l0x
import RPi.GPIO as GPIO

# Initialize I2C bus and sensor.

def average(values):
    return sum(values)/len(values)



class Pomodoro:
    WAITING = 'waiting'
    WORKING = 'working'
    RESTING = 'resting'
    DURATION = 60*25 # 25 mins
    BREAK = 60*5
    RANGE_LIMIT = 400 # if range is closer than that, I'm at my desk

    def __init__(self, beeper):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)
        self.state = self.WAITING
        self.time = 0
        self.ranges = 5*[2 * self.RANGE_LIMIT]
        self.beeper = beeper

    def tick(self):
        if self.state == self.WAITING:
            if self.at_desk():
                self.state = self.WORKING
                self.time = 0
                return
            else:
                return
        elif self.state == self.WORKING:
            self.time += 1
            if self.at_desk():
                if self.time > self.DURATION:
                    self.beeper.beep(1, 400)
                    sleep(10) # time to get up
                else:
                    return
            else:
                self.state = self.RESTING
                self.time = 0
                return
        else: # must be resting
            self.time += 1
            if self.at_desk():
                self.time = 0
                self.state = self.WORKING
                return
            else:
                if self.time > self.BREAK:
                    for i in range(3):
                        self.beeper.beep(1, 100)
                        sleep(10) # time to come back
                        return



    def at_desk(self):
        self.ranges = self.ranges[1:]+[self.vl53.range]
        return average(self.ranges) > self.RANGE_LIMIT


# Main loop will check the range and
class Beeper:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        self.buzzer = GPIO.PWM(18, 400)

    def beep(self, seconds, freq):
        self.buzzer.ChangeFrequency(freq)
        self.buzzer.start(50)
        sleep(seconds)
        self.buzzer.stop()


beeper = Beeper()
pomodoro = Pomodoro(beeper)
while True:
    pomodoro.tick()
