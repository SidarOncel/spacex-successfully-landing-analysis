# import required packages "requests, beautifulsoup4"
### TODO: Add a dynamic scraper that can be scraped based on the year filter
import sys
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd

### HELPER FUNCTIONS
def date_time(table_cells):
    """
    This function returns the data and time from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out

def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass

def extract_column_from_header(row):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    if (row.br):
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
        
    colunm_name = ' '.join(row.contents)
    
    # Filter the digit and empty names
    if not(colunm_name.strip().isdigit()):
        colunm_name = colunm_name.strip()
        return colunm_name    
    

static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

# request the HTML page from the above URL and get a `response` object
# use requests.get() method with the provided static_url and headers
# assign the response to a object
def fetch_json(static_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(3):  # try 3 times
        try:
            response = requests.get(static_url, headers=headers, timeout=30)
            return response
        except requests.exceptions.ReadTimeout:
            print(f"Timeout... retrying ({i+1}/3)")

    raise Exception("Failed after multiple retries")
# Call the function to get response
response = fetch_json(static_url)

# Use BeautifulSoup() to create a BeautifulSoup object from a response text content
# Create BeautifulSoup object
soup = BeautifulSoup(response.text, 'html.parser')

#Test
print(response.status_code)
# Use soup.title attribute
print(soup.title)


### Extract all column/variable names from the HTML table header
# Assign the result to a list called `html_tables`
html_tables = soup.find_all('table')

# Let's print the third table and check its content
first_launch_table = html_tables[2]
print(first_launch_table)

# We just need to iterate through the `<th>` elements and apply the provided `extract_column_from_header()` to extract column name one by one
id="th_final"
column_names = []

th_elements = first_launch_table.find_all('th')

for th in th_elements:
    name = extract_column_from_header(th)
    
    if name is not None and len(name) > 0:
        column_names.append(name)

print(column_names)


### Create a data frame by parsing the launch HTML tables
launch_dict= dict.fromkeys(column_names)

# Remove an irrelvant column
del launch_dict['Date and time ( )']

# Let's initial the launch_dict with each value to be an empty list
launch_dict['Flight No.'] = []
launch_dict['Launch Site'] = []
launch_dict['Payload'] = []
launch_dict['Payload mass'] = []
launch_dict['Orbit'] = []
launch_dict['Customer'] = []
launch_dict['Launch outcome'] = []
# Added some new columns
launch_dict['Version Booster']=[]
launch_dict['Booster landing']=[]
launch_dict['Date']=[]
launch_dict['Time']=[]

# Next, we just need to fill up the launch_dict with launch records extracted from table rows.

extracted_row = 0

# Extract each table
for table_number, table in enumerate(soup.find_all('table', "wikitable plainrowheaders collapsible")):

    # Get table rows
    for rows in table.find_all("tr"):

        # Check if row has flight number
        if rows.th:
            if rows.th.string:
                flight_number = rows.th.string.strip()
                flag = flight_number.isdigit()
            else:
                flag = False
        else:
            flag = False

        # Get table cells
        row = rows.find_all('td')

        # If valid launch row
        if flag:
            extracted_row += 1

            # Flight Number
            launch_dict['Flight No.'].append(flight_number)

            # Date & Time
            datatimelist = date_time(row[0])
            date = datatimelist[0].strip(',')
            time = datatimelist[1]

            launch_dict['Date'].append(date)
            launch_dict['Time'].append(time)

            # Booster Version
            bv = booster_version(row[1])
            if not bv:
                bv = row[1].a.string

            launch_dict['Version Booster'].append(bv)

            # Launch Site
            launch_site = row[2].a.string
            launch_dict['Launch Site'].append(launch_site)

            # Payload
            payload = row[3].a.string
            launch_dict['Payload'].append(payload)

            # Payload Mass
            payload_mass = get_mass(row[4])
            launch_dict['Payload mass'].append(payload_mass)

            # Orbit
            orbit = row[5].a.string
            launch_dict['Orbit'].append(orbit)

            # Customer
            customer = row[6].get_text(strip=True)
            launch_dict['Customer'].append(customer)

            # Launch Outcome
            launch_outcome = list(row[7].strings)[0]
            launch_dict['Launch outcome'].append(launch_outcome)

            # Booster Landing
            booster_landing = landing_status(row[8])
            launch_dict['Booster landing'].append(booster_landing)

df= pd.DataFrame({ key:pd.Series(value) for key, value in launch_dict.items() })
print(df.head)
df.to_csv('spacex_web_scraped.csv', index=False)