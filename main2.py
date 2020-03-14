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
        self.window.same_events = objects_events

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
        self.vilki_o = []

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
            self.get_total_total_vilka(val_pari,val_xbet)


    def get_total_total_vilka(self,val_pari,val_xbet):
        points_pari = [bet['points'] for bet in val_pari['total_total']['more']]
        points_xbet = [bet['points'] for bet in val_xbet['total_total']['more']]
        print(points_pari)
        print(points_xbet)
        coincidences = [p1 for p1 in points_pari for p2 in points_xbet if p1 == p2]
        print(coincidences)
        if coincidences:
            koef_pari = [bet['coef'] for bet in val_pari['total_total']['more']
                         for point in coincidences if bet['points'] == point]
            koef_xbet = [bet['coef'] for bet in val_xbet['total_total']['smaller']
                         for point in coincidences if bet['points'] == point]
            vilki = [1/koef_pari[i] + 1/koef_xbet[i] for i in range(len(coincidences))]
            value = [100*(1-vilka) for vilka in vilki]
            print(koef_pari)
            print(koef_xbet)
            print(vilki)
            print(value)

class Vilka(SameGame):
    def __init__(self, samegame, vilka_type, point, koef_pari, koef_xbet ):
        super().__init__(samegame.hrefs, samegame.champs, samegame.commands, samegame.window)


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
                        event.get_odds()
            except Exception as ex:
                print(ex)
                print(traceback.format_exc())


if __name__ == "__main__":
    main()