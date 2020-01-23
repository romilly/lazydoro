#! /usr/bin/python3
import sys
sys.path.append('.') # ugh!
from lazydoro.pi.blinkt_leds import BlinktLEDs
from lazydoro.pi.hat_clock import HatClock
from lazydoro.pi.lazy_oo import Schedule, PomodoroTimer, Clock
from lazydoro.pi.pwmbuzzer import PwmBuzzer
from lazydoro.pi.vl53l0x import VL53L0XToF


if __name__ == '__main__':
    time_units = 60 if len(sys.argv) < 2 else 1 # to run a demo, just append 'demo' after the script name
    tof_sensor = VL53L0XToF()
    schedule = Schedule(25*60, 5*60, 5, 5) if len(sys.argv) < 2 else Schedule(10, 5, 3, 3)
    clock = HatClock()
    buzzer = PwmBuzzer(pin=6)
    led = BlinktLEDs()
    pom = PomodoroTimer(clock, tof_sensor, buzzer, led)
    pom.run(schedule)