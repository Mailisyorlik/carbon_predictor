


import requests
import schedule
import time
from twilio.rest import Client

import json

# Read the secrets from the JSON file
with open('/Users/liamkilroy/Documents/py_projects/carbon_predictor/secrets.json') as file:
    secrets = json.load(file)

# Access the secrets using their keys
api_url = 'https://api.electricitymap.org/v3/carbon-intensity/latest?zone=US-NW-NEVP'
api_key = secrets['api_key']
emap_api_username = secrets['username']
emap_api_password = secrets['password']


# zone = zone/US-NW-NEVP for nv energy customers

# ElectricityMap API endpoint
api_url = 'https://api-access.electricitymaps.com/free-tier/carbon-intensity/history'


# Twilio credentials
account_sid = secrets['account_sid']
auth_token = secrets['auth_token']
twilio_phone_number = secrets['twilio_phone_number']
your_phone_number = secrets['your_phone_number']

def fetch_hourly_data(zone='US-NW-NEVP', timestamp='YYYY-MM-DD'):
    url = api_url.format(zone=zone, timestamp=timestamp)
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        print(f'Error fetching data: {response.status_code} - {response.text}')
        return None

def get_lowest_carbon_intensity_hours(data):
    hourly_carbon_intensity = data['data']['carbonIntensity']
    lowest_hours = sorted(hourly_carbon_intensity, key=lambda x: x['value'])[:2]
    return lowest_hours

def get_yesterdays_ci():
    yesterday = '2023-07-12'  # Replace with the actual date in the format YYYY-MM-DD
    hourly_data = fetch_hourly_data(timestamp=yesterday)
    if hourly_data:
        lowest_hours = get_lowest_carbon_intensity_hours(hourly_data)
        print(f"The two lowest carbon intensity hours for {yesterday}:")
        for hour in lowest_hours:
            print(f"Hour: {hour['startTime']}, Carbon Intensity: {hour['value']}")
        return lowest_hours

get_yesterdays_ci()
# Send SMS using Twilio
def send_sms(message):
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=your_phone_number
        )
        print('SMS sent successfully!')
    except Exception as e:
        print(f'Error sending SMS: {str(e)}')

# Job function to fetch forecast and send SMS - needs to fetch for the day and send a lsit of the three least CI intensive hours
# of the day
def job():
    get_yesterday = get_yesterdays_ci()
    if get_yesterday:
        carbon_intensity = get_yesterday['forecast']['carbonIntensity']
        message = f"Lowest CI Hours{lowest_hours}"
        print(message)
        send_sms(message)

#job()

# Schedule the job to run at 9 am PST
schedule.every().day.at('06:00').do(job)

# Keep the program running
##while True:
   # schedule.run_pending()
   # time.sleep(1)

