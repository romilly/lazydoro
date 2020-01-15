from unittest import TestCase

from hamcrest import assert_that, equal_to

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class AbstractClock():
    def tick(self):
        pass


class MockClock(AbstractClock):
    def __init__(self):
        self.limit = 5*30*60
        self.count = 0

    def tick(self):
        self.count += 1
        return self.count <= self.limit


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
        while True:
            self.clock.tick()
            distance = self.tof_sensor.distance()
            (state, buzzing, colour) = state.update(distance)
            self.buzzer.buzz(buzzing)
            self.led.color = colour


class Script:
    def __init__(self, *events):
        self._events = events



class LazyTest(TestCase):
    def setUp(self):
        self.clock = MockClock()
        self.tof_sensor = MockTofSensor()
        self.buzzer = MockBuzzer()
        self.led = MockLed()
        self.eventQueue = []
        self.pom = PomodoroTimer(self.clock, self.tof_sensor, self.buzzer, self.led)

    def test_can_run_a_single_pomodoro(self):
        script = Script(self.buzzer_is_quiet,
                        self.person_appears,
                        self.led_is_green,
                        self.wait(minutes=30),
                        self.buzzer_is_buzzing,
                        self.wait(minutes=0, seconds=1),
                        self.buzzer_is_quiet)
        self.pom.run()

    def buzzer_is_quiet(self):
        if self.buzzer.is_quiet():
            return
        self.fail('buzzer is not buzzing')

    def led_is_green(self):
        pass

    def wait(self, minutes, seconds=0):
        pass

    def person_appears(self):
        self.tof_sensor.person_is_present()

    def person_is_absent(self):
        self.tof_sensor.person_is_absent()
