from bs4 import BeautifulSoup
import lxml
import re
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from local_settings import postresql as settings
from db_helper.DBHelper import *

keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
if not all(key in keys for key in settings.keys()):
    raise Exception('Bad confid file')

helper = DBHelper(
    settings['pguser'],
    settings['pgpasswd'],
    settings['pghost'],
    settings['pgport'],
    settings['pgdb']
)

helper.create_table()

BASE_URL = 'https://www.wildberries.ru'

class Crawler:

    def get_html(self):
        pass

    def get_card_info(self):
        pass


class Crawler:

    def get_html(self, url):
        pass

    def parse_url(self, html):
        pass


class CrawlerWB(Crawler):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless=new")

        self.browser = webdriver.Chrome(options=chrome_options)

    def get_html(self, url):
        self.browser.get(url)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        SCROLL_PAUSE_TIME = 3

        # Get scroll height
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return self.browser.page_source

    def parse_url(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('article')

        projects = []
        for row in cards:
            cols = row.find('div', {'class': 'product-card__wrapper'})
            projects.append({
                'title': cols.a['aria-label'],
                'url': cols.a['href']
            })
            print(cols.a['aria-label'], cols.a['href'])
        return projects

def main():
    crawler = CrawlerWB()
    all_url = crawler.parse_url(crawler.get_html(BASE_URL))

if __name__ == '__main__':
    main()