
import os
from collections import defaultdict
import csv
import argparse

# ANSI escape sequences for colors
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"

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

                    line = next(file)
                    monthly_data = []
                    # Split the line using CSV reader
                    data = list(csv.reader([line]))[0]
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


# Class for calculations for reports
class Weather_report_calculation:
    def __init__(self) -> None:
        self.max_temperature = {'temperature': float(
            '-inf'), 'day': '', 'month': ''}

        self.min_temperature = {'temperature': float(
            'inf'), 'day': '', 'month': ''}

        self.max_humidity = {'humidity': float(
            '-inf'), 'day': '', 'month': ''}

        self.mean_humidities = []
        self.max_temperatures = []
        self.min_temperatures = []

    def get_max_temperature(self, temperature, day, month):

        if temperature:
            temperature = float(temperature)
            if self.max_temperature['temperature'] != max(self.max_temperature['temperature'], temperature):
                self.max_temperature['day'] = day + 1
                self.max_temperature['month'] = month

            self.max_temperature['temperature'] = max(
                self.max_temperature['temperature'], temperature)

    def get_min_temperature(self, temperature, day, month):

        if temperature:

            temperature = float(temperature)
            if self.min_temperature['temperature'] != min(self.min_temperature['temperature'], temperature):
                self.min_temperature['day'] = day + 1
                self.min_temperature['month'] = month

            self.min_temperature['temperature'] = min(
                self.min_temperature['temperature'], temperature)

    def get_max_humidity(self, humidity, day, month):

        if humidity:

            humidity = float(humidity)
            if self.max_humidity['humidity'] != max(self.max_humidity['humidity'], humidity):
                self.max_humidity['day'] = day + 1
                self.max_humidity['month'] = month

            self.max_humidity['humidity'] = max(
                self.max_humidity['humidity'], humidity)

    def yearly_report(self, year, weather_data):
        for month in weather_data.get(year, {}):
            for day, daily in enumerate(weather_data.get(year, {}).get(month, [])):

                max_temperature_str = daily.get(
                    'max_temperature', float("-inf"))
                if max_temperature_str:
                    self.get_max_temperature(max_temperature_str, day, month)
                min_temperature_str = daily.get(
                    'min_temperature', float("inf"))

                if min_temperature_str:
                    self.get_min_temperature(min_temperature_str, day, month)
                max_humidity_str = daily.get('max_humidity', float("-inf"))

                if max_humidity_str:
                    self.get_max_humidity(max_humidity_str, day, month)

        print(f'\nYearly Report for {year} .....\n')
        print(
            f'Max Temperature: {self.max_temperature["temperature"]}°C (Day: {self.max_temperature["day"]}, Month: {self.max_temperature["month"]})')
        print(
            f'Min Temperature: {self.min_temperature["temperature"]}°C (Day: {self.min_temperature["day"]}, Month: {self.min_temperature["month"]})')
        print(
            f'Max Humidity: {self.max_humidity["humidity"]}% (Day: {self.max_humidity["day"]}, Month: {self.max_humidity["month"]})')

    def get_max_temperature_average(self, max_temperature_str):
        if max_temperature_str:
            self.max_temperatures.append(float(max_temperature_str))

        if len(self.max_temperatures):
            return sum(self.max_temperatures)/len(self.max_temperatures)

    def get_min_temperature_average(self, min_temperature_str):
        if min_temperature_str:
            self.min_temperatures.append(float(min_temperature_str))

        if len(self.min_temperatures):
            return sum(self.min_temperatures)/len(self.min_temperatures)

    def get_mean_humidities_average(self, mean_humidity_str):
        if mean_humidity_str:
            self.mean_humidities.append(float(mean_humidity_str))

        if len(self.mean_humidities):
            return sum(self.mean_humidities)/len(self.mean_humidities)

    def monthly_report(self, year, month, weather_data):
        max_temperature_average = None
        min_temperature_average = None
        mean_humidity_average = None

        if weather_data[year]:
            for daily in (weather_data.get(year, {}).get(month, [])):

                max_temperature_str = daily.get(
                    'max_temperature', float("-inf"))

                max_temperature_average = self.get_max_temperature_average(
                    max_temperature_str)

                min_temperature_str = daily.get(
                    'min_temperature', float("inf"))
                min_temperature_average = self.get_min_temperature_average(
                    min_temperature_str)

                mean_humidity_str = daily.get('mean_humidity', float("-inf"))
                mean_humidity_average = self.get_mean_humidities_average(
                    mean_humidity_str)

            print(f'\nMonthly Report for {month}/{year} .....\n')
            print(
                f'Highest Temperature Average: {round(max_temperature_average,2)}°C')
            print(
                f'Lowest Temperature Average: {round(min_temperature_average,2)}°C')
            print(f'Mean Humidity Average: {round(mean_humidity_average,2)}%')
        else:
            print("\nSorry, Don't have data  for this year.. \n ")

    def horizontal_bar_charts(self, year, month, weather_data):
        print("\nHorizontal Bar Reports for highest and lowest temperatures in multiple lines.. \n")
        if weather_data[year]:
            for day, daily in enumerate(weather_data.get(year, {}).get(month, [])):

                max_temperature_str = daily.get(
                    'max_temperature', float("-inf"))
                min_temperature_str = daily.get(
                    'min_temperature', float("inf"))

                if max_temperature_str:
                    print(
                        f"\n{CYAN} {day + 1}  {RED }  { '+' * int(max_temperature_str)}   {CYAN}{float(max_temperature_str)}°C")
                else:
                    pass

                if min_temperature_str:
                    print(
                        f"{CYAN} {day + 1}  {GREEN }  { '+' * int(min_temperature_str)}  {CYAN} {float(min_temperature_str)}°C\n")
                else:
                    pass
        else:
            print("\nSorry, Don't have data  for this year..  \n")

    def bounus(self, year, month, weather_data):
        print("\nHorizontal Bar Reports for highest and lowest temperatures in single line.. \n")
        if weather_data[year]:
            for day, daily in enumerate(weather_data.get(year, {}).get(month, [])):
                max_temperature_str = daily.get(
                    'max_temperature', float("-inf"))
                min_temperature_str = daily.get(
                    'min_temperature', float("inf"))

                if max_temperature_str and min_temperature_str:
                    print(f"\n{CYAN} {day + 1} "
                          f"{GREEN} {'+' * int(min_temperature_str)}"
                          f"{RED} {'+' * int(max_temperature_str)} "
                          f"{CYAN} {float(min_temperature_str)}°C - {CYAN}{float(max_temperature_str)}°C")
                elif max_temperature_str:
                    print(f"\n{CYAN} {day + 1} "
                          f"{RED} {'+' * int(max_temperature_str)} "
                          f"{CYAN}{float(max_temperature_str)}°C")
                elif min_temperature_str:
                    print(f"\n{CYAN} {day + 1} "
                          f"{RED} {'+' * int(min_temperature_str)} "
                          f"{CYAN}{float(min_temperature_str)}°C")
                else:
                    pass
        else:
            print("\nSorry, Don't have data  for this year..  \n")


