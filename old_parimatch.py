from bs4 import BeautifulSoup as BS
import json
import request as req
import time


class ParimatchParser:
    def __init__(self):
        self.url = 'http://ru.parimatch.com/live.html'
        self.headers = {
            'Host': 'ru.parimatch.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def get_request_events(self):
        return [self.url], [self.headers]

    def get_events(self, response):
        soup = BS(response, 'lxml')
        sport_basketball = soup.select('.sport.basketball')
        # with open('parimatch.html', 'w', encoding='utf8') as html_file:
        #     html_file.write(str(sport_basketball))
        if sport_basketball:
            champs = sport_basketball[0].select('.sport.item')
        else:
            return []
        champs_dict = {}
        for champ in champs:
            champs_dict[champ.select('a')[0]['id']] = champ.text
        events = sport_basketball[0].select('.subitem')
        events_info = []
        for event in events:
            name_block = event.select('.td_n')
            champ = champs_dict[event['id'].replace('Item', '')]
            for match in name_block:
                if not match.select('a'):
                    return []
                href = match.select('a')[0]['href']
                score_full = match.select('.score')[0].text
                commands = match.text.replace(score_full, '').strip()
                command1 = commands.split(' - ')[0].strip()
                command2 = commands.split(' - ')[1].strip()
                total_score1 = score_full.split('(')[0].split('-')[0]
                total_score2 = score_full.split('(')[0].split('-')[-1] # есть ошибка, видимо в начале матча
                if total_score1:
                    total_score1 = int(total_score1)
                else:
                    total_score1 = 0
                if total_score2:
                    total_score2 = int(total_score2)
                else:
                    total_score2 = 0
                try:
                    score_sets = score_full.split('(')[1].replace(')', '')
                    scores_1 = [el.split('-')[0] for el in score_sets.split(',')]
                    scores_2 = [el.split('-')[1] for el in score_sets.split(',')]
                except IndexError:
                    scores_1 = [0]
                    scores_2 = [0]
                event_info = {
                    'href': href,
                    'champ': champ,
                    'command1': command1,
                    'command2': command2,
                    'total_score1': total_score1,
                    'total_score2': total_score2,
                    'scores_1': scores_1,
                    'scores_2': scores_2,
                    'time': None,
                }
                events_info.append(event_info)
        return events_info

    def get_request_value(self, href):
        url = 'http://ru.parimatch.com/' + href
        headers = self.headers
        headers['Referer'] = self.url
        return url, headers

    def get_value(self, response):
        soup = BS(response, 'lxml')
        main_block = soup.select('#oddsList')
        main_info = main_block[0].select('.bk')
        if not main_info:
            return {}
        tds = main_info[0].select('td')
        value_main = {}
        if len(tds) == 3 and tds[2].text == 'Прием ставок приостановлен':
            print('Прием ставок приостановлен')
            return value_main
        if len(tds) == 2 or len(tds) == 5 or len(tds) == 4:
            print('Нету коэф')
            return value_main
        with open('parimatch.html', 'w', encoding='utf8') as html_file:
             html_file.write(str(main_block))
        t_ot_m = [{'coef': float(tds[5].text), 'points': float(tds[4].text)}]
        t_ot_s = [{'coef': float(tds[6].text), 'points': float(tds[4].text)}]
        if len(tds) == 13:
            t_it_m_1 = [{'coef': tds[11].select('u')[0].text, 'points': float(tds[10].select('b')[0].text)}]
            t_it_s_1 = [{'coef': tds[12].select('u')[0].text, 'points': float(tds[10].select('b')[0].text)}]
            t_it_m_2 = [{'coef': tds[11].select('u')[1].text, 'points': float(tds[10].select('b')[1].text)}]
            t_it_s_2 = [{'coef': tds[12].select('u')[1].text, 'points': float(tds[10].select('b')[1].text)}]
            value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
            value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
            value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
            return value_main
        elif len(tds) == 11:
            t_it_m_1 = [{'coef': tds[9].select('u')[0].text, 'points': float(tds[8].select('b')[0].text)}]
            t_it_s_1 = [{'coef': tds[10].select('u')[0].text, 'points': float(tds[8].select('b')[0].text)}]
            t_it_m_2 = [{'coef': tds[9].select('u')[1].text, 'points': float(tds[8].select('b')[1].text)}]
            t_it_s_2 = [{'coef': tds[10].select('u')[1].text, 'points': float(tds[8].select('b')[1].text)}]
            value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
            value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
            value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
            return value_main
        elif len(tds) == 10:
            t_it_m_1 = [{'coef': False, 'points': False}]
            t_it_s_1 = [{'coef': False, 'points': False}]
            t_it_m_2 = [{'coef': False, 'points': False}]
            t_it_s_2 = [{'coef': False, 'points': False}]
            value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
            value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
            value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
            return value_main


class ParimatchParserTest:
    def get_events(self):
        try:
            with open("parimtatch_events.json", "r") as file:
                return json.load(file)
        except PermissionError:
            time.sleep(1)
            with open("parimtatch_events.json", "r") as file:
                return json.load(file)

    def get_value(self):
        try:
            with open("parimtatch_value.json", "r") as file:
                return json.load(file)
        except PermissionError:
            time.sleep(1)
            with open("parimtatch_value.json", "r") as file:
                return json.load(file)


if __name__ == "__main__":
    parser = ParimatchParserTest()
    events = parser.get_events()
    while True:
        print(parser.get_value())
