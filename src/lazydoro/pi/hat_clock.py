from time import sleep

from lazydoro.pi.lazy_oo import Clock


class HatClock(Clock):
    def tick(self) -> bool:
        sleep(1)
        return True
