from abc import ABC, abstractmethod
from datetime import datetime
import argparse
from weather_man import ParseData


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
        self.stats = {'from_date': datetime.strptime(from_date, '%Y-%m-%d'),
                      'to_date': datetime.strptime(to_date, '%Y-%m-%d'),
                      'max_temp': float("-inf")}

    @staticmethod
    def compare_dates(start, end, date_to_compare):
        return start <= date_to_compare <= end

    def is_record_required(self, date_to_compare):
        compare_date = datetime.strptime(date_to_compare['PKT'], '%Y-%m-%d')
        return MaxTempStat.compare_dates(self.stats['from_date'], self.stats['to_date'], compare_date)

    def perform_calculations(self, record):
        print("reciord", record['Max TemperatureC'])
        if record['Max TemperatureC']:
            if int(record['Max TemperatureC']) > self.stats['max_temp']:
                self.stats['max_temp'] = int(record['Max TemperatureC'])
                print(self.stats['max_temp'])


def main():
    # Folder path
    folder_path = "../weatherfiles"
    weather_data = ParseData()
    # Returning Parsed data
    parsed_data = weather_data.parse_weather_data(folder_path)

    # Custom type function for year and month validation

    def validate_date(date):
        if date is None:
            raise argparse.ArgumentTypeError("No value for date found")
        try:
            year, month, day = date.split('-')
            year = int(year)
            month = int(month)
            day = int(day)
            if year < 0 or day < 1  or day > 31 or month < 1 or month > 12:
                raise argparse.ArgumentTypeError(
                    "Invalid YEAR/MONTH format or values")
            return date
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid YEAR/MONTH format")

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Weather related stats reporting  Program")

    # Add argument for -f flag
    parser.add_argument("-f", metavar="from_date",
                        type=validate_date,
                        help="Getting from date for a range")

    # Add argument for -t flag
    parser.add_argument("-t", metavar="to_date",
                        type=validate_date,
                        help="Getting to date for a range")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Process the -f anf -t  flag
    if args.f and args.t:
        max_temp = MaxTempStat(args.f, args.t)
        max_temp.process_records(parsed_data['2005']['5'][15])


if __name__ == "__main__":
    main()
