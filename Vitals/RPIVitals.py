from gpiozero import CPUTemperature, LoadAverage
from twilio.rest import Client
import os
import time
import firebase_admin
from firebase_admin import db
import geocoder
import datetime

class RaspberryPiVitals:
    
    def __init__(self):
        firebase_admin.initialize_app(firebase_admin.credentials.Certificate("/home/pi/Desktop/Raspberry_Pi_Programs/Vitals/rpi-vitals-firebase-adminsdk-o250d-c3ab522ee5.json"), {"databaseURL":"https://rpi-vitals-default-rtdb.firebaseio.com/"})
        self.retrieveSerialNumber()
        self.rpiVitalsDB = db.reference("/").child(self.rpiSerialNumber + "/")
        
        self.twilioRaspberryPiVitalsClient = Client("AC326232047B7E0241C7B3D7428E077E25", "d2e2baec5e6ebb380e8ce899fec906b4")
        self.raspberryPiVitalsCPU = CPUTemperature()
        self.raspberryPiVitalsLoad = LoadAverage()
    def retrieveSerialNumber(self):
        with open("/proc/cpuinfo", "r") as cpuInfoText:
            for oneLineCPUInfo in cpuInfoText:
                if "Serial" in oneLineCPUInfo:
                    # Removes the \n at the end too
                    self.rpiSerialNumber = str(oneLineCPUInfo.split(":")[-1]).replace("\n", "")
                    break
            cpuInfoText.close()
    def moniterCPUVitals(self):
        while True:
            try:
                self.rpiVitalsDB.child("CPU Temperature").set(self.raspberryPiVitalsCPU.temperature)
                self.rpiVitalsDB.child("CPU Load Average").set(self.raspberryPiVitalsLoad.load_average)
                
                currentRPILocationCoordinates = geocoder.ipinfo("me").latlng
                if currentRPILocationCoordinates != None:
                    self.rpiVitalsDB.child("Location (Lat)").set(currentRPILocationCoordinates[0])
                    self.rpiVitalsDB.child("Location (Long)").set(currentRPILocationCoordinates[-1])
                self.rpiVitalsDB.child("Date & Time").set(str(datetime.datetime.now()))
                
                if self.raspberryPiVitalsCPU.temperature >= 90:
                    self.twilioRaspberryPiVitalsClient.messages.create(to="+14084440130", from_="+15305573687", body="Your Raspberry Pi's CPU has risen to a severe temperature of " + str(self.raspberryPiVitalsCPU.temperature) + "º F. Rebooting now...")
                    os.system("sudo reboot")
                if self.raspberryPiVitalsLoad.load_average >= 0.90:
                    self.twilioRaspberryPiVitalsClient.messages.create(to="+14084440130", from_="+15305573687", body="Your Raspberry Pi's Load Average has risen to a severe load of " + str(self.raspberryPiVitalsLoad.load_average) + ". Rebooting now...")
                    os.system("sudo reboot")
            except:
                print("ERROR Collecting Vitals")
            time.sleep(1)

raspberryPiCPUVitalsMoniter = RaspberryPiVitals()
raspberryPiCPUVitalsMoniter.moniterCPUVitals()

                
            
