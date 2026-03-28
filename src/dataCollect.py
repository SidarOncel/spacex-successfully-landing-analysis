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
# Trouble shoot the reason that makes the program slowww
import time

# ============================================================
# PARALLEL API CALLS USING THREADPOOLEXECUTOR
# ============================================================
# Normally, API requests are executed sequentially:
#     request → wait → request → wait → ...
# This is slow because each request waits for network response
# before starting the next one.
#
# In our case, we have MANY API calls (e.g., 100+ payloads/cores),
# so sequential execution leads to long runtimes (~1–2 minutes).
#
# ThreadPoolExecutor allows us to run multiple requests in parallel
# using multiple threads. Since API calls are I/O-bound (waiting
# for network), Python can overlap them efficiently.
from concurrent.futures import ThreadPoolExecutor


# Setting this option will print all collumns of a dataframe
pd.set_option('display.max_columns', None)
# Setting this option will print all of the data in a feature
pd.set_option('display.max_colwidth', None)

# Helper function to safely fetch JSON from an API
def fetch_json(url):
    # Send GET request with timeout (prevents infinite waiting)
    return requests.get(url, timeout=10).json()

# -------- ROCKET DATA --------
def getBoosterVersion(data, rocket_cache):
    # We simply map rocket IDs to names using cache (NO API here)
    # Much faster because we already fetched data earlier
    return [rocket_cache.get(x) for x in data['rocket']]

# -------- LAUNCH SITE DATA --------
def getLaunchSite(data, launchpad_cache):
    # Initialize empty lists
    Longitude, Latitude, LaunchSite = [], [], []

    # Loop through each launchpad ID
    for x in data['launchpad']:
        # Get stored values from cache (no API call here)
        lon, lat, name = launchpad_cache.get(x, (None, None, None))

        # Append values to lists
        Longitude.append(lon)
        Latitude.append(lat)
        LaunchSite.append(name)

    return Longitude, Latitude, LaunchSite

# -------- PAYLOAD DATA --------
def getPayloadData(data, payload_cache):
    PayloadMass, Orbit = [], []

    # Loop through payload IDs
    for load in data['payloads']:
        # Get payload info from cache
        mass, orbit = payload_cache.get(load, (None, None))

        PayloadMass.append(mass)
        Orbit.append(orbit)

    return PayloadMass, Orbit

# -------- CORE DATA --------
def getCoreData(data, core_cache):
    # Initialize all output lists
    Block, ReusedCount, Serial = [], [], []
    Outcome, Flights, GridFins = [], [], []
    Reused, Legs, LandingPad = [], [], []

    # Loop through each core dictionary
    for core in data['cores']:
        # Extract core ID
        core_id = core['core']

        # Get core details from cache (NO API call here)
        block, reuse, serial = core_cache.get(core_id, (None, None, None))

        # Append API-based values
        Block.append(block)
        ReusedCount.append(reuse)
        Serial.append(serial)

        # Append values directly from dataset (no API needed)
        Outcome.append(f"{core['landing_success']} {core['landing_type']}")
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])

    return (
        Block, ReusedCount, Serial,
        Outcome, Flights, GridFins,
        Reused, Legs, LandingPad
    )

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

# =========================
# PRE-FETCH ALL API DATA
# =========================

start = time.time()
# -------- ROCKET CACHE --------
rocket_cache = {}

# Get unique rocket IDs (avoids repeated API calls)
for rocket_id in data['rocket'].dropna().unique():
    # Fetch rocket info once
    response = fetch_json("https://api.spacexdata.com/v4/rockets/" + rocket_id)

    # Store only the name
    rocket_cache[rocket_id] = response['name']

print("Rocket cache time:", time.time() - start)

start = time.time()
# -------- LAUNCHPAD CACHE --------
launchpad_cache = {}

for launchpad_id in data['launchpad'].dropna().unique():
    response = fetch_json("https://api.spacexdata.com/v4/launchpads/" + launchpad_id)

    # Store tuple (longitude, latitude, name)
    launchpad_cache[launchpad_id] = (
        response['longitude'],
        response['latitude'],
        response['name']
    )
print("Launchpad cache time:", time.time() - start)

start = time.time()
# -------- PAYLOAD CACHE --------
payload_cache = {}

payload_ids = data['payloads'].dropna().unique()

def fetch_payload(payload_id):
    response = fetch_json("https://api.spacexdata.com/v4/payloads/" + payload_id)
    return payload_id, (response['mass_kg'], response['orbit'])

# Run requests in parallel (10 threads)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(fetch_payload, payload_ids)

for payload_id, value in results:
    payload_cache[payload_id] = value

print("Payload cache time:", time.time() - start)
start = time.time()


start = time.time()
# -------- CORE CACHE --------
core_cache = {}

core_ids = data['cores'].apply(
    lambda x: x['core'] if isinstance(x, dict) else None
).dropna().unique()

def fetch_core(core_id):
    response = fetch_json("https://api.spacexdata.com/v4/cores/" + core_id)
    return core_id, (
        response['block'],
        response['reuse_count'],
        response['serial']
    )

with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(fetch_core, core_ids)

for core_id, value in results:
    core_cache[core_id] = value

print("Core cache time:", time.time() - start)
'''From the rocket we would like to learn the booster name
From the payload we would like to learn the mass of the payload and the orbit that it is going to
From the launchpad we would like to know the name of the launch site being used, the longitude, and the latitude.
From cores we would like to learn the outcome of the landing, the type of the landing, number of flights with that core, 
whether gridfins were used, whether the core is reused, whether legs were used, the landing pad used, the block of the core 
which is a number used to seperate version of cores, the number of times this specific core has been reused, and the serial of the core.
The data from these requests will be stored in lists and will be used to create a new dataframe.'''

#Global variables 
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

BoosterVersion = getBoosterVersion(data, rocket_cache)
print(BoosterVersion[:5])

# Use cached data to generate lists (NO API calls here)
BoosterVersion = getBoosterVersion(data, rocket_cache)

Longitude, Latitude, LaunchSite = getLaunchSite(data, launchpad_cache)

PayloadMass, Orbit = getPayloadData(data, payload_cache)

Block, ReusedCount, Serial, Outcome, Flights, GridFins, Reused, Legs, LandingPad = getCoreData(data, core_cache)
# Finally lets construct our dataset using the data we have obtained. We combine the columns into a dictionary.
launch_dict = {'FlightNumber': list(data['flight_number']),
'Date': list(data['date']),
'BoosterVersion':BoosterVersion,'PayloadMass':PayloadMass, 'Orbit':Orbit,'LaunchSite':LaunchSite,'Outcome':Outcome,
'Flights':Flights, 'GridFins':GridFins,'Reused':Reused,'Legs':Legs, 'LandingPad':LandingPad,
'Block':Block, 'ReusedCount':ReusedCount, 'Serial':Serial, 'Longitude': Longitude,'Latitude': Latitude}

#Then, we need to create a Pandas data frame from the dictionary launch_dict.
df = pd.DataFrame(launch_dict)
df.describe()

### Filter the dataframe to only include `Falcon 9` launches
data_falcon9 = df[df['BoosterVersion'] == 'Falcon 9']

# Now that we have removed some values we should reset the FlgihtNumber column 
data_falcon9.loc[:,'FlightNumber'] = list(range(1, data_falcon9.shape[0]+1))
print(data_falcon9.head)

### Data Wrangling
# Some of the rows are missing values in our dataset.

print(data_falcon9.isnull().sum())