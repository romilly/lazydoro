from abc import ABC, abstractmethod


class Schedule():
    def __init__(self, pomodoro_duration: int, break_duration: int, grace_period: int, timeout: int):
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration
        self.grace_period = grace_period
        self.timeout = timeout

    def scale(self, units):
        if units != 1:
            self.pomodoro_duration *= units
            self.break_duration *= units
            self.grace_period *= units
            self.timeout *= units


class Clock(ABC):
    @abstractmethod
    def tick(self) -> bool:
        pass


class ToFSensor(ABC):
    @abstractmethod
    def is_someone_there(self):
        pass

    @abstractmethod
    def distance(self)-> int:
        pass


class Buzzer(ABC):
    @abstractmethod
    def buzz(self):
        pass


class Led(ABC):
    RED = 'Red'
    GREEN = 'Green'
    BLUE = 'Blue'
    YELLOW = 'Yellow'
    OFF = 'Off'
    @abstractmethod
    def set_color(self, color):
        pass

    @abstractmethod
    def color(self):
        pass


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


class Resting(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = schedule.break_duration

    def update(self, person_there: bool) -> ('State', bool, str):
        self.tick()
        if person_there:
            return Running(self.schedule), False, Led.GREEN
        if self.due():
            return Summoning(self.schedule), True, Led.RED
        else:
            return self, False, Led.YELLOW

    def name(self) -> str:
        return 'Resting'


class Running(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration =  schedule.pomodoro_duration

    def update(self, person_there) -> ('State', bool, str):
        self.tick()
        if not person_there:
            return Resting(self.schedule), False, Led.YELLOW
        due = self.due()
        if due:
            return self, True, Led.RED
        else:
            return self, False, Led.GREEN

    def name(self) -> str:
        return 'Running'


class Waiting(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = 0

    def update(self, person_there: bool):
        if person_there:
            return Running(self.schedule), False, Led.GREEN
        else:
            return self, False, Led.BLUE

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
            return Running(self.schedule), False, Led.GREEN
        if self.due():
            return Waiting(self.schedule), False, Led.BLUE
        return self, True, Led.YELLOW


class PomodoroTimer:
    def __init__(self, clock: Clock, tof_sensor: ToFSensor, buzzer: Buzzer, led: Led):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.tof_sensor = tof_sensor

    def run(self, schedule: Schedule, units=60, verbosity=0):
        schedule.scale(units)
        state = Waiting(schedule)
        self.led.set_color(Led.BLUE)
        while self.clock.tick():
            (state, buzzing, color) = state.update(self.person_there())
            if verbosity > 0:
                print(state.name())
            if buzzing:
                self.buzzer.buzz()
            self.led.set_color(color)
            if verbosity > 1:
                print(self.tof_sensor.distance())

    def person_there(self):
        return self.tof_sensor.is_someone_there()



