import board
import busio as io
import time
i2c = io.I2C(board.SCL, board.SDA)
import adafruit_ssd1306
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
while True:
    oled.text('MicroPython has',0,0)
    oled.text('Wings!', 0, 10)
    oled.show()
    time.sleep(2)
    for i in range (128):
        oled.scroll(-1,0)
        oled.show()