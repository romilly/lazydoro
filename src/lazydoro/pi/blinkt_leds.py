from lazydoro.pi.lazy_oo import Led, Display
from blinkt import set_pixel, set_brightness, show, clear


class BlinktLEDs(Led):
    def __init__(self):
        self._display = Display.OFF
        set_brightness(0.1)
        clear()

    def display(self):
        return self._display

    def set_display(self, display: Display):
        self._display = display
        index = min(7, int((8 * display.current) / display.limit))
        clear()
        if display.color == Display.RED:
            set_pixel(index, 255, 0, 0)
        elif display.color == Display.YELLOW:
            set_pixel(index, 255, 255, 0)
        elif display.color == Display.BLUE:
            set_pixel(index, 0, 0, 255)
        elif display.color == Display.GREEN:
            set_pixel(index, 0, 255, 0)
        show()
        return