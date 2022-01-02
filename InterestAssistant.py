import geocoder
import requests
from datetime import datetime

class InterestAssistant:

    def __init__(self):
        self.interestCategories = ["Weather", "Stocks"]
        self.currentPhrase = ""
        
    def weatherIntent(self):
        
        weatherLocationCoord = requests.get("https://api.ipdata.co?api-key=7d44ff756d003d34bd935df9dc7b4e1d59cf75f77cc32448db68b1a3").json()
        weatherJSONRequest = requests.get("https://api.weatherbit.io/v2.0/forecast/minutely?lat=" + str(weatherLocationCoord["latitude"]) + "&lon=" + str(weatherLocationCoord["longitude"]) + "&key=d5d500e4803d47aeb904d9c7b6f617ab&units=I").json()
        weatherJSONData = (weatherJSONRequest["data"])
        
        didFindWeatherMatch = False
        
        for oneWeatherJSONDataDict in (weatherJSONData):
            
            actualLocalDateTime = datetime.strptime(oneWeatherJSONDataDict["timestamp_local"], "%Y-%m-%dT%H:%M:%S")
            currentDatetimeNow = datetime.now()
            if actualLocalDateTime > currentDatetimeNow:
                if oneWeatherJSONDataDict["precip"] >= 0:
                    didFindWeatherMatch = True
                    self.currentPhrase += "There is a " + str(oneWeatherJSONDataDict["precip"] * 100) + "% chance of rain starting in " + str(round((actualLocalDateTime - currentDatetimeNow).total_seconds()/60)) + " minutes." 
                    print(self.currentPhrase)
                
InterestAssistant().weatherIntent()
