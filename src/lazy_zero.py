#! /usr/bin/python3
import sys
from time import sleep

sys.path.append('.') # ugh!
from lazydoro.pi.blinkt_leds import BlinktLEDs
from lazydoro.pi.hat_clock import HatClock
from lazydoro.pi.lazy_oo import Schedule, PomodoroTimer, DistanceBasedDetector
from lazydoro.pi.pwmbuzzer import PwmBuzzer
from lazydoro.pi.vl53l0x import VL53L0XToF


if __name__ == '__main__':
    detector = DistanceBasedDetector(VL53L0XToF(), 400)
    schedule = Schedule(25*60, 5*60, 4, 4) if len(sys.argv) < 2 else Schedule(16, 8, 4, 4)
    clock = HatClock()
    buzzer = PwmBuzzer(pin=6)
    led = BlinktLEDs()
    pom = PomodoroTimer(clock, detector, buzzer, led, schedule)
    pom.run()