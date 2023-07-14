
import os
from collections import defaultdict
import csv
import argparse
import datetime
import calendar
from reporting import MaxTempStat, MinTempStat, MaxHumidityStat, ChainProcess, RecordPreprocessor, AverageMaxTempStat, AverageMinTempStat, AverageMeanHumidity


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


class ParseData:
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


class WeatherReportCalculation:
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


def get_dates(year, month):
    from_date = datetime.datetime.strptime(f'{year}-{month}-{1}', '%Y-%m-%d')
    start, end = calendar.monthrange(year, month)

    to_date = datetime.datetime.strptime(f'{year}-{month}-{end}', '%Y-%m-%d')
    return from_date, to_date


def main():
    # Folder path
    folder_path = "../weatherfiles"
    weather_data = ParseData()
    # Returning Parsed data
    parsed_data = weather_data.parse_weather_data(folder_path)

    # Now Calculating the results
    cal = WeatherReportCalculation()

    # Custom type function for year and month validation

    def validate_year_month(value):
        if value is None:
            raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")
        try:
            year, month = value.split('/')
            year = int(year)
            month = int(month)
            if year < 0 or month < 1 or month > 12:
                raise argparse.ArgumentTypeError(
                    "Invalid YEAR/MONTH format or values")
            return str(year), str(month)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Weather Report Program")

    # Add argument for -c flag
    parser.add_argument("-c", metavar="YEAR/MONTH",
                        type=validate_year_month,
                        help="Generate horizontal bar charts for a specific year and month")

    # Add argument for -a flag
    parser.add_argument("-a", metavar="YEAR/MONTH",
                        type=validate_year_month,
                        help="Generate monthly report for a specific year and month")

    # Add argument for -e flag
    parser.add_argument("-e", metavar="YEAR",
                        type=int,
                        help="Generate yearly report for a specific year")

    # Add argument for -b flag
    parser.add_argument("-b", metavar="YEAR/MONTH",
                        type=validate_year_month,
                        help="Generate bonus report for a specific year and month")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Process the -e flag
    if args.e:
        year, month = args.c
        start, end = get_dates(int(year), int(month))
        max_humidity = MaxHumidityStat(start, end)
        max_temp = MaxTempStat(start, end)
        min_temp = MinTempStat(start, end)
        avergae_max_temp = AverageMaxTempStat(start, end)
        # have to create object of preprocessor
        preprocessor = RecordPreprocessor()
        chain_process = ChainProcess(
            preprocessor, max_temp, max_humidity, min_temp, avergae_max_temp)
        for month in parsed_data.get(year, {}):
            for daily in parsed_data.get(year, {}).get(month, []):
                chain_process.process_record(daily)

        # cal.horizontal_bar_charts(year, month, parsed_data)

    # Process the -a flag
    if args.a:
        year, month = args.a
        start, end = get_dates(int(year), int(month))
        avergae_max_temp = AverageMaxTempStat(start, end)
        avergae_min_temp = AverageMinTempStat(start, end)
        avergae_mean_humidity = AverageMeanHumidity(start, end)

        # have to create object of preprocessor
        preprocessor = RecordPreprocessor()
        chain_process = ChainProcess(
            preprocessor, avergae_max_temp, avergae_min_temp, avergae_mean_humidity)
        for month in parsed_data.get(year, {}):
            for daily in parsed_data.get(year, {}).get(month, []):
                chain_process.process_record(daily)
        # cal.monthly_report(year, month, parsed_data)

    # Process the -e flag
    if args.e:
        year = args.e
        start, end = get_dates(int(year), int(month))
        max_temp = MaxHumidityStat(year, parsed_data)
        max_temp.process_records(parsed_data['2006']['5'][20])
        # cal.yearly_report(year, parsed_data)


if __name__ == "__main__":
    main()
