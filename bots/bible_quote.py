import requests
import json
import os
from helpers.sms import send_sms
from helpers.database import get

# Build request
url = "https://uncovered-treasure-v1.p.rapidapi.com/today"

headers = {
    'x-rapidapi-host': "uncovered-treasure-v1.p.rapidapi.com",
    'x-rapidapi-key': os.getenv('UNCOVERED_TREASURE_KEY')
    }

# Make request for bible quote
response = requests.request("GET", url, headers=headers)
response = json.loads(response.text)['results'][0]

# Parse response
context = response['context']
quote = response['text']
body = context + '\n' + quote
print(body)

users = get('bible_quote')

# Send SMS
send_sms(body, users)