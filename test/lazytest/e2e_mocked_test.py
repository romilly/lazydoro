from collections import defaultdict
from unittest import TestCase

from hamcrest import assert_that, equal_to

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


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
                assertion() # run the relevant function
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


class AbstractBuzzer:
    def buzz(self, status):
        pass


class MockBuzzer(AbstractBuzzer):
    def __init__(self):
        self.buzzing = False

    def is_quiet(self):
        return not self.buzzing

    def is_buzzing(self):
        return self.buzzing


class MockLed(object):
    def __init__(self):
        self.color = (0, 0, 0)


class State:
    def update(self, range):
        pass


class PomodoroRunning(State):
    pass


pomodoro_running = PomodoroRunning()


class Waiting(State):
    def update(self, distance):
        if distance < 1000:
            return pomodoro_running, False, GREEN
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
            distance = self.tof_sensor.distance()
            (state, buzzing, colour) = state.update(distance)
            self.buzzer.buzz(buzzing)
            self.led.color = colour


class Script:
    def __init__(self, *events):
        self._events = events


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
        self.pom.run()

    def buzzer_is_quiet(self):
        assert_that(not self.buzzer.buzzing,'buzzer is not quiet')

    def led_is_blue(self):
        assert_that(self.led.color, equal_to(BLUE))




    def wait(self, minutes, seconds=0):
        pass

    def person_appears(self):
        self.tof_sensor.person_is_present()

    def person_is_absent(self):
        self.tof_sensor.person_is_absent()
