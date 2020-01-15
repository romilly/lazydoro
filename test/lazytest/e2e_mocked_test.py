from abc import ABC, abstractmethod
from collections import defaultdict
from unittest import TestCase

from hamcrest import assert_that, equal_to

RED = 'Red'
GREEN = 'Green'
BLUE = 'Blue'
YELLOW = 'Yellow'

DURATION = 10
BREAK = 3


class AbstractClock():
    def tick(self) -> bool:
        pass


class MockClock(AbstractClock):
    def __init__(self, limit=31*60):
        self.limit = limit
        self.count = 0
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

    def at(self, time, *fns):
        self.assertions[time]+=fns


class MockTofSensor:
    def __init__(self):
        self._distance = 1000

    def distance(self):
        return self._distance

    def person_is_present(self):
        self._distance = 200

    def person_is_absent(self):
        self._distance = 1000


class AbstractBuzzer(ABC):
    @abstractmethod
    def buzz(self, status):
        pass


class MockBuzzer(AbstractBuzzer):
    def buzz(self, status: bool):
        self.buzzing = status

    def __init__(self):
        self.buzzing = False

    def is_quiet(self):
        return not self.buzzing

    def is_buzzing(self):
        return self.buzzing


class MockLed(object):
    def __init__(self):
        self.color = (0, 0, 0)


class State(ABC):
    @abstractmethod
    def update(self, person_there: bool) -> ('State', bool, str):
        pass


class Resting(State):
    def __init__(self, duration):
        self.ticks = 0
        self.duration = duration

    def update(self, person_there: bool) -> ('State', bool, str):
        self.ticks += 1
        if person_there:
            return PomodoroRunning(DURATION), False, GREEN
        if self.ticks < self.duration:
            return self, True, YELLOW
        return self, False, YELLOW


class PomodoroRunning(State):
    def __init__(self, duration):
        self.ticks = 0
        self.duration = duration

    def update(self, person_there) -> ('State', bool, str):
        self.ticks += 1
        if not person_there:
            return Resting(BREAK), False, YELLOW
        if self.ticks < self.duration:
            return self, False, GREEN
        else:
            return self, True, RED


class Waiting(State):
    def update(self, person_there: bool):
        if person_there:
            return PomodoroRunning(DURATION), False, GREEN
        else:
            return self, False, BLUE


class PomodoroTimer:

    def __init__(self, clock, tof_sensor, buzzer, led):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.tof_sensor = tof_sensor

    def run(self):
        state = Waiting()
        self.led.color = BLUE
        while self.clock.tick():
            (state, buzzing, colour) = state.update(self.person_there())
            self.buzzer.buzz(buzzing)
            self.led.color = colour

    def person_there(self):
        return self.tof_sensor.distance() < 400


class LazyTest(TestCase):
    def setUp(self):
        self.tof_sensor = MockTofSensor()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        self.clock = MockClock()
        self.pom = PomodoroTimer(self.clock, self.tof_sensor, self.buzzer, self.led)

    def test_can_run_a_single_pomodoro(self):
        self.clock.at(1, self.buzzer_is_quiet)
        self.clock.at(1, self.led_is_blue)
        self.clock.at(2, self.person_appears)
        self.clock.at(3, self.led_is_green)
        self.clock.at(DURATION+2, self.buzzer_is_quiet, self.led_is_green) # pomodoro started at time 3
        self.clock.at(DURATION+3, self.buzzer_is_buzzing, self.led_is_red)
        self.clock.at(DURATION+4, self.person_is_absent)
        self.clock.at(DURATION+5, self.buzzer_is_quiet, self.led_is_yellow)


        self.pom.run()

    def buzzer_is_quiet(self):
        assert_that(not self.buzzer.buzzing,'buzzer is not quiet')

    def buzzer_is_buzzing(self):
        assert_that(self.buzzer.buzzing,'buzzer is quiet')

    def led_is_blue(self):
        assert_that(self.led.color, equal_to(BLUE))

    def led_is_red(self):
        assert_that(self.led.color, equal_to(RED))

    def led_is_green(self):
        assert_that(self.led.color, equal_to(GREEN))

    def led_is_yellow(self):
        assert_that(self.led.color, equal_to(YELLOW))


    def person_appears(self):
        self.tof_sensor.person_is_present()

    def person_is_absent(self):
        self.tof_sensor.person_is_absent()
