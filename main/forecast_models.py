import numpy as np
import pandas as pd
#import tensorflow as tf
import datetime
from statsmodels.tsa.arima_model import ARIMA
import requests
import json
# Read the secrets from the JSON file
from app import fetch_test

with open('/Users/liamkilroy/Documents/py_projects/carbon_predictor/secrets.json') as file:
    secrets = json.load(file)
api_url = 'https://api.electricitymap.org/v3/carbon-intensity/past-range?zone=DE&start=2022-07-15T21:00:00Z&end=2023-07-15T00:00:00Z'
api_key = secrets['api_key']
emap_api_username = secrets['username']
emap_api_password = secrets['password']

url = api_url
json_response = fetch_test(api_key, url) #maybe add api key as second argument
if json_response:
    df = pd.read_json(json_response)
    

def data_processor(df):
    df = df.apply(lambda row: f"{row.name + 1} {row['zone']} carbonIntensity: {row['history']['carbonIntensity']}", axis=1)
    return df


historical_data = df

def stationarity_test(historical_data):
    pass


