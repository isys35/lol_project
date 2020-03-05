from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class ParimatchParser:
    def __init__(self):
        self.url = 'https://www.parimatch.ru/live'
        self.vis_browser = False
        self.browser = None
        self.main_page_load = False
        self.games_found = False
        self.start_work_time = 0

    def open_browser(self):
        options = Options()
        options.headless = self.vis_browser
        self.browser = webdriver.Firefox(options=options)

    def get_main_page(self):
        if not self.browser:
            self.open_browser()
        if len(self.browser.window_handles) == 1:
            self.browser.get(self.url)
        else:
            current_urls = self.get_current_urls()
            if self.url in current_urls:
                while self.browser.current_url != self.url:
                    for page in self.browser.window_handles:
                        self.browser.switch_to.window(page)
        content = self.browser.page_source
        soup = BS(content, 'lxml')
        while not soup.select('main-markets'):
            time.sleep(0.1)
            content = self.browser.page_source
            soup = BS(content, 'lxml')
        if not soup.select('.live-group-item.sportcolor-bg-B'):
            self.games_found = False
            return
        element = self.browser.find_element_by_css_selector('.live-group-item.sportcolor-bg-B')
        self.games_found = True
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        while True:
            live_blocks = element.find_elements_by_css_selector('.live-block-column.live-block-column_data')
            hrefs = []
            for live_block in live_blocks:
                if live_block.get_attribute("href") == 'https://www.parimatch.ru/null':
                    self.browser.execute_script("arguments[0].scrollIntoView();", live_block)
                    hrefs.append('https://www.parimatch.ru/null')
            if not 'https://www.parimatch.ru/null' in hrefs:
                self.start_work_time = time.time()
                self.main_page_load = True
                break

    def get_events(self):
        if not self.main_page_load:
            self.get_main_page()
        if time.time() - self.start_work_time > 180:
            self.get_main_page()
        if not self.games_found:
            return []
        if self.browser.current_url == self.url:
            content = self.browser.page_source
        else:
            while self.browser.current_url == self.url:
                for page in self.browser.window_handles:
                    self.browser.switch_to.window(page)
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
                    'total_score1': int(total_score1),
                    'total_score2': int(total_score2),
                    'scores_1': scores1,
                    'scores_2': scores2,
                    'time': time_match,
                }
                events_info.append(event_info)
        return events_info

    def get_current_urls(self):
        if self.browser:
            current_urls = []
            for page in self.browser.window_handles:
                self.browser.switch_to.window(page)
                current_urls.append(self.browser.current_url)
            return current_urls

    def get_value(self, href):
        url = 'https://www.parimatch.ru' + href
        self.browser.execute_script(f'window.open("{url}", "new window")')
        self.browser.switch_to.window(self.browser.window_handles[-1])
        while True:
            try:
                element = self.browser.find_element_by_css_selector('.event-outcome__value')
                if element.get:
                    break
            except NoSuchElementException:
                pass
        content = self.browser.page_source
        soup = BS(content, 'lxml')
        with open('parimatch_match.html', 'w', encoding='utf8') as html_file:
            html_file.write(str(soup))

parser = ParimatchParser()
parser.open_browser()
parser.get_value("/event/B%7CLTU%7CPT2931:2830420522/21388070")