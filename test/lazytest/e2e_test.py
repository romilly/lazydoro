from unittest import TestCase
from hamcrest import assert_that, equal_to
from hamcrest.core.base_matcher import BaseMatcher

from lazytest.helpers import MockTofSensor, MockBuzzer, MockLed
from src.lazydoro.pi.lazy_oo import Clock, Schedule, PomodoroTimer, Display, PersonDetector

DURATION = 10
BREAK = 5
GRACE = 2
TIMEOUT = 3


class MockClock(Clock):
    def __init__(self, limit=31*60):
        Clock.__init__(self)
        self.limit = limit
        self._running = True

    def running(self):
        return self.ticks <= self.limit and self._running

    def stop(self):
        self._running = False


class DisplayMatcher(BaseMatcher):
    def __init__(self, display: Display):
        self.display = display

    def describe_to(self, description):
        description.append_text(str(self.display))

    def _matches(self, item):
        if not isinstance(item, Display):
            return False
        result = (item.color == self.display.color
                  and self.display.current == item.current
                  and self.display.limit == item.limit)
        return result


def shows(display: Display):
    return DisplayMatcher(display)


class MockPersonDetector(PersonDetector):
    def is_person_present(self) -> bool:
        return self.person_present

    def __init__(self):
        self.person_present = False

    def person_comes(self):
        self.person_present = True

    def person_leaves(self):
        self.person_present = False


class LazydoroTest(TestCase):
    def setUp(self):
        self.detector = MockPersonDetector()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        schedule = Schedule(DURATION, BREAK, GRACE, TIMEOUT)
        self.clock = MockClock()
        self.pom = PomodoroTimer(self.clock, self.detector, self.buzzer, self.led, schedule)

    def test_can_run_a_single_pomodoro(self):
        self.skip(1)
        assert_that(self.led.display(), shows(Display.blue(0, 8)))
        assert_that(self.buzzer.is_quiet())
        self.person_comes()
        self.skip(1)
        assert_that(self.led.display(), shows(Display.green(1, 80)))
        assert_that(self.buzzer.is_quiet())
        self.skip(0, seconds=1)
        assert_that(self.led.display(), shows(Display.green(10, 80)))
        self.skip(4, seconds=8)
        assert_that(self.led.display(), shows(Display.green(79, 80)))
        self.skip(1)
        assert_that(self.led.display(), shows(Display.red(0, 1)))
        assert_that(self.buzzer.is_buzzing())


        # self.after(DURATION-1, 'still running', self.buzzer_is_quiet, self.led_is_green)
        # self.after(1, 'timer has completed', self.buzzer_is_buzzing, self.led_is_red)
        # self.after(1, 'I get up for a break', self.person_leaves)
        # self.after(1, 'starting a break', self.buzzer_is_quiet, self.led_is_yellow)
        # self.after(BREAK-3, 'still on a break', self.buzzer_is_quiet, self.led_is_yellow)
        # self.after(3, 'break timer has completed', self.buzzer_is_buzzing, self.led_is_red)
        # self.after(1, 'I sit down again', self.person_comes)
        # self.after(3, 'next Pomodoro starts', self.led_is_green)
        # self.after(1, 'stopping', self.stop)

    # def test_pomodoro_stops_if_I_get_up_early(self):
    #     self.after(1, 'initial state', self.buzzer_is_quiet, self.led_is_blue)
    #     self.after(1, 'I sit down at my desk', self.person_comes)
    #     self.after(1, 'Pomodoro timer has started', self.led_is_green)
    #     self.after(DURATION-5, 'still running', self.buzzer_is_quiet, self.led_is_green)
    #     self.after(1,'I get up early',  self.person_leaves)
    #     self.after(3, 'waiting', self.buzzer_is_quiet, self.led_is_blue)
    #     self.after(1, 'stopping', self.stop)
    #     self.pom.run()
    #     self.clock.stop()
    #     self.clock.check()

    def buzzer_is_quiet(self):
        assert_that(not self.buzzer.buzzing,'buzzer is buzzing but should be quiet')

    def buzzer_is_buzzing(self):
        assert_that(self.buzzer.buzzing,'buzzer is quiet but should be buzzing')

    def led_is_blue(self):
        assert_that(self.led.color(), equal_to(Display.BLUE))

    def led_is_red(self):
        assert_that(self.led.color(), equal_to(Display.RED))

    def led_is_green(self):
        assert_that(self.led.color(), equal_to(Display.GREEN))

    def led_is_yellow(self):
        assert_that(self.led.color(), equal_to(Display.YELLOW))

    def person_comes(self):
        self.detector.person_comes()

    def person_leaves(self):
        self.detector.person_leaves()

    def stop(self):
        self.clock.stop()

    def skip(self, ticks: int, seconds: int = 0) -> None:
        self.clock.reset()
        self.clock.limit = ticks + self.clock.TICKS_PER_SECOND * seconds
        self.pom.run()
