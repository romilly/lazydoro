from lazydoro.pi.lazy_oo import Led
from blinkt import set_pixel, set_brightness, show, clear


class BlinktLEDs(Led):
    def __init__(self):
        self.color = Led.OFF
        set_brightness(0.1)

    def color(self):
        return self.color()

    def set_color(self, color):
        self.color = color
        if color == Led.RED:
            set_pixel(0, 255, 0, 0)
            return
        if color == Led.YELLOW:
            set_pixel(0, 0, 255, 255)
            return
        if color == Led.BLUE:
            set_pixel(0, 0, 0, 255)
            return
        if color == Led.GREEN:
            set_pixel(0, 0, 255, 0)
            return