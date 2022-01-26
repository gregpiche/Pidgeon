from twilio.rest import Client
import os

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOK')
twilio_num = os.getenv('TWILIO_NUMBER')

# This function goes through the subscribed accounts and sends the required message
def send_sms(body, result):
    client = Client(account_sid, auth_token) 

    for row in result:
        print(row)
        try:
            message = client.messages.create(body=body, from_=twilio_num, to='+' + row[0])
            print('Message sent to: ' + row[0] + ' for ' + row[2])
            print('SID: ' + message.sid + '\n')
        except:
            print('FAILED ALERT | Message failed to send to ' + row[2] + '\n')
