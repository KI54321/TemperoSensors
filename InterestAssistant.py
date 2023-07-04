import geocoder
import requests
from datetime import datetime

class InterestAssistant:

    def __init__(self):
        self.interestCategories = ["Weather", "Stocks"]
        self.currentPhrase = ""
        
    def weatherIntent(self):
        
        weatherLocationCoord = requests.get("https://api.ipdata.co?api-key=XXXX").json()
        weatherJSONRequest = requests.get("https://api.weatherbit.io/v2.0/forecast/minutely?lat=" + str(weatherLocationCoord["latitude"]) + "&lon=" + str(weatherLocationCoord["longitude"]) + "&key=XXXX&units=I").json()
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
