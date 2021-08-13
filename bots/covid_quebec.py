from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import select 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from twilio.rest import Client
from dotenv import load_dotenv 
import datetime
import time
import locale
import requests
import re
import os

# load the environment variables from .env file
load_dotenv()

# Date format functions for English
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Date format functions for French
def get_date_french():
    loc = 'fr' 
    locale.setlocale(locale.LC_ALL, loc)
    return time.strftime("%d %b %Y")

# get data from the gov website
def get_data():
    page = requests.get("https://www.quebec.ca/en/health/health-issues/a-z/2019-coronavirus/situation-coronavirus-in-quebec/")

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        div = soup.find(id='c47903')
        text = div.getText()

        # Pattern to get comma separated numbers (e.g. 11,234)
        pattern = re.compile('\d*,*\d+')

        # Get cases
        cases = re.search(pattern, re.search('\d*,*\d+.new case', text).group()).group()
        print('Cases: ' + cases)

        # Get deaths
        death = re.search(pattern, re.search('\d*,*\d+.new deaths', text).group()).group()
        print('Death: ' + death)

        # Get hospitalizations
        hospitalizations = re.search(pattern, re.search('\d*,*\d+.hospitalizations', text).group()).group()
        print('Hospitalizations: ' + hospitalizations)

        # Get ICU
        icu = re.search(pattern, re.search('\d*,*\d+.people in intensive care', text).group()).group()
        print('ICU: ' + icu)

        # Get doses
        doses = re.search(pattern, re.search('\d*,*\d+.doses administered are added', text).group()).group()
        print('Doses: ' + doses )
    
        # Get date with proper format in English
        date_eng = custom_strftime('%B {S}, %Y', datetime.now())

        # Get date with proper format in French
        date_fr = get_date_french()

        # Create body message
        body_eng = ('Quebec COVID-19 stats for ' + date_eng + ':\n' 
            + 'Confirmed cases: ' + cases + '\n' 
            + 'Deaths: ' + death + '\n' 
            + 'Hospitalizations: ' + hospitalizations + '\n' 
            + 'ICU: ' + icu + '\n'
            + 'Doses of Vaccine: ' + doses)

        print('\nEN: \n' + body_eng)

        body_fr = ('Données sur la COVID-19 au Québec pour le ' + date_fr + ':\n'
            + 'Cas comfirmés: ' + cases + '\n'
            + 'Décès: ' + death + '\n'
            + 'Hospitalisations: ' + hospitalizations + '\n'
            + 'Soins intensif: ' + icu + '\n'
            + 'Vaccins administrées: ' + doses)

        print('\nFR: \n' + body_fr + '\n')
        return body_eng, body_fr
    else:
        return ConnectionError

# Used to get users from db and send SMS
def send_sms(body):
    # Extract messages from tuples
    body_eng = body[0]
    body_fr = body[1]

    # an Engine, which the Session will use for connection resources
    db_string = os.getenv('DATABASE_URI')
    db = create_engine(db_string)

    # Retrieve relevant data from table (ENGLISH)
    result_eng = db.execute("SELECT phone, firstName, email FROM covid_19_quebec WHERE (CURRENT_DATE<cancelDate OR cancelDate IS NULL) AND language='English'")

    # Retrieve relevant data from table (FRENCH)
    result_fr = db.execute("SELECT phone, firstName, email FROM covid_19_quebec WHERE (CURRENT_DATE<cancelDate OR cancelDate IS NULL) AND language='French'")

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOK')
    twilio_num = os.getenv('TWILIO_NUMBER')

    client = Client(account_sid, auth_token) 

    for row in result_eng:
        print(row)
        try:
            message = client.messages.create(body=body_eng, from_=twilio_num, to='+' + row[0])
            print('Message sent to: ' + row[0] + ' for ' + row[2])
            print('SID: ' + message.sid + '\n')
        except:
            print('FAILED ALERT | Message failed to send to ' + row[2] + '\n')
        

    for row in result_fr:
        print(row)
        try:
            message = client.messages.create(body=body_fr, from_=twilio_num, to='+' + row[0])
            print('Message sent to: ' + row[0] + ' for ' + row[2])
            print('SID: ' + message.sid + '\n')
        except:
            print('FAILED ALERT | Message failed to send to ' + row[2] + '\n')

def main():
    # stop scheduler if it is weekend as gvt doesn't update website
    day = datetime.datetime.today().weekday()
    print('Day: ' + str(day))
    if day == 5 or day == 6:
        print('Today is a weekend')
        exit()
    
    # retrieve data from gvt website
    body = get_data()

    # send SMS
    send_sms(body)

if __name__ == "__main__":
    main()