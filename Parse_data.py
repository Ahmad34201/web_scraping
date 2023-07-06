
import os
from collections import defaultdict


# class Parse_data
class Parse_data:
    def __init__(self):
        self.weather_reading = defaultdict(lambda: defaultdict(dict))

    def parse_daily_data(self, data):
        daywise_data = {
            'date': data[0],
            'max_temperature': data[1],
            'mean_temperature': data[2],
            'min_temperature': data[3],
            'dew_point': data[4],
            'mean_dew_point': data[5],
            'min_dew_point': data[6],
            'max_humidity': data[7],
            'mean_humidity': data[8],
            'min_humidity': data[9],
            'max_sea_level_pressure': data[10],
            'mean_sea_level_pressure': data[11],
            'min_sea_level_pressure': data[12],
            'max_visibility': data[13],
            'mean_visibility': data[14],
            'min_visibility': data[15],
            'max_wind_speed': data[16],
            'mean_wind_speed': data[17],
            'max_gust_speed': data[18],
            'precipitation': data[19],
            'cloud_cover': data[20],
            'events': data[21],
            'wind_direction_degrees': data[22]
        }
        return daywise_data

    def parse_weather_data(self, folder_path):

        for filename in os.listdir(folder_path):
            # Filter files with a specific extension, e.g., .txt
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, 'r') as file:
                    # Skip the header line
                    next(file)
                    monthly_data = []
                    # Purpose for to get year and month
                    data = next(file).split(',')
                    year, month, day = data[0].split('-')
                    monthly_data.append(self.parse_daily_data(data))

                    for line in file:
                        line = line.strip()
                        if line:
                            data = line.split(',')
                            # Create a dictionary and store the data
                            monthly_data.append(self.parse_daily_data(data))

            self.weather_reading[year][month] = monthly_data
        return self.weather_reading


class Weather_report_Calculation:
    def __init__(self) -> None:
        self.max_temperature = {'temperature': float(
            '-inf'), 'day': '', 'month': ''}

        self.min_temperature = {'temperature': float(
            'inf'), 'day': '', 'month': ''}

        self.max_humidity = {'humidity': float(
            '-inf'), 'day': '', 'month': ''}

    def tofind_max_temperature(self, temperature, day, month):

        if temperature:
            try:
                temperature = float(temperature)
                if self.max_temperature['temperature'] != max(self.max_temperature['temperature'], temperature):
                    self.max_temperature['day'] = day
                    self.max_temperature['month'] = month

                self.max_temperature['temperature'] = max(
                    self.max_temperature['temperature'], temperature)

            except ValueError:
                pass

    def tofind_min_temperature(self, temperature, day, month):

        if temperature:
            try:
                temperature = float(temperature)
                if self.min_temperature['temperature'] != min(self.min_temperature['temperature'], temperature):
                    self.min_temperature['day'] = day
                    self.min_temperature['month'] = month

                self.min_temperature['temperature'] = min(
                    self.min_temperature['temperature'], temperature)

            except ValueError:
                pass

    def tofind_max_humidity(self, humidity, day, month):

        if humidity:
            try:
                humidity = float(humidity)
                if self.max_humidity['humidity'] != max(self.max_humidity['humidity'], humidity):
                    self.max_humidity['day'] = day
                    self.max_humidity['month'] = month

                self.max_humidity['humidity'] = max(
                    self.max_humidity['humidity'], humidity)

            except ValueError:
                pass

    def yearly_report(self, year, weatherData):
        for month in weatherData.get(year, {}):
            for day, daily in enumerate(weatherData.get(year, {}).get(month, [])):
                max_temperature_str = daily.get(
                    'max_temperature', float("-inf"))
                self.tofind_max_temperature(max_temperature_str, day, month)
                min_temperature_str = daily.get(
                    'min_temperature', float("inf"))
                self.tofind_min_temperature(min_temperature_str, day, month)
                max_humidity_str = daily.get('max_humidity', float("-inf"))
                self.tofind_max_humidity(max_humidity_str, day, month)

        print(
            f'Max Temperature: {self.max_temperature["temperature"]}C (Day: {self.max_temperature["day"]}, Month: {self.max_temperature["month"]})')
        print(
            f'Min Temperature: {self.min_temperature["temperature"]}C (Day: {self.min_temperature["day"]}, Month: {self.min_temperature["month"]})')
        print(
            f'Max Humidity: {self.max_humidity["humidity"]}% (Day: {self.max_humidity["day"]}, Month: {self.max_humidity["month"]})')


# Folder path
folder_path = "../weatherfiles"
weather_data = Parse_data()
# Returning Parsed data
parsed_data = weather_data.parse_weather_data(folder_path)

# # Now Calculating the result's
cal = Weather_report_Calculation()

cal.yearly_report('2005', parsed_data)
