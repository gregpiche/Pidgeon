import requests
from bs4 import BeautifulSoup

# get data from the gov website
def get_data():
    page = requests.get("https://www.quebec.ca/en/health/health-issues/a-z/2019-coronavirus/situation-coronavirus-in-quebec/")

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        div = soup.find(id='c47903').find_all('li')
        for li in div:
            print(li)        

def send_sms():
    return 

def main():
    print('In Main')
    get_data()

if __name__ == "__main__":
    main()