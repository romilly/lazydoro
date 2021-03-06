from collections import defaultdict
from unittest import TestCase

from hamcrest import assert_that, equal_to

from src.lazydoro.pi.lazy_oo import Clock, ToFSensor, Buzzer, Schedule, Led, PomodoroTimer


DURATION = 10
BREAK = 3
GRACE = 2
TIMEOUT = 3


class MockClock(Clock):
    def __init__(self, limit=31*60):
        self.limit = limit
        self.count = 0
        self.last_event_at = 0
        self.assertions = defaultdict(list)

    def tick(self):
        self.count += 1
        if self.count in self.assertions:
            for assertion in self.assertions[self.count]:
                try:
                    assertion() # run the relevant function
                except Exception as e:
                    print('at time %d' % self.count)
                    raise e
        return self.count <= self.limit

    def after(self, time: int, *fns):
        next_event_at = time + self.last_event_at
        self.assertions[next_event_at]+=fns
        self.last_event_at = next_event_at


class MockTofSensor(ToFSensor):
    def __init__(self):
        self._person_there = False

    def person_comes(self):
        self._person_there = True

    def person_leaves(self):
        self._person_there = False

    def is_someone_there(self):
        return self._person_there


class MockBuzzer(Buzzer):
    def on(self, status: bool):
        self.buzzing = status

    def __init__(self):
        self.buzzing = False

    def is_quiet(self):
        return not self.buzzing

    def is_buzzing(self):
        return self.buzzing


class MockLed(Led):
    def __init__(self):
        self._color = Led.OFF

    def set_display(self, color):
        self._color = color

    def display(self):
        return self._color


class LazydoroTest(TestCase):
    def setUp(self):
        self.tof_sensor = MockTofSensor()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        self.clock = MockClock()
        self.pom = PomodoroTimer(self.clock, self.tof_sensor, self.buzzer, self.led)
        self.schedule = Schedule(DURATION, BREAK, GRACE, TIMEOUT)

    def test_can_run_a_single_pomodoro(self):
        self.after(1, self.buzzer_is_quiet, self.led_is_blue) # initial state
        self.after(1, self.person_comes) # I sit down at my desk
        self.after(1, self.buzzer_is_quiet, self.led_is_green)  # Pomodoro timer has started
        self.after(DURATION, self.buzzer_is_quiet, self.led_is_green) # still running
        self.after(1, self.buzzer_is_buzzing, self.led_is_red) # timer has completed
        self.after(1, self.person_leaves) # I get up for a break
        self.after(1, self.buzzer_is_quiet, self.led_is_yellow) # timing a break
        self.after(BREAK, self.buzzer_is_quiet, self.led_is_yellow) # timing a break
        self.after(1, self.buzzer_is_buzzing, self.led_is_red) # timer has completed
        self.after(1, self.person_comes) # I sit down at my desk
        self.after(1, self.led_is_green) # next Pomodoro  has started

    def test_pomodoro_stops_if_I_get_up_early(self):
        self.after(1, self.buzzer_is_quiet, self.led_is_blue)  # initial state
        self.after(1, self.person_comes)  # I sit down at my desk
        self.after(1, self.led_is_green) # Pomodoro timer has started
        self.after(DURATION, self.buzzer_is_quiet, self.led_is_green)  # still running
        self.after(1, self.person_leaves) # I get up for a break
        self.after(1, self.buzzer_is_quiet, self.led_is_yellow) # timing a break


    def test_pomodoro_restarts_if_I_finish_break__early(self):
        self.after(1, self.person_comes)  # I sit down at my desk
        self.after(1, self.person_leaves)  # I get up for a break
        self.after(1, self.buzzer_is_quiet, self.led_is_yellow)  # timing a break
        self.after(1, self.person_comes)  # I sit down at my desk
        self.after(1, self.buzzer_is_quiet, self.led_is_green)  # initial state

        self.pom.run(self.schedule)

    def after(self, time: int, *fns):
        self.clock.after(time, *fns)

    def buzzer_is_quiet(self):
        assert_that(not self.buzzer.buzzing,'buzzer is buzzing but should be quiet')

    def buzzer_is_buzzing(self):
        assert_that(self.buzzer.buzzing,'buzzer is quiet but should be buzzing')

    def led_is_blue(self):
        assert_that(self.led.display(), equal_to(Led.BLUE))

    def led_is_red(self):
        assert_that(self.led.display(), equal_to(Led.RED))

    def led_is_green(self):
        assert_that(self.led.display(), equal_to(Led.GREEN))

    def led_is_yellow(self):
        assert_that(self.led.display(), equal_to(Led.YELLOW))

    def person_comes(self):
        self.tof_sensor.person_comes()

    def person_leaves(self):
        self.tof_sensor.person_leaves()
