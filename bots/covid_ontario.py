from bs4 import BeautifulSoup
from datetime import datetime
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
import datetime as dt
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

# get data from the gov website
def get_data():
    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--lang=en")
    chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox") 
    driver = webdriver.Chrome(execution_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
    
    # Get website for cases and deaths
    driver.get("https://covid-19.ontario.ca/data/case-numbers-and-spread")

    # Wait for element to appear on screen
    element = None
    count = 0
    while(element == None and count != 5):
        try:
            element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cviz-overview-header"))
            )
        except TimeoutException:
            count += 1
            driver.refresh()

    if count >= 5:
        print("Max refresh general data!")
        exit()

    # Get parents element
    li = driver.find_elements_by_class_name("cviz-overview-list")[0].find_elements_by_tag_name("li")
    
    # Get Cases
    cases = li[0].find_elements_by_class_name("cviz-label-value--value")[1].text
    print('Cases: ' + cases)

    # Get Deaths
    death_num = li[2].find_elements_by_class_name("cviz-label-value--value")[1].text
    deaths = '0' if death_num == '―' else death_num
    print('Deaths: ' + deaths)

    # Get website for hospitalizations and ICU admissions
    driver.get("https://covid-19.ontario.ca/data/hospitalizations")

    # Get general data
    element = None
    count = 0
    while(element == None and count != 5):
        try:
            element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cviz-overview-header"))
            )
        except TimeoutException:
            count += 1
            driver.refresh()

    if count >= 5:
        print("Max refresh general data!")
        exit()

    # Get containers
    container = driver.find_elements_by_class_name("cviz-overview-list")

    # Get hospitalizations
    hospitalizations = container[0].find_elements_by_class_name("cviz-label-value--value")
    hospitalizations_cur = hospitalizations[0].text
    hospitalizations_new = hospitalizations[1].text
    hosp_status = '+' if hospitalizations[1].find_element_by_tag_name('img').get_attribute('alt') == 'increase from previous business day' else '-'
    hospitalizations_str = hospitalizations_cur + ' (' + hosp_status + hospitalizations_new + ')'
    print('Hospitalizations: ' + hospitalizations_str)

    # Get ICU
    icu = container[1].find_elements_by_tag_name("li")[0].find_elements_by_class_name("cviz-label-value--value")
    icu_cur = icu[0].text
    icu_new = icu[1].text
    icu_status = '+' if icu[1].find_element_by_tag_name('img').get_attribute('alt') == 'increase from previous business day' else '-'
    icu_str = icu_cur + ' (' + icu_status + icu_new + ')'
    print('ICU: ' + icu_str)
    
    # Get website for vaccines administered
    driver.get("https://covid-19.ontario.ca/data")

    # Get general data
    element = None
    count = 0
    while(element == None and count != 5):
        try:
            element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cviz-overview-3col-header"))
            )
        except TimeoutException:
            count += 1
            driver.refresh()

    if count >= 5:
        print("Max refresh general data!")
        exit()

    # Get vaccination data
    doses = driver.find_elements_by_class_name("cviz-overview-list")[0].find_elements_by_class_name("cviz-label-value--4col-value")[1].text
    print('Vaccines: ' + doses)
    
    # Get date with proper format in English
    date = custom_strftime('%B {S}, %Y', datetime.now())

    # Create body message
    body = ('COVID-19 stats for Ontario on ' + date + ':\n' 
        + 'Confirmed cases: ' + cases + '\n' 
        + 'Deaths: ' + deaths + '\n' 
        + 'Hospitalizations: ' + hospitalizations_str + '\n' 
        + 'ICU: ' + icu_str + '\n'
        + 'Vaccines Administered: ' + doses)
    print('\n' + body + '\n')

    return body

# Used to get users from db and send SMS
def send_sms(body):

    # an Engine, which the Session will use for connection resources
    db_string = os.getenv('DATABASE_URI')
    db = create_engine(db_string)

    # Retrieve relevant data from table (ENGLISH)
    results = db.execute("SELECT phone, firstName, email FROM covid_19_ontario WHERE CURRENT_DATE<cancelDate OR cancelDate IS NULL")

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOK')
    twilio_num = os.getenv('TWILIO_NUMBER')

    client = Client(account_sid, auth_token) 

    for row in results:
        print(row)
        try:
            message = client.messages.create(body=body, from_=twilio_num, to='+' + row[0])
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