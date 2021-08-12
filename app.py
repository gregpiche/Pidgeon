from flask import Flask, request, abort
from model import Subscription
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from twilio.rest import Client 
import os
import json
import re

app = Flask(__name__)
auth = HTTPBasicAuth()
db_string = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = create_engine(db_string)

users = {
    os.getenv('API_USERNAME'): generate_password_hash(os.getenv('API_PASS'))
}

# Verify API using basic auth
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

# Create subscription from Zapier webhook
@app.route('/subscription-start', methods=['POST'])
@auth.login_required
def subscription_start():
    content = request.get_json()

    # Get user info
    person = content['person']
    email = person['$email']
    phone = person['$phone_number'].replace('+', '')

    # Get Item info
    items = content['event_properties']['Items']
    products = re.findall("'ProductName': '[\w?\d?\-?\s?]+', ", items)
    for product in products:
        product = product.split(':')[1].replace(',', '').replace("'", '').strip()
        # Splits product into table_name (product name) and language
        product_elements = product.split(' - ')
        table_name = product_elements[0].strip().replace('-', '_').replace(' ', '_')
        language = product_elements[1].strip()

        # Create subscription object and save to db
        subscription = Subscription.Subscription(table_name, email, phone, language)
        subscription.create(db)

        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        print('Before SID print')
        print('SID: ' + str(account_sid))
        auth_token = os.getenv('TWILIO_AUTH_TOK')
        client = Client(account_sid, auth_token) 
        
        message = client.messages.create(
                                    body='Thank you for subscribing to the Pidgeon alert. All alerts will be sent from this number. To manage your account, use magic link sent to your email or via your Pidgeon account.',
                                    from_=os.getenv('TWILIO_NUMBER'),         
                                    to='+' + phone 
                                ) 
        
        print(message.sid)
    return ('Webhook verified', 200)

# Cancel subscription from Zapier webhook
@app.route('/subscription-cancel', methods=['POST'])
@auth.login_required
def subscription_cancel():
    content = request.get_json()

    # Get user info
    person = content['person']
    email = person['$email']
    phone = person['$phone_number'].replace('+', '')

    # Get Item info
    items = content['event_properties']['Items']
    products = re.findall("'ProductName': '[\w?\d?\-?\s?]+', ", items)
    for product in products:
        product = product.split(':')[1].replace(',', '').replace("'", '').strip()
        # Splits product into table_name (product name) and language
        product_elements = product.split(' - ')
        table_name = product_elements[0].strip().replace('-', '_').replace(' ', '_')
        language = product_elements[1].strip()

        # Create subscription object and save to db
        subscription = Subscription.Subscription(table_name, email, phone, language)
        subscription.cancel(db)

    return ('Webhook verified', 200)

# Reactivate subscription from zapier webhook
@app.route('/subscription-reactivate', methods=['POST'])
@auth.login_required
def subscription_reactivate():
    content = request.get_json()

    # Get user info
    person = content['person']
    email = person['$email']
    phone = person['$phone_number'].replace('+', '')

    # Get Item info
    items = content['event_properties']['Items']
    products = re.findall("'ProductName': '[\w?\d?\-?\s?]+', ", items)
    for product in products:
        product = product.split(':')[1].replace(',', '').replace("'", '').strip()
        # Splits product into table_name (product name) and language
        product_elements = product.split(' - ')
        table_name = product_elements[0].strip().replace('-', '_').replace(' ', '_')
        language = product_elements[1].strip()

        # Create subscription object and save to db
        subscription = Subscription.Subscription(table_name, email, phone, language)
        subscription.reactivate(db)

    return ('Webhook verified', 200)

if __name__ == "__main__":
    app.run()