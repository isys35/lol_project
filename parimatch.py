import requests
from requests import Session
from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class ParimatchParser:
    def __init__(self):
        self.url = 'https://www.parimatch.ru/live'
        self.vis_browser = False
        self.browser = None

    def open_browser(self):
        options = Options()
        options.headless = self.vis_browser
        self.browser = webdriver.Firefox(options=options)

    def get_page(self):
        if not self.browser:
            self.open_browser()
        self.browser.get(self.url)
        time.sleep(30)
        content = self.browser.page_source
        soup = BS(content, 'lxml')
        with open('parimatch.html', 'w', encoding='utf8') as html_file:
            html_file.write(str(soup))
        self.browser.quit()

parser = ParimatchParser()
parser.get_page()
