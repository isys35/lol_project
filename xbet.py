import requests
from bs4 import BeautifulSoup as BS
import time
from requests.exceptions import ConnectionError


# with open('xbet.html', 'w', encoding='utf8') as html_file:
#     html_file.write(r.text)

class XBetParser:
    def __init__(self):
        self.url = 'https://1xstavka.ru/live/Basketball/'
        self.delay = 0.15
        self.main_headers = {
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
        }

    def get_response(self, url, headers):
        time.sleep(self.delay)
        while True:
            print('connect...')
            r = None
            while not r:
                try:
                    r = requests.get(url, headers=headers)
                except ConnectionError:
                    print('[WARNING] Проблема с соединением')
                    time.sleep(1)
            if r.status_code == 200:
                return r

    def get_events(self):
        response = self.get_response(self.url, self.main_headers)
        soup = BS(response.content, 'lxml')
        champs = soup.select('.c-events__liga')
        champs_string = []
        for champ in champs:
            champs_string.append(champ.text.strip())
        events = soup.select('.c-events__item.c-events__item_col')
        events_info = []
        for i in range(0, len(events)):
            event_info = {}
            href = events[i].select('.c-events__name')[0]['href']
            print(href)
            print(len(events_info))
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
                if not events[i].select('.c-events__time')[0].select('span'):
                    continue
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
        return events_info

    def selected_values(self, json_object):
        if json_object['Value']['GE']:
            value = {}
            for el in json_object['Value']['GE']:
                if el['G'] == 4:
                    t_ot_m = [{'coef': t['C'], 'points':t['P']} for t in el['E'][0]]
                    t_ot_s = [{'coef': t['C'], 'points':t['P']} for t in el['E'][1]]
                    value['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
                if el['G'] == 5:
                    t_it_m_1 = [{'coef': t['C'], 'points':t['P']} for t in el['E'][0]]
                    t_it_s_1 = [{'coef': t['C'], 'points':t['P']} for t in el['E'][1]]
                    value['individ_total_1'] = {'more':t_it_m_1, 'smaller': t_it_s_1}
                if el['G'] == 6:
                    t_it_m_2 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][0]]
                    t_it_s_2 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][1]]
                    value['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
            if 'SG' in json_object['Value']:
                value['id_quarter'] = str(json_object['Value']['SG'][-1]['I'])
                if 'PN' in json_object['Value']['SG'][-1]:
                    value['name_quarter'] = json_object['Value']['SG'][-1]['PN']
        else:
            # ставок нету
            value = {}
        return value

    def get_id(self, url):
        return url.split('/')[-2].split('-')[0], url.split('/')[-2].replace(url.split('/')[-2].split('-')[0], '')+'/'

    def get_value_json(self, id, url):
        url_koef = f'https://1xstavka.ru/LiveFeed/GetGameZip?id={id}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=250&partner=51&grMode=2'
        headers = self.main_headers
        headers['Referer'] = 'https://1xstavka.ru/' + id + url
        response = self.get_response(url_koef, headers)
        return response.json()

    def get_value(self, href):
        id, split_href = self.get_id(href)
        values_main_time_json = self.get_value_json(id, split_href)
        values_main_time = self.selected_values(values_main_time_json)
        if 'id_quarter' in values_main_time:
            values_qurter_json = self.get_value_json(values_main_time['id_quarter'], split_href)
            values_qurter = self.selected_values(values_qurter_json)
        else:
            values_qurter = {}
        return values_main_time, values_qurter

