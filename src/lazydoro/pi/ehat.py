from time import sleep

from lazydoro.pi.lazy_oo import Schedule, PomodoroTimer, Clock, Buzzer, Led
from lazydoro.pi.pwmbuzzer import PwmBuzzer
from lazydoro.pi.vl53l0x import VL53L0XToF

import board
import busio

import explorerhat as eh
import RPi.GPIO as GPIO


class HatClock(Clock):
    def tick(self) -> bool:
        sleep(1)
        return True


class HatLEDs(Led):
    def __init__(self):
        self.color = Led.OFF

    def color(self):
        return self.color()

    def set_color(self, color):
        self.color = color
        eh.light.off()
        if color == Led.RED:
            eh.light.red.on()
            return
        if color == Led.YELLOW:
            eh.light.yellow.on()
            return
        if color == Led.BLUE:
            eh.light.blue.on()
            return
        if color == Led.GREEN:
            eh.light.green.on()
            return


if __name__ == '__main__':
    tof_sensor = VL53L0XToF()
    #schedule = Schedule(25*60, 5*60, 60, 60)
    schedule = Schedule(20, 5, 3, 3)
    clock = HatClock()
    buzzer = PwmBuzzer(pin=18)
    led = HatLEDs()
    pom = PomodoroTimer(clock, tof_sensor, buzzer, led)
    pom.run(schedule)