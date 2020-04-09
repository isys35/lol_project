import json
import requests


class XBetGrab:
    MAIN_HEADERS = {
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'Referer': 'https://1xstavka.ru/live/Basketball/'
        }
    URL = 'https://1xstavka.ru/LiveFeed/BestGamesExtVZip?sports=3&count=10&antisports=188&partner=51&getEmpty=true&mode=4&country=22'
    BROKER = '1xставка'

    def get_request_events(self):
        return [self.URL], [self.MAIN_HEADERS]


    def get_events(self, response):
        data = json.loads(response)
        events = []
        for event in data['Value']:
            index = event['I']
            champ = event['L']
            if 'O1' not in event or 'O2' not in event:
                continue
            command1 = event['O1']
            command2 = event['O2']
            if not event['SC']['FS']:
                continue
            if 'S1' in event['SC']['FS']:
                total_score1 = event['SC']['FS']['S1']
            else:
                total_score1 = 0
            if 'S2' in event['SC']['FS']:
                total_score2 = event['SC']['FS']['S2']
            else:
                total_score2 = 0
            scores_1 = []
            for sc in event['SC']['PS']:
                if 'S1' in sc['Value']:
                    scores_1.append(sc['Value']['S1'])
                else:
                    scores_1.append(0)
            scores_2 = []
            for sc in event['SC']['PS']:
                if 'S2' in sc['Value']:
                    scores_2.append(sc['Value']['S2'])
                else:
                    scores_2.append(0)
            timer = event['SC']['TS']
            event_info = {'champ': champ, 'command1': command1, 'command2': command2,
                          'total_score1': int(total_score1), 'total_score2': int(total_score2), 'scores_1': scores_1,
                          'scores_2': scores_2, 'time': timer, 'id': index}
            events.append(event_info)
        return events

    def get_request_value(self, id):
        # возможно referer не требуется
        url = f'https://1xstavka.ru/LiveFeed/GetGameZip?id={id}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true' \
            f'&allEventsGroupSubGames=true&countevents=250&partner=51&grMode=2 '
        headers = self.MAIN_HEADERS
        return url, headers

    def get_value(self, response, quarter=False):
        data = json.loads(response)
        if data['Value']['GE']:
            value = {}
            for el in data['Value']['GE']:
                if el['G'] == 4:
                    t_ot_m = [{'coef': t['C'], 'points': t['P']} for t in el['E'][0]]
                    t_ot_s = [{'coef': t['C'], 'points': t['P']} for t in el['E'][1]]
                    value['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
                if el['G'] == 5:
                    t_it_m_1 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][0]]
                    t_it_s_1 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][1]]
                    value['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
                if el['G'] == 6:
                    t_it_m_2 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][0]]
                    t_it_s_2 = [{'coef': t['C'], 'points': t['P']} for t in el['E'][1]]
                    value['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
            if value:
                if quarter:
                    if 'CPS' in data['Value']['SC']:
                        value['quarter'] = data['Value']['SC']['CPS']
                        if 'SG' in data['Value']:
                            value['quarters_ids'] = [[el['I'], el['PN']] for el in data['Value']['SG'] if 'PN' in el and 'TG' not in el]
                            quarters_value = {}
                            for index in value['quarters_ids']:
                                url, headers = self.get_request_value(index[0])
                                response = requests.get(url, headers=headers)
                                quarter_value = self.get_value(response.text, False)
                                quarters_value[index[1]] = quarter_value
                            value['quarters_values'] = quarters_value
        else:
            value = {}
        print(value)
        return value


if __name__ == "__main__":
    parser = XBetGrab()
    urls, headers = parser.get_request_events()
    while True:
        data = requests.get(urls[0], headers = headers[0])
        print(data)