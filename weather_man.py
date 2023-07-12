
import os
from collections import defaultdict
import csv
import argparse
from abc import ABC, abstractmethod
from datetime import datetime


# ANSI escape sequences for colors
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
END_COLOR = "\033[0m"

# class Parse_data


def print_cyan(text):
    print(f"{CYAN}{text}{END_COLOR}",  end="")


def print_green(text):
    print(f"{GREEN} {text}{END_COLOR}",  end="")


def print_red(text):
    print(f"{RED} {text}{END_COLOR}",  end="")


class Parse_Data:
    def __init__(self):
        self.weather_reading = defaultdict(lambda: defaultdict(dict))

    def parse_weather_data(self, folder_path):
        for filename in os.listdir(folder_path):
            # Filter files with a specific extension, e.g., .txt
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, 'r') as file:
                    reader = csv.DictReader(file, delimiter=',')

                    # Skip the header line
                    next(reader)

                    monthly_data = []
                    year, month = None, None

                    for row in reader:

                        # Check if the row is blank
                        if not any(row.values()):
                            continue

                        # Retrieve the 'date' value from the row using 'get()' with two possible key names
                        date_value = row.get('PKST') or row.get('PKT')

                        if not year or not month:
                            if date_value:
                                # Extract year and month from the first row
                                date_parts = date_value.split('-')
                                year, month = date_parts[0], date_parts[1]

                        # Store the row dictionary in monthly_data
                        monthly_data.append(row)

                if year and month:
                    self.weather_reading[year][month] = monthly_data

        return self.weather_reading

# Class for calculations for reports


class Weather_Report_Calculation:
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
                    'Max TemperatureC', float("-inf"))

                self.get_max_temperature(max_temperature_str, day, month)

                min_temperature_str = daily.get(
                    'Min TemperatureC', float("inf"))
                self.get_min_temperature(min_temperature_str, day, month)

                max_humidity_str = daily.get('Max Humidity', float("-inf"))
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
                    'Max TemperatureC', float("-inf"))

                max_temperature_average = self.get_max_temperature_average(
                    max_temperature_str)

                min_temperature_str = daily.get(
                    'Min TemperatureC', float("inf"))
                min_temperature_average = self.get_min_temperature_average(
                    min_temperature_str)

                mean_humidity_str = daily.get('Mean Humidity', float("-inf"))
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
                    'Max TemperatureC', float("-inf"))
                min_temperature_str = daily.get(
                    'Min TemperatureC', float("inf"))

                if max_temperature_str:
                    print_cyan(day + 1)
                    print_red('+' * int(max_temperature_str))
                    print_cyan(f"{float(max_temperature_str)}°C \n")
                else:
                    pass

                if min_temperature_str:
                    print_cyan(day + 1)
                    print_green('+' * int(min_temperature_str))
                    print_cyan(f"{float(min_temperature_str)}°C\n")
                else:
                    pass
        else:
            print("\nSorry, Don't have data  for this year..  \n")

    def bounus(self, year, month, weather_data):
        print("\nHorizontal Bar Reports for highest and lowest temperatures in single line.. \n")
        if weather_data[year]:
            print("Inn ")
            for day, daily in enumerate(weather_data.get(year, {}).get(month, [])):
                max_temperature_str = daily.get(
                    'Max TemperatureC', float("-inf"))
                min_temperature_str = daily.get(
                    'Min TemperatureC', float("inf"))

                if max_temperature_str and min_temperature_str:
                    print_cyan(day + 1)
                    print_green('+' * int(min_temperature_str))
                    print_red('+' * int(max_temperature_str))
                    print_cyan(
                        f"{float(min_temperature_str)}°C - {float(max_temperature_str)}°C\n")
                else:
                    pass
        else:
            print("\nSorry, Don't have data  for this year..  \n")


class Reporting(ABC):
    def __init__(self):
        self.stats = {}

    @abstractmethod
    def is_record_required(self, record):
        pass

    @abstractmethod
    def perform_calculations(self, record):
        pass

    def process_records(self, record):
        if self.is_record_required(record):
            self.perform_calculations(record)


class MaxTempStat(Reporting):
    def __init__(self, from_date, to_date):
        self.stats = {'from_date': from_date,
                      'to_date': to_date}
        self.max_temp = float("-inf")

    @staticmethod
    def compare_dates(start, end, date_to_compare):
        return start <= date_to_compare <= end

    def is_record_required(self, date_to_compare):
        from_date = self.stats['from_date']
        to_date = self.stats['to_date']

        start_date = datetime.strptime(from_date, '%Y-%m-%d')
        end_date = datetime.strptime(to_date, '%Y-%m-%d')
        compare_date = datetime.strptime(date_to_compare['PKT'], '%Y-%m-%d')
        return MaxTempStat.compare_dates(start_date, end_date, compare_date)

    def perform_calculations(self, record):
        if record['Max TemperatureC']:
            if int(record['Max TemperatureC']) > self.max_temp:
                self.max_temp = int(record['Max TemperatureC'])


def main():
    # Folder path
    folder_path = "../weatherfiles"
    weather_data = Parse_Data()
    # Returning Parsed data
    parsed_data = weather_data.parse_weather_data(folder_path)

    # Now Calculating the results
    cal = Weather_Report_Calculation()
    max_temp = MaxTempStat('2005-5-1', '2005-5-10')
    max_temp.process_records(parsed_data['2005']['5'][5])

    # Custom type function for year and month validation
    # def validate_year_month(value):
    #     if value is None:
    #         raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")
    #     try:
    #         year, month = value.split('/')
    #         year = int(year)
    #         month = int(month)
    #         if year < 0 or month < 1 or month > 12:
    #             raise argparse.ArgumentTypeError(
    #                 "Invalid YEAR/MONTH format or values")
    #         return str(year), str(month)
    #     except ValueError:
    #         raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")

    # # Create an ArgumentParser object
    # parser = argparse.ArgumentParser(description="Weather Report Program")

    # # Add argument for -c flag
    # parser.add_argument("-c", metavar="YEAR/MONTH",
    #                     type=validate_year_month,
    #                     help="Generate horizontal bar charts for a specific year and month")

    # # Add argument for -a flag
    # parser.add_argument("-a", metavar="YEAR/MONTH",
    #                     type=validate_year_month,
    #                     help="Generate monthly report for a specific year and month")

    # # Add argument for -e flag
    # parser.add_argument("-e", metavar="YEAR",
    #                     type=int,
    #                     help="Generate yearly report for a specific year")

    # # Add argument for -b flag
    # parser.add_argument("-b", metavar="YEAR/MONTH",
    #                     type=validate_year_month,
    #                     help="Generate bonus report for a specific year and month")

    # # Parse the command-line arguments
    # args = parser.parse_args()

    # # Process the -c flag
    # if args.c:
    #     year, month = args.c
    #     cal.horizontal_bar_charts(year, month, parsed_data)

    # # Process the -a flag
    # if args.a:
    #     year, month = args.a
    #     cal.monthly_report(year, month, parsed_data)

    # # Process the -e flag
    # if args.e:
    #     year = args.e
    #     cal.yearly_report(year, parsed_data)

    # # Process the -b flag
    # if args.b:
    #     year, month = args.b
    #     cal.bounus(year, month, parsed_data)


if __name__ == "__main__":
    main()
