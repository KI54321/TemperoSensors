import RPi.GPIO as gpio
import time
import os
import subprocess

class TemperoSensorsDisplay:
    
    def __init__(self):
        
        self.digitPins = [14, 15, 18, 23]
        self.partsOfNumberPins = [24, 25, 8, 7, 1, 12, 16]
        self.decimalPointPin = 20

        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)

        # This sets-up all of the pins for outputting their individual LED's
        for oneDigitPin in self.digitPins:
            gpio.setup(oneDigitPin, gpio.OUT)
        for onePartNumberPin in self.partsOfNumberPins:
            gpio.setup(onePartNumberPin, gpio.OUT)
        gpio.setup(self.decimalPointPin, gpio.OUT)
        
        # This maps all of the possible numbers that cna be displayed on the LED
        self.allPossibleNumbers = [[1, 1, 1, 1, 1, 1, 0],
                              [0, 1, 1, 0, 0, 0, 0],
                              [1, 1, 0, 1, 1, 0, 1],
                              [1, 1, 1, 1, 0, 0, 1],
                              [0, 1, 1, 0, 0, 1, 1],
                              [1, 0, 1, 1, 0, 1, 1],
                              [1, 0, 1, 1, 1, 1, 1],
                              [1, 1, 1, 0, 0, 0, 0],
                              [1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 0, 1, 1]]

    def displayTemperoTemprature(self, numberDisplay):
        
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
        
        gpio.output(self.digitPins, totalPinsOn)
        
        for i in range(len(totalPlacesArray)):
            
            totalPinsOn = [1, 1, 1, 1]

            totalPinsOn[i] = 0
            gpio.output(self.digitPins, totalPinsOn)
            
            gpio.output(self.partsOfNumberPins, [0, 0, 0, 0, 0, 0, 0])
            gpio.output(self.decimalPointPin, 0)
            
          
            gpio.output(self.partsOfNumberPins, self.allPossibleNumbers[int(totalPlacesArray[i])])
            
            gpio.output(self.decimalPointPin, 0)

            for oneDecimalPointPlace in totalDecimalPointsArray:
                if oneDecimalPointPlace == i:
                    gpio.output(self.decimalPointPin, 1)
                
            time.sleep(0.005)

    