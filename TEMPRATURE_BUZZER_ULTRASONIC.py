from gpiozero import *
import RPi.GPIO as MainGPIO
import time
import piplates.TINKERplate as tinkerKit
from twilio.rest import Client
import os
from gpiozero.pins.pigpio import PiGPIOFactory
from RPLCD.pigpio import CharLCD
import pigpio
# import request
# from firebase import firebase

twilioTempClient = Client("XXXX", "XXXX")
lowestTemprature = 65

# time.sleep(1)
tempratureBuzzer = Buzzer(3)
tempratureBuzzer.off()

tinkerKit.setMODE(0, 1, "temp")
tinkerKit.setMODE(0, 78, "range")

messageTimeBegin = time.time()

while True:
    try:
        currentTemp = tinkerKit.getTEMP(0, 1, "f")
        gestureDistance = tinkerKit.getRANGEfast(0, 78)
        if currentTemp <= lowestTemprature and (time.time() - messageTimeBegin) >= 7200:
            
            messageTimeBegin = time.time()
            twilioTempClient.messages.create(to="+XXXX", from_="+XXXX", body="Alert: Temprature Drop to " + str(currentTemp) + "º F")
            
        if int(gestureDistance) <= 10:
            tempratureBuzzer.on()
            time.sleep(2)
            tempratureBuzzer.off()
            
        time.sleep(1)
    except:
        print("Failure Getting Data")
# def sendCurrentDataFirebase():
    
