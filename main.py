import folium
import gpxpy
from PIL import Image

def convert_gpx_to_map(gpx_file, output_image):
    # Parse GPX file
    gpx = gpxpy.parse(open(gpx_file))

    # Extract latitude and longitude coordinates
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append([point.latitude, point.longitude])

    # Create map object using Folium
    map_obj = folium.Map(location=points[0], zoom_start=13)

    # Plot coordinates on the map
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map_obj)

    # Save the map as HTML file
    map_obj.save("temp_map.html")

    # Convert HTML to image using PIL
    img = Image.open("temp_map.html")
    img.save(output_image, "PNG")

    # Remove temporary HTML file
    #os.remove("temp_map.html")

# Example usage
gpx_file = "gpx_files/2023-06-29_1189884966_afterwork.gpx"
output_image = "output_images/test.png"
convert_gpx_to_map(gpx_file, output_image)
