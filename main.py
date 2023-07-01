import folium
import gpxpy
from selenium import webdriver
import time
import os
import numpy as np
import math

# Calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    distance = np.linalg.norm(np.array(point1) - np.array(point2))
    return distance

def push_markers_apart(icon1, icon2, min_distance):
    distance = calculate_distance(icon1.location, icon2.location)
    if distance < min_distance:
        # Calculate the vector between the icon positions
        vector = np.array(icon1.location) - np.array(icon2.location)
        vector = vector / np.linalg.norm(vector)  # Normalize the vector

        # Calculate the new positions to push the icons apart
        shift = (min_distance - distance) / 2
        new_position1 = (icon1.location + vector * shift).tolist()
        new_position2 = (icon2.location - vector * shift).tolist()

        # Update the icon positions
        icon1.location = new_position1
        icon2.location = new_position2

def get_bar_icon_from_coordinates(coord):
    bars_coordinates = {
        "zoomai":[[43.2459, 5.4255], "logos/Logo_Zoomai.png"],
        "keg":[[43.2459, 5.4255], "logos/Logo_Keg.png"]
    }

    closest_coordinates = None
    min_distance = float('inf')  # Initialize with a large value

    for key, coordinates in bars_coordinates.items():
        x2, y2 = coordinates[0]
        distance = math.sqrt((coord[0] - x2) ** 2 + (coord[1] - y2) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_coordinates = key

    return closest_coordinates

    return icon


def convert_gpx_to_map(gpx_file, output_image):

    # Parse GPX file
    gpx = gpxpy.parse(open(gpx_file))

    # Extract latitude and longitude coordinates
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append([point.latitude, point.longitude])

    # Calculate the midpoint between the minimum and maximum latitude and longitude values (to center the map)
    midpoint_lat = (min(p[0] for p in points) + max(p[0] for p in points)) / 2
    midpoint_lon = (min(p[1] for p in points) + max(p[1] for p in points)) / 2

    # Calculate the difference between the minimum and maximum latitude and longitude values (to influence how zoomed in the map is)
    delta_lat = max(p[0] for p in points) - min(p[0] for p in points)
    delta_lon = max(p[1] for p in points) - min(p[1] for p in points)
    max_delta = max(delta_lat, delta_lon)
    print(max_delta)

    # Create map object using Folium
    resolution = 1024
    map_obj = folium.Map(
        tiles = "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=6d83354b-5801-4255-ac4b-6b41df50cf8c", 
        attr = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        location=[midpoint_lat, midpoint_lon], 
        width=resolution, 
        height=resolution,
        zoom_control=False, 
        prefer_canvas=True, 
        zoom_start=13.3 + max_delta)

    # Plot coordinates on the map
    # color="#1381FA"
    folium.PolyLine(points, color="yellow", weight=4, line_cap="round", line_join="round", opacity=0.9).add_to(
        map_obj)

    # Add start and end markers
    start_lat, start_lon = points[0]
    end_lat, end_lon = points[-1]
    icon_size = (60, 60)
    bar_icon = get_bar_icon_from_coordinates([end_lat, end_lon])
    start_icon = folium.features.CustomIcon("logos/Logo_MB.png", icon_size=icon_size, icon_anchor=(icon_size[0] / 2, icon_size[1] + 2))
    end_icon = folium.features.CustomIcon(bar_icon, icon_size=icon_size, icon_anchor=(icon_size[0] / 2, icon_size[1] + 2))
    start_marker = folium.Marker([start_lat, start_lon], icon=start_icon)
    end_marker = folium.Marker([end_lat, end_lon], icon=end_icon)
    print([end_lat, end_lon])

    # Create a list of icons
    icons = [start_marker, end_marker]

    # Push the icons apart if they are too close
    min_distance = (icon_size[0] / 2) + 5
    min_distance = 0.0055
    push_markers_apart(start_marker, end_marker, min_distance)

    # Add the markers to the map
    for icon in icons:
        icon.add_to(map_obj)

    # Save the map as an HTML file
    map_obj.save("temp_map.html")

    # Convert HTML to image using Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"--window-size={resolution},{resolution}")
    driver = webdriver.Chrome(options=options)
    driver.get("file://" + os.path.abspath("temp_map.html"))
    time.sleep(1)  # Delay to let the map tiles load properly
    driver.save_screenshot(output_image)
    driver.quit()

gpx_file = "gpx_files/Massilia Bastards M17.gpx"
output_image = f"output_images/test_{os.path.basename(gpx_file)}.png"
convert_gpx_to_map(gpx_file, output_image)
