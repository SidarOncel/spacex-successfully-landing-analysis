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