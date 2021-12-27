import RPi.GPIO as gpio
import time
import os
import subprocess


def getCurrentTemprature():
    currentTempratureOuput, currentTempratureError = subprocess.Popen(["cat", "/sys/bus/w1/devices/28-8000002cc86d/w1_slave"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    if currentTempratureError == None: # If there is  no error running the command
        tempratureDataOutputSplit = str(currentTempratureOuput.split()[-1])
        
        finalTempratureNumber = ""
        for eachTempratureDataDigit in tempratureDataOutputSplit:
            if len(finalTempratureNumber) < 2 and (eachTempratureDataDigit).isnumeric():
                finalTempratureNumber += str(eachTempratureDataDigit)
                
        return str(round((float(finalTempratureNumber) * 1.8) + 32, 2)) # Converts to fahrenheit
        print("Got Current Temprature")
def displayNumber(numberDisplay):
    
    totalPlaces = (str(numberDisplay))
    totalPlacesArray = []
    totalDecimalPointsArray = []
    
    counter = 0
    for eachPlace in totalPlaces:
        if eachPlace != ".":
            totalPlacesArray.append((eachPlace))
        else:
            # This is because the decimal point added here belongs to the previous number in totalPlacesArray
            totalDecimalPointsArray.append(len(totalPlacesArray)-1)            
        counter += 1
            
    # Common cathode needs everything to be 1 except the ones I want one
    totalPinsOn = [1, 1, 1, 1]
    
    gpio.output(digitPins, totalPinsOn)
    
    for i in range(len(totalPlacesArray)):
        
        totalPinsOn = [1, 1, 1, 1]

        totalPinsOn[i] = 0
        gpio.output(digitPins, totalPinsOn)
        
        gpio.output(partsOfNumberPins, [0, 0, 0, 0, 0, 0, 0])
        gpio.output(decimalPointPin, 0)
        
      
        gpio.output(partsOfNumberPins, allPossibleNumbers[int(totalPlacesArray[i])])
        
        gpio.output(decimalPointPin, 0)

        for oneDecimalPointPlace in totalDecimalPointsArray:
            if oneDecimalPointPlace == i:
                gpio.output(decimalPointPin, 1)
            
        time.sleep(0.005)
        
def startDisplayTimer(motionDetectedDisplayPin):
    gpio.remove_event_detect(motionDetectionPin)
    startTime = time.time()
    lastKnownTemprature = getCurrentTemprature()

    while (time.time() - startTime) <= 300:
        
        displayNumber(lastKnownTemprature)
     
    gpio.add_event_detect(motionDetectionPin, gpio.RISING, callback=startDisplayTimer)
    


digitPins = [14, 15, 18, 23]
partsOfNumberPins = [24, 25, 8, 7, 1, 12, 16]
decimalPointPin = 20

motionDetectionPin = 21

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

# This is for motion detection
gpio.setup(motionDetectionPin, gpio.IN)
gpio.add_event_detect(motionDetectionPin, gpio.RISING, callback=startDisplayTimer)
#gpio.add_event_detect(motionDetectionPin, gpio.FALLING, callback=b)

# This sets-up all of the pins for outputting their individual LED's
for oneDigitPin in digitPins:
    gpio.setup(oneDigitPin, gpio.OUT)
for onePartNumberPin in partsOfNumberPins:
    gpio.setup(onePartNumberPin, gpio.OUT)
gpio.setup(decimalPointPin, gpio.OUT)
allPossibleNumbers = [[1, 1, 1, 1, 1, 1, 0],
                      [0, 1, 1, 0, 0, 0, 0],
                      [1, 1, 0, 1, 1, 0, 1],
                      [1, 1, 1, 1, 0, 0, 1],
                      [0, 1, 1, 0, 0, 1, 1],
                      [1, 0, 1, 1, 0, 1, 1],
                      [1, 0, 1, 1, 1, 1, 1],
                      [1, 1, 1, 0, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1],
                      [1, 1, 1, 1, 0, 1, 1]]

startDisplayTimer(21)

