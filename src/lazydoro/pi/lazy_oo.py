from abc import ABC, abstractmethod


class Schedule():
    def __init__(self, pomodoro_duration: int, break_duration: int, grace_period: int, timeout: int):
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration
        self.grace_period = grace_period
        self.timeout = timeout


class Clock(ABC):
    @abstractmethod
    def tick(self) -> bool:
        pass


class ToFSensor(ABC):
    @abstractmethod
    def is_someone_there(self):
        pass


class Buzzer(ABC):
    @abstractmethod
    def buzz(self, status):
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
        return self.ticks < self.duration

    @abstractmethod
    def update(self, person_there: bool) -> ('State', bool, str):
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
            return Summoning(self.schedule), True, Led.YELLOW
        return self, False, Led.YELLOW


class Running(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration =  schedule.pomodoro_duration

    def update(self, person_there) -> ('State', bool, str):
        self.tick()
        if not person_there:
            return Resting(self.schedule), False, Led.YELLOW
        if self.due():
            return self, False, Led.GREEN
        else:
            return self, True, Led.RED


class Waiting(State):
    def __init__(self, schedule):
        State.__init__(self, schedule)
        self.duration = 0

    def update(self, person_there: bool):
        if person_there:
            return Running(self.schedule), False, Led.GREEN
        else:
            return self, False, Led.BLUE


class Summoning(State):
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
    def __init__(self, clock: Clock, tof_sensor: ToFSensor, buzzer: Buzzer, led):
        self.led = led
        self.buzzer = buzzer
        self.clock = clock
        self.tof_sensor = tof_sensor

    def run(self, schedule: Schedule):
        state = Waiting(schedule)
        self.led.set_color(Led.BLUE)
        while self.clock.tick():
            (state, buzzing, color) = state.update(self.person_there())
            self.buzzer.buzz(buzzing)
            self.led.set_color(color)

    def person_there(self):
        return self.tof_sensor.is_someone_there()


