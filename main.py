import folium
import gpxpy
from selenium import webdriver
import time
import os
import math

def get_bar_icon_from_coordinates(coord):
    # Figure out which bar icon should be displayed at the end 
    # of the route based on their gps coords

    bars_coordinates = {
        "zoomai":[[43.28615, 5.38671], "logos/Logo_Zoomai.png"],
        "keg":[[43.24596, 5.42558], "logos/Logo_Keg.png"]
    }

    min_distance = float('inf')  # Initialize with a large value

    for key, coordinates in bars_coordinates.items():
        x2, y2 = coordinates[0]
        distance = math.sqrt((coord[0] - x2) ** 2 + (coord[1] - y2) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_bar = key
    
    return bars_coordinates[closest_bar][1] # Icon

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

    # Create map object using Folium
    resolution = 1024
    map_obj = folium.Map(
        tiles = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png", 
        attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        location=[midpoint_lat, midpoint_lon], 
        width=resolution, 
        height=resolution,
        zoom_control=False, 
        prefer_canvas=True, 
        zoom_start = 14)
    
    # Calculate the bounds of the GPX track
    min_lat = min(p[0] for p in points)
    max_lat = max(p[0] for p in points)
    min_lon = min(p[1] for p in points)
    max_lon = max(p[1] for p in points)

    # Fit the map to the bounds of the GPX track
    map_obj.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)], padding = (40,40))

    # Plot coordinates on the map
    folium.PolyLine(points, color="#1573DF", weight=5, line_cap="round", line_join="round", opacity=0.9).add_to(
        map_obj)

    # Add start and end markers
    start_lat, start_lon = points[0]
    end_lat, end_lon = points[-1]
    icon_size = (60, 60)
    bar_icon = get_bar_icon_from_coordinates([end_lat, end_lon])
    start_icon = folium.features.CustomIcon("logos/Logo_MB.png", icon_size=icon_size, icon_anchor=(icon_size[0] / 2, icon_size[1] + 4))
    end_icon = folium.features.CustomIcon(bar_icon, icon_size=icon_size, icon_anchor=(icon_size[0] / 2, icon_size[1] + 4))
    folium.Marker([start_lat, start_lon], icon=start_icon).add_to(map_obj)
    folium.Marker([end_lat, end_lon], icon=end_icon, z_index_offset=1000).add_to(map_obj)
    

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

    print(output_image)

for file in os.listdir("gpx_files/"):
    if file.endswith(".gpx"):
        gpx_file = os.path.join("gpx_files/",file)
        output_image = f"output_images/map_{os.path.basename(gpx_file).split('.')[0]}.png"
        convert_gpx_to_map(gpx_file, output_image)