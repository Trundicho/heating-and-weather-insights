import json

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

below_degrees = 15
energy_source = 'Gas'
max_tank_liters = 1560
minimum_tank_level_percent = 25
maximum_tank_level_percent = 85

# unit, maximum y-display-value, y-display-ticks
heating_consumption_unit = ['kWh', 5500, 500]
# heating_consumption_unit = ['Liter', 1000, 100]
# heating_consumption_unit = ['%', 60, 5]

with open("data/heat_period_config.json", "r") as f:
    date_ranges = json.load(f)

heating_consumption_data = './data/heat_consumption_data.csv'
weather_data_file_template = './data/weather_data_{}.json'

temperature_bin_size = 4

tank_df = pd.read_csv(heating_consumption_data, parse_dates=['Date'], dayfirst=True)
tank_df['Tank level in %'] = (tank_df['Tank level in %']
                              .apply(lambda x: ((x - minimum_tank_level_percent) /
                                                (maximum_tank_level_percent - minimum_tank_level_percent)) * 100))

available_colors = ['gray', 'red', 'green', 'blue', 'black', 'purple', 'brown', 'orange']
colors = []

fig, ax = plt.subplots(2, 1, figsize=(10, 10))
weather_data = []

for year in date_ranges.keys():
    with open(weather_data_file_template.format(year), 'r') as f:
        weather_data_per_year = json.load(f)
        weather_data.extend(weather_data_per_year)

weather_df = pd.DataFrame(weather_data)
weather_df['date'] = pd.to_datetime(weather_df['date'])

row = - 1


def energy_converter(energy_consumption_in_percent, heating_unit, energy_source, max_tank_liters):
    # 100% = 1560L volle Tankfüllung von 0 auf 100%
    # 47% = 47 * 1560 / 100 L
    # Ein Liter (l) Flüssiggas enthält ca. 7.13 Kilowattstunden (kWh) Brennwert Energie.
    # https://fluessiggas.de/wissen/fluessiggas/fluessiggas-umrechnung/#fluessiggas-rechner
    if heating_unit == 'kWh':
        return energy_consumption_in_percent * (max_tank_liters / 100) * 7.13
    elif heating_unit == 'Liter':
        return energy_consumption_in_percent * (max_tank_liters / 100)
    return energy_consumption_in_percent


def fill_missing_values(tank_df, dates_filter):
    tank_year = tank_df.copy()
    tank_year.set_index('Date', inplace=True)
    tank_year = tank_year.reindex(dates_filter)
    # Forward fill the missing values
    tank_year.interpolate(method='pchip', inplace=True)
    # Reset the index
    tank_year.reset_index(inplace=True)
    tank_year.rename(columns={'index': 'Date'}, inplace=True)
    return tank_year


years = [int(year) for year in date_ranges.keys()]

for year in years:
    row = row + 1
    colors.append(available_colors[row])

    date_range_of_interest = date_ranges[str(year)]
    all_dates_filter = pd.date_range(date_range_of_interest["start"], date_range_of_interest["end"])

    tank_year = fill_missing_values(tank_df, all_dates_filter)

    weather_df['min_temperature'] = weather_df['temperature'].apply(lambda x: x['min'])
    weather_df['max_temperature'] = weather_df['temperature'].apply(lambda x: x['max'])
    weather_df['avg_temperature'] = (weather_df['min_temperature'] + weather_df['max_temperature']) / 2

    merged_df = pd.merge(tank_year, weather_df, left_on='Date', right_on='date', how='outer')

    merged_df = merged_df[
        (merged_df['Date'].dt.year >= years[0]) & (merged_df['Date'].dt.year <= years[years.__len__() - 1] + 1)]

    merged_df['{} Consumption in %'.format(energy_source)] = -merged_df['Tank level in %'].diff()
    total_energy_consumption = merged_df['{} Consumption in %'.format(energy_source)].sum()

    total_energy_consumption = energy_converter(total_energy_consumption,
                                                heating_consumption_unit[0],
                                                energy_source,
                                                max_tank_liters)

    merged_df['below_degrees'] = below_degrees - merged_df[merged_df['avg_temperature'] < below_degrees][
        'avg_temperature']
    sum_below_degrees = merged_df['below_degrees'].sum()
    energyPerWinter = 0
    if sum_below_degrees > 0:
        energyPerWinter = round(total_energy_consumption / sum_below_degrees, 2)
    label = '{}/{}\n{}'.format(year, year + 1, round(energyPerWinter, 2))
    ax[0].bar(label, total_energy_consumption, color=colors[row], alpha=0.6)
    ax[0].bar(label, sum_below_degrees, color='blue', alpha=0.6)

weather_df.set_index('date', inplace=True)
monthly_avg_temperatures = weather_df['avg_temperature'].resample('ME').mean()

ax[0].set_xlabel('Heating period and consumption / Sum of degrees under {}° (the lower the better)'.format(
    below_degrees))
ax[0].set_ylabel('Sum of degrees under {}°\nTotal consumption ({})'.format(below_degrees,
                                                                           heating_consumption_unit[0]))
ax[0].set_title('Total {} consumption per year'.format(energy_source))
ax[0].set_yticks(np.arange(0, heating_consumption_unit[1], heating_consumption_unit[2]))
ax[0].grid(True, axis='y')
ax[0].legend()

ax[1].plot(monthly_avg_temperatures.index, monthly_avg_temperatures.values)

ax[1].set_xlim([mdates.date2num(pd.Timestamp('{}-07-01'.format(years[0]))),
                mdates.date2num(pd.Timestamp('{}-08-30'.format(years[years.__len__() - 1] + 1)))])
ax[1].set_title('Monthly average temperatures')
ax[1].set_xlabel('Month')
ax[1].set_ylabel('Average temperature')
ax[1].set_yticks(np.arange(0, 30, 5))
ax[1].grid(True, axis='y')

plt.tight_layout()
plt.show()
