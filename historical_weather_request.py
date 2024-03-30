import requests
import json
import os
from datetime import datetime, timedelta

weather_data_file_template = './data/weather_data_{}.json'

# OpenWeatherMap API endpoint
api_url = "https://api.openweathermap.org/data/3.0/onecall/day_summary"
api_key = "d14645e9effd825a1f72dc191a3dd253"

# Location coordinates
lat = 48.67357
lon = 7.94265

start_date = datetime(2016, 4, 28)
end_date = datetime(2016, 4, 30)


def add_or_replace_data_element_to_file(file_path, data_element):
    date_to_add = data_element.get("date")
    if not date_to_add:
        print("Error: Data element must have a 'date' field.")
        return

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = json.load(f)

        for i, existing_element in enumerate(existing_data):
            if existing_element.get("date") == date_to_add:
                existing_data[i] = data_element
                break
        else:
            existing_data.append(data_element)

        sorted_data = sorted(existing_data, key=lambda x: x.get("date"))
        with open(file_path, 'w') as f:
            json.dump(sorted_data, f, separators=(',', ':'))
        print(f"Data element added/updated in {file_path}: {data_element}")
    else:
        # Create a new file with the data element
        with open(file_path, 'w') as f:
            json.dump([data_element], f, separators=(',', ':'))
        print(f"New file {file_path} created with the data element")


def insert_multi_lines(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        modified_content = content.replace('{"lat"', '\n  {"lat"')
        modified_content = modified_content.replace(']', '\n]')

        with open(file_path, 'w') as f:
            f.write(modified_content)
    except FileNotFoundError:
        print(f"File {file_path} not found.")


current_date = start_date
while current_date <= end_date:
    formatted_date = current_date.strftime("%Y-%m-%d")

    api_params = {
        "units": "metric",
        "lang": "de",
        "lat": lat,
        "lon": lon,
        "date": formatted_date,
        "appid": api_key,
    }

    response = requests.get(api_url, params=api_params)

    if response.status_code == 200:
        data = response.json()
        date_ = data['date']
        year = date_.split("-")[0]
        file_path = './data/weather_data_{}.json'.format(year)
        add_or_replace_data_element_to_file(file_path, data)
        insert_multi_lines(file_path)
    else:
        print(f"Error for {formatted_date}: {response.status_code}")

    current_date += timedelta(days=1)
