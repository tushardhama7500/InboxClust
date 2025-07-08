import time,datetime
from datetime import date
import random
def Stamp():
    event_number = random.randint(1000000000,9999999999)
    event_date = date.today()
    now = datetime.datetime.now()
    event_time = now.strftime("%H:%M:%S")
    ret_val = f"{event_date} {event_time}  Unique Id: {event_number}"
    return ret_val
