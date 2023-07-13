


import requests
import schedule
import time
from twilio.rest import Client

# ElectricityMap API endpoint and API key
api_url = 'https://api.electricitymap.org/v3/zones/{zone}/{timestamp}/forecast'
api_key = 'YOUR_ELECTRICITYMAP_API_KEY'

# Twilio credentials
account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
twilio_phone_number = 'YOUR_TWILIO_PHONE_NUMBER'
your_phone_number = 'YOUR_PHONE_NUMBER'

# Fetch forecast from ElectricityMap
def fetch_forecast(zone='YOUR_ZONE', timestamp='latest'):
    url = api_url.format(zone=zone, timestamp=timestamp)
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        print(f'Error fetching forecast: {response.status_code} - {response.text}')
        return None

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
    forecast = fetch_forecast()
    if forecast:
        carbon_intensity = forecast['forecast']['carbonIntensity']
        message = f"Forecast carbon intensity: {carbon_intensity}"
        send_sms(message)

# Schedule the job to run at 9 am PST
schedule.every().day.at('09:00').do(job)

# Keep the program running
while True:
    schedule.run_pending()
    time.sleep(1)

