# coding: utf-8
# cron job: 
#   0 5 * * * /usr/bin/python3
#   /path/to/your_script.py

import requests
from datetime import datetime, timedelta
from caldav import DAVClient, Calendar
import re
from icalendar import Calendar, Event
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://forecast.weather.gov/product.php?site=IND&issuedby=IND&product=ZFP&format=txt&version=1&glossary=0"

r = requests.get(url)
splitted = r.text.split("\n")

cal_url = os.getenv("CAL_URL")
cal_user = os.getenv("CAL_USER")
cal_pass = os.getenv("CAL_PASS")
CITY = os.getenv("CITY")
       
client = DAVClient(cal_url, username=cal_user, password=cal_pass)
calendars = client.principal().calendars()

ok = False
weather_data = []
today = [".TODAY", ".TONIGHT"]
any_cap = r"^\.FRI"
pattern = r'^(%s)' % '|'.join(today)
city_weather = f"Including the city of {CITY}"
for i, item in enumerate(splitted):
    match = re.match(pattern, item)
    other_match = re.match(any_cap, item)
    if item == city_weather or splitted[i-1] == city_weather or splitted[i-2] == city_weather:
        ok = True
        continue
    if ok and other_match and not match:
        ok = False
    if ok:
        weather_data.append(item)
weather = "\n".join(weather_data)

if calendars:
    # Use the first calendar
    calendar = calendars[0]

    # Create an all-day event for today
    event = Calendar()
    e = Event()
    now = datetime.now()
    today = now.date()
    e.add('summary', f'Weather for {today:%B %d}')
    e.add('dtstart', today)
    e.add('dtend', (now + timedelta(days=1)).date())
    e.add('dtstamp', now)
    e.add('description', weather)
    event.add_component(e)

    # Add the event to the calendar
    calendar.add_event(event.to_ical())

    print("Event added successfully.")
else:
    print("No calendars found.")
