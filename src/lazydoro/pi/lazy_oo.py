from abc import ABC, abstractmethod


def average(values):
    return sum(values)/len(values)


class Schedule():
    SCALE = 10
    def __init__(self, pomodoro_duration: int, break_duration: int, grace_period: int, timeout: int):
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration
        self.grace_period = grace_period
        self.timeout = timeout
        self.scale(self.SCALE)

    def scale(self, units):
        if units != 1:
            self.pomodoro_duration *= units
            self.break_duration *= units
            self.grace_period *= units
            self.timeout *= units


class Clock(ABC):
    INCREMENT = 1.0 / Schedule.SCALE

    def __init__(self):
        self._time = 0.0

    def advance(self):
        self._time += self.INCREMENT

    @abstractmethod
    def tick(self) -> bool:
        pass

    def time(self) -> float:
        return self._time


class ToFSensor(ABC):
    @abstractmethod
    def distance(self)-> int:
        pass


class Buzzer(ABC):
    @abstractmethod
    def buzz(self):
        pass


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
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.ticks = 0
        self.duration = 0

    def due(self):
        return self.ticks > self.duration

    @abstractmethod
    def update(self, person_there: bool) -> ('State', bool, str):
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def tick(self):
        self.ticks += 1

    def stage(self):
        return float(self.ticks) / self.duration


class Resting(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = schedule.break_duration

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return Running(self.schedule), False, Display.green(self.stage())
        if self.due():
            return Summoning(self.schedule), True, Display.red(self.stage())
        else:
            return self, False, Display.yellow(self.stage())

    def name(self) -> str:
        return 'Resting'


class Running(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = schedule.pomodoro_duration

    def update(self, person_there) -> ('State', bool, str):
        self.tick()
        if not person_there:
            return Resting(self.schedule), False, Display.yellow(self.stage())
        due = self.due()
        if due:
            return self, True, Display.red(self.stage())
        else:
            return self, False, Display.green(self.stage())

    def name(self) -> str:
        return 'Running'


class Waiting(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = 1

    def update(self, person_there: bool):
        if person_there:
            return Running(self.schedule), False, Display.green(self.stage())
        else:
            return self, False, Display.blue(self.stage())

    def name(self) -> str:
        return 'Waiting'


class Summoning(State):
    def name(self) -> str:
        return 'Summoning'

    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = schedule.timeout

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return Running(self.schedule), False, Display.green(self.stage())
        if self.due():
            return Waiting(self.schedule), False, Display.blue(self.stage())
        return self, True, Display.yellow(self.stage())


class PomodoroTimer:
    WATCH_PERIOD = 5

    def __init__(self, clock: Clock, tof_sensor: ToFSensor, buzzer: Buzzer, led: Led,
                 threshold: int = 400):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.tof_sensor = tof_sensor
        self.threshold = threshold
        self.presence = self.WATCH_PERIOD * [0]

    def person_there(self):
        self.presence = self.presence[1:] + [1 if self.distance() < self.threshold else 0]
        count = sum(self.presence)
        return count >= 0.5 * self.WATCH_PERIOD

    def run(self, schedule: Schedule, units=60, verbosity=0):
        schedule.scale(units)
        state = Waiting(schedule)
        self.led.set_display(Display.blue(0.0))
        while self.clock.tick():
            old_state = state
            (state, buzzing, color) = state.update(self.person_there())
            self.monitor(old_state, state, verbosity)
            if buzzing:
                self.buzzer.buzz()
            self.led.set_display(color)
            self.monitor_distance(verbosity)

    def monitor_distance(self, verbosity):
        if verbosity > 1:
            print(self.tof_sensor.distance())

    def monitor(self, old_state, state, verbosity):
        if verbosity > 1:
            print(state.name())
        else:
            if verbosity > 0 and state != old_state:
                print('at %d %s -> %s' % (self.clock.time(), old_state.name(), state.name()))

    def distance(self):
        return self.tof_sensor.distance()



