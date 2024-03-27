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
year_of_interest = 2022
# year_of_interest = 2023

heating_consumption_data = './data/gas.csv'
weather_data_file_template = './data/weather_data_{}.json'

temperature_bin_size = 4
weather_data = []
temps = []
years = [
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024
]
fig, ax = plt.subplots(2, 1, figsize=(10, 10))
for year in years:
    temps.append(0)
    with open(weather_data_file_template.format(year), 'r') as f:
        weather_data_per_year = json.load(f)
        weather_data.extend(weather_data_per_year)
weather_df = pd.DataFrame(weather_data)
weather_df['date'] = pd.to_datetime(weather_df['date'])
gas_tank_df = pd.read_csv(heating_consumption_data, parse_dates=['Date'], dayfirst=True)

if 2017 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2017-06-22', end='2018-04-02')
if 2018 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2018-04-03', end='2019-05-24')
if 2019 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2019-05-25', end='2020-07-02')
if 2020 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2020-06-01', end='2021-07-04')
if 2021 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2021-07-05', end='2022-05-25')
if 2022 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2022-06-01', end='2023-07-01')
if 2023 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2023-07-01', end='2024-03-15')
if 2024 == year_of_interest:
    all_dates_gas_filter = pd.date_range(start='2024-03-16', end='2024-03-31')

gas_tank_year = gas_tank_df.copy()
gas_tank_year.set_index('Date', inplace=True)
gas_tank_year = gas_tank_year.reindex(all_dates_gas_filter)

# Forward fill the missing values
gas_tank_year.interpolate(method='pchip', inplace=True)

# Reset the index
gas_tank_year.reset_index(inplace=True)
gas_tank_year.rename(columns={'index': 'Date'}, inplace=True)

# Split the temperature into min and max
weather_df['min_temperature'] = weather_df['temperature'].apply(lambda x: x['min'])
weather_df['max_temperature'] = weather_df['temperature'].apply(lambda x: x['max'])

weather_df['avg_temperature'] = (weather_df['min_temperature'] + weather_df['max_temperature']) / 2

# Merge the two DataFrames on the date
merged_df = pd.merge(gas_tank_year, weather_df, left_on='Date', right_on='date', how='outer')

merged_df = merged_df[
    (merged_df['Date'].dt.year >= year_of_interest) & (merged_df['Date'].dt.year <= year_of_interest + 1)]

# Plot the gas tank percentage
# plt.figure(figsize=(10, 6))
ax[0].plot(merged_df['Date'], merged_df['Gas tank in %'], label='Gas tank in %')

# Plot the min and max temperature
ax[0].plot(merged_df['Date'], merged_df['min_temperature'], label='Min temperature')
ax[0].plot(merged_df['Date'], merged_df['max_temperature'], label='Max temperature')

ax[0].plot(merged_df['Date'], merged_df['avg_temperature'], label='Avg temperature')

ax[0].set_xlabel('Date')
ax[0].set_ylabel('Füllstand')
ax[0].set_title('Gas tank % and Temperature over Time')
ax[0].set_yticks(np.arange(0, 101, 10))
ax[0].grid(True, axis='y')
ax[0].legend()

#####################

# # Calculate the daily gas consumption
merged_df['Gas Consumption in %'] = -merged_df['Gas tank in %'].diff()
# merged_df['avg_temperature'] = merged_df['avg_temperature'].round() # round if you like

# Define the temperature bins
bins = np.arange(merged_df['avg_temperature'].min(), merged_df['avg_temperature'].max(), temperature_bin_size)

# Add a new column to the DataFrame for the temperature bin of each day
merged_df['Temperature Bin'] = pd.cut(merged_df['avg_temperature'], bins)

ax[1].set_xlabel('Temperaturbereich')
ax[1].set_ylabel('Täglicher Gasverbrauch')
ax[1].set_title(str(year_of_interest))
ax[1].grid(True, axis='y')
sns.boxplot(x='Temperature Bin', y='Gas Consumption in %', data=merged_df)
ax[1].legend()

plt.tight_layout()
plt.show()
