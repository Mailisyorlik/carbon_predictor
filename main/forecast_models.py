import numpy as np
import pandas as pd
#import tensorflow as tf
import datetime
from statsmodels.tsa.arima_model import ARIMA
import requests
import json
# Read the secrets from the JSON file
with open('/Users/liamkilroy/Documents/py_projects/carbon_predictor/secrets.json') as file:
    secrets = json.load(file)
api_url = 'https://api.electricitymap.org/v3/carbon-intensity/past-range?zone=DE&start=2022-07-15T21:00:00Z&end=2023-07-15T00:00:00Z'
api_key = secrets['api_key']
emap_api_username = secrets['username']
emap_api_password = secrets['password']


def fetch_test(api_key) -> str: #eventually put the api key as a called argument
    url = api_url #zone is set for NV energy 
    headers = {
  "auth-token": api_key #fix this, they should not be referring to the same thing
    }

    response = requests.get(url, headers=headers)
    #print(response.text)
    return response.text

json_response = fetch_test(api_key) #maybe add api key as second argument
if json_response:
    df = pd.read_json(json_response)


