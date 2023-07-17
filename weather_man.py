
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


def get_dates(year, month):
    from_date = datetime.datetime.strptime(f'{year}-{month}-{1}', '%Y-%m-%d')
    start, end = calendar.monthrange(year, month)

    to_date = datetime.datetime.strptime(f'{year}-{month}-{end}', '%Y-%m-%d')
    return from_date, to_date


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


def validate_year(value):
    if value is None:
        raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")
    try:
        year = int(value)
        if year < 0:
            raise argparse.ArgumentTypeError(
                "Invalid YEAR/MONTH format or values")
        return str(year)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")


def main():

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Weather Report Program")

    # Add argument for -c flag
    parser.add_argument("-c", metavar="YEAR",
                        type=validate_year,

                        help="Generate horizontal bar charts for a specific year and month")

    # Add argument for -a flag
    parser.add_argument("-a", metavar="YEAR/MONTH",
                        type=validate_year_month,
                        help="Generate monthly report for a specific year and month")

    # Add argument for -e flag
    parser.add_argument("-e", metavar="YEAR/MONTH",
                        type=validate_year_month,
                        help="Generate yearly report for a specific year")

    # Add argument for -b flag
    parser.add_argument("-path", metavar="PATH",
                        type=str,
                        help="Folder Path for files")

    # Parse the command-line arguments
    args = parser.parse_args()

    weather_data = ParseData()
    # Returning Parsed data
    if args.path:
        folder_path = args.path
        parsed_data = weather_data.parse_weather_data(folder_path)
    else:
        print("Folder Path not given")

    # Process the -e flag
    if args.e:
        year, month = args.e
        start, end = get_dates(int(year), int(month))
        max_humidity = MaxHumidityStat(start, end)
        max_temp = MaxTempStat(start, end)
        min_temp = MinTempStat(start, end)
        # have to create object of preprocessor
        preprocessor = RecordPreprocessor()
        chain_process = ChainProcess(
            preprocessor, max_temp, max_humidity, min_temp)
        for month in parsed_data.get(year, {}):
            for daily in parsed_data.get(year, {}).get(month, []):
                chain_process.process_record(daily)

        stats = chain_process.collect_stats()
        print(
            f"Highest temperature: {stats['max_temp']:.2f}C")
        print(
            f"Lowest temperature: {stats['min_temp']:.2f}C")
        print(
            f"Maximum humidity: {stats['max_humidity']:.2f}C")

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

        stats = chain_process.collect_stats()
        print(
            f"Highest average temperature: {stats['average_max_temp']:.2f}C")
        print(
            f"Lowest average temperature: {stats['average_min_temp']:.2f}C")
        print(
            f"Avergae mean humidity: {stats['average_mean_humidity']:.2f}C")

    # Process the -c flag
    if args.c:
        year = args.c
        for month in range(1, 13):
            start, end = get_dates(int(year), int(month))
            max_humidity = MaxHumidityStat(start, end)
            max_temp = MaxTempStat(start, end)
            min_temp = MinTempStat(start, end)

            # have to create object of preprocessor
            preprocessor = RecordPreprocessor()
            chain_process = ChainProcess(
                preprocessor, max_temp, max_humidity, min_temp)
            for month in parsed_data.get(year, {}):
                for daily in parsed_data.get(year, {}).get(month, []):
                    chain_process.process_record(daily)

        stats = chain_process.collect_stats()
        print(
            f"Highest temperature: {stats['max_temp']:.2f}C")
        print(
            f"Lowest temperature: {stats['min_temp']:.2f}C")
        print(
            f"Maximum humidity: {stats['max_humidity']:.2f}C")


if __name__ == "__main__":
    main()
