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
df=pd.read_csv("src/dataset_part_1.csv")
#print(df.head(5))

'''We can plot out the FlightNumber vs. PayloadMassand overlay the outcome of the launch. 
We see that as the flight number increases, the first stage is more likely to land successfully.
The payload mass also appears to be a factor; even with more massive payloads, the first stage often returns successfully.'''

sns.catplot(y="PayloadMass", x="FlightNumber",hue="Outcome", data=df, aspect = 5)
plt.xlabel("Flight Number",fontsize=20)
plt.ylabel("Pay load Mass (kg)",fontsize=20)
plt.show()