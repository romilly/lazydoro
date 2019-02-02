from unittest import TestCase

from hamcrest import assert_that, equal_to

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class AbstractClock():
    def tick(self):
        pass


class MockClock(AbstractClock):
    pass


class MockTofSensor:
    def distance(self):
        pass


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


class Waiting(State):
    def update(self, range):
        if range < 1000:
            return (PomodoroRunning(), False, GREEN)
        else:
            return (self, False, BLUE)



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
            range = self.tof_sensor.range()
            (state, buzzing, led) = state.update(range)
            self.buzzer.buzz(buzzing)
            self.led.color = led



class LazyTest(TestCase):
    def setUp(self):
        self.clock = MockClock()
        self.tof_sensor = MockTofSensor()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        self.eventQueue = []
        self.pom = PomodoroTimer(self.clock, self.tof_sensor, self.buzzer, self.led)

    def test_can_run_a_single_pomodoro(self):
        self.pom.run()
        assert_that(self.buzzer.is_quiet())
        self.tof_distance(300)
        # TODO: create colour matcher
        assert_that(self.led.color, equal_to(GREEN))
        self.wait(30)
        assert_that(self.buzzer.is_buzzing())
        self.wait(0, 1)
        assert_that(self.buzzer.is_quiet())
        self.tof_distance(1000)

    def tof_distance(self, param):
        return self.tof_sensor.distance()

    def wait(self, minutes, seconds=0):
        pass
