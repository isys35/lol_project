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
            return r.content

    def get_champs(self):
        response = self.get_response(self.url, self.main_headers)
        soup = BS(response, 'lxml')
        champs = soup.select('.c-events__liga')
        champs_string = []
        for champ in champs:
            champs_string.append(champ.text.strip())
        events = soup.select('.c-events__item.c-events__item_col')
        events_info = []
        for i in range(0, len(events)):
            event_info = {}
            href = events[i].select('.c-events__name')[0]['href']
            if i!=0:
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
            total_score1 = total_score[0].text
            total_score2 = total_score[1].text
            scores = events[i].select('.c-events-scoreboard__cell')
            scores_1 = [int(el.text) for el in scores[1:int(len(scores)/2)]]
            scores_2 = [int(el.text) for el in scores[int(len(scores) / 2 + 1):]]
            event_info['href'] = href
            event_info['champ'] = champ
            event_info['command1'] = command1
            event_info['command2'] = command2
            event_info['total_score1'] = int(total_score1)
            event_info['total_score2'] = int(total_score2)
            event_info['scores_1'] = scores_1
            event_info['scores_2'] = scores_2
            events_info.append(event_info)
        for event in events_info:
            print(event)


xbet_parser = XBetParser()
xbet_parser.get_champs()
