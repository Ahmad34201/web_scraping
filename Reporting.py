from abc import ABC, abstractmethod
from datetime import datetime

class Reporting(ABC):
    def __init__(self):
        self.stats = {}

    def is_record_required(self, record):
        return self.stats['from_date'] <= record['PKT'] <= self.stats['to_date']

    @abstractmethod
    def perform_calculations(self, record):
        pass

    def process_record(self, record):
        if self.is_record_required(record):
            self.perform_calculations(record)


class MaxTempStat(Reporting):
    def __init__(self, from_date, to_date):
        self.stats = {'from_date': from_date,
                      'to_date': to_date,
                      'max_temp': float("-inf")}

    def perform_calculations(self, record):
        print("Before Max temp ", self.stats['max_temp'])
        if record['Max TemperatureC']:
            self.stats['max_temp'] = max(
                (self.stats['max_temp']), (record['Max TemperatureC']))
        print("Before Max temp ", self.stats['max_temp'])


class MinTempStat(Reporting):
    def __init__(self, from_date, to_date):
        self.stats = {'from_date': from_date,
                      'to_date': to_date,
                      'min_temp': float("inf")}

    def perform_calculations(self, record):
        print("Before Min temp ", self.stats['min_temp'])
        if record['Min TemperatureC']:
            self.stats['min_temp'] = min(
                (self.stats['min_temp']), (record['Min TemperatureC']))
        print("After min temp ", self.stats['min_temp'])


class MaxHumidityStat(Reporting):
    def __init__(self, from_date, to_date):
        self.stats = {'from_date': from_date,
                      'to_date': to_date,
                      'max_humidity': float("-inf")}

    def perform_calculations(self, record):
        print("Before max humidity ", self.stats['max_humidity'])
        if record['Max Humidity']:
            self.stats['max_humidity'] = min(
                (self.stats['max_humidity']), (record['Max Humidity']))
        print("After max humidity ", self.stats['max_humidity'])


class ChainProcess:
    def __init__(self, *args):
        self.handlers = args

    def process_record(self, record):
        for handler in self.handlers:
            handler.process_record(record)


class RecordPreprocessor:
    def process_record(self, record):
        if 'PKT' not in record:
            record['PKT'] = record.pop('PKST')
        record['PKT'] = datetime.strptime(record['PKT'], '%Y-%m-%d')

        if record['Max TemperatureC']:
            record['Max TemperatureC'] = float(record['Max TemperatureC'])
        else:
            record['Max TemperatureC'] = None

        if record['Min TemperatureC']:
            record['Min TemperatureC'] = float(record['Min TemperatureC'])
        else:
            record['Min TemperatureC'] = None

        if record['Max Humidity']:
            record['Max Humidity'] = float(record['Max Humidity'])
        else:
            record['Max Humidity'] = None

        return record
