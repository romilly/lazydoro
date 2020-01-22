from time import sleep

from lazydoro.pi.lazy_oo import Clock, Schedule


class HatClock(Clock):
    INCREMENT = 1.0 / Schedule.SCALE

    def __init__(self):
        Clock.__init__(self)

    def tick(self) -> bool:
        self.advance()
        sleep(self.INCREMENT)
        return True

