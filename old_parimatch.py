from bs4 import BeautifulSoup as BS
import request as req


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

    def get_events(self):
        response = req.response(self.url, self.headers)
        soup = BS(response.content, 'lxml')
        sport_basketball = soup.select('.sport.basketball')
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
            href = name_block[0].select('a')[0]['href']
            score_full = name_block[0].select('.score')[0].text
            commands = name_block[0].text.replace(score_full, '').strip()
            command1 = commands.split(' - ')[0].strip()
            command2 = commands.split(' - ')[1].strip()
            champ = champs_dict[event['id'].replace('Item', '')]
            total_score1 = score_full.split('(')[0].split('-')[0]
            total_score2 = score_full.split('(')[0].split('-')[-1] # есть ошибка, видимо в начале матча
            score_sets = score_full.split('(')[1].replace(')', '')
            scores_1 = [el.split('-')[0] for el in score_sets.split(',')]
            scores_2 = [el.split('-')[1] for el in score_sets.split(',')]
            event_info = {
                'href': href,
                'champ': champ,
                'command1': command1,
                'command2': command2,
                'total_score1': int(total_score1),
                'total_score2': int(total_score2),
                'scores_1': scores_1,
                'scores_2': scores_2,
                'time': None,
            }
            events_info.append(event_info)
        return events_info

    def get_value(self, href):
        url = 'http://ru.parimatch.com/' + href
        print(url)
        headers = self.headers
        headers['Referer'] = self.url
        response = req.response(url, headers)
        soup = BS(response.content, 'lxml')
        main_block = soup.select('.row1')
        tds = main_block[0].select('td')
        value_main = {}
        if len(tds) < 13:
            return value_main
        value_main = {}
        t_ot_m = [{'coef': tds[5].text, 'points': tds[4].text}]
        t_ot_s = [{'coef': tds[6].text, 'points': tds[4].text}]
        t_it_m_1 = [{'coef': tds[11].select('u')[0].text, 'points': tds[10].select('b')[0].text}]
        t_it_s_1 = [{'coef': tds[12].select('u')[0].text, 'points': tds[10].select('b')[0].text}]
        t_it_m_2 = [{'coef': tds[11].select('u')[1].text, 'points': tds[10].select('b')[1].text}]
        t_it_s_2 = [{'coef': tds[12].select('u')[1].text, 'points': tds[10].select('b')[1].text}]
        value_main['total_total'] = {'more': t_ot_m, 'smaller': t_ot_s}
        value_main['individ_total_1'] = {'more': t_it_m_1, 'smaller': t_it_s_1}
        value_main['individ_total_2'] = {'more': t_it_m_2, 'smaller': t_it_s_2}
        return value_main


if __name__ == "__main__":
    parser = ParimatchParser()
    events = parser.get_events()
    for event in events:
        value = parser.get_value(event['href'])
        print(value)
