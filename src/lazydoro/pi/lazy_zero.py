from lazydoro.pi.blinkt_leds import BlinktLEDs
from lazydoro.pi.hat_clock import HatClock
from lazydoro.pi.lazy_oo import Schedule, PomodoroTimer, Clock
from lazydoro.pi.pwmbuzzer import PwmBuzzer
from lazydoro.pi.vl53l0x import VL53L0XToF


if __name__ == '__main__':
    tof_sensor = VL53L0XToF()
    #schedule = Schedule(25*60, 5*60, 60, 60)
    schedule = Schedule(20, 5, 3, 3)
    clock = HatClock()
    buzzer = PwmBuzzer(pin=18)
    led = BlinktLEDs()
    pom = PomodoroTimer(clock, tof_sensor, buzzer, led)
    pom.run(schedule)