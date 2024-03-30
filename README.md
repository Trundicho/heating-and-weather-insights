# Heating and weather insights

This tool gives you an analysis of your heating consumption with respect to the actual weather.

If you change your behaviour or optimize your heating source then you can compare your consumption with previous years 
even if the weather was totally different.

![example_multi_years.png](resources%2Fexample_multi_years.png)
![example_in_year.png](./resources%2Fexample_in_year.png)

## Installation

`pip install -r requirements.txt`

## 1. Get historical weather data
In `historical_weather_request.py` you have to configure your location (get `longitude and latitude` from google maps 
for example).

Then specify `start and end date`. Each day will be a request to a weather API (openweathermap).

## 2. Add heat consumption data
Place your heat consumption here: `./data/heat_consumption_data.csv`

## 3. Heating and weather in year insights
Run `python heating_and_weather_in_year.py`

## 4. Heating and weather over multiple years insights
Run `python heating_and_weather_multi_years.py`