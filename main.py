# Flask App Code (app.py)

from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# Replace with your OpenWeatherMap API Key
API_KEY = 'f30cd060d8761667ae940c154a87fe10'
OPENWEATHERMAP_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Function to fetch live weather data
def fetch_weather_data(lat, lon):
    try:
        response = requests.get(
            f'{OPENWEATHERMAP_API_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        )
        if response.status_code == 200:
            data = response.json()
            if 'weather' in data and 'main' in data and 'wind' in data:
                return data
            else:
                return {"error": "Invalid data received from API."}
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# API endpoint to retrieve live disaster information for specified coordinates
@app.route('/api/disasters', methods=['GET'])
def get_live_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    date = request.args.get('date')  # Fetch date from request (not functional in this example)

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    data = fetch_weather_data(lat, lon)

    if 'error' not in data:
        weather = data['weather'][0]['description'].lower()
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        temperature = data['main']['temp']

        if "storm" in weather or "thunderstorm" in weather:
            disaster_type = "Thunderstorm"
        elif wind_speed > 20 and "rain" in weather:
            disaster_type = "Cyclone"
        elif temperature > 30 and humidity > 70:
            disaster_type = "Heatwave or Heavy Rainfall"
        elif "heavy rain" in weather and humidity > 85:
            disaster_type = "Flood Risk"
        else:
            disaster_type = "No major disaster risk detected"

        disaster_info = {
            'location': data.get('name', 'Unknown'),
            'temperature': temperature,
            'weather': weather,
            'wind_speed': wind_speed,
            'humidity': humidity,
            'predicted_disaster': disaster_type,
            'date': date
        }
        return jsonify(disaster_info)
    else:
        return jsonify(data), 500

# Main route to serve the map with embedded Leaflet.js
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disaster Management System</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <style>
            #map { height: 500px; width: 100%; }
            #disaster-info { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Disaster Management System</h1>
        <div id="map"></div>
        <div id="disaster-info">
            <h3>Disaster Information</h3>
            <label for="date-picker">Select Date:</label>
            <input type="date" id="date-picker">
            <p id="disaster-type">Select a location on the map to see disaster details.</p>
            <p id="disaster-description"></p>
        </div>

        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([20.5937, 78.9629], 5);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 18,
            }).addTo(map);

            function onMapClick(e) {
                var latitude = e.latlng.lat;
                var longitude = e.latlng.lng;
                var date = document.getElementById('date-picker').value;

                fetch(`/api/disasters?lat=${latitude}&lon=${longitude}&date=${date}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            document.getElementById('disaster-type').textContent = 'Error: ' + data.error;
                            document.getElementById('disaster-description').textContent = '';
                        } else {
                            document.getElementById('disaster-type').textContent = 'Predicted Disaster: ' + data.predicted_disaster;
                            document.getElementById('disaster-description').textContent = 
                                'Location: ' + data.location + ', Date: ' + data.date + ', Temperature: ' + data.temperature + '°C, Weather: ' + data.weather +
                                ', Wind Speed: ' + data.wind_speed + ' m/s, Humidity: ' + data.humidity + '%';
                        }
                    })
                    .catch(error => console.error('Error fetching disaster data:', error));
            }

            map.on('click', onMapClick);
        </script>
    </body>
    </html>
    '''

# Function to run the Flask app
def run_app():
    app.run(port=5030, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_app()
