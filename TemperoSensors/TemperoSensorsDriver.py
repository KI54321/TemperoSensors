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
        firebase_admin.initialize_app(firebase_admin.credentials.Certificate("/temperosensors-firebase-adminsdk-49k00-4fdc22e590.json"), {"databaseURL":"https://temperosensors-default-rtdb.firebaseio.com/"})


        # FirebaseDatabase Reference
        self.currentDBReference = db.reference("/")
        self.currentDBReference = self.currentDBReference.child(str(sensorID) + "/")
        
        self.getAllTemperoSensorDatabaseData()
        self.getCurrentTemprature()
           
        self.temperoRefreshToken = "1//06h5wjwU7e4LHCgYIARAAGAYSNwF-L9Irtp-otUvdGwqkeabey3z20mtiSla5rpyI60nj1q93DJ61Vzs6ZRu683qYOtfC7YLtlYg"
        self.temperoThermostatDeviceID = "AVPHwEvPDSwQV6XAQLjrO9QQIxurpT5Vs7ns0ZkWonqnN6afdhDUklji7wXP45t9HOuQxRE8Qkee5UxByfPNkJ0CNzqpXg"
        self.temperoGCPProjectID = "4acc3863-dacf-446b-9b56-a339a4ea8f45"
        self.temperoCurrentThermostatMode = None
        self.temperoTempratureDisplay = TemperoSensorsDisplay.TemperoSensorsDisplay()
        
        self.getCurrentNestThermostatInformation()
        
        # Getting all of the set-up data
        self.sensorID = sensorID
        
        
    def getAllTemperoSensorDatabaseData(self):
        dictionarySensorDataValues = self.currentDBReference.get()

        for oneSensorDataName in dictionarySensorDataValues:
            if oneSensorDataName == "Location":
                self.location = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Name":
                self.name = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "New_Temprature":
                self.new_tempero_temprature = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Sensor_Value":
                self.sensor_value = dictionarySensorDataValues[oneSensorDataName]
            elif oneSensorDataName == "Sensor_Enabled":
                self.sensor_enabled = bool(dictionarySensorDataValues[oneSensorDataName])
            elif oneSensorDataName == "Sensor_Value_Date":
                self.sensor_value_date = dictionarySensorDataValues[oneSensorDataName]
    
    def updateCurrentData(self):
        while True:
            try:
                self.getAllTemperoSensorDatabaseData()
                self.getCurrentTemprature()
                self.getCurrentNestThermostatInformation()
                
                
            except:
                print("ERROR Update Current Data")
                
            time.sleep(10)
            
            
    def startTemperoExamination(self):

        while True:
            try:
                if self.sensor_enabled:
                    
                
                    # This makes sure the time is within the schedule
                    print("Checking Moniter Data")
                    
                    if self.new_tempero_temprature > self.sensor_value:
                        self.adjustNestThermostat(self.temperoCurrentThermostatTemprature + (abs(self.new_tempero_temprature - self.sensor_value) / 2))
                    elif self.new_tempero_temprature < self.sensor_value:
                        self.adjustNestThermostat(self.temperoCurrentThermostatTemprature - (abs(self.new_tempero_temprature - self.sensor_value) / 2))
                    else:
                        print("Temperatures are the exact same")
                    
                    # Every 5 minutes check the current nest temprature
                    time.sleep(300)
                else:
                    time.sleep(1)
            except:
                print("ERROR Monitering Data")
            
    def getNewAccessCodeNestThermostat(self):
        nestThermostatAccessCodeRequest = requests.post("https://www.googleapis.com/oauth2/v4/token?client_id=1069978862635-epurbtin9o4s53i45gftds4tq88e0jpf.apps.googleusercontent.com&client_secret=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&refresh_token=" + self.temperoRefreshToken + "&grant_type=refresh_token")
        return str(nestThermostatAccessCodeRequest.json()["access_token"])
    def getCurrentNestThermostatInformation(self):

        nestThermostatRequestInformationRequest = requests.get("https://smartdevicemanagement.googleapis.com/v1/enterprises/" + self.temperoGCPProjectID + "/devices/" + self.temperoThermostatDeviceID, headers={"Content-Type":"application/json", "Authorization":("Bearer " + self.getNewAccessCodeNestThermostat())})
        nestThermostatInformationJSON = nestThermostatRequestInformationRequest.json()
        
        self.temperoCurrentThermostatMode = nestThermostatInformationJSON["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
        self.temperoCurrentThermostatTemprature = (nestThermostatInformationJSON["traits"]["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"] * (9/5)) + 32
        
        temperoNestThermostatDBReference = self.currentDBReference.parent.child("Nest_Thermostat")
        temperoNestThermostatDBReference.child("Temperature").set((round((nestThermostatInformationJSON["traits"]["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"] * (9/5)) + 32, 2)))
        temperoNestThermostatDBReference.child("Mode").set(nestThermostatInformationJSON["traits"]["sdm.devices.traits.ThermostatMode"]["mode"])
        temperoNestThermostatDBReference.child("Data_Date").set(datetime.now(pytz.timezone("US/Pacific")).strftime("%c"))
        
    def adjustNestThermostat(self, newTemprature):
       
        settingNewThermostatTempratureJSONData = {
                "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
                "params": {
                    self.temperoCurrentThermostatMode.lower() + "Celsius": (newTemprature - 32) * (5/9)
                }
            }

        temperoSetTempratureResponse = requests.post("https://smartdevicemanagement.googleapis.com/v1/enterprises/" + self.temperoGCPProjectID + "/devices/" + self.temperoThermostatDeviceID + ":executeCommand", json=settingNewThermostatTempratureJSONData, headers={"Content-Type":"application/json", "Authorization":("Bearer " + self.getNewAccessCodeNestThermostat())})
        
        if len(temperoSetTempratureResponse.json()) == 0:
           print("Adjusted Thermostat Successfully for " + str(newTemprature) + " in " + self.temperoCurrentThermostatMode + " mode")
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
        else:
            print(currentTempratureError)        

        self.sensor_value_date = datetime.now(pytz.timezone("US/Pacific")).strftime("%c")
        self.currentDBReference.child("Sensor_Value_Date").set(self.sensor_value_date)

    def displayTemperoSensor(self):
        while True:
            try:
                self.temperoTempratureDisplay.displayTemperoTemprature(self.sensor_value)
            except:
                print("ERROR Display")
temperoMainDriverObject = TemperoSensorsDriver("7645b9f9")

_thread.start_new_thread(temperoMainDriverObject.updateCurrentData, ())
_thread.start_new_thread(temperoMainDriverObject.displayTemperoSensor, ())
_thread.start_new_thread(temperoMainDriverObject.startTemperoExamination, ())


