'''
Install the below libraries
!pip install pandas
!pip install numpy'''

# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
#NumPy is a library for the Python programming language, adding support for large, 
# multi-dimensional arrays and matrices, along with a large collection of high-level 
# mathematical functions to operate on these arrays
import numpy as np

# Load Space X dataset, from last section.
df=pd.read_csv("dataset_part_1.csv")
print(df.head(10))

# Identify and calculate the percentage of the missing values in each attribute
print(df.isnull().sum()/len(df)*100)

# Identify which columns are numerical and categorical
print(df.dtypes)

# Calculate the number of launches on each site
print(df['LaunchSite'].value_counts())

# Calculate the number and occurrence of each orbit
# Apply value_counts on Orbit column
print(df['Orbit'].value_counts())

# Calculate the number and occurence of mission outcome of the orbits
landing_outcomes = df['Outcome'].value_counts()

# True Ocean means the mission outcome was successfully landed to a specific region of the ocean while 
# False Ocean means the mission outcome was unsuccessfully landed to a specific region of the ocean. 
# True RTLS means the mission outcome was successfully landed to a ground pad 
# False RTLS means the mission outcome was unsuccessfully landed to a ground pad.
# True ASDS means the mission outcome was successfully landed to a drone ship 
# False ASDS means the mission outcome was unsuccessfully landed to a drone ship.
# None ASDS and None None these represent a failure to land.

for i,outcome in enumerate(landing_outcomes.keys()):
    print(i,outcome)

# We create a set of outcomes where the second stage did not land successfully:
bad_landing = set(landing_outcomes.keys()[[1,3,5,6,7]])
print(bad_landing)


# Create landing outcome label (0 = failure, 1 = success)
df['Class'] = df['Outcome'].apply(
    lambda x: 0 if x.startswith(('False', 'None')) else 1
)

# Check results
print(df[['Outcome', 'Class']].head(10))

# We can use the following line of code to determine the success rate
print(df['Class'].mean())