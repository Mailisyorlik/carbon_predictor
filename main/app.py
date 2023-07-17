

#also consider co2 signal as an option?
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

url = "https://api-access.electricitymaps.com/free-tier/carbon-intensity/history?zone=US-NW-NEVP"
def fetch_test(api_key, url) -> str: #eventually put the api key as a called argument
    url = url #zone is set for NV energy 
    headers = {
  "auth-token": api_key #fix this, they should not be referring to the same thing
    }

    response = requests.get(url, headers=headers)
    #print(response.text)
    return response.text

json_response = fetch_test(api_key, url) #maybe add api key as second argument


timestamp = date.today() - timedelta(days = 1)
historical_url = 'https://api.electricitymap.org/v3/carbon-intensity/past-range?zone=DE&start=2022-07-15T21:00:00Z&end=2023-07-15T00:00:00Z'
url = historical_url 
historical_json = fetch_test(api_key, url)
def historical_data(historical_json):
    historical_df = pd.read_json(historical_json)
    print("THIS IS HISTORICAL DATA: +", historical_df)


historical_data(historical_json)



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


json_response = fetch_test(api_key, url) #maybe add api key as second argument


if json_response:
    df = pd.read_json(json_response)
    #print(df)
    # Format each row in the desired format and create a new column 'Formatted'
    df['Formatted'] = df.apply(lambda row: f"{row.name + 1} {row['zone']} carbonIntensity: {row['history']['carbonIntensity']}", axis=1)

    #Drop the 'zone' and 'history' columns, as they are no longer needed
    df.drop(columns=['zone', 'history'], inplace=True)
    #df.columns = ['Interval', 'Balancing Authority', 'Carbon Intensity']
    print(df)

#if __name__ == "__main__":

def format_time(hour_value):
    formatted_time = str(hour_value).zfill(2)
    return f"{formatted_time}:00"

#df.insert(0,'Formatted Hour', df['hour'].apply(format_time))
#df.drop(columns=['hour', inplace = True])

print(df)

def get_lowest_hours(df):
    df['carbonIntensity'] = df['Formatted'].str.extract(r'carbonIntensity:\s+(\d+)').astype(int)
    #df['carbonIntensity'] = df['carbonIntensity'].astype(int)
    lowest_two = df.nsmallest(2, 'carbonIntensity')
    return lowest_two

lowest_hours = get_lowest_hours(df)
print(lowest_hours)
def get_yesterdays_ci():
    yesterday = date.today() - timedelta(days = 1)  # Replace with the actual date in the format YYYY-MM-DD
    hourly_data = fetch_hourly_data(timestamp=yesterday)
    if hourly_data:
        lowest_hours = get_lowest_hours(hourly_data)
        print(f"The two lowest carbon intensity hours for {yesterday}:")
        for hour in lowest_hours:
            print(f"Hour: {hour['startTime']}, Carbon Intensity: {hour['value']}")
            lowest_hours = lowest_hours.iloc[1:].reset_index(drop=True)
            return lowest_hours
#get_yesterdays_ci()
# Send SMS using Twilio

def create_message(lowest_hours):
    message = "Yesterday's lowest CI values for NEVP were:\n"
    for _, row in lowest_hours.iterrows():
        message += f"#{row['Formatted']} \n gCo2e/kwh. \n Run your appliances at that time today" 
        return message #this seems to only return one value
#the issue is that this is returning somewhat inconsistent values. 
#{row['Formatted']} - 
create_message(lowest_hours)
def send_sms(message):
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=your_phone_number
        )
        print('SMS sent to 775-527-6840 successfully!')
    except Exception as e:
        print(f'Error sending SMS: {str(e)}')


send_sms(create_message(lowest_hours))

# Job function to fetch forecast and send SMS - needs to fetch for the day and send a lsit of the three least CI intensive hours
# of the day
def job():
    get_yesterday = get_yesterdays_ci()
    if get_yesterday:
        carbon_intensity = get_yesterday['forecast']['carbonIntensity']
        message = f"Lowest CI Hours: {lowest_ci_hours}"
        print(message)
        send_sms(message)




#job()
def produce_forecast() -> None:
    '''placeholder function for inference from forecast_models.py'''
    pass



if __name__ == '__main__':
    fetch_test(api_key, url)
    send_sms(create_message(lowest_hours))
#job()

# Schedule the job to run at 9 am PST
schedule.every().day.at('06:00').do(job)

# Keep the program running
##while True:
   # schedule.run_pending()
   # time.sleep(1)

