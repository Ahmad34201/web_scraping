

# class Parse_data:

class WeatherData:
    def __init__(self):
        self.weather_reading = []

    def parse_weather_file(self, file_path):
        with open(file_path, 'r') as file:
            # Skip the header line
            next(file)

            for line in file:
                line = line.strip()
                if line:
                    data = line.split(',')

                    # Create a dictionary and store the data

                    self.weather_reading = {
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


# Example usage
file_path = "./weatherfiles/Murree_weather_2004_Aug.txt"
weather_data = WeatherData()
weather_data.parse_weather_file(file_path)
# Accessing the parsed data
print(weather_data.weather_reading)
