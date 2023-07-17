from abc import ABC, abstractmethod
from datetime import datetime


class Reporting(ABC):
    def __init__(self, from_date, to_date, key, header_key):
        self.key = key
        self.header_key = header_key
        self.stats = {'from_date': from_date, 'to_date': to_date, self.key: 0}

    def is_record_required(self, record):
        return self.stats['from_date'] <= record['PKT'] <= self.stats['to_date']

    def perform_calculations(self, record):
        if record[self.header_key]:
            self.stats[self.key] = self.get_updated_stat(
                record[self.header_key])

    def process_record(self, record):
        if self.is_record_required(record):
            self.perform_calculations(record)

    @abstractmethod
    def get_updated_stat(self, new_value):
        pass


class MaxTempStat(Reporting):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'max_temp', 'Max TemperatureC')

    def get_updated_stat(self, new_value):
        return max(self.stats[self.key], new_value)


class MinTempStat(Reporting):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'min_temp', 'Min TemperatureC')

    def get_updated_stat(self, new_value):
        return min(self.stats[self.key], new_value)


class MaxHumidityStat(Reporting):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'max_humidity', 'Max Humidity')

    def get_updated_stat(self, new_value):
        return max(self.stats[self.key], new_value)


class AverageStat(Reporting):
    def __init__(self, from_date, to_date, key, header_key):
        super().__init__(from_date, to_date, key, header_key)
        self.count = 0

    def perform_calculations(self, record):
        if record[self.header_key]:
            self.count += 1
            self.stats[self.key] = (
                self.stats[self.key] + record[self.header_key]) / self.count
    
    def get_updated_stat(self):
        pass

class AverageMaxTempStat(AverageStat):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'average_max_temp', 'Max TemperatureC')


class AverageMinTempStat(AverageStat):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'average_min_temp', 'Min TemperatureC')


class AverageMeanHumidity(AverageStat):
    def __init__(self, from_date, to_date):
        super().__init__(from_date, to_date, 'average_mean_humidity', 'Mean Humidity')


class ChainProcess:
    def __init__(self, *args):
        self.handlers = args

    def process_record(self, record):
        for handler in self.handlers:
            handler.process_record(record)
    
    def collect_stats(self):
        results = {handler.key: handler.stats[handler.key] for handler in self.handlers[1:]}
        return results


class RecordPreprocessor:
    def process_record(self, record):
        if 'PKT' not in record:
            record['PKT'] = record.pop('PKST')
        if not isinstance(record["PKT"], datetime):
            record['PKT'] = datetime.strptime(record['PKT'], '%Y-%m-%d')

        for key in ['Max TemperatureC', 'Min TemperatureC', 'Max Humidity', 'Mean Humidity']:
            if key in record and record[key]:
                record[key] = float(record[key])
            else:
                record[key] = None

        return record
