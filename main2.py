from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
import mainwindow
import traceback
import sys
from old_parimatch import ParimatchParser
from xbet import XBetParser
import vilkawidget
import time
import async_request
from PyQt5 import sip


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parimatch = ParimatchParser()
        self.xbet = XBetParser()
        self.find_same_matches = ThreadParser(self)
        self.find_same_matches.start()
        self.update_same_matches = ThreadUpdateSameMatches(self)
        self.update_same_matches.start()
        self.same_events = []
        self.pushButton_2.clicked.connect(self.update_vilka_wigets)
        self.pushButton_2.setVisible(False)
        self.pushButton.setVisible(False)
        self.active_widgets = []

    def clear_widgets(self):
        for widget in self.active_widgets:
            print(widget.vilka.status)
            if widget.vilka.status == 'dead':
                print('удаляем мёртвый виджет')
                widget.setVisible(False)
                self.active_widgets.remove(widget)
                # self.verticalLayout_5.removeWidget(widget)
                # sip.delete(widget)

    def update_vilka_wigets(self):
        print('CLICK')
        print(self.same_events)
        try:
            if not self.active_widgets:
                for events in self.same_events:
                    for total_vilka in events.vilki['total_total']:
                        vilkawidg = VilkaWidget(total_vilka)
                        self.verticalLayout_5.addWidget(vilkawidg)
                        self.active_widgets.append(vilkawidg)
                    for individ1_vilka in events.vilki['individ_total_1']:
                        vilkawidg = VilkaWidget(individ1_vilka)
                        self.verticalLayout_5.addWidget(vilkawidg)
                        self.active_widgets.append(vilkawidg)
                    for individ2_vilka in events.vilki['individ_total_2']:
                        vilkawidg = VilkaWidget(individ2_vilka)
                        self.verticalLayout_5.addWidget(vilkawidg)
                        self.active_widgets.append(vilkawidg)
            else:
                self.clear_widgets()
                for widget in self.active_widgets:
                    widget.update_odds_labels()
                active_vilki = [widget.vilka for widget in self.active_widgets]
                print('АКТИВНЫЕ ВИЛКИ')
                print(active_vilki)
                for events in self.same_events:
                    for total_vilka in events.vilki['total_total']:
                        if total_vilka.status == 'life' and total_vilka not in active_vilki:
                            vilkawidg = VilkaWidget(total_vilka)
                            self.verticalLayout_5.addWidget(vilkawidg)
                            self.active_widgets.append(vilkawidg)
                    for individ1_vilka in events.vilki['individ_total_1']:
                        if individ1_vilka.status == 'life' and individ1_vilka not in active_vilki:
                            vilkawidg = VilkaWidget(individ1_vilka)
                            self.verticalLayout_5.addWidget(vilkawidg)
                            self.active_widgets.append(vilkawidg)
                    for individ2_vilka in events.vilki['individ_total_2']:
                        if individ2_vilka.status == 'life' and individ2_vilka not in active_vilki:
                            vilkawidg = VilkaWidget(individ2_vilka)
                            self.verticalLayout_5.addWidget(vilkawidg)
                            self.active_widgets.append(vilkawidg)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())


class VilkaWidget(QtWidgets.QWidget, vilkawidget.Ui_Form):
    def __init__(self, vilka):
        super().__init__()
        self.setupUi(self)
        self.vilka = vilka
        self.update_main_labels()
        self.update_odds_labels()

    def update_main_labels(self):
        self.label_7.setText(self.vilka.commands[0][0] + ' - ' + self.vilka.commands[0][1])
        self.label_9.setText(self.vilka.commands[1][0] + ' - ' + self.vilka.commands[1][1])
        self.label_8.setText(self.vilka.champs[0])
        self.label_10.setText(self.vilka.champs[1])

    def update_odds_labels(self):
        self.label.setText(str(int(self.vilka.time_life)))
        self.label_2.setText(str(round(self.vilka.value,2)))
        self.label_11.setText(str(self.vilka.point))
        self.label_12.setText(str(self.vilka.point))
        self.label_15.setText(str(self.vilka.koef_pari))
        self.label_16.setText(str(self.vilka.koef_xbet))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


