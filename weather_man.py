from collections import defaultdict
import argparse
import datetime
import calendar
import csv
import os
import re
from reporting import *


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


def discover_files(folder_path, extension='txt'):
    file_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith("." + extension):
            file_list.append(filename)
    return file_list


def extract_year_and_month(filename):
    # Correct regular expression to find the year (four consecutive digits) and the month abbreviation (three letters) in the filename
    year_month_match = re.search(
        r"(\d{4}).*?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", filename)

    if year_month_match:
        year = year_month_match[1]
        month_abbrev = year_month_match[2]  # Capture the month abbreviation
        # Convert month abbreviation to its numerical representation
        month = month_to_number(month_abbrev)

        return year, month
    else:
        return None, None


class ParseData:
    def __init__(self):
        self.weather_reading = defaultdict(lambda: defaultdict(dict))

    def parse_weather_data(self, folder_path, year_to_read, month_to_read):
        files_to_read = discover_files(folder_path, extension='txt')

        for filename in files_to_read:
            file_path = os.path.join(folder_path, filename)

            year, month = extract_year_and_month(filename)

            if year_to_read == year and month_to_read == month:
                with open(file_path, 'r') as file:
                    reader = csv.DictReader(file, delimiter=',')

                    # Skip the header line
                    next(reader)

                    monthly_data = []

                    for row in reader:
                        # Check if the row is blank
                        if not any(row.values()):
                            continue

                        # Retrieve the 'date' value from the row using 'get()' with two possible key names
                        date_value = row.get('PKST') or row.get('PKT')

                        if date_value:
                            datetime_obj = datetime.strptime(
                                date_value, "%Y-%m-%d")
                            year, month = str(datetime_obj.year), str(
                                datetime_obj.month)

                        # Store the row dictionary in monthly_data
                        monthly_data.append(row)

                if year and month:
                    self.weather_reading[year][month] = monthly_data

        return self.weather_reading


def get_dates(year, month):
    from_date = datetime.strptime(f'{year}-{month}-{1}', '%Y-%m-%d')
    start, end = calendar.monthrange(year, month)

    to_date = datetime.strptime(f'{year}-{month}-{end}', '%Y-%m-%d')
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


def month_to_number(month_name):
    months_dict = {
        'Jan': '1',
        'Feb': '2',
        'Mar': '3',
        'Apr': '4',
        'May': '5',
        'Jun': '6',
        'Jul': '7',
        'Aug': '8',
        'Sep': '9',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    # upper_month_name = month_name.upper()
    return months_dict.get(month_name)


def process_statistics(year, month, statistics_classes, parsed_data):
    chain_process = ChainProcess(*statistics_classes)

    for month in parsed_data.get(year, {}):
        for daily in parsed_data.get(year, {}).get(month, []):
            chain_process.process_record(daily)

    stats = chain_process.collect_stats()
    return stats

# Returning Parsed data


def handle_file_handling(args, year, month):
    folder_path = args.path
    weather_data = ParseData()
    return weather_data.parse_weather_data(folder_path, year, month)


def process_statistics_for_flags(args, year, month, statistics_classes):
    parsed_data = handle_file_handling(args, year, month)
    start, end = get_dates(int(year), int(month))

    # Create the necessary statistics classes
    preprocessor = RecordPreprocessor()
    statistics_instances = [cls(start, end) for cls in statistics_classes]
    statistics_instances.insert(0, preprocessor)

    stats = process_statistics(year, month, statistics_instances, parsed_data)
    return stats


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

    parser.add_argument("-path", metavar="PATH", type=str, required=True,
                        help="Folder Path for files")  # Making args.path a required parameter

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.e:
        year, month = args.e
        statistics_classes = [MaxTempStat, MaxHumidityStat, MinTempStat]
        stats = process_statistics_for_flags(
            args, year, month, statistics_classes)
        print(f"Highest temperature: {stats['max_temp']:.2f}C")
        print(f"Lowest temperature: {stats['min_temp']:.2f}C")
        print(f"Maximum humidity: {stats['max_humidity']:.2f}C")

    if args.a:
        year, month = args.a
        statistics_classes = [AverageMaxTempStat,
                              AverageMinTempStat, AverageMeanHumidity]
        stats = process_statistics_for_flags(
            args, year, month, statistics_classes)
        print(f"Highest average temperature: {stats['average_max_temp']:.2f}C")
        print(f"Lowest average temperature: {stats['average_min_temp']:.2f}C")
        print(f"Average mean humidity: {stats['average_mean_humidity']:.2f}C")

    if args.c:
        year = args.c
        statistics_classes = [MaxTempStat, MaxHumidityStat, MinTempStat]
        for month in range(1, 13):
            stats = process_statistics_for_flags(
                args, year, str(month), statistics_classes)
            print(f"For month {month}:")
            print(f"Highest temperature: {stats['max_temp']:.2f}C")
            print(f"Lowest temperature: {stats['min_temp']:.2f}C")
            print(f"Maximum humidity: {stats['max_humidity']:.2f}C")


if __name__ == "__main__":
    main()
