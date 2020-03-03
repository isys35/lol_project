import requests
from requests import Session
from bs4 import BeautifulSoup as BS
import time


class ParimatchParser:
    def __init__(self):
        self.url = 'https://www.parimatch.ru/'
        self.delay = 0.5
        self.session = Session()
        self.session.get(self.url)
        self.headers = {
            'Host': 'www.parimatch.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.parimatch.ru/event/championship/21263466',
            'TE': 'Trailers'
        }


    def get_response(self, url, headers):
        time.sleep(self.delay)
        while True:
            print('connect...')
            r = self.session.get(url, headers=headers)
            if r.status_code == 200:
                print(r.encoding)
                return r


parser = ParimatchParser()
resp = parser.get_response('https://www.parimatch.ru/event/championship/21263466', parser.headers)
with open('pari', 'wb') as html_file:
     html_file.write(resp.content)
