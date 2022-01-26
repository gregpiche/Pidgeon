from bs4 import BeautifulSoup
from datetime import datetime as dt
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

from helpers.sms import send_sms
from helpers.database import get

# load the environment variables from .env file
load_dotenv()

# Date format functions for English
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# get data from the gov website
def get_data():
    page = requests.get("https://www.alberta.ca/covid-19-alberta-data.aspx")

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        columns = soup.find(id='goa-grid28054').find('table').findAll('tr')[2].findAll('td')

        # Pattern to get comma separated numbers (e.g. 11,234)
        pattern = re.compile('\d*,*\d+')

        # Get cases
        cases = re.search(pattern, re.search('\d*,*\d+ on ', columns[0].getText()).group()).group()
        print('Cases: ' + cases)

        # Get active cases
        active = columns[1].getText()
        print('Active: ' + active)

        # Get hospitalizations
        hospitalizations = columns[3].getText()
        print('In hospital: ' + hospitalizations)

        # Get ICU
        icu = columns[4].getText()
        print('In ICU: ' + icu)

        # Get deaths
        deaths = columns[5].getText()
        print('Total deaths: ' + deaths)

        # Get tests completed
        tests = re.search(pattern, re.search('\d*,*\d+ on ', columns[6].getText()).group()).group()
        print('Tests completed: ' + tests)

        # Get date with proper format in English
        date = custom_strftime('%B {S}, %Y', dt.now())

        # Create body message
        body = ('COVID-19 stats for Alberta on ' + date + ':\n' 
            + 'Confirmed cases: ' + cases + '\n' 
            + 'Active cases: ' + active + '\n'
            + 'Total deaths: ' + deaths + '\n' 
            + 'In hospital: ' + hospitalizations + '\n' 
            + 'In ICU: ' + icu + '\n'
            + 'Tests completed: ' + tests)

        print('\nEN: \n' + body + '\n')

        return body
    else:
        return ConnectionError

def main():
    # stop scheduler if it is weekend as gvt doesn't update website
    day = datetime.datetime.today().weekday()
    print('Day: ' + str(day))
    if day == 5 or day == 6:
        print('Today is a weekend')
        exit()
    
    # retrieve data from gvt website
    body = get_data()

    # Retrieve users from database
    users = get('covid_19_alberta')

    # send SMS
    send_sms(body, users)

if __name__ == "__main__":
    main()