class ThreadParser(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def get_events(self):
        self.window.statusBar().showMessage('connect...')
        url_p,head_p = self.window.parimatch.get_request_events()
        url_x,head_x = self.window.xbet.get_request_events()
        url_p.append(url_x[0])
        head_p.append(head_x[0])
        async_req_urls = url_p
        async_req_head = head_p
        responces = async_request.input_reuqests(async_req_urls, async_req_head)
        events_parimatch = self.window.parimatch.get_events(responces[0])
        events_xbet = self.window.xbet.get_events(responces[1])
        self.window.label_5.setText(str(len(events_parimatch)))
        self.window.label_3.setText(str(len(events_xbet)))
        return {'pari':events_parimatch, 'xbet':events_xbet}

    def search_matches(self, events: dict):
        print('[INFO] Поиск одинаковых событий')
        same_matches = []
        for match_p in events['pari']:
            for match_x in events['xbet']:
                if match_p['total_score1'] and match_p['total_score2']:
                    if match_p['total_score1'] == match_x['total_score1'] \
                            and match_p['total_score2'] == match_x['total_score2']:
                        same_matches.append([match_p, match_x])
        return same_matches

    def main(self):
        print('[INFO] Получение событий')
        events = self.get_events()
        same_events = self.search_matches(events)
        print(f'[INFO] Одинаковые события {len(same_events)} штук'
              f' {same_events}')
        self.window.label_2.setText(f'{len(same_events)}')
        objects_events = [SameGame(
            [match['href'] for match in events],
            [match['champ'] for match in events],
            [[match['command1'], match['command2']] for match in events],
            self.window
        ) for events in same_events]
        if not self.window.same_events:
            self.window.same_events = objects_events
        else:
            hrefs = [window_event.hrefs for window_event in self.window.same_events]
            for event in objects_events:
                if event.hrefs not in hrefs:
                    print('[INFO] Добавление новых матчей')
                    self.window.same_events.append(event)

    def run(self):
        try:
            while True:
                self.main()
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())


class SameGame:
    def __init__(self, hrefs, champs, commands, window):
        super().__init__()
        print(f' инициализация обЪекта {self}')
        self.hrefs = hrefs
        self.champs = champs
        self.commands = commands
        self.window = window
        self.vilki = {
            'total_total': [],
            'individ_total_1': [],
            'individ_total_2': []
        }
        self.count_dead = 0
        self.status = 'life'

    def get_odds(self):
        print(f'[INFO] Получение коэфф-тов для {self.commands} {self}')
        url_p, head_p = self.window.parimatch.get_request_value(self.hrefs[0])
        url_x, head_x = self.window.xbet.get_request_value(self.hrefs[1])
        url = [url_p, url_x]
        head = [head_p, head_x]
        responces = async_request.input_reuqests(url, head)
        val_pari = self.window.parimatch.get_value(responces[0])
        val_xbet = self.window.xbet.get_value(responces[1])
        print(f'[INFO] Коэфф-ты для {self.commands} париматч')
        print(val_pari)
        print(f'[INFO] Коэфф-ты для {self.commands} 1хставка')
        print(val_xbet)
        if val_pari and val_xbet:
            self.count_dead = 0
            for key in self.vilki:
                self.get_value(val_pari, val_xbet, key)
        if not val_pari and not val_xbet:
            if self.count_dead == 2:
                self.status = 'dead'
                vilki = [vilka for key, items in self.vilki.items() for vilka in items]
                for vilka in vilki:
                    vilka.status = 'dead'
            else:
                self.count_dead += 1
        time.sleep(0.5)
        self.window.pushButton_2.click()

    def get_value(self, val_pari, val_xbet, key):
        print(f'[INFO] Поиск вилок {self.commands} {key}')
        try:
            points_pari = [bet['points'] for bet in val_pari[key]['more']]
            points_xbet = [bet['points'] for bet in val_xbet[key]['smaller']]
        except KeyError:
            for vilki in self.vilki[key]:
                vilki.update([])
            return
        print(f'[INFO] Очки {key} {self.commands} париматч {points_pari}')
        print(f'[INFO] Очки {key} {self.commands} 1ставка {points_xbet}')
        coincidences = [p1 for p1 in points_pari for p2 in points_xbet if p1 == p2]
        print(f'[INFO] Совпавшие очки {key} {self.commands} {coincidences}')
        if not coincidences:
            for vilki in self.vilki[key]:
                vilki.update([])
            return
        koef_pari = [float(bet['coef']) for bet in val_pari[key]['more']
                     for point in coincidences if bet['points'] == point]
        print(f'[INFO] Коэф-ты париматч {key} {self.commands} для {coincidences} : {koef_pari}')
        koef_xbet = [bet['coef'] for bet in val_xbet[key]['smaller']
                     for point in coincidences if bet['points'] == point]
        print(f'[INFO] Коэф-ты 1хставка {key} {self.commands} для {coincidences} : {koef_xbet}')
        vilki = [1 / koef_pari[i] + 1 / koef_xbet[i] for i in range(len(coincidences))]
        print(f'[INFO] Вилки {key} {self.commands} : {vilki}')
        value = [100 * (1 - vilka) for vilka in vilki]
        print(f'[INFO] Доходность {key} {self.commands} : {value}')
        vilki_o = [Vilka(self,
                         key,
                         coincidences[i],
                         koef_pari[i],
                         koef_xbet[i],
                         value[i]) for i in range(len(coincidences))]
        if not self.vilki[key]:
            self.vilki[key] = vilki_o
        else:
            points = [vilki.point for vilki in self.vilki[key] if vilki.status == 'life']
            for vilki in self.vilki[key]:
                if vilki.status == 'life':
                    vilki.update(vilki_o)
            for new_vilki in vilki_o:
                if new_vilki.point not in points:
                    self.vilki[key].append(new_vilki)


