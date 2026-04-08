'''Perform exploratory Data Analysis and Feature Engineering using Pandas and Matplotlib
Exploratory Data Analysis
Preparing Data Feature Engineering'''

#Import Libraries and Define Auxiliary Functions
'''
import piplite
await piplite.install(['numpy'])
await piplite.install(['pandas'])
await piplite.install(['seaborn'])
'''

# pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
#NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices,
#  along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Matplotlib is a plotting library for python and pyplot gives us a MatLab like plotting framework. We will use this in our plotter function to plot data.
import matplotlib.pyplot as plt
#Seaborn is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics
import seaborn as sns

# First, let's read the SpaceX dataset into a Pandas dataframe and print its summary
df=pd.read_csv("dataset_part_1.csv")
#print(df.head(5))

'''We can plot out the FlightNumber vs. PayloadMassand overlay the outcome of the launch. 
We see that as the flight number increases, the first stage is more likely to land successfully.
The payload mass also appears to be a factor; even with more massive payloads, the first stage often returns successfully.'''
'''
sns.catplot(y="PayloadMass", x="FlightNumber",hue="Outcome", data=df, aspect = 5)
plt.xlabel("Flight Number",fontsize=20)
plt.ylabel("Pay load Mass (kg)",fontsize=20)
plt.show()'''
'''
# Visualize the relationship between Flight Number and Launch Site
sns.catplot(y="LaunchSite", x="FlightNumber",hue="Outcome", data=df, aspect = 5)
plt.xlabel("Flight Number",fontsize=20)
plt.ylabel("LaunchSite",fontsize=20)
plt.show()

#Visualize the relationship between Payload Mass and Launch Site
sns.catplot(data=df, x="LaunchSite", y="PayloadMass", hue="Outcome", aspect=4)
plt.xlabel("LaunchSite",fontsize=20)
plt.ylabel("Pay load Mass (kg)",fontsize=20)
plt.show()
'''
'''
# Visualize the relationship between success rate of each orbit type
orbit_success = df.groupby("Orbit")["Class"].mean().reset_index()
sns.catplot(
    data=orbit_success,
    x="Orbit",
    y="Class",
    kind="bar",
    aspect=5
)
plt.ylabel("Success Rate")
plt.show()
'''
# Visualize the relationship between FlightNumber and Orbit type
sns.scatterplot(
    data=df,
    x="FlightNumber",
    y="Orbit",
    hue="Class"
)

plt.xlabel("Flight Number")
plt.ylabel("Orbit")
plt.show()
'''We can observe that in the LEO orbit, success seems to be related to the number of flights. 
Conversely, in the GTO orbit, there appears to be no relationship between flight number and success.'''

# Visualize the relationship between Payload Mass and Orbit type
sns.scatterplot(
    data=df,
    x="PayloadMass",
    y="Orbit",
    hue="Class"
)

plt.xlabel("PayloadMass")
plt.ylabel("Orbit")
plt.show()

'''
With heavy payloads the successful landing or positive landing rate are more for Polar,LEO and ISS.
However, for GTO, it's difficult to distinguish between successful and unsuccessful landings as both outcomes are present.'''


# Visualize the launch success yearly trend

# A function to Extract years from the date 
year=[]
def Extract_year():
    for i in df["Date"]:
        year.append(i.split("-")[0])
    return year
Extract_year()
df['Date'] = year
df.head()

# Plot a line chart with x axis to be the extracted year and y axis to be the success rate
sns.lineplot(
    data=df,
    x="Date",
    y="Class",
)

plt.xlabel("Year")
plt.ylabel("Success Rate")
plt.show()
# observe that the sucess rate since 2013 kept increasing till 2020    

# Features Engineering
features = df[['FlightNumber', 'PayloadMass', 'Orbit', 'LaunchSite', 'Flights', 'GridFins', 'Reused', 'Legs', 'LandingPad', 'Block', 'ReusedCount', 'Serial']]
print(features.head())


# Create dummy variables to categorical columns
features_one_hot = pd.get_dummies(
    features,
    columns=["Orbit", "LaunchSite", "LandingPad", "Serial"]
)
features_one_hot.head()

#Cast all numeric columns to float64
features_one_hot= features_one_hot.astype("float64")
features_one_hot.head()

# export it to a CSV
features_one_hot.to_csv('dataset_part_3.csv', index=False)