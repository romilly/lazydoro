from lazydoro.pi.lazy_oo import Led
from blinkt import set_pixel, set_brightness, show, clear


class BlinktLEDs(Led):
    def __init__(self):
        self.color = Led.OFF
        set_brightness(0.1)
        clear()

    def color(self):
        return self.color()

    def set_color(self, color):
        self.color = color
        clear()
        if color == Led.RED:
            set_pixel(0, 255, 0, 0)
        elif color == Led.YELLOW:
            set_pixel(0, 0, 255, 255)
        elif color == Led.BLUE:
            set_pixel(0, 0, 0, 255)
        elif color == Led.GREEN:
            set_pixel(0, 0, 255, 0)
        show()
        return