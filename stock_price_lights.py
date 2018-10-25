#Basic code that looks up the specified stock ticker name and turns a Hue blub green if stock price percentage is up and red if it is down
#Idea adapted from https://staceyoniot.com/how-to-create-ambient-notifications-with-python-and-a-smart-bulb/

import requests
def stock_price_lights():
    #Ask for stock ticker name and format in upper case
    ticker = input('Enter Stock Ticker Name: ').upper()
    #Create the stock URL based on user input
    stockurl = 'https://api.iextrading.com/1.0/stock/' + ticker + '/previous'
    #Get the stock price data from web
    r = requests.get(url=stockurl)
    #Format the ruturned data in json
    data = r.json()
    #Get the stock change percentage from the json data
    percentage = data['changePercent']
    
    #Hue light information
    #Hue bulb color parameters can vary by bulb type. You'll need to determin the "hue", "sat", and "xy" values for your specific bulb.
    huelight = '5'
    green    = '{"on":true,"bri":254,"hue":18432,"sat":254,"xy":[0.193,0.7251]}'
    red      = '{"on":true,"bri":254,"hue":2304,"sat":1,"xy":[0.6818,0.3061]}'
    hueurl   = 'http://<LOCAL HUE HUB IP ADDRESS>/api/<HUE HUB USERNAME>/lights/' + huelight + '/state'
    
    #Set Hue light color based on stock price percentage
    if percentage >= 0:
        huestate = green
    elif percentage < 0:
        huestate = red
    
    #Send color change command to the Hue Hub and print the value
    changecolor = requests.put(url=hueurl, data=huestate)
    print(ticker + ' price change today: ' + str(percentage) + '%')

#Run stock_price_lights() until repeat = n
loop = 'n'
a = ''
while a != loop:
    stock_price_lights()
    repeat = input('Check another stock? [y/n]: ')
    if repeat == 'n':
        a = 'n'
        print('exiting program')