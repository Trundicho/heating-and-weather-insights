import requests
from datetime import datetime, timedelta

# OpenWeatherMap API endpoint
api_url = "https://api.openweathermap.org/data/3.0/onecall/day_summary"
api_key = "Replace with your OpenWeatherMap API key"

# Location coordinates
lat = 48.67357
lon = 7.94265

# Date range for December 2023
start_date = datetime(2024, 4, 29)
end_date = datetime(2024, 4, 30)

# Loop through each day in December 2023
current_date = start_date
while current_date <= end_date:
    # Format date in 'YYYY-MM-DD' for the API request
    formatted_date = current_date.strftime("%Y-%m-%d")

    # Construct the API request URL
    api_params = {
        "units": "metric",
        "lang": "de",
        "lat": lat,
        "lon": lon,
        "date": formatted_date,
        "appid": api_key,
    }

    # Make the API request
    response = requests.get(api_url, params=api_params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Process the API response here (you can print or save the data)
        data = response.json()
        print(f"{data}")
    else:
        print(f"Error for {formatted_date}: {response.status_code}")

    # Move to the next day
    current_date += timedelta(days=1)
