from abc import ABC, abstractmethod
from time import sleep


def average(values):
    return sum(values)/len(values)


class Schedule:
    def __init__(self, pomodoro_duration: int, break_duration: int, grace_period: int, timeout: int):
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration
        self.grace_period = grace_period
        self.timeout = timeout


class Clock(ABC):
    TICKS_PER_SECOND = 8
    TICK_DURATION = 1.0 / TICKS_PER_SECOND

    def __init__(self, ):
        self.ticks = 0

    @abstractmethod
    def running(self):
        pass

    def tick(self) -> None:
        self.ticks += 1

    def reset(self):
        self.ticks = 0


class ToFSensor(ABC):
    @abstractmethod
    def distance(self) -> int:
        pass


class PersonDetector(ABC):
    @abstractmethod
    def is_person_present(self) -> bool:
        pass


class DistanceBasedDetector(PersonDetector):
    def __init__(self, sensor: ToFSensor, threshold: int):
        self.sensor = sensor
        self.threshold = threshold
        self.readings = 5

    def is_person_present(self) -> bool:
        count = 0
        for index in range(5):
            distance = self.sensor.distance()
            if distance < self.threshold:
                count += 1
            sleep(0.1)
        return count > 0.5 * self.readings


class Buzzer(ABC):
    def on(self):
        self.buzzing = True

    def off(self):
        self.buzzing = False

    def __init__(self):
        self.buzzing = False

    def is_quiet(self):
        return not self.is_buzzing()

    def is_buzzing(self):
        return self.buzzing


class Display:
    RED = 'Red'
    GREEN = 'Green'
    BLUE = 'Blue'
    YELLOW = 'Yellow'
    OFF = 'Off'

    def __init__(self, color: str, current: int, limit: int):
        if color not in [self.RED, self.GREEN, self.BLUE, self.YELLOW, self.OFF]:
            raise ValueError('% is not a valid color' % color)
        self.color = color
        self.current = current
        self.limit = limit

    @classmethod
    def green(cls, current:int, limit: int):
        return Display(Display.GREEN, current, limit)

    @classmethod
    def red(cls, current: int, limit: int):
        return Display(Display.RED, current, limit)

    @classmethod
    def blue(cls, current: int, limit: int):
        return Display(Display.BLUE, current, limit)

    @classmethod
    def yellow(cls, current: int, limit: int):
        return Display(Display.YELLOW, current, limit)

    def __str__(self):
        return 'Display.%s(%d,%d)' % (self.color, self.current, self.limit)


class Led(ABC):
    @abstractmethod
    def set_display(self, color: Display):
        pass

    @abstractmethod
    def display(self) -> Display:
        pass

    def color(self) -> str:
        return self.display().color


class State(ABC):
    _substates = {}

    def __init__(self, clock: Clock, duration_seconds: int):
        self.clock = clock
        self.duration = duration_seconds * clock.TICKS_PER_SECOND
        self.ticks = 0

    @classmethod
    def add_state(cls, state: 'State'):
        cls._substates[state.name()] = state

    @classmethod
    def new_state(cls, name: str):
        next_state = cls._substates[name]
        next_state.reset()
        return next_state

    def due(self):
        return self.ticks > self.duration

    def reset(self):
        self.ticks = 0

    @abstractmethod
    def update(self, person_there: bool) -> ('State', bool, str):
        pass

    def tick(self):
        self.ticks += 1

    def time(self):
        return self.ticks * Clock.TICK_DURATION

    def name(self) -> str:
        return type(self).__name__


class Resting(State):
    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return self.new_state('Running'), False, Display.green(self.ticks, self.duration)
        if self.due():
            return self.new_state('Alarming'), True, Display.red(self.ticks, self.duration)
        else:
            return self, False, Display.yellow(self.ticks, self.duration)


class Running(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if not person_there:
            return self.new_state('Waiting'), False, Display.blue(0, 1)
        due = self.due()
        if due:
            return self.new_state('TimeForABreak'), True, Display.red(0, 1)
        else:
            return self, False, Display.green(self.ticks, self.duration)


class TimeForABreak(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        if not person_there:
            return self.new_state('Resting'), False, Display.yellow(0, 1)
        return self, True, Display.red(self.ticks, self.duration)


class Waiting(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool):
        if person_there:
            return self.new_state('Running'), False, Display.green(0, 1)
        else:
            return self, False, Display.blue(self.ticks, self.duration)


class Alarming(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return self.new_state('Running'), False, Display.green(0, 1)
        if self.due():
            return self.new_state('Waiting'), False, Display.blue(0, 1)
        return self, True, Display.red(self.ticks, self.duration)


class PomodoroTimer:
    WATCH_PERIOD = 5

    def __init__(self, clock: Clock, detector: PersonDetector, buzzer: Buzzer, led: Led,
                 schedule: Schedule, threshold: int = 400):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.detector = detector
        self.threshold = threshold
        self.presence = self.WATCH_PERIOD * [0]
        State.add_state(Waiting(clock, 1))
        State.add_state(Running(clock, schedule.pomodoro_duration))
        State.add_state(Resting(clock, schedule.break_duration))
        State.add_state(Alarming(clock, schedule.timeout))
        State.add_state(TimeForABreak(clock, schedule.grace_period))
        self.state = State.new_state('Waiting')
        self.led.set_display(Display.blue(0, 1))

    def is_person_present(self) -> bool:
        return self.detector.is_person_present()

    def run(self, trace=0):
        while self.clock.running():
            self.clock.tick()
            old_state = self.state
            (self.state, buzzing, color) = self.state.update(self.is_person_present())
            if buzzing:
                self.buzzer.on()
            else:
                self.buzzer.off()
            self.led.set_display(color)
            self.monitor(old_state, trace)

    def monitor(self, old_state, trace):
        if trace > 1:
            print(self.clock.ticks, self.state.name(), self.detector.is_person_present(), self.sound(), self.led.color())
        else:
            if trace == 1 and self.state != old_state:
                print('at %d %s -> %s' % (self.clock.ticks, old_state.name(), self.state.name()))

    def sound(self):
        return 'buzzing' if self.buzzer.is_buzzing() else 'quiet'



