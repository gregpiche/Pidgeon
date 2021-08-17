from bs4 import BeautifulSoup
from datetime import datetime as dt
from sqlalchemy import select 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from twilio.rest import Client
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import locale
import time
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
    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--lang=en")
    chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox") 
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
    
    # Get info for cases, deaths, tests performed, percent positive, active cases
    driver.get("https://health-infobase.canada.ca/covid-19/epidemiological-summary-covid-19-cases.html")
    
    # set implicit wait time
    print('WAIT | 10 second wait')
    driver.implicitly_wait(10) 

    # Get table
    table = driver.find_element_by_id("newCases").find_elements_by_class_name("nationalNumbers-canada")
    
    # Get cases
    cases = table[1].text
    print('Cases: ' + cases)

    # Get deaths
    deaths = table[2].text
    print('Deaths: ' + deaths)

    # Get Tests performed
    tests = table[3].text
    print('Tests: ' + tests)

    # Get percent positive cases
    percent_pos = driver.find_elements_by_class_name("percentPositive")[0].text + '%'
    print('Percent positive: ' + percent_pos)

    # Get Active cases
    active = driver.find_elements_by_class_name("active")[0].text
    print('Active: ' + active)

    # Get info for cases, deaths, tests performed, percent positive, active cases
    driver.get("https://health-infobase.canada.ca/covid-19/vaccine-administration/")
    
    # set implicit wait time
    print('WAIT | 10 second wait')
    driver.implicitly_wait(10)

    # Get vaccines administered
    doses = driver.find_elements_by_class_name("numdelta_all_administered_txt")[0].text

    # Get date with proper format in English
    date_eng = custom_strftime('%B {S}, %Y', dt.now())

    # Get date with proper format in French
    date_fr = get_date_french()

    # Create body message
    body_eng = ('COVID-19 stats for Canada on ' + date_eng + ':\n' 
        + 'Confirmed cases: ' + cases + '\n' 
        + 'Deaths: ' + deaths + '\n' 
        + 'Tests performed: ' + tests + '\n' 
        + '% positive cases: ' + percent_pos + '\n'
        + 'Active cases: ' + active + '\n'
        + 'Vaccines Administered: ' + doses )
    print('\nEN: \n' + body_eng)

    body_fr = ('Données sur la COVID-19 au Canada pour le ' + date_fr + ':\n'
        + 'Cas comfirmés: ' + cases + '\n'
        + 'Décès: ' + deaths + '\n'
        + 'Tests effectués: ' + tests + '\n'
        + '% cas positifs: ' + percent_pos + '\n'
        + 'Cas actifs: ' + active + '\n' 
        + 'Vaccins administrées: ' + doses)
    print('\nFR: \n' + body_fr + '\n')
    return body_eng, body_fr

# Used to get users from db and send SMS
def send_sms(body):
    # Extract messages from tuples
    body_eng = body[0]
    body_fr = body[1]

    # an Engine, which the Session will use for connection resources
    db_string = os.getenv('DATABASE_URI')
    db = create_engine(db_string)

    # Retrieve relevant data from table (ENGLISH)
    result_eng = db.execute("SELECT phone, firstName, email FROM covid_19_canada WHERE (CURRENT_DATE<cancelDate OR cancelDate IS NULL) AND language='English'")

    # Retrieve relevant data from table (FRENCH)
    result_fr = db.execute("SELECT phone, firstName, email FROM covid_19_canada WHERE (CURRENT_DATE<cancelDate OR cancelDate IS NULL) AND language='French'")

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
    
    # retrieve data from gvt website
    body = get_data()

    # send SMS
    send_sms(body)

if __name__ == "__main__":
    main()