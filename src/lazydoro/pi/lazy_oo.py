from abc import ABC, abstractmethod


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
        self._ticks = 0.0

    @abstractmethod
    def running(self):
        pass

    def tick(self) -> None:
        self._ticks += 1

    def ticks(self) -> float:
        return self._ticks


class ToFSensor(ABC):
    @abstractmethod
    def distance(self)-> int:
        pass


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

    def __init__(self, color: str, intensity: float = 0.0):
        if color not in [self.RED, self.GREEN, self.BLUE, self.YELLOW, self.OFF]:
            raise ValueError('% is not a valid color' % color)
        self.color = color
        self.intensity = intensity

    @classmethod
    def green(cls, intensity: float):
        return Display(Display.GREEN, intensity)

    @classmethod
    def red(cls, intensity: float):
        return Display(Display.RED, intensity)

    @classmethod
    def blue(cls, intensity: float):
        return Display(Display.BLUE, intensity)

    @classmethod
    def yellow(cls, intensity: float):
        return Display(Display.YELLOW, intensity)


class Led(ABC):
    @abstractmethod
    def set_display(self, color: Display):
        pass

    @abstractmethod
    def display(self) -> Display:
        pass

    def color(self) -> str:
        return self.display().color

    def intensity(self) -> float:
        return self.display().intensity


class State(ABC):
    _substates = {}

    def __init__(self, clock: Clock, duration: int):
        self.clock = clock
        self.duration = duration
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
        return self.time() > self.duration

    def reset(self):
        self.ticks = 0

    @abstractmethod
    def update(self, person_there: bool) -> ('State', bool, str):
        pass

    def tick(self):
        self.ticks += 1

    def stage(self):
        return (self.time()) / self.duration

    def time(self):
        return self.ticks * Clock.TICK_DURATION

    def name(self) -> str:
        return type(self).__name__


class Resting(State):
    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return self.new_state('Running'), False, Display.green(self.stage())
        if self.due():
            return self.new_state('Alarming'), True, Display.red(self.stage())
        else:
            return self, False, Display.yellow(self.stage())


class Running(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if not person_there:
            return self.new_state('Waiting'), False, Display.blue(0)
        due = self.due()
        if due:
            return self.new_state('TimeForABreak'), True, Display.red(0)
        else:
            return self, False, Display.green(self.stage())


class TimeForABreak(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        if not person_there:
            return self.new_state('Resting'), False, Display.yellow(0)
        return self, True, Display.red(self.stage())


class Waiting(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool):
        if person_there:
            return self.new_state('Running'), False, Display.green(0)
        else:
            return self, False, Display.blue(self.stage())


class Alarming(State):
    def __init__(self, clock, duration):
        State.__init__(self, clock, duration)

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return self.new_state('Running'), False, Display.green(0)
        if self.due():
            return self.new_state('Waiting'), False, Display.blue(0)
        return self, True, Display.red(self.stage())


class PomodoroTimer:
    WATCH_PERIOD = 5

    def __init__(self, clock: Clock, tof_sensor: ToFSensor, buzzer: Buzzer, led: Led,
                 schedule: Schedule, threshold: int = 400):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.tof_sensor = tof_sensor
        self.threshold = threshold
        self.presence = self.WATCH_PERIOD * [0]
        State.add_state(Waiting(clock, -1))
        State.add_state(Running(clock, schedule.pomodoro_duration))
        State.add_state(Resting(clock, schedule.break_duration))
        State.add_state(Alarming(clock, schedule.timeout))
        State.add_state(TimeForABreak(clock, schedule.grace_period))
        self.state = State.new_state('Waiting')

    def person_there(self):
        self.presence = self.presence[1:] + [1 if self.distance() < self.threshold else 0]
        count = sum(self.presence)
        return count >= 0.5 * self.WATCH_PERIOD

    def run(self, verbosity=0):
        self.led.set_display(Display.blue(0.0))
        while self.clock.running():
            self.clock.tick()
            old_state = self.state
            (self.state, buzzing, color) = self.state.update(self.person_there())
            if buzzing:
                self.buzzer.on()
            else:
                self.buzzer.off()
            self.led.set_display(color)
            self.monitor(old_state, verbosity)

    def monitor(self, old_state, verbosity):
        if verbosity > 1:
            print(self.clock.ticks(), self.state.name(), self.tof_sensor.distance(), self.sound(), self.led.color())
        else:
            if verbosity == 1 and self.state != old_state:
                print('at %d %s -> %s' % (self.clock.ticks(), old_state.name(), self.state.name()))

    def sound(self):
        return 'buzzing' if self.buzzer.is_buzzing() else 'quiet'

    def distance(self):
        return self.tof_sensor.distance()



