#from threading import Thread
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


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parimatch = ParimatchParser()
        self.xbet = XBetParser()
        self.pushButton.clicked.connect(self.start_find_same_matches)
        self.pushButton_2.clicked.connect(self.update_vilka_widgets)
        self.find_same_matches = ThreadParser(self)
        self.threadparserodds = ThreadParserOdds(self)
        self.same_matches = []
        self.same_matches_objects = []
        self.vilka_widgets = []

    def start_find_same_matches(self):
        self.find_same_matches.start()
        self.threadparserodds.start()

    def update_vilka_widgets(self):
        vilka_not_del = []
        for match in self.same_matches_objects:
            for vilka in self.vilka_widgets:
                for game in match.vilka_data:
                    if not False in [game[0] == vilka.hrefs,
                                    game[1] == vilka.champs,
                                    game[2] == vilka.commands,
                                    game[3] == vilka.point,
                                    vilka not in vilka_not_del]:
                        vilka_not_del.append(vilka)
        for vilka in self.vilka_widgets:
            if vilka not in vilka_not_del:
                self.vilka_widgets.remove(vilka)
                self.verticalLayout_5.removeWidget(vilka)
                sip.delete(vilka)
        for match in self.same_matches_objects:
            for game in match.vilka_data:
                v = VilkaWidget(
                        game[0],
                        game[1],
                        game[2],
                        game[3],
                        game[4],
                        game[5],
                        game[6]
                    )
                self.vilka_widgets.append(v)
                match.vilka_data.remove(game)
                self.verticalLayout_5.addWidget(v)

            # self.verticalLayout_5.removeWidget(v)
            # sip.delete(v)


    def update_same_matches(self):
        if not self.same_matches:
            return
        if not self.same_matches_objects:
            for same_match in self.same_matches:
                match_object = SameGame([match['href'] for match in same_match],
                                            [match['champ'] for match in same_match],
                                            [[match['command1'], match['command2']] for match in same_match],
                                            self)
                self.same_matches_objects.append(match_object)
            print(self.same_matches_objects)


class VilkaWidget(QtWidgets.QWidget, vilkawidget.Ui_Form):
    def __init__(self,hrefs, champs, commands, point, k_p, k_x, d):
        super().__init__()
        self.setupUi(self)
        self.hrefs = hrefs
        self.champs = champs
        self.commands = commands
        self.point = point
        self.k_p = k_p
        self.k_x = k_x
        self.d = d
        self.update_main_labels()
        self.update_odds_labels()

    def update_main_labels(self):
        self.label_7.setText(self.commands[0][0] + ' - ' + self.commands[0][1])
        self.label_9.setText(self.commands[1][0] + ' - ' + self.commands[1][1])
        self.label_8.setText(self.champs[0])
        self.label_10.setText(self.champs[1])

    def update_odds_labels(self):
        self.label_2.setText(str(round(self.d,2)))
        self.label_11.setText(str(self.point))
        self.label_12.setText(str(self.point))
        self.label_15.setText(str(self.k_p))
        self.label_16.setText(str(self.k_x))


class SameGame:
    def __init__(self, hrefs, champs, commands, window):
        super().__init__()
        self.hrefs = hrefs
        self.champs = champs
        self.commands = commands
        self.value = []
        self.window = window
        self.vilka_data = []

    def update_vilki(self):
        print('Обновление вилок')
        if not self.value:
            return
        if not self.value[0] or not self.value[1]:
            return
        print(self.value)
        t_points_pari = []
        t_points_xbet = []
        for bet in self.value[0]['total_total']['more']:
            t_points_pari.append(bet['points'])
        for bet in self.value[1]['total_total']['more']:
            t_points_xbet.append(bet['points'])
        t_tootal_point = []
        print(t_points_pari)
        print(t_points_xbet)
        for point in t_points_pari:
            if point in t_points_xbet:
                t_tootal_point.append(point)
        t_koef_pari = []
        t_koef_xbet = []
        t_vilki = []
        if t_tootal_point:
            print(t_tootal_point)
            for point in t_tootal_point:
                for bet in self.value[0]['total_total']['more']:
                    if bet['points'] == point:
                        t_koef_pari.append(bet['coef'])
                        break
                for bet in self.value[1]['total_total']['smaller']:
                    if bet['points'] == point:
                        t_koef_xbet.append(bet['coef'])
                        break
            for i in range(0,len(t_koef_pari)):
                vilka = 1/t_koef_pari[i] + 1/t_koef_xbet[i]
                t_vilki.append(vilka)
        print(t_koef_pari)
        print(t_koef_xbet)
        print(t_vilki)
        d = [100*(1-vilka) for vilka in t_vilki]
        print(d)
        self.vilka_data = []
        for i in range(0, len(d)):
            self.vilka_data.append([self.hrefs,
                               self.champs,
                               self.commands,
                               t_tootal_point[i],
                               t_koef_pari[i],
                               t_koef_xbet[i],
                               d[i]])
        for game in self.vilka_data:
            for vilka in self.window.vilka_widgets:
                if not False in [game[0] == vilka.hrefs,
                                 game[1] == vilka.champs,
                                 game[2] == vilka.commands,
                                 game[3] == vilka.point]:
                    vilka.k_p = game[4]
                    vilka.k_x = game[5]
                    vilka.d = game[6]
                    vilka.update_odds_labels()
                    self.vilka_data.remove(game)
        print('CLICK')
        try:
            self.window.pushButton_2.click()
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())


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
        return {'pari':events_parimatch, 'xbet':events_xbet }

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

    def run(self):
        while True:
            events = self.get_events()
            self.window.same_matches = self.search_matches(events)
            if self.window.same_matches:
                self.window.update_same_matches()


class ThreadParserOdds(QThread):
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
            if self.window.same_matches_objects:
                time.sleep(1)
                try:
                    self.get_odds()
                except Exception as ex:
                    print(ex)
                    print(traceback.format_exc())


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainApp()
        window.show()
        app.exec_()
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())

if __name__ == "__main__":
    main()