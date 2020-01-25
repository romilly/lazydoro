from lazydoro.pi.lazy_oo import ToFSensor, Buzzer, Led, Display


class MockTofSensor(ToFSensor):
    def __init__(self):
        self._distance = 8190

    def distance(self) -> int:
        return self._distance

    def person_comes(self):
        self._distance = 390

    def person_leaves(self):
        self._distance = 8190


class MockBuzzer(Buzzer):
    pass


class MockLed(Led):
    def __init__(self):
        self._display = Display(Display.OFF, 0, 1)

    def set_display(self, display):
        self._display = display

    def display(self):
        return self._display

