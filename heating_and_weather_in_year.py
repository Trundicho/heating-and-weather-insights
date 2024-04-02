import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import seaborn as sns

# year_of_interest = 2017
# year_of_interest = 2018
# year_of_interest = 2019
# year_of_interest = 2020
# year_of_interest = 2021
# year_of_interest = 2022
year_of_interest = 2023
# year_of_interest = 2024

energy_source = 'Gas'
heating_consumption_data = './data/heat_consumption_data.csv'
weather_data_file_template = './data/weather_data_{}.json'

temperature_bin_size = 4
weather_data = []
temps = []

with open("data/heat_period_config.json", "r") as f:
    date_ranges = json.load(f)

years = list(date_ranges.keys())

fig, ax = plt.subplots(2, 1, figsize=(10, 10))
for year in years:
    temps.append(0)
    with open(weather_data_file_template.format(year), 'r') as f:
        weather_data_per_year = json.load(f)
        weather_data.extend(weather_data_per_year)
weather_df = pd.DataFrame(weather_data)
weather_df['date'] = pd.to_datetime(weather_df['date'])
tank_df = pd.read_csv(heating_consumption_data, parse_dates=['Date'], dayfirst=True)

date_range_of_interest = date_ranges[str(year_of_interest)]
all_dates_filter = pd.date_range(date_range_of_interest["start"], date_range_of_interest["end"])

tank_year = tank_df.copy()
tank_year.set_index('Date', inplace=True)
tank_year = tank_year.reindex(all_dates_filter)

# Forward fill the missing values
tank_year.interpolate(method='pchip', inplace=True)

# Reset the index
tank_year.reset_index(inplace=True)
tank_year.rename(columns={'index': 'Date'}, inplace=True)

# Split the temperature into min and max
weather_df['min_temperature'] = weather_df['temperature'].apply(lambda x: x['min'])
weather_df['max_temperature'] = weather_df['temperature'].apply(lambda x: x['max'])

weather_df['avg_temperature'] = (weather_df['min_temperature'] + weather_df['max_temperature']) / 2

# Merge the two DataFrames on the date
merged_df = pd.merge(tank_year, weather_df, left_on='Date', right_on='date', how='outer')

merged_df = merged_df[
    (merged_df['Date'].dt.year >= year_of_interest) & (merged_df['Date'].dt.year <= year_of_interest + 1)]

# Plot the gas tank percentage
# plt.figure(figsize=(10, 6))
ax[0].plot(merged_df['Date'], merged_df['Tank level in %'], label='Tank level in %')

# Plot the min and max temperature
ax[0].plot(merged_df['Date'], merged_df['min_temperature'], label='Min temperature')
ax[0].plot(merged_df['Date'], merged_df['max_temperature'], label='Max temperature')

ax[0].plot(merged_df['Date'], merged_df['avg_temperature'], label='Avg temperature')

ax[0].set_xlabel('Date')
ax[0].set_ylabel('Tank level')
ax[0].set_title('Gas tank % and Temperature over Time')
ax[0].set_yticks(np.arange(0, 101, 10))
ax[0].grid(True, axis='y')
ax[0].legend()

#####################

merged_df['{} consumption in %'.format(energy_source)] = -merged_df['Tank level in %'].diff()
# merged_df['avg_temperature'] = merged_df['avg_temperature'].round() # round if you like

# Define the temperature bins
bins = np.arange(merged_df['avg_temperature'].min(), merged_df['avg_temperature'].max(), temperature_bin_size)

# Add a new column to the DataFrame for the temperature bin of each day
merged_df['Temperature Bin'] = pd.cut(merged_df['avg_temperature'], bins)

ax[1].set_xlabel('Temperature range')
ax[1].set_ylabel('Daily consumption in %')
ax[1].set_title(str(year_of_interest))
ax[1].grid(True, axis='y')
sns.boxplot(x='Temperature Bin', y='{} consumption in %'.format(energy_source), data=merged_df)
ax[1].legend()

plt.tight_layout()
plt.show()
