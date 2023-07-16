


import requests
import schedule
import time
from twilio.rest import Client
from datetime import timedelta, date
import json
import pandas as pd

# Read the secrets from the JSON file
with open('/Users/liamkilroy/Documents/py_projects/carbon_predictor/secrets.json') as file:
    secrets = json.load(file)

# Access the secrets using their keys
api_url = 'https://api.electricitymap.org/v3/carbon-intensity/latest?zone=US-NW-NEVP'
api_key = secrets['api_key']
emap_api_username = secrets['username']
emap_api_password = secrets['password']


# zone = zone/US-NW-NEVP for nv energy customers


#api_url = 'https://api-access.electricitymaps.com/free-tier/carbon-intensity/history'


# Twilio credentials
account_sid = secrets['account_sid']
auth_token = secrets['auth_token']
twilio_phone_number = secrets['twilio_phone_number']
your_phone_number = secrets['your_phone_number']


def fetch_test(api_key) -> str: #eventually put the api key as a called argument
    url = "https://api-access.electricitymaps.com/free-tier/carbon-intensity/history?zone=US-NW-NEVP" #zone is set for NV energy 
    headers = {
  "auth-token": api_key #fix this, they should not be referring to the same thing
    }

    response = requests.get(url, headers=headers)
    print(response.text)
    return response.text

json_response = fetch_test(api_key) #maybe add api key as second argument


timestamp = date.today() - timedelta(days = 1)


def fetch_hourly_data(zone='US-NW-NEVP', timestamp = timestamp) -> str: #what should this be returning
    url = api_url.format(zone=zone, timestamp=timestamp)
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        print(f'Error fetching hourly data: {response.status_code} - {response.text}')
        return None
#data = fetch_hourly_data(zone='US-NW-NEVP', timestamp = timestamp)

def get_lowest_carbon_intensity_hours(data):
    hourly_carbon_intensity = data['data']['carbonIntensity']
    lowest_hours = sorted(hourly_carbon_intensity, key=lambda x: x['value'])[:2]
    print(lowest_hours)
    return lowest_hours


json_response = fetch_test(api_key) #maybe add api key as second argument

if json_response:
    df = pd.read_json(json_response)
    print(df)
    ci_sorted = df.sort_values(by = 'carbonIntensity')
    ci_lowest_hours = ci_sorted[['zone', 'history']].head(2)
    ci_lowest_hours['startTime'] = pd.to_datetime(ci_lowest_hours['history'].apply(lambda x: x['startTime']))
    ci_lowest_hours.rename(columns = {'startTime':'Date', 'zone':'Zone'}, inplace = True)
    ci_lowest_hours.drop(columns = 'history', inplace = True)
    print(ci_lowest_hours)
#get_lowest_carbon_intensity_hours(nv_dataframe)
#fetch_hourly_data(zone = 'US-NW-NEVP', timestamp = timestamp)
#get_lowest_carbon_intensity_hours(response.json)

#if __name__ == "__main__":


def get_yesterdays_ci():
    yesterday = '2023-07-12'  # Replace with the actual date in the format YYYY-MM-DD
    hourly_data = fetch_hourly_data(timestamp=yesterday)
    if hourly_data:
        lowest_hours = get_lowest_carbon_intensity_hours(hourly_data)
        print(f"The two lowest carbon intensity hours for {yesterday}:")
        for hour in lowest_hours:
            print(f"Hour: {hour['startTime']}, Carbon Intensity: {hour['value']}")
        return lowest_hours
#get_yesterdays_ci()
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

job()
def produce_forecast() -> None:
    '''placeholder function for inference from forecast_models.py'''
    pass


#job()

# Schedule the job to run at 9 am PST
schedule.every().day.at('06:00').do(job)

# Keep the program running
##while True:
   # schedule.run_pending()
   # time.sleep(1)