def main():
    # Folder path
    folder_path = "../weatherfiles"
    weather_data = Parse_data()
    # Returning Parsed data
    parsed_data = weather_data.parse_weather_data(folder_path)

    # Now Calculating the results
    cal = Weather_report_calculation()

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Weather Report Program")

    # Add argument for -c flag
    parser.add_argument("-c", metavar="YEAR/MONTH",
                        help="Generate horizontal bar charts for a specific year and month")

    # Add argument for -a flag
    parser.add_argument("-a", metavar="YEAR/MONTH",
                        help="Generate monthly report for a specific year and month")

    # Add argument for -e flag
    parser.add_argument("-e", metavar="YEAR",
                        help="Generate yearly report for a specific year")

    # Add argument for -b flag
    parser.add_argument("-b", metavar="YEAR/MONTH",
                        help="Generate bonus report for a specific year and month")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Process the -c flag
    if args.c:
        year, month = args.c.split('/')
        # Perform validation on year and month
        if not year.isdigit() or not month.isdigit() or int(year) < 0 or int(month) < 1 or int(month) > 12:
            print("Invalid YEAR/MONTH format or values")
            return
        cal.horizontal_bar_charts(year, month, parsed_data)

    # Process the -a flag
    if args.a:
        year, month = args.a.split('/')
        # Perform validation on year and month
        if not year.isdigit() or not month.isdigit() or int(year) < 0 or int(month) < 1 or int(month) > 12:
            print("Invalid YEAR/MONTH format or values")
            return
        cal.monthly_report(year, month, parsed_data)

    # Process the -e flag
    if args.e:
        year = args.e
        # Perform validation on year
        if not year.isdigit() or int(year) < 0:
            print("Invalid YEAR value")
            return
        cal.yearly_report(year, parsed_data)

    # Process the -b flag
    if args.b:
        year, month = args.b.split('/')
        # Perform validation on year and month
        if not year.isdigit() or not month.isdigit() or int(year) < 0 or int(month) < 1 or int(month) > 12:
            print("Invalid YEAR/MONTH format or values")
            return
        cal.bounus(year, month, parsed_data)


if __name__ == "__main__":
    main()
