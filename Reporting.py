from abc import ABC, abstractmethod
from datetime import datetime


class Reporting(ABC):
    def __init__(self):
        self.stats = {}

    @abstractmethod
    def is_record_required(self, record):
        pass

    @abstractmethod
    def perform_calculations(self, record):
        pass

    @staticmethod
    def compare_dates(start, end, date_to_compare):
        return start <= date_to_compare <= end

    def process_records(self, record):
        if self.is_record_required(record):
            self.perform_calculations(record)


class MaxTempStat(Reporting):
    def __init__(self, from_date, to_date, weather_data):
        self.stats = {'from_date': datetime.strptime(from_date, '%Y-%m-%d'),
                      'to_date': datetime.strptime(to_date, '%Y-%m-%d'),
                      'max_temp': float("-inf")}

        self.set_max_temp(weather_data)

    def set_max_temp(self, weather_data):
        year = str(self.stats['from_date'].year)
        from_month = str(self.stats['from_date'].month)
        to_month = str(self.stats['to_date'].month)

        if from_month is to_month:
            for daily in weather_data.get(year, {}).get(month, []):
                max_temperature_str = daily.get(
                    'Max TemperatureC', float("-inf"))

                if max_temperature_str:
                    self.stats['max_temp'] = max(
                        self.stats['max_temp'], float(max_temperature_str))
        else:
            for month in weather_data.get(year, {}):
                for daily in weather_data.get(year, {}).get(month, []):
                    max_temperature_str = daily.get(
                        'Max TemperatureC', float("-inf"))

                    if max_temperature_str:
                        self.stats['max_temp'] = max(
                            self.stats['max_temp'], float(max_temperature_str))

    def is_record_required(self, date_to_compare):
        compare_date = datetime.strptime(date_to_compare['PKT'], '%Y-%m-%d')
        return self.compare_dates(self.stats['from_date'], self.stats['to_date'], compare_date)

    def perform_calculations(self, record):
        if record['Max TemperatureC']:
            self.stats['max_temp'] = max(
                (self.stats['max_temp']), float(record['Max TemperatureC']))


class MinTempStat(Reporting):
    def __init__(self, from_date, to_date, weather_data):
        self.stats = {'from_date': datetime.strptime(from_date, '%Y-%m-%d'),
                      'to_date': datetime.strptime(to_date, '%Y-%m-%d'),
                      'min_temp': float("inf")}

        self.set_min_temp(weather_data)

    def set_min_temp(self, weather_data):
        year = str(self.stats['from_date'].year)
        from_month = str(self.stats['from_date'].month)
        to_month = str(self.stats['to_date'].month)
        # if range is about to month
        if from_month is to_month:
            for daily in weather_data.get(year, {}).get(month, []):
                min_temperature_str = daily.get(
                    'Min TemperatureC', float("inf"))
                if self.stats['min_temp'] is None:
                    self.stats['min_temp'] = float(min_temperature_str)

                if min_temperature_str:
                    self.stats['min_temp'] = min(
                        self.stats['min_temp'], float(min_temperature_str))

        else:
            for month in weather_data.get(year, {}):
                for daily in weather_data.get(year, {}).get(month, []):
                    min_temperature_str = daily.get(
                        'Min TemperatureC', float("inf"))
                    if self.stats['min_temp'] is None:
                        self.stats['min_temp'] = float(min_temperature_str)

                    if min_temperature_str:
                        self.stats['min_temp'] = min(
                            self.stats['min_temp'], float(min_temperature_str))

    def is_record_required(self, date_to_compare):
        compare_date = datetime.strptime(date_to_compare['PKT'], '%Y-%m-%d')
        return self.compare_dates(self.stats['from_date'], self.stats['to_date'], compare_date)

    def perform_calculations(self, record):
        print("Before Min temp ", self.stats['min_temp'])
        if record['Min TemperatureC']:
            self.stats['min_temp'] = min(
                (self.stats['min_temp']), float(record['Min TemperatureC']))
        print("After min temp ", self.stats['min_temp'])


class MaxHumidityStat(Reporting):
    def __init__(self, from_date, to_date , weather_data):
        self.stats = {'from_date': datetime.strptime(from_date, '%Y-%m-%d'),
                      'to_date': datetime.strptime(to_date, '%Y-%m-%d'),
                      'max_humidity': float("-inf")}

        self.set_max_humidity(weather_data)

    def set_max_humidity(self, weather_data):
        year = str(self.stats['from_date'].year)
        from_month = str(self.stats['from_date'].month)
        to_month = str(self.stats['to_date'].month)
        # if range is about to a month
        if from_month is to_month:
            for daily in weather_data.get(year, {}).get(month, []):
                max_humidity_str = daily.get(
                    'Max Humidity', float("-inf"))

                if max_humidity_str:
                    self.stats['max_humidity'] = max(
                        self.stats['max_humidity'], float(max_humidity_str))

        else:
            for month in weather_data.get(year, {}):
                for daily in weather_data.get(year, {}).get(month, []):
                    max_humidity_str = daily.get(
                        'Max Humidity', float("-inf"))

                    if max_humidity_str:
                        self.stats['max_humidity'] = max(
                            self.stats['max_humidity'], float(max_humidity_str))

    @staticmethod
    def compare_dates(start, end, date_to_compare):
        return start <= date_to_compare <= end

    def is_record_required(self, date_to_compare):
        compare_date = datetime.strptime(date_to_compare['PKT'], '%Y-%m-%d')
        return self.compare_dates(self.stats['from_date'], self.stats['to_date'], compare_date)

    def perform_calculations(self, record):
        print("before max humidity ", self.stats['max_humidity'])
        if record['Max Humidity']:
            self.stats['max_humidity'] = min(
                (self.stats['max_humidity']), float(record['Max Humidity']))
        print("after max humidity ", self.stats['max_humidity'])
