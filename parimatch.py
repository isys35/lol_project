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
        print('connect...')
        if self.browser.current_url != self.url:
            self.browser.get(self.url)
        delta = 0
        list_height = []
        down = True
        while True:
            content = self.browser.page_source
            soup = BS(content, 'lxml')
            hrefs = []
            live_blocks = soup.select('.live-block-column.live-block-column_data')
            if live_blocks:
                for live_block in live_blocks:
                    hrefs.append(live_block['href'])
                    if live_block['href'] == 'null':
                        hrefs.append('null')
                        continue
                if not 'null' in hrefs:
                    break
            height = self.browser.execute_script("return document.body.scrollHeight")
            if not list_height:
                list_height.append(height)
            else:
                if height == list_height[-1]:
                    list_height.append(height)
                    if len(list_height) > 20:
                        if down:
                            down = False
                        else:
                            down = True
                        list_height = []
                else:
                    list_height = []
            self.browser.execute_script("window.scrollTo(0, %f);" % (delta))
            if down:
                delta += 200
            else:
                delta = 0
        with open('parimatch.html', 'w', encoding='utf8') as html_file:
            html_file.write(str(soup))
        main_block = soup.select('.live-group-item.sportcolor-bg-B')
        blocks_champions = main_block[0].select('.live-block-championship')
        for block_champion in blocks_champions:
            champ = block_champion.select('.championship-name-title')[0]
            champ_title = champ.text
            print(champ_title)
            l_blocks = block_champion.select('.live-block-column.live-block-column_data')
            for l_block in l_blocks:
                href = l_block['href']
                print(href)
                commands = l_block.select('.competitor-name')
                commands = commands[0].select('span')
                command1 = commands[0].text
                command2 = commands[1].text
                print(command1, command2)
                time_match = l_block.select('.live-block-sore')[0].text
                print(time_match)





        # heads = [el.text.lower() for el in soup.select('.live-block-head-title__text')]
        # if 'баскетбол' in heads:
        #     baskets = []
        #     print('[DEBUG]')
        #     for live_block in soup.select('.live-block-column.live-block-column_data'):
        #         if live_block['href'].split('/')[2].split('|')[0] == 'B':
        #             baskets.append(live_block)
        #     for basket in baskets:
        #         print(basket)
        #         print(basket.select('.championship-name-title__text'))
        # else:
        #     print('[INFO] Игры не найдены')
        self.browser.quit()

parser = ParimatchParser()
parser.get_page()
