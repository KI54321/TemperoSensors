from gpiozero import CPUTemperature, LoadAverage
from twilio.rest import Client
import os
import _thread
import time
import firebase_admin
from firebase_admin import db
import geocoder

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
    def moniterCPUVitals(self):
        while True:
            
            self.rpiVitalsDB.child("CPU Temperature").set(self.raspberryPiVitalsCPU.temperature)
            self.rpiVitalsDB.child("CPU Load Average").set(self.raspberryPiVitalsLoad.load_average)
            
            currentRPILocationCoordinates = geocoder.ipinfo("me").latlng
            self.rpiVitalsDB.child("Location (Lat)").set(currentRPILocationCoordinates[0])
            self.rpiVitalsDB.child("Location (Long)").set(currentRPILocationCoordinates[-1])
            
            if self.raspberryPiVitalsCPU.temperature >= 90:
                self.twilioRaspberryPiVitalsClient.messages.create(to="+14084440130", from_="+15305573687", body="Your Raspberry Pi's CPU has risen to a severe temperature of " + str(self.raspberryPiVitalsCPU.temperature) + "º F. Rebooting now...")
                os.system("sudo reboot")
            if self.raspberryPiVitalsLoad.load_average >= 0.90:
                self.twilioRaspberryPiVitalsClient.messages.create(to="+14084440130", from_="+15305573687", body="Your Raspberry Pi's Load Average has risen to a severe load of " + str(self.raspberryPiVitalsLoad.load_average) + ". Rebooting now...")
                os.system("sudo reboot")
            time.sleep(1)

raspberryPiCPUVitalsMoniter = RaspberryPiVitals()
_thread.start_new_thread(raspberryPiCPUVitalsMoniter.moniterCPUVitals, ())

                
            