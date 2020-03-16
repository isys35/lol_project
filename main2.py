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
        self.active_widgets = []

    def update_vilka_wigets(self):
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
            if self.active_widgets:
                for widget in self.active_widgets:
                    if widget.vilka.status == 'dead':
                        print('удаляем мёртвый виджет')
                        self.verticalLayout_5.removeWidget(widget)
                        sip.delete(widget)
                self.active_widgets = [widget for widget in self.active_widgets if widget.vilka.status != 'dead']
                for widget in self.active_widgets:
                    widget.update_odds_labels()
                active_vilki = [widget.vilka for widget in self.active_widgets]
                for events in self.same_events:
                    for total_vilka in events.vilki['total_total']:
                        if total_vilka not in active_vilki:
                            vilkawidg = VilkaWidget(total_vilka)
                            self.verticalLayout_5.addWidget(vilkawidg)
                            self.active_widgets.append(vilkawidg)
                    for individ1_vilka in events.vilki['individ_total_1']:
                        if individ1_vilka not in active_vilki:
                            vilkawidg = VilkaWidget(individ1_vilka)
                            self.verticalLayout_5.addWidget(vilkawidg)
                            self.active_widgets.append(vilkawidg)
                    for individ2_vilka in events.vilki['individ_total_2']:
                        if individ2_vilka not in active_vilki:
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
        self.label.setText(str(self.vilka.time_life))
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
        self.window.statusBar().showMessage('получение игр...')
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
        same_matches = []
        for match_p in events['pari']:
            for match_x in events['xbet']:
                if match_p['total_score1'] and match_p['total_score2']:
                    if match_p['total_score1'] == match_x['total_score1'] \
                            and match_p['total_score2'] == match_x['total_score2']:
                        same_matches.append([match_p, match_x])
        self.window.label_2.setText(f'{len(same_matches)}')
        return same_matches

    def main(self):
        events = self.get_events()
        same_events = self.search_matches(events)
        objects_events = [SameGame(
             [match['href'] for match in events],
             [match['champ'] for match in events],
             [[match['command1'], match['command2']] for match in events],
             self.window
        ) for events in same_events]
        if not self.window.same_events:
            self.window.same_events = objects_events
        else:
            not_add_list = []
            for event in objects_events:
                for window_event in self.window.same_events:
                    if event.hrefs == window_event.hrefs:
                        not_add_list.append(event)
                        break
            for event in objects_events:
                if event not in not_add_list:
                    self.window.same_events.append(event)

    def run(self):
        while True:
            self.main()


class SameGame:
    def __init__(self, hrefs, champs, commands, window):
        super().__init__()
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
        url_p, head_p = self.window.parimatch.get_request_value(self.hrefs[0])
        url_x, head_x = self.window.xbet.get_request_value(self.hrefs[1])
        url = [url_p, url_x]
        head = [head_p, head_x]
        responces = async_request.input_reuqests(url, head)
        val_pari = self.window.parimatch.get_value(responces[0])
        val_xbet = self.window.xbet.get_value(responces[1])
        print(val_pari)
        print(val_xbet)
        if val_pari and val_xbet:
            self.count_dead = 0
            for key in self.vilki:
                self.get_value(val_pari, val_xbet, key)
        if not val_pari and not val_xbet:
            if self.count_dead == 4:
                self.status = 'dead'
            else:
                self.count_dead += 1


    def get_value(self,val_pari,val_xbet,key):
        print(key)
        points_pari = [bet['points'] for bet in val_pari[key]['more']]
        points_xbet = [bet['points'] for bet in val_xbet[key]['more']]
        print(points_pari)
        print(points_xbet)
        coincidences = [p1 for p1 in points_pari for p2 in points_xbet if p1 == p2]
        print(coincidences)
        if not coincidences:
            return
        koef_pari = [float(bet['coef']) for bet in val_pari[key]['more']
                     for point in coincidences if bet['points'] == point]
        koef_xbet = [bet['coef'] for bet in val_xbet[key]['smaller']
                     for point in coincidences if bet['points'] == point]
        print(koef_pari)
        print(koef_xbet)
        vilki = [1 / koef_pari[i] + 1 / koef_xbet[i] for i in range(len(coincidences))]
        value = [100 * (1 - vilka) for vilka in vilki]
        print(koef_pari)
        print(koef_xbet)
        print(vilki)
        print(value)
        vilki_o = [Vilka(self,
                         key,
                         coincidences[i],
                         koef_pari[i],
                         koef_xbet[i],
                         value[i]) for i in range(len(coincidences))]
        if not self.vilki[key]:
            self.vilki[key] = vilki_o
        else:
            for vilki in self.vilki[key]:
                vilki.update()
                self.window.pushButton_2.click()
        #     update_list = []
        #     for vilki in vilki_o:
        #         for vilki_wind in self.vilki[key]:
        #             if vilki.hrefs == vilki_wind.hrefs and vilki.point == vilki_wind.point:
        #                 print('такой виджет уже есть')
        #                 vilki_wind.koef_pari = vilki.koef_pari
        #                 vilki_wind.koef_xbet = vilki.koef_xbet
        #                 vilki_wind.value = vilki_wind.value
        #                 vilki_wind.time_life = time.time() - vilki_wind.t0
        #                 update_list.append(vilki)
        #     for vilki in self.vilki[key]:
        #         if vilki not in update_list:
        #             vilki.status = 'dead'
        #     self.vilki[key] = [vilki for vilki in self.vilki[key] if vilki.status != 'dead']
        #     for vilki in vilki_o:
        #         if vilki not in update_list:
        #             self.vilki[key].append(vilki)
        # print(self.vilki[key])


