from lazydoro.pi.lazy_oo import Buzzer
import RPi.GPIO as GPIO
from time import sleep


class PwmBuzzer(Buzzer):
    def __init__(self, pin=6):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.buzzer = GPIO.PWM(pin, 400)

    def buzz(self, status):
        self.beep(1, 400)

    def beep(self, seconds, freq):
        self.buzzer.ChangeFrequency(freq)
        self.buzzer.start(50)
        sleep(seconds)
        self.buzzer.stop()

buzzer = PwmBuzzer()
while True:
    buzzer.beep(1,200)
    sleep(1)
