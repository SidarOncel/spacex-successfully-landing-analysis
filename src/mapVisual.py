'''Import required Python packages for this lab:
import piplite
await piplite.install(['folium'])
await piplite.install(['pandas'])
'''

import folium
import pandas as pd
# Import folium MarkerCluster plugin
from folium.plugins import MarkerCluster
# Import folium MousePosition plugin
from folium.plugins import MousePosition
# Import folium DivIcon plugin
from folium.features import DivIcon

spacex_df=pd.read_csv('dataset_part_1.csv')


# Select relevant sub-columns
spacex_df = spacex_df[['LaunchSite', 'Latitude', 'Longitude', 'Class']]
launch_sites_df = spacex_df.groupby(['LaunchSite'], as_index=False).first()
launch_sites_df = launch_sites_df[['LaunchSite', 'Latitude', 'Longitude']]
print(launch_sites_df)

# Start location is NASA Johnson Space Center
nasa_coordinate = [29.559684888503615, -95.0830971930759]
site_map = folium.Map(location=nasa_coordinate, zoom_start=10)

# We could use folium.Circle to add a highlighted circle area with a text label on a specific coordinate. For example:

''' For experiment
# Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
circle = folium.Circle(
    nasa_coordinate,
    radius=1000,
    color='#d35400',
    fill=True
).add_child(folium.Popup('NASA Johnson Space Center'))

marker = folium.Marker(
    nasa_coordinate,
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html='<div style="font-size: 12; color:#d35400;"><b>NASA JSC</b></div>'
    )
)

site_map.add_child(circle)
site_map.add_child(marker)

# IMPORTANT
site_map.save("map.html") '''


for _, row in launch_sites_df.iterrows():
    
    location = [row['Latitude'], row['Longitude']]
    
    # Circle
    circle = folium.Circle(
        location=location,
        radius=1000,
        color='#d35400',
        fill=True
    ).add_child(
        folium.Popup(row['LaunchSite'])
    )
    
    site_map.add_child(circle)

    # Text label 
    marker = folium.Marker(
        location=location,
        icon=DivIcon(
            icon_size=(20,20),
            icon_anchor=(0,0),
            html=f'<div style="font-size: 10pt; color:#d35400;"><b>{row["LaunchSite"]}</b></div>'
        )
    )
    
    site_map.add_child(marker)

# Save map
site_map.save("map2.html")

# Create a new column in spacex_df called marker_color
# green = success, red = failure
spacex_df['marker_color'] = spacex_df['Class'].apply(
    lambda x: 'green' if x == 1 else 'red'
)

marker_cluster = MarkerCluster()

# Add marker cluster to current site map
site_map.add_child(marker_cluster)

# For each row in spacex_df, add a marker to the cluster
for index, record in spacex_df.iterrows():
    marker = folium.Marker(
        location=[record['Latitude'], record['Longitude']],
        icon=folium.Icon(color='white', icon_color=record['marker_color'])
    )
    marker_cluster.add_child(marker)

formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)

site_map.add_child(mouse_position)
site_map.save("map3.html")


from math import sin, cos, sqrt, atan2, radians

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# =========================================================
#  DISTANCE TO COASTLINE 
# =========================================================

# Example: CCAFS site
launch_site_lat = 28.5618571
launch_site_lon = -80.577366

# Closest coastline point
coastline_lat = 28.56367
coastline_lon = -80.57163

# Calculate distance
distance = calculate_distance(
    launch_site_lat, launch_site_lon,
    coastline_lat, coastline_lon
)

# Add distance marker
distance_marker = folium.Marker(
    [coastline_lat, coastline_lon],
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html=f'<div style="font-size: 12px; color:blue;"><b>{distance:.2f} KM</b></div>'
    )
)

site_map.add_child(distance_marker)

# Draw line
lines = folium.PolyLine(
    locations=[
        [launch_site_lat, launch_site_lon],
        [coastline_lat, coastline_lon]
    ],
    weight=2,
    color='blue'
)

site_map.add_child(lines)

# Final save
site_map.save("map_final.html")