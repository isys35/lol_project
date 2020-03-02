import requests
from bs4 import BeautifulSoup as BS
import time


# with open('xbet.html', 'w', encoding='utf8') as html_file:
#     html_file.write(r.text)



class XBetParser:
    def __init__(self):
        self.url = 'https://1xstavka.ru/live/Basketball/'
        self.delay = 0.5
        self.main_headers = {
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
        }

    def get_response(self, url, headers):
        time.sleep(self.delay)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r

    def get_champs(self):
        response = self.get_response(self.url, self.main_headers)
        soup = BS(response.content , 'lxml')
        champs = soup.select('.c-events__liga')
        champs_string = []
        for champ in champs:
            champs_string.append(champ.text.strip())
        events = soup.select('.c-events__item.c-events__item_col')
        events_info = []
        for i in range(0, len(events)):
            event_info = {}
            href = events[i].select('.c-events__name')[0]['href']
            if i != 0:
                if events_info[i-1]['href'].split('/')[-3] == href.split('/')[-3]:
                    champ = events_info[i-1]['champ']
                else:
                    champ = champs_string.pop(0)
            else:
                champ = champs_string.pop(0)
            teams = events[i].select('.c-events__team')
            command1 = teams[0].text
            command2 = teams[1].text
            total_score = events[i].select('.c-events-scoreboard__cell.c-events-scoreboard__cell--all')
            if total_score:
                total_score1 = total_score[0].text
                total_score2 = total_score[1].text
                time_event = events[i].select('.c-events__time')[0].select('span')[0].text
                scores = events[i].select('.c-events-scoreboard__cell')
                scores_1 = [int(el.text) for el in scores[1:int(len(scores) / 2)]]
                scores_2 = [int(el.text) for el in scores[int(len(scores) / 2 + 1):]]
            else:
                total_score1 = 0
                total_score2 = 0
                time_event = '00:00'
                scores_1 = 0
                scores_2 = 0
            id = self.get_id(href)
            value = self.get_value(id, href)
            event_info['href'] = href
            event_info['champ'] = champ
            event_info['command1'] = command1
            event_info['command2'] = command2
            event_info['total_score1'] = int(total_score1)
            event_info['total_score2'] = int(total_score2)
            event_info['scores_1'] = scores_1
            event_info['scores_2'] = scores_2
            event_info['time'] = time_event
            events_info.append(event_info)

    def get_id(self, url):
        return url.split('/')[-2].split('-')[0]

    def get_value(self, id, url):
        url_koef = f'https://1xstavka.ru/LiveFeed/GetGameZip?id={id}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=250&partner=51&grMode=2'
        headers = self.main_headers
        headers['Referer'] = 'https://1xstavka.ru/'+url
        response = self.get_response(url_koef, headers)
        print(response.json())


xbet_parser = XBetParser()
xbet_parser.get_champs()
