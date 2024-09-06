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


url = os.getenv("NWS_URL")
r = requests.get(url)
splitted = r.text.split("\n")

cal_url = os.getenv("CAL_URL")
cal_user = os.getenv("CAL_USER")
cal_name = os.getenv("CAL_NAME")
cal_pass = os.getenv("CAL_PASS")
city = os.getenv("city")
       
client = DAVClient(cal_url, username=cal_user, password=cal_pass)
calendars = client.principal().calendars()
for cal in list(calendars):
    if cal_name == cal.name:
        calendar = cal

ok = False
now = datetime.now()
today = now.date()
title = f'Weather for {today:%B %d, %Y}'
weather_data = [f"{now:%Y-%m-%d %H:%M}"]
forecast_list = [".TODAY", ".TONIGHT"]
pattern = r'^(%s)' % '|'.join(forecast_list)
city_weather = f"Including the city of {city}"
for i, item in enumerate(splitted):
    match = re.match(pattern, item)
    if item == city_weather or splitted[i-1] == city_weather or splitted[i-2] == city_weather:
        ok = True
        continue
    if ok:
        weather_data.append(item)
weather = "\n".join(weather_data)


existing_entry = False
if calendar:
    # Use the first calendar
    # calendar = calendars[0]
    events = calendar.events()

    for caldav_event in events:
        ical_event = Calendar.from_ical(caldav_event.data)

        for component in ical_event.walk():
            if component.name == "VEVENT":
                if component.get('summary') == title:
                    component['description'] = weather
                    caldav_event.data = ical_event.to_ical()
                    caldav_event.save()
                    print("Event updated.")
                    existing_entry = True
                    break

    # Create an all-day event for today
    if not existing_entry:
        event = Calendar()
        e = Event()
        e.add('summary', title)
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
