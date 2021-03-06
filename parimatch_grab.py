from bs4 import BeautifulSoup as BS
import requests


class ParimatchGrab:
    MAIN_HEADERS = {
        'Host': 'ru.parimatch.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'http://ru.parimatch.com/live.html'
    }
    URL = 'http://ru.parimatch.com/live_as.html?curs=0&curName=$&shed=0'

    def get_request_events(self):
        return [self.URL], [self.MAIN_HEADERS]

    def get_events(self, response):
        soup = BS(response, 'lxml')
        sport_basketball = soup.select('.sport.basketball')
        #sport_basketball = soup.select('.sport.volleyball')
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
                total_score2 = score_full.split('(')[0].split('-')[-1]  # есть ошибка, видимо в начале матча
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
                    'id': href.split('=')[-1],
                    'champ': champ,
                    'command1': command1,
                    'command2': command2,
                    'total_score1': total_score1,
                    'total_score2': total_score2,
                    'scores_1': scores_1,
                    'scores_2': scores_2
                }
                events_info.append(event_info)
        return events_info

    def get_request_value(self, id):
        url = f'http://ru.parimatch.com/live_ar.html?hl={id}&hl={id},&curs=0&curName=$'
        headers = self.MAIN_HEADERS
        headers['Referer'] = f'http://ru.parimatch.com/bet.html?hl={id}'
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
        elif len(tds) == 11:
            t_it_m_1 = [{'coef': tds[9].select('u')[0].text, 'points': float(tds[8].select('b')[0].text)}]
            t_it_s_1 = [{'coef': tds[10].select('u')[0].text, 'points': float(tds[8].select('b')[0].text)}]
            t_it_m_2 = [{'coef': tds[9].select('u')[1].text, 'points': float(tds[8].select('b')[1].text)}]
            t_it_s_2 = [{'coef': tds[10].select('u')[1].text, 'points': float(tds[8].select('b')[1].text)}]
            value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
            value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
            value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
        elif len(tds) == 10:
            t_it_m_1 = [{'coef': False, 'points': False}]
            t_it_s_1 = [{'coef': False, 'points': False}]
            t_it_m_2 = [{'coef': False, 'points': False}]
            t_it_s_2 = [{'coef': False, 'points': False}]
            value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
            value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
            value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
        props = main_block[0].select_one('.row1.props')
        trs = props.select('tr')
        bks = props.select('.bk')
        quarter_values = {}
        qurter_keys = []
        for bk in bks:
            tds = bk.select('td')
            if 'четв.' in tds[1].text:
                qurter_keys.append(tds[1].text)
                quarter_values[tds[1].text] = {'total_total':{'more': [{'coef': float(tds[5].text), 'points': float(tds[4].text)}],
                                              'smaller':[{'coef': float(tds[6].text), 'points': float(tds[4].text)}]}}
                qurter_keys.append(tds[1].text)
            if '\xa0' == tds[1].text:
                quarter_values[qurter_keys[-1]]['total_total']['more'].append({'coef': float(tds[4].text), 'points': float(tds[3].text)})
                quarter_values[qurter_keys[-1]]['total_total']['smaller'].append({'coef': float(tds[5].text), 'points': float(tds[3].text)})
        value_main['quarter_value'] = quarter_values
        tr_dop = get_tr_dop_info(trs)
        if tr_dop:
            dop_coefs = get_dop_coef(tr_dop)
            for coef in dop_coefs:
                value_main['total_total']['more'].append({'coef': coef[1], 'points': coef[0]})
                value_main['total_total']['smaller'].append({'coef': coef[2], 'points': coef[0]})
        return value_main


def get_tr_dop_info(trs):
    for tr in trs:
        btb = tr.select_one('.btb')
        if btb:
            th = btb.select_one('th')
            if th:
                if th.text == 'Дополнительные тоталы:':
                    return tr


def get_dop_coef(tr_dop):
    coefs = []
    txt = tr_dop.text.replace(' Дополнительные тоталы: ', '')
    bets = [el for el in txt.split('(') if el]
    for bet in bets:
        point = float(bet.split(') ')[0])
        more_coef_txt = bet.split(') ')[1].split('; ')[0]
        more_coef = float(more_coef_txt.replace('больше ', ''))
        smaller_coef_txt = bet.split(') ')[1].split('; ')[1]
        smaller_coef = float(smaller_coef_txt.replace('меньше ', ''))
        coefs.append([point,more_coef,smaller_coef])
    return coefs

# Достать индивидуальные тоталы по четвертям

if __name__ == "__main__":
    parser = ParimatchGrab()
    urls, headers = parser.get_request_events()
    data = requests.get(urls[0], headers= headers[0])
    events = parser.get_events(data.text)
    for event in events:
        url, headers = parser.get_request_value(event['id'])
        data = requests.get(url, headers=headers)
        # with open(f"""{event['id']}.html""", 'w', encoding='utf8') as html_file:
        #     html_file.write(str(data.text))
        value = parser.get_value(data.text)
        print(value)