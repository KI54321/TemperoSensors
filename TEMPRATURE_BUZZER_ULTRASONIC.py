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

twilioTempClient = Client("AC326232047B7E0241C7B3D7428E077E25", "d2e2baec5e6ebb380e8ce899fec906b4")
# temperatureFirebase = firebase.FirebaseApplication('https://raspberry-info-tracker-default-rtdb.firebaseio.com', None)
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
            twilioTempClient.messages.create(to="+14082187763", from_="+15305573687", body="Alert: Temprature Drop to " + str(currentTemp) + "º F")
            
        if int(gestureDistance) <= 10:
            os.system("espeak \"Danger Annika Iyengar Back Away You Are Within " + str(gestureDistance) + " inches that'S Too Close and the temprature is " + str(currentTemp) + " degrees Fahrenheit\" -s 125")
            tempratureBuzzer.on()
            time.sleep(2)
            tempratureBuzzer.off()
            
        time.sleep(1)
    except:
        print("Failure Getting Data")
# def sendCurrentDataFirebase():
    