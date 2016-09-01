#! python3
# Name: Brooks Becton
# Date: 6/20/2016
# Purpose: Takes in a location and returns the weather for that place

from datetime import datetime
import json
import requests
import shelve
import os.path
import re
import sys
import webbrowser


class PyWeather:

    daysInForecast = 7
    keyFile = 'key.txt'
    settings = {}
    settingsFile = 'settings.db'
    settingsDefaultShelve = 'defaultSettings.db'
    weather = {}
    queryLocation = ''
    queryMode = ''

    def __init__(self):
        if self.defaultShelveMade() is not True:
            self.initSettingsShelve()

        self.key = self.getApiKey()

        # Gathering Sys Arugments
        if len(sys.argv) <= 1:
            self.setDefaultSettings()
        elif len(sys.argv) <= 4:
            self.setCustomSettings()
        else:
            self.printUsage()
            exit()

        self.weather = self.getWeather(self.queryLocation, self.queryMode)

    def defaultShelveMade(self):
        return os.path.isfile(self.settingsDefaultShelve + '.dir')

    def getWeather(self, targetLocation, queryMode):

        # Building URL based
        if str(queryMode) == 'current':
            url = 'http://api.openweathermap.org/data/2.5/weather'
            url += '?q='
            url += targetLocation
            url += '&appid='
            url += self.key
            url += '&units=imperial'
        elif str(queryMode) == 'forecast':
            url = 'http://api.openweathermap.org/data/2.5/forecast/daily'
            url += '?q='
            url += targetLocation
            url += '&appid='
            url += self.key
            url += '&units=imperial'
        else:
            print(str(queryMode) + ' is not a valid query mode.')
            exit()

        # Querying Url for Json
        print("Loading Weather data...", end="")
        response = requests.get(url)
        print("Done")
        response.raise_for_status()
        return json.loads(response.text)

    def getApiKey(self):
        # Reading API Key
        try:
            f = open(self.keyFile, 'r')
            k = f.read()
            f.close()
        except:
            print('Error Opening' + str(self.keyFile))
            k = self.promptInitialKey()
        return k

    def hasNumber(inputStr):
        return bool(re.search(r'\d', inputStr))

    def initSettingsShelve(self):
        print('Initializing the Shelve...')
        defaultDaysInForcast = 7
        defaultQueryLocation = 'Martin, TN'
        defaultQueryMode = {'value': 'forecast',
                            'options': ['forecast', 'current']}

        f = shelve.open(self.settingsDefaultShelve, 'n')
        f['daysInForecast'] = defaultDaysInForcast
        f['queryMode'] = defaultQueryMode
        f['location'] = defaultQueryLocation
        f.close()

    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def printUsage(self):
        print('\nUsage: ')
        print('\nSpecified Location:')
        print('python pyWeather.py (location) (mode) (days in forecast)')
        print('\nDefault Location:')
        print('python pyWeather.py')
        sys.exit()

    def printCurrentWeather(self):
        daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        daysOfWeek += ['Saturday', 'Sunday']
        utcTimeStamp = self.weather['dt']
        date = datetime.utcfromtimestamp(utcTimeStamp).date()
        dayOfWeek = daysOfWeek[date.weekday()]

        currentTemp = str(self.weather['main']['temp'])
        tempHigh = str(self.weather['main']['temp_max'])
        tempLow = str(self.weather['main']['temp_min'])

        weatherDesc = str(self.weather['weather'][0]['description'])

        print('\nLocation: ' + str(self.queryLocation))
        print('Day: ' + str(dayOfWeek))

        print('\nTemperatures')
        print('High: ' + tempHigh)
        print('Low: ' + tempLow)
        print('Current: ' + currentTemp)

        print('\nSky: ')
        print(weatherDesc)

    def printCurrentSettings(self):
        print(self.queryLocation)
        print(self.queryMode)
        print(self.daysInForecast)

    def printWeatherForecast(self):
        daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        daysOfWeek += ['Saturday', 'Sunday']

        print('\nLocation: ' + str(self.queryLocation))

        print('\n\n' + str(self.weather) + '\n\n')

        for i in range(0, self.daysInForecast):
            utcTimeStamp = self.weather['list'][i]['dt']
            date = datetime.utcfromtimestamp(utcTimeStamp).date()
            dayOfWeek = daysOfWeek[date.weekday()]

            dayTemp = str(self.weather['list'][i]['temp']['day'])
            degreeSymbol = chr(176)
            tempHigh = str(self.weather['list'][i]['temp']['max'])
            tempLow = str(self.weather['list'][i]['temp']['min'])

            skyDesc = self.weather['list'][i]['weather'][0]['main']

            print('\nDate:')
            print(str(dayOfWeek) + ' ' + str(date))

            print('\nTemperatures:')
            print('High: ' + tempHigh + degreeSymbol)
            print('Low: ' + tempLow + degreeSymbol)
            print('Day: ' + dayTemp + degreeSymbol)

            print('\nSky: ')
            print(skyDesc)

    def promptForNewDefaultSettings(self):
        userInput = ''
        settingsOptions = []
        settingsToChange = []

        f = shelve.open(self.settingsDefaultShelve, writeback=True)
        for option in f:
            settingsOptions.append(option)

        prompt = 'Enter the number(s) to the setting you want to change\n'

        print(prompt)

        for i in range(0, len(settingsOptions)):
            print(str(i) + ') ' + settingsOptions[i])

        userInput = input()

        # TODO: Refactor this
        if userInput:
            settingsToChange = userInput.split()
            for i in settingsToChange:
                i = int(i)

                if settingsOptions[i] == 'daysInForecast':
                    prompt = 'Enter the number of days to forecast\n'
                    prompt += 'There is a 16 day limit'

                    newDaysInForecast = input(prompt)
                    if self.is_number(newDaysInForecast):
                        newDaysInForecast = int(newDaysInForecast)
                        f['daysInForecast'] = newDaysInForecast
                    else:
                        print('Please enter a valid number')

                if settingsOptions[i] == 'location':
                    locationMessage = "Enter a zip, an OpenWeater API ID,"
                    locationMessage += "or a (city,state)"

                    newLocation = input(locationMessage)
                    f['location'] = newLocation

                if settingsOptions[i] == 'queryMode':
                    possibleOptions = f[settingsOptions[i]]['options']

                    print('Enter a Query Mode\nAvailible Options: ')
                    for option in possibleOptions:
                        print(option)

                    # Making sure response is valid
                    newQueryMode = ''
                    while (newQueryMode not in possibleOptions and
                           str(newQueryMode.lower()) != "cancel"):
                        newQueryMode = input()
                        if newQueryMode not in possibleOptions:
                            errorMessage = 'ERROR: Please Enter a valid option'
                            errorMessage += '\n or type \'cancel\''
                            print(errorMessage)
                            for option in possibleOptions:
                                print(option)
                            print('\n')

                    print('New Query Mode: ' + str(newQueryMode))
                    f['queryMode']['value'] = newQueryMode
                    print('Here: ' + str(f['queryMode']['value']))

        f.close()

    def promptInitialKey(self):
        apiKeyUrl = 'http://openweathermap.org/appid'

        keyMessage = 'Please enter your Open Weather API key\n'
        keyMessage += 'If you don\'t have a key, hit ENTER '
        userInput = input(keyMessage)
        if userInput:
            f = open('key.txt', 'w')
            f.write(userInput)
            f.close()
            return userInput
        else:
            print('An API Key is required to fetch weather data')
            userInput = input('Go to website to obtain key? (y/n)')
            if str(userInput.lower()) == 'y':
                webbrowser.open(apiKeyUrl)
                sys.exit()
            else:
                sys.exit()

    def setDefaultSettings(self):
        f = shelve.open(self.settingsDefaultShelve)
        self.daysInForecast = f['daysInForecast']
        self.queryMode = f['queryMode']['value']
        self.queryLocation = f['location']
        f.close()

    def setCustomSettings(self):
        self.queryLocation = str(sys.argv[1])
        self.queryMode = str(sys.argv[2])
        self.daysInForecast = int(sys.argv[3])

myWeather = PyWeather()
if myWeather.queryMode == 'current':
    myWeather.printCurrentWeather()
elif myWeather.queryMode == 'forecast':
    myWeather.printWeatherForecast()
# myWeather.promptForNewDefaultSettings()
