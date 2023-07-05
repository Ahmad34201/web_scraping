
import os
# class Parse_data:


class WeatherData:
    def __init__(self):
        self.weather_reading = {}

    def parse_weather_data(self, folder_path):

        for filename in os.listdir(folder_path):
            # Filter files with a specific extension, e.g., .txt
            if filename.endswith(".txt"):

                file_path = os.path.join(folder_path, filename)

                with open(file_path, 'r') as file:
                    # Skip the header line
                    next(file)
                    weather_data = []
                    for line in file:
                        line = line.strip()
                        if line:
                            data = line.split(',')

                            # Create a dictionary and store the data

                            weather_data.append({
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
                            })
            
            filename.strip()
            # getting a particular year from filename
            year = filename.split('_')[2]
            if year not in self.weather_reading:
                self.weather_reading[year] = []
                
            self.weather_reading[year].append(weather_data)

folder_path = "../weatherfiles"
weather_data = WeatherData()
weather_data.parse_weather_data(folder_path)
# Accessing the parsed data

for year, data in weather_data.weather_reading.items():
    print(f"Year: {year}, Data Length: {len(data)}")
            
