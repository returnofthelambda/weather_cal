# Python Script to Scrape NWS Weather and add to CalDAV Calendar

This script will pull weather data from the National Weather Service and add it to a CalDAV Calendar. A cron job can be used to run this script automatically. 

Using a virtual environment, such as venv is recommended. To do so, after creating a new directory, run `python -m venv .venv` (on linux) and then activate by running `. .venv/bin/activate`. Then, install required python packages running `pip install -r requirements.txt`.

User will also need to modify the `.env-example` file and rename it `.env`.
