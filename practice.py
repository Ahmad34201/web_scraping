import datetime
import pytz

pakistan_tz = pytz.timezone('Asia/Karachi')
current_time = datetime.datetime.now(pakistan_tz)
print(current_time)
print(datetime.datetime.now())
