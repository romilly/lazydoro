from time import sleep

from lazydoro.pi.lazy_oo import Clock


class HatClock(Clock):

    def running(self):
        return True

    def __init__(self):
        Clock.__init__(self)

    def tick(self) -> None:
        sleep(Clock.TICK_DURATION)
        Clock.tick(self)

