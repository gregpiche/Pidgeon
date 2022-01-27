import requests
import json
import os
from helpers.sms import send_sms
from helpers.database import get

url = "https://motivational-quotes1.p.rapidapi.com/motivation"

payload = "{\n    \"key1\": \"value\",\n    \"key2\": \"value\"\n}"
headers = {
    'content-type': "application/json",
    'x-rapidapi-host': "motivational-quotes1.p.rapidapi.com",
    'x-rapidapi-key': "76ee81f4b4msh8170b12f240f205p18289ajsn72071473c289"
    }

response = requests.request("POST", url, data=payload, headers=headers)
body = response.text

print(body)

#users = get('motivational_quote')
users = get('motivational_quotes')

# Send SMS
send_sms(body, users)