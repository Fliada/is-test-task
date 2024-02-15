from bs4 import BeautifulSoup
import lxml
import re
import requests
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
from tqdm import trange

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


def get_card_url(article):
    return f'{BASE_URL}/catalog/{article}/detail.aspx'


class Crawler:

    def get_html(self, url):
        pass

    def get_card(self, url):
        pass


class Parser:

    def parse_url(self, soup):
        pass

    def parse_card(self, soup):
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
        return BeautifulSoup(self.browser.page_source, 'html.parser')

    def get_card(self, url):
        PAUSE_TIME = 3

        self.browser.get(url)
        # Wait to load page
        time.sleep(PAUSE_TIME)

        soup_card = BeautifulSoup(self.browser.page_source, 'html.parser')
        return soup_card


class ParserWB(Parser):
    def parse_url(self, soup):
        cards = soup.find_all('article')

        projects = []
        for row in cards:
            projects.append(
                row['data-nm-id']  # article
            )
            print(row['data-nm-id'])
        return projects

    def parse_card(self, nm_id, soup):
        page = soup.find('div', class_='product-page')
        card = {
            'nm_id': nm_id,
            'name': self.__get_name(page),
            'brand': self.__get_brand(page),
            'brand_id': self.__get_brand_id(page),
            'site_brand_id': self.__get_site_brand_id(page),
            'supplier_id': self.__get_supplier_id(page),
            'sale': self.__get_sale(page),
            'price': self.__get_price(page),
            'sale_price': self.__get_sale_price(page),
            'rating': self.__get_rating(page),
            'feedbacks': self.__get_feedbacks(page),
            'colors': self.__get_colors(page),
            # self.__get_quantity(page),
        }
        print(card)
        return Product(**card)

    def __get_name(self, soup):
        header = soup.find('div', class_='product-page__header-wrap')
        return header.find('h1').text

    def __get_brand(self, soup):
        header = soup.find('div', class_='product-page__header')
        return header.find('a').text

    # ?
    def __get_brand_id(self, soup):
        header = soup.find('div', class_='product-page__header')
        brand = header.find('a', class_='product-page__header-brand', href=True)['href'].split(sep='/')
        return brand[len(brand) - 1]

    def __get_site_brand_id(self, soup):
        header = soup.find('div', class_='product-page__header')
        brand = header.find('a', class_='product-page__header-brand', href=True)
        return BASE_URL + brand['href']

    def __get_supplier_id(self, soup):
        if soup.find('div', class_='seller-info__header--no-data') is not None:
            return 0

        seller = soup.find('div', class_='seller-info__content').find('a', href=True)['href'].split(sep='/')
        return seller[len(seller) - 1]

    def __get_sale(self, soup):
        return self.__get_price(soup) - self.__get_sale_price(soup)

    def __get_price(self, soup):
        price_block = soup.find('div', class_='price-block')
        if price_block.find('del', class_='price-block__old-price') is None:
            return self.__get_sale_price(soup)

        return int(
            "".join(re.findall(r'\b\d+\b', price_block.find('del', class_='price-block__old-price').find('span').text)))

    def __get_sale_price(self, soup):
        price_block = soup.find('div', class_='price-block')
        return int("".join(re.findall(r'\b\d+\b', price_block.find('ins', class_='price-block__final-price').text)))

    def __get_rating(self, soup):
        info = soup.find('div', class_='product-page__common-info')
        rating = info.find('span', class_='product-review__rating').text
        if rating == 'Нет оценок':
            return 0

        return rating

    def __get_feedbacks(self, soup):
        info = soup.find('div', class_='product-page__common-info')
        if info is None:
            return ''

        return "".join(re.findall(r'\b\d+\b', info.find('span', class_='product-review__count-review').text))

    def __get_colors(self, soup):
        info = soup.find('div', class_='color-name')
        if info is None:
            return ''

        return info.find('span', class_='color').text


#    def __get_quantity(self, soup):
#        pass


def main():
    crawler = CrawlerWB()
    parser = ParserWB()

    for i in trange(1, ncols=80, desc='Total'):
        all_articles = parser.parse_url(crawler.get_html(BASE_URL))
        cards = []
        for article in all_articles:
            print(article, '!')
            cards.append(parser.parse_card(article, crawler.get_card(get_card_url(article))))
        # parser.parse_card(crawler.get_card(get_card_url(8914542)))

        helper.insert(cards)


if __name__ == '__main__':
    main()
