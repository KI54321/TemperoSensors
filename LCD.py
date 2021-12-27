import RPi.GPIO as MainGPIO
from RPLCD.gpio import CharLCD
import time

MainGPIO.setwarnings(False)
MainGPIO.setmode(MainGPIO.BCM)


showTextLCD = CharLCD(pin_rs=19, pin_rw=None, pin_e=16, pins_data=[21, 18, 23, 24], numbering_mode=MainGPIO.BCM, cols=16, rows=2, dotsize=8)

showTextLCD.clear()
showTextLCD.write_string("Whats Up")


time.sleep(100)
showTextLCD.close()
MainGPIO.cleanup()