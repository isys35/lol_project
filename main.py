from threading import Thread
from xbet import XBetParser
from parimatch import ParimatchParser
import time


class Parsing(Thread):
    def __init__(self, website_object, name):
        super().__init__()
        self.website_object = website_object
        self.name = name
        self.events = []

    def parsing(self):
        self.events = self.website_object.get_events()

    def run(self):
        while True:
            self.parsing()


def transform_name(events, key):
    names = []
    for event in events:
        name = event[key].lower()
        name = name.replace(' ', '')
        name = name.replace('(', '')
        name = name.replace(')', '')
        name = name.replace('-', '')
        name = name.replace('жен', '')
        name = name.replace('ж', '')
        name = name.replace('люб', '')
        for i in range(0, 10):
            name = name.replace(f'{i}', '')
        name = name.replace('U', '')
        name = name.replace('u', '')
        names.append(name)
    return names


xbet_parser = XBetParser()
parimatch_parser = ParimatchParser()
xbet_th = Parsing(xbet_parser, '1Xbet')
xbet_th.start()
parimatch_th = Parsing(parimatch_parser, 'parimatch')
parimatch_th.start()
while True:
    events_xbet = xbet_th.events
    events_parimatch = parimatch_th.events
    if events_xbet and events_parimatch:
        command1_transform_xbet = transform_name(events_xbet, 'command1')
        command1_transform_parimatch = transform_name(events_parimatch, 'command1')
        matches = []
        for i in range(0, len(command1_transform_xbet)):
            if command1_transform_xbet[i] in command1_transform_parimatch:
                match = [xbet_th.events[i],
                         parimatch_th.events[command1_transform_parimatch.index(command1_transform_xbet[i])]]
                if not match in matches:
                    matches.append(match)
        command2_transform_xbet = transform_name(events_xbet, 'command2')
        command2_transform_parimatch = transform_name(events_parimatch, 'command2')
        for i in range(0, len(command2_transform_xbet)):
            if command2_transform_xbet[i] in command2_transform_parimatch:
                match = [xbet_th.events[i],
                         parimatch_th.events[command2_transform_parimatch.index(command2_transform_xbet[i])]]
                if not match in matches:
                    matches.append(match)
        print(f'[INFO] Найдено {len(matches)} совпадений')
        for match in matches:
            print(f'Основные данные для {matches.index(match)+1} -го совпадения')
            print('********1xbet*************')
            print(match[0])
            print('********Parimatch***********')
            print(match[1])
            total_value, set_value = xbet_parser.get_value(match[0]['href'])
            print(f'Коэф-ты для {matches.index(match) + 1} -го совпадения')
            print('********1xbet*************')
            print('Общие')
            print(total_value)
            print('По четверти')
            print(set_value)
            total_value2 = parimatch_parser.get_value(match[1]['href'])
            print('********Parimatch*************')
            print('Общие')
            print(total_value2)