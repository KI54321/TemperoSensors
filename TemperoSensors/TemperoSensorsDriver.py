import random
import subprocess
import firebase_admin
from firebase_admin import db
from datetime import datetime
import time
import pytz
import RPi.GPIO as gpio
import requests
import _thread

import TemperoSensorsDisplay

class TemperoSensorsDriver:

    def __init__(self, sensorID):
        # Authenticates the TemperoSensors Firebase Database Application
        firebase_admin.initialize_app(firebase_admin.credentials.Certificate("/home/pi/Desktop/Raspberry_Pi_Programs/TemperoSensors/temperosensors-firebase-adminsdk-49k00-4fdc22e590.json"), {"databaseURL":"https://temperosensors-default-rtdb.firebaseio.com/"})

        # FirebaseDatabase Reference
        self.currentDBReference = db.reference("/")
        self.currentDBReference = self.currentDBReference.child(str(sensorID) + "/")

        # Getting all of the set-up data
        self.sensorID = sensorID

        self.getAllTemperoSensorDatabaseData()
                
        self.temperoRefreshToken = "1//06h5wjwU7e4LHCgYIARAAGAYSNwF-L9Irtp-otUvdGwqkeabey3z20mtiSla5rpyI60nj1q93DJ61Vzs6ZRu683qYOtfC7YLtlYg"
        self.temperoThermostatDeviceID = "AVPHwEvPDSwQV6XAQLjrO9QQIxurpT5Vs7ns0ZkWonqnN6afdhDUklji7wXP45t9HOuQxRE8Qkee5UxByfPNkJ0CNzqpXg"
        self.temperoGCPProjectID = "4acc3863-dacf-446b-9b56-a339a4ea8f45"
        self.temperoCurrentThermostatMode = None
        self.temperoTempratureDisplay = TemperoSensorsDisplay.TemperoSensorsDisplay()
        
    def getAllTemperoSensorDatabaseData(self):
        dictionarySensorDataValues = self.currentDBReference.get()

        for oneSensorDataName in dictionarySensorDataValues:
            if oneSensorDataName == "End_Time":
                self.end_time = dictionarySensorDataValues[oneSensorDataName]
                if self.end_time == 0:
                    self.end_time = 24
            elif oneSensorDataName == "Location":
                self.location = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Lower_Bound":
                self.lower_bound = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Name":
                self.name = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Start_Time":
                self.start_time = dictionarySensorDataValues[oneSensorDataName]
                
                if self.start_time == 0:
                    self.start_time = 24
            elif oneSensorDataName == "Upper_Bound":
                self.upper_bound = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Sensor_Value":
                self.sensor_value = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Sensor_Value_Date":
                self.sensor_value_date = dictionarySensorDataValues[oneSensorDataName]
    def updateCurrentTemprature(self):
        while True:
            self.getCurrentTemprature()
            time.sleep(30)
            
    def startTemperoExamination(self):

        while True:
            self.getAllTemperoSensorDatabaseData()
            
            currentPacific24HRTime = int(datetime.now(pytz.timezone("US/Pacific")).strftime("%H"))
            
            # This makes sure the time is within the schedule
            if self.start_time <= currentPacific24HRTime and currentPacific24HRTime < self.end_time:
                print("Checking Moniter Data")
                self.moniterTemperoTemprature()
            # Every 10 minutes check the current nest temprature
            time.sleep(600)

    def moniterTemperoTemprature(self):
        print("Monitering")
        if self.lower_bound >= self.sensor_value:
            # Sets current temprature to lower_bound and adds 10 degrees
            self.adjustNestThermostat(self.lower_bound+10)
        elif self.upper_bound <= self.sensor_value:
            # Sets current temprature to upper_bound and decreases 10 degrees
            self.adjustNestThermostat(self.upper_bound-10)


    def getNewAccessCodeNestThermostat(self):
        nestThermostatAccessCodeRequest = requests.post("https://www.googleapis.com/oauth2/v4/token?client_id=1069978862635-epurbtin9o4s53i45gftds4tq88e0jpf.apps.googleusercontent.com&client_secret=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&refresh_token=" + self.temperoRefreshToken + "&grant_type=refresh_token")
        return str(nestThermostatAccessCodeRequest.json()["access_token"])
    def getCurrentNestThermostatInformation(self):

        nestThermostatRequestInformationRequest = requests.get("https://smartdevicemanagement.googleapis.com/v1/enterprises/" + self.temperoGCPProjectID + "/devices/" + self.temperoThermostatDeviceID, headers={"Content-Type":"application/json", "Authorization":("Bearer " + self.getNewAccessCodeNestThermostat())})
        nestThermostatInformationJSON = nestThermostatRequestInformationRequest.json()

        self.temperoCurrentThermostatMode = nestThermostatInformationJSON["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]

    def adjustNestThermostat(self, newTemprature):

        self.getCurrentNestThermostatInformation()
       
        settingNewThermostatTempratureJSONData = {
                "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
                "params": {
                    self.temperoCurrentThermostatMode.lower() + "Celsius": (newTemprature - 32) * (5/9)
                }
            }

        temperoSetTempratureResponse = requests.post("https://smartdevicemanagement.googleapis.com/v1/enterprises/" + self.temperoGCPProjectID + "/devices/" + self.temperoThermostatDeviceID + ":executeCommand", json=settingNewThermostatTempratureJSONData, headers={"Content-Type":"application/json", "Authorization":("Bearer " + self.getNewAccessCodeNestThermostat())})
        
        if len(temperoSetTempratureResponse.json()) == 0:
           print("Adjusted Thermostat Successfully for " + self.temperoCurrentThermostatMode)
        else:
            print("ERROR Adjusting Nest Thermostat")
            print(temperoSetTempratureResponse.json())

    def getCurrentTemprature(self):
        # Test Temprature
        currentTempratureOuput, currentTempratureError = subprocess.Popen(["cat", "/sys/bus/w1/devices/28-8000002cc86d/w1_slave"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if currentTempratureError == None: # If there is no error running the command
            tempratureDataOutputSplit = str(currentTempratureOuput.split()[-1])
            
            finalTempratureNumber = ""
            for eachTempratureDataDigit in tempratureDataOutputSplit:
                if len(finalTempratureNumber) < 5 and (eachTempratureDataDigit).isnumeric():
                    finalTempratureNumber += str(eachTempratureDataDigit)
            
            self.sensor_value = (round(((float(finalTempratureNumber) / 1000.0) * 1.8) + 32, 2)) # Converts to fahrenheit
            self.currentDBReference.child("Sensor_Value").set(self.sensor_value)
            print(self.sensor_value)
        else:
            print(currentTempratureError)
        print("Got Current Temprature")
        

        self.sensor_value_date = datetime.now(pytz.timezone("US/Pacific")).strftime("%c")
        self.currentDBReference.child("Sensor_Value_Date").set(self.sensor_value_date)

    def displayTemperoSensor(self):
       while True:
           
           self.temperoTempratureDisplay.displayTemperoTemprature(self.sensor_value)

temperoMainDriverObject = TemperoSensorsDriver("7645b9f9")

_thread.start_new_thread(temperoMainDriverObject.startTemperoExamination, ())
_thread.start_new_thread(temperoMainDriverObject.displayTemperoSensor, ())
_thread.start_new_thread(temperoMainDriverObject.updateCurrentTemprature, ())
