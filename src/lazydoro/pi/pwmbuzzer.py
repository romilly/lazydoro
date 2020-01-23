from lazydoro.pi.lazy_oo import Buzzer
import RPi.GPIO as GPIO
from time import sleep


class PwmBuzzer(Buzzer):
    def __init__(self, pin=19):
        Buzzer.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.buzzer = GPIO.PWM(pin, 400)

    def on(self):
        Buzzer.on()
        self.buzzer.ChangeFrequency(400)
        self.buzzer.start(50)

    def off(self):
        Buzzer.off()
        self.buzzer.stop()