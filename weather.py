import streamlit as st
import requests
from datetime import datetime

# Constants
API_KEY = st.secrets["OPEN_WEATHER_API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(query):
    params = {
        "q": query if ',' not in query else None,
        "lat": float(query.split(',')[0]) if ',' in query else None,
        "lon": float(query.split(',')[1]) if ',' in query else None,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()

def display_main_weather(data, title):
    main_weather = data["weather"][0]
    main_data = data["main"]
    sys_data = data["sys"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"## {title}")
        st.markdown(f"**Temperature:** {main_data['temp']}°C")
        st.markdown(f"**Humidity:** {main_data['humidity']}%")
        st.markdown(f"**Pressure:** {main_data['pressure']} hPa")
        st.markdown(f"**Wind Speed:** {data['wind']['speed']} m/s")

    with col2:
        st.markdown("## ")
        st.markdown(f"**Description:** {main_weather['description'].title()}")
        st.markdown(f"**Sunrise:** {datetime.fromtimestamp(sys_data['sunrise']).strftime('%H:%M:%S')}")
        st.markdown(f"**Sunset:** {datetime.fromtimestamp(sys_data['sunset']).strftime('%H:%M:%S')}")

        if 'visibility' in data:
            st.markdown(f"**Visibility:** {data['visibility'] / 1000} km")
        if 'rain' in data and '1h' in data['rain']:
            st.markdown(f"**Rain (last 1 hour):** {data['rain']['1h']} mm")
        if 'snow' in data and '1h' in data['snow']:
            st.markdown(f"**Snow (last 1 hour):** {data['snow']['1h']} mm")

    icon_url = f"http://openweathermap.org/img/w/{main_weather['icon']}.png"
    st.image(icon_url)

def display_nearby_weather(data, title):
    main_weather = data["weather"][0]
    main_data = data["main"]

    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown(f"**Temperature:** {main_data['temp']}°C")
    st.markdown(f"**Condition:** {main_weather['description'].title()}")

    icon_url = f"http://openweathermap.org/img/w/{main_weather['icon']}.png"
    st.image(icon_url, width=50)

# Streamlit App
st.title("Weather App")

city = st.text_input("Enter City Name:")
submit = st.button("Submit")

if submit and city:
    data = get_weather_data(city)
    if data.get("cod") == 200:
        display_main_weather(data, city.title())

        # Coordinates for the entered city
        lat, lon = data['coord']['lat'], data['coord']['lon']

        # Offsets for nearby cities (approximations)
        offsets = [(0.1, 0.1), (-0.1, -0.1), (0.1, -0.1), (-0.1, 0.1), (0.15, 0)]

        st.markdown("## Nearby Locations:")
        for offset in offsets:
            nearby_data = get_weather_data(f"{lat + offset[0]},{lon + offset[1]}")
            if nearby_data.get("cod") == 200:
                nearby_city = nearby_data['name']
                display_nearby_weather(nearby_data, nearby_city)
    else:
        st.error(f"Error fetching data for {city}. Please check the city name.")