class Vilka:
    def __init__(self, samegame, vilka_type, point, koef_pari, koef_xbet, value):
        super().__init__()
        self.champs = samegame.champs
        self.window = samegame.window
        self.commands = samegame.commands
        self.vilka_type = vilka_type
        self.point = point
        self.koef_pari = koef_pari
        self.koef_xbet = koef_xbet
        self.value = value
        self.dead_count = 0
        self.status = 'life'
        self.t0 = time.time()
        self.time_life = 0

    def update(self, vilki):
        print(vilki)
        print(f'[INFO] Обновление вилки {self.point} {self.vilka_type} {self.commands}')
        confidence_vilka = [vilka for vilka in vilki if vilka.point == self.point]
        if not confidence_vilka:
            self.status = 'dead'
            return
        self.koef_pari = confidence_vilka[0].koef_pari
        self.koef_xbet = confidence_vilka[0].koef_xbet
        self.value = confidence_vilka[0].value
        self.time_life = time.time() - self.t0

    def get_value(self, val_pari, val_xbet, key):
        print(f'[INFO] Получаем очки для {self.commands} {key}')
        points_pari = [bet['points'] for bet in val_pari[key]['more']]
        points_xbet = [bet['points'] for bet in val_xbet[key]['more']]
        print(f'[INFO] Очки {key} {self.commands} париматч {points_pari}')
        print(f'[INFO] Очки {key} {self.commands} 1ставка {points_xbet}')
        if self.point not in points_pari or self.point not in points_xbet:
            print(f'[INFO] Очки {self.point} нету ')
            self.status = 'dead'
            return
        else:
            self.dead_count = 0
            self.koef_pari = [float(bet['coef']) for bet in val_pari[key]['more'] if bet['points'] == self.point][0]
            self.koef_xbet = [bet['coef'] for bet in val_xbet[key]['smaller'] if bet['points'] == self.point][0]
            print(f'[INFO] Коэф-т париматч {key} {self.commands} для {self.point} : {self.koef_pari}')
            print(f'[INFO] Коэф-т 1хставка {key} {self.commands} для {self.point} : {self.koef_xbet}')
            vilki = 1 / self.koef_pari + 1 / self.koef_xbet
            print(f'[INFO] Вилка {key} {self.commands} для {self.point} : {self.koef_xbet}')
            self.value = 100 * (1 - vilki)
            print(vilki)
            print(self.value)
            self.time_life = int(time.time() - self.t0)


class ThreadUpdateSameMatches(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        while True:
            try:
                if self.window.same_events:
                    self.window.same_events = [event for event in self.window.same_events if event.status != 'dead']
                    for event in self.window.same_events:
                        event.get_odds()
            except Exception as ex:
                print(ex)
                print(traceback.format_exc())


if __name__ == "__main__":
    main()