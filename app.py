from flask import Flask, render_template, jsonify, request
import requests
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# ⚠️ APNI ACTIVE API KEY YAHAN REHNE DEIN
API_KEY = "39e1f38beca95f256d623b5f8a127455" 

# --- Helper for Icon Mapping (Forecast ke liye zaroori) ---
def get_weather_icon(icon_code):
    icon_map = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "🌥️", "04n": "🌥️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "🌨️", "13n": "🌨️",
        "50d": "🌫️", "50n": "🌫️",
    }
    return icon_map.get(icon_code, "❓")

# --- Helper for Forecast Processing ---
def process_forecast(forecast_list):
    daily_forecasts = {}
    
    # 5-day forecast mein har din ka High/Low nikalne ke liye
    for item in forecast_list:
        dt_object = datetime.fromtimestamp(item['dt'])
        day_key = dt_object.strftime('%A') # Example: Monday, Tuesday
        
        temp_max = item['main']['temp_max']
        temp_min = item['main']['temp_min']
        
        if day_key not in daily_forecasts:
            # Naya din: Max/Min ko initialize karo, aur noon-time icon le lo
            daily_forecasts[day_key] = {
                'day': dt_object.strftime('%a'), # Short form (Mon, Tue)
                'high': temp_max,
                'low': temp_min,
                'icon': get_weather_icon(item['weather'][0]['icon'])
            }
        else:
            # Existing din: Max/Min ko update karo
            daily_forecasts[day_key]['high'] = max(daily_forecasts[day_key]['high'], temp_max)
            daily_forecasts[day_key]['low'] = min(daily_forecasts[day_key]['low'], temp_min)
            
    # Sirf next 5 entries ko list mein convert karo (aaj ke din ko chhodkar)
    forecast_result = list(daily_forecasts.values())
    
    # Aaj ka din (first entry) ko 'Today' kehne ke bajaye, usko chhod do ya next 5 days ko lo
    # OpenWeatherMap data mein 40 entries hoti hain. Hum next 5 days ko lenge (12pm entry).
    
    # Simple fix: Return only the next 5 days' unique entries
    return forecast_result[:5]


def fetch_weather_data(city):
    """Fetches CURRENT and FORECAST data."""
    url_base = "http://api.openweathermap.org/data/2.5"
    city_attempts = [city, f"{city},in"]
    
    current_data = None
    forecast_list = None
    
    for attempt in city_attempts:
        # 1. Current Weather
        current_url = f"{url_base}/weather?q={attempt}&appid={API_KEY}&units=metric"
        current_response = requests.get(current_url)
        
        # 2. 5-Day Forecast
        forecast_url = f"{url_base}/forecast?q={attempt}&appid={API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url)
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_list = forecast_response.json()['list']
            break 
    
    if current_data is None:
        # Error handling pehle jaisa hi rahega (agar koi bhi API call fail ho toh)
        try:
            error_data = current_response.json()
            error_message = error_data.get('message', f'Status {current_response.status_code} Error')
        except:
            error_message = f"API Request Failed (Status: {current_response.status_code})"

        return {'error': f'Weather API Failed: {error_message}'}

    # Data Processing and structuring
    main_data = current_data.get('main', {})
    wind_data = current_data.get('wind', {})
    weather_data = current_data.get('weather', [{}])[0]
    wind_speed_ms = wind_data.get('speed', 0)

    return {
        'current': {
            'city': current_data.get('name', city),
            'temperature': round(main_data.get('temp', 0)),
            'feels_like': round(main_data.get('feels_like', 0)),
            'humidity': main_data.get('humidity', 'N/A'),
            'wind_speed': round(wind_speed_ms * 3.6, 1),
            'pressure': main_data.get('pressure', 'N/A'),
            'description': weather_data.get('description', 'Data Unavailable'),
            'icon': get_weather_icon(weather_data.get('icon', '01d'))
        },
        'forecast': process_forecast(forecast_list)
    }

@app.route('/')
def home():
    default_city = "Aligarh"
    # Note: Ab weather_data mein 'current' aur 'forecast' dono honge
    weather_data = fetch_weather_data(default_city)
    return render_template('index.html', initial_weather=weather_data)

@app.route('/weather')
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City name is required'}), 400

    weather_data = fetch_weather_data(city)
    
    if 'error' in weather_data:
        status_code = 404 if 'city not found' in weather_data['error'].lower() else 500
        return jsonify(weather_data), status_code
        
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)