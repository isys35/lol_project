import requests
from requests import Session
from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.common.action_chains import ActionChains


class ParimatchParser:
    def __init__(self):
        self.url = 'https://www.parimatch.ru/live'
        self.vis_browser = False
        self.browser = None
        self.main_page_load = False

    def open_browser(self):
        options = Options()
        options.headless = self.vis_browser
        self.browser = webdriver.Firefox(options=options)

    def get_main_page(self):
        if not self.browser:
            self.open_browser()
        if self.browser.current_url != self.url:
            self.browser.get(self.url)
        content = self.browser.page_source
        soup = BS(content, 'lxml')
        while not soup.select('main-markets'):
            print('.')
            time.sleep(0.1)
            content = self.browser.page_source
            soup = BS(content, 'lxml')
        element = self.browser.find_element_by_css_selector('.live-group-item.sportcolor-bg-B')
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        #actions = ActionChains(self.browser)
        #actions.move_to_element(element).perform()
        while True:
            live_blocks = element.find_elements_by_css_selector('.live-block-column.live-block-column_data')
            hrefs = []
            for live_block in live_blocks:
                if live_block.get_attribute("href") == 'https://www.parimatch.ru/null':
                    self.browser.execute_script("arguments[0].scrollIntoView();", live_block)
                    hrefs.append('https://www.parimatch.ru/null')
                print(live_block.get_attribute("href"))
            if not 'https://www.parimatch.ru/null' in hrefs:
                self.main_page_load = True
                break
                #actions = ActionChains(self.browser)
                #actions.move_to_element(live_block).perform()

    def get_events(self):
        if not self.main_page_load:
            self.get_main_page()
        print('connect...')
        content = self.browser.page_source
        soup = BS(content, 'lxml')
        with open('parimatch.html', 'w', encoding='utf8') as html_file:
            html_file.write(str(soup))
        main_block = soup.select('.live-group-item.sportcolor-bg-B')
        blocks_champions = main_block[0].select('.live-block-championship')
        events_info = []
        for block_champion in blocks_champions:
            champ = block_champion.select('.championship-name-title')[0]
            champ_title = champ.text
            l_blocks = block_champion.select('.live-block-column.live-block-column_data')
            for l_block in l_blocks:
                href = l_block['href']
                commands = l_block.select('.competitor-name')
                commands = commands[0].select('span')
                command1 = commands[0].text
                command2 = commands[1].text
                time_match = l_block.select('.live-block-sore')[0].text
                total_score = l_block.select('.live-score-box__total')
                if not total_score:
                    total_score1 = 0
                    total_score2 = 0
                else:
                    total_score = total_score[0].select('span')
                    total_score1 = total_score[0].text
                    total_score2 = total_score[1].text
                scores = l_block.select('.live-score-box__set')
                scores1 = [score.select('span')[0].text for score in scores]
                scores2 = [score.select('span')[1].text for score in scores]
                event_info = {
                    'href': href,
                    'champ': champ_title,
                    'command1': command1,
                    'command2': command2,
                    'total_score1': total_score1,
                    'total_score2': total_score2,
                    'scores_1': scores1,
                    'scores_2': scores2,
                    'time': time_match,
                }
                events_info.append(event_info)
        return events_info





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

parser = ParimatchParser()
while True:
    print(parser.get_events())
