from flask import Flask, render_template, request
import requests
import json
import folium
import os
from flask import send_from_directory

app = Flask(__name__)

TOMTOM_API_KEY = "34SweTGuE4gGTzzbWGeZWhXYd2HXjrPw"
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"


# Fetch weather data from Open-Meteo API
def get_weather_data(lat, lon):
    api_url = f"{OPEN_METEO_API_URL}?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(api_url)
    data = response.json()
    weather = data.get('current_weather', {})
    return {
        "temperature": weather.get('temperature'),
        "rainfall": weather.get('precipitation'),
        "windspeed": weather.get('windspeed')
    }


# Fetch traffic data from TomTom API
def get_traffic_data(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{start_lon},{start_lat},{end_lon},{end_lat}.json?key={TOMTOM_API_KEY}"
    response = requests.get(url)
    traffic_data = response.json()

    # Print the response data for debugging
    print("Traffic Data Response:", json.dumps(traffic_data, indent=4))

    # Check if 'flowSegmentData' exists in the response
    if 'flowSegmentData' in traffic_data:
        return traffic_data['flowSegmentData']['currentSpeed']
    else:
        print("Error: 'flowSegmentData' not found in response.")
        return None  # Return None or handle as appropriate (e.g., return 0 or a default value)


# Route to display the home page
@app.route('/')
def index():
    return render_template('index.html')


# Route to calculate route and display results
@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    start = request.form['start']
    destination = request.form['destination']

    # Example coordinates for start and destination (could be fetched via geocoding API)
    start_lat, start_lon = 52.52, 13.405  # Replace with dynamic geocoding data
    dest_lat, dest_lon = 52.52, 13.405  # Replace with dynamic geocoding data

    # Get weather data for destination
    weather = get_weather_data(dest_lat, dest_lon)

    # Get traffic data for the route
    traffic = get_traffic_data(start_lat, start_lon, dest_lat, dest_lon)

    # Generate the map using Folium
    folium_map = folium.Map(location=[dest_lat, dest_lon], zoom_start=12)
    folium.Marker([dest_lat, dest_lon], popup=f"Destination: {destination}").add_to(folium_map)

    # Save the map to the static folder
    map_file_name = f"map_{start}_{destination}.html"
    map_file_path = os.path.join(app.static_folder, map_file_name)
    folium_map.save(map_file_path)

    # Return the results to the user
    return render_template('route_result.html', weather=weather, traffic=traffic, start=start, destination=destination, map_file=map_file_name)


# Serve static files (the map file) if requested
@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    app.run(debug=True)
