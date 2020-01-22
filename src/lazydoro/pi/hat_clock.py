from time import sleep

from lazydoro.pi.lazy_oo import Clock, Schedule


class HatClock(Clock):
    def tick(self) -> bool:
        sleep(1.0/ Schedule.SCALE)
        return True
