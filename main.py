import folium
import gpxpy
from selenium import webdriver
import time
import os

def convert_gpx_to_map(gpx_file, output_image):

    # Parse GPX file
    gpx = gpxpy.parse(open(gpx_file))

    # Extract latitude and longitude coordinates
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append([point.latitude, point.longitude])

    # Calculate the average latitude and longitude of each points (to center map)
    avg_lat = sum(p[0] for p in points) / len(points)
    avg_lon = sum(p[1] for p in points) / len(points)

    # Create map object using Folium
    resolution = 200
    map_obj = folium.Map(location=[avg_lat, avg_lon], width = 16*resolution, height = 9*resolution, zoom_control = False, prefer_canvas = True, zoom_start=13)

    # Plot coordinates on the map
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map_obj)

    # Save the map as an HTML file
    map_obj.save("temp_map.html")

    # Convert HTML to image using Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument(f"--window-size={16*resolution},{9*resolution}")
    driver = webdriver.Chrome(options=options)
    driver.get("file://" + os.path.abspath("temp_map.html"))
    time.sleep(2) # Delay to let the map tiles load properly
    driver.save_screenshot(output_image)
    driver.quit()

#gpx_file = "gpx_files/2023-06-23_1180613941_Col de l'Espigoulier - parc naturel régional de la Sainte-Baume.gpx"
gpx_file = "gpx_files/2023-06-29_1189884966_afterwork.gpx"
output_image = "output_images/test.png"
convert_gpx_to_map(gpx_file, output_image)