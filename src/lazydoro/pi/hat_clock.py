from time import sleep

from lazydoro.pi.lazy_oo import Clock, Schedule


class HatClock(Clock):

    def __init__(self, schedule: Schedule):
        Clock.__init__(self, schedule)

    def tick(self) -> bool:
        self.advance()
        sleep(self.increment())
        return True

