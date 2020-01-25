import sys
from collections import defaultdict
from unittest import TestCase
from hamcrest import assert_that, equal_to

from lazytest.helpers import MockTofSensor, MockBuzzer, MockLed
from lazydoro.pi.lazy_oo import Clock, Schedule, PomodoroTimer, Display

DURATION = 10
BREAK = 5
GRACE = 2
TIMEOUT = 3


class MockClock(Clock):
    def __init__(self, limit=31*60):
        Clock.__init__(self)
        self.limit = limit
        self.last_event_at = 0
        self.assertions = defaultdict(list)
        self.descriptions = {}
        self._failures = False
        self._running = True

    def tick(self):
        Clock.tick(self)
        if self._ticks in self.assertions:
            for assertion in self.assertions[self._ticks]:
                try:
                    assertion() # run the relevant function
                except Exception as e:
                    print('at time %d assertion %s failed' % (self.ticks(), self.descriptions[self._ticks]), file=sys.stderr)
                    self._failures = True
                    continue
            print(self.ticks(), self.descriptions[self._ticks], 'OK')

    def running(self):
        return self.ticks() <= self.limit and self._running

    def after(self, seconds: int, description: str, *fns):
        next_event_at = (seconds * self.TICKS_PER_SECOND) + self.last_event_at
        self.assertions[next_event_at]+=fns
        self.descriptions[next_event_at] = description
        self.last_event_at = next_event_at

    def check(self):
        if self._failures:
            raise Exception('tests failed')

    def stop(self):
        self._running = False


class LazydoroTest(TestCase):
    def setUp(self):
        self.tof_sensor = MockTofSensor()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        schedule = Schedule(DURATION, BREAK, GRACE, TIMEOUT)
        self.clock = MockClock()
        self.pom = PomodoroTimer(self.clock, self.tof_sensor, self.buzzer, self.led, schedule)

    def test_can_run_a_single_pomodoro(self):
        self.after(1, 'initial state', self.buzzer_is_quiet, self.led_is_blue)
        self.after(1, 'I sit down', self.person_comes)
        self.after(1, 'Pomodoro timer has started', self.buzzer_is_quiet, self.led_is_green)
        self.after(DURATION-1, 'still running', self.buzzer_is_quiet, self.led_is_green)
        self.after(1, 'timer has completed', self.buzzer_is_buzzing, self.led_is_red)
        self.after(1, 'I get up for a break', self.person_leaves)
        self.after(1, 'starting a break', self.buzzer_is_quiet, self.led_is_yellow)
        self.after(BREAK-3, 'still on a break', self.buzzer_is_quiet, self.led_is_yellow)
        self.after(3, 'break timer has completed', self.buzzer_is_buzzing, self.led_is_red)
        self.after(1, 'I sit down again', self.person_comes)
        self.after(3, 'next Pomodoro starts', self.led_is_green)
        self.after(1, 'stopping', self.stop)
        self.pom.run()
        self.clock.check()

    def test_pomodoro_stops_if_I_get_up_early(self):
        self.after(1, 'initial state', self.buzzer_is_quiet, self.led_is_blue)
        self.after(1, 'I sit down at my desk', self.person_comes)
        self.after(1, 'Pomodoro timer has started', self.led_is_green)
        self.after(DURATION-5, 'still running', self.buzzer_is_quiet, self.led_is_green)
        self.after(1,'I get up early',  self.person_leaves)
        self.after(3, 'waiting', self.buzzer_is_quiet, self.led_is_blue)
        self.after(1, 'stopping', self.stop)
        self.pom.run()
        self.clock.stop()
        self.clock.check()

    def after(self, time: int, *fns):
        self.clock.after(time, *fns)

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
        self.tof_sensor.person_comes()

    def person_leaves(self):
        self.tof_sensor.person_leaves()

    def stop(self):
        self.clock.stop()
