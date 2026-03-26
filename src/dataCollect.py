'''Will make a get request to the SpaceX API'''
'''User should run:  python -m pip install -r requirements'''
# Import the following libraries into a lab

# Requests allows us to make HTTP requests which we will use to get data from an API
import requests 
# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
# NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Datetime is a library that allows us to represent dates
import datetime

# Setting this option will print all collumns of a dataframe
pd.set_option('display.max_columns', None)
# Setting this option will print all of the data in a feature
pd.set_option('display.max_colwidth', None)

def getBoosterVersion(data):
    BoosterVersion = []
    cache = {}   # store already fetched rockets for speed improvements

    for x in data['rocket']:
        if x:
            if x not in cache:
                response = requests.get(
                    "https://api.spacexdata.com/v4/rockets/" + str(x)
                ).json()
                cache[x] = response['name']
            BoosterVersion.append(cache[x])
    return BoosterVersion

# From the launchpad we would like to know the name of the launch site being used, the logitude, and the latitude.
def getLaunchSite(data):
    for x in data['launchpad']:
       if x:
         response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
         Longitude.append(response['longitude'])
         Latitude.append(response['latitude'])
         LaunchSite.append(response['name'])

# From the payload we would like to learn the mass of the payload and the orbit that it is going to.
def getPayloadData(data):
    for load in data['payloads']:
       if load:
        response = requests.get("https://api.spacexdata.com/v4/payloads/"+load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])

# Takes the dataset and uses the cores column to call the API and append the data to the lists
def getCoreData(data):
    for core in data['cores']:
            if core['core'] != None:
                response = requests.get("https://api.spacexdata.com/v4/cores/"+core['core']).json()
                Block.append(response['block'])
                ReusedCount.append(response['reuse_count'])
                Serial.append(response['serial'])
            else:
                Block.append(None)
                ReusedCount.append(None)
                Serial.append(None)
            Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
            Flights.append(core['flight'])
            GridFins.append(core['gridfins'])
            Reused.append(core['reused'])
            Legs.append(core['legs'])
            LandingPad.append(core['landpad'])

# Let's start requesting rocket launch data from SpaceX API with the following URL:
spacex_url="https://api.spacexdata.com/v4/launches/past"

response = requests.get(spacex_url)

# Check the content of the response 
# print(response.content) we should see massive amount of data

# Request and parse the SpaceX launch data using the GET request
# To make the requested JSON results more consistent, we will use the following static response object for this project:

static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'

# We should see that the request was successfull with the 200 status response code
response=requests.get(static_json_url)
print(response.status_code)

# Decode the response content as a Json using .json() and turn it into a Pandas dataframe using .json_normalize() 
# bcs SpaceX API returns nested JSON, not flat data so we cant just dataframe it

df = pd.json_normalize(response.json())
#print(df.head)


# You will notice that a lot of the data are IDs. For example the rocket column has no information about the rocket just an identification number.
# We will now use the API again to get information about the launches using the IDs given for each launch. Specifically we will be using columns rocket, payloads, launchpad, and cores.

# Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
data = df[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

# We will remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket.
data = data[data['cores'].map(len)==1]
data = data[data['payloads'].map(len)==1]

# Since payloads and cores are lists of size 1 we will also extract the single value in the list and replace the feature.
data['cores'] = data['cores'].map(lambda x : x[0])
data['payloads'] = data['payloads'].map(lambda x : x[0])

# We also want to convert the date_utc to a datetime datatype and then extracting the date leaving the time
data['date'] = pd.to_datetime(data['date_utc']).dt.date

# Using the date we will restrict the dates of the launches
data = data[data['date'] <= datetime.date(2020, 11, 13)]

'''From the rocket we would like to learn the booster name
From the payload we would like to learn the mass of the payload and the orbit that it is going to
From the launchpad we would like to know the name of the launch site being used, the longitude, and the latitude.
From cores we would like to learn the outcome of the landing, the type of the landing, number of flights with that core, 
whether gridfins were used, whether the core is reused, whether legs were used, the landing pad used, the block of the core 
which is a number used to seperate version of cores, the number of times this specific core has been reused, and the serial of the core.

The data from these requests will be stored in lists and will be used to create a new dataframe.'''

#Global variables 
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

# These functions will apply the outputs globally to the above variables. 
# Let's take a looks at BoosterVersion variable. Before we apply getBoosterVersion the list is empty:

BoosterVersion = getBoosterVersion(data)
print(BoosterVersion[:5])