class Vilka(SameGame):
    def __init__(self, samegame, vilka_type, point, koef_pari, koef_xbet, value):
        super().__init__(samegame.hrefs, samegame.champs, samegame.commands, samegame.window)
        self.vilka_type = vilka_type
        self.point = point
        self.koef_pari = koef_pari
        self.koef_xbet = koef_xbet
        self.value = value
        self.dead_count = 0
        self.status = 'life'
        self.t0 = time.time()
        self.time_life = 0

    def update(self):
        url_p, head_p = self.window.parimatch.get_request_value(self.hrefs[0])
        url_x, head_x = self.window.xbet.get_request_value(self.hrefs[1])
        url = [url_p, url_x]
        head = [head_p, head_x]
        responces = async_request.input_reuqests(url, head)
        val_pari = self.window.parimatch.get_value(responces[0])
        val_xbet = self.window.xbet.get_value(responces[1])
        print(val_pari)
        print(val_xbet)
        if val_pari and val_xbet:
            self.get_value(val_pari, val_xbet, self.vilka_type)

    def get_value(self, val_pari, val_xbet, key):
        print(key)
        points_pari = [bet['points'] for bet in val_pari[key]['more']]
        points_xbet = [bet['points'] for bet in val_xbet[key]['more']]
        if self.point not in points_pari or self.point not in points_xbet:
            print(points_pari)
            print(points_xbet)
            print(f'{self.point} нету в ответе на запрос')
            print(self.dead_count)
            if self.dead_count == 4:
                self.status = 'dead'
            else:
                self.dead_count += 1
            return
        self.dead_count = 0
        self.koef_pari = [float(bet['coef']) for bet in val_pari[key]['more'] if bet['points'] == self.point][0]
        self.koef_xbet = [bet['coef'] for bet in val_xbet[key]['smaller'] if bet['points'] == self.point][0]
        vilki = 1 / self.koef_pari + 1 / self.koef_xbet
        self.value = 100 * (1 - vilki)
        print(self.koef_pari)
        print(self.koef_xbet)
        print(vilki)
        print(self.value)
        self.time_life = time.time() - self.t0


class ThreadUpdateSameMatches(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def get_odds(self):
        urls_pari = []
        heads_pari = []
        urls_xbet = []
        heads_xbet = []
        same_matches_objects = self.window.same_matches_objects
        hrefs_pari = []
        hrefs_xbet = []
        for same_match_object in same_matches_objects:
            hrefs_pari.append(same_match_object.hrefs[0])
            url_p, head_p =self.window.parimatch.get_request_value(same_match_object.hrefs[0])
            urls_pari.append(url_p)
            heads_pari.append(head_p)
            hrefs_xbet.append(same_match_object.hrefs[1])
            url_x, head_x = self.window.xbet.get_request_value(same_match_object.hrefs[1])
            urls_xbet.append(url_x)
            heads_xbet.append(head_x)
        urls_pari.extend(urls_xbet)
        hrefs_pari.extend(hrefs_xbet)
        heads_pari.extend(heads_xbet)
        async_req_urls = urls_pari
        async_req_heads = heads_pari
        print(async_req_urls)
        print(async_req_heads)
        responces = async_request.input_reuqests(async_req_urls, async_req_heads)
        i = int(len(responces)/2)
        if i == 1:
            responces_pari = [responces[0]]
            responces_xbet = [responces[1]]
        else:
            responces_pari = responces[:i]
            responces_xbet = responces[i:]
        value_pari = []
        for resp in responces_pari:
            val_pari = self.window.parimatch.get_value(resp)
            value_pari.append(val_pari)
        value_xbet = []
        for resp in responces_xbet:
            val_xbet = self.window.xbet.get_value(resp)
            value_xbet.append(val_xbet)
        value_pari.extend(value_xbet)
        print('value_pari')
        print(value_pari)
        for same_match_object in self.window.same_matches_objects:
            same_match_object.value = []
            for href in same_match_object.hrefs:
                if href in hrefs_pari:
                    print('True')
                    same_match_object.value.append(value_pari[hrefs_pari.index(href)])
            same_match_object.update_vilki()

    def run(self):
        while True:
            try:
                if self.window.same_events:
                    for event in self.window.same_events:
                        if event.status == 'dead':
                            self.window.same_events.remove(event)
                        else:
                            event.get_odds()
            except Exception as ex:
                print(ex)
                print(traceback.format_exc())


if __name__ == "__main__":
    main()