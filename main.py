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
        self.same_matches = []
        self.vilka_wigets = []

    def start_find_same_matches(self):
        self.find_same_matches.start()

    def update_vilka_widgets(self):
        if not self.same_matches:
            return
        if not self.vilka_wigets:
            for same_match in self.same_matches:
                 vilka_widget = VilkaWidget([match['href'] for match in same_match],
                                            [match['champ'] for match in same_match],
                                            [[match['command1'], match['command2']] for match in same_match])
                 self.vilka_wigets.append(vilka_widget)
                 self.verticalLayout_5.addWidget(vilka_widget)
        print(self.vilka_wigets)




class VilkaWidget(QtWidgets.QWidget, vilkawidget.Ui_Form):
    def __init__(self, hrefs, champs, commands):
        super().__init__()
        self.setupUi(self)
        self.hrefs = hrefs
        self.champs = champs
        self.commands = commands
        self.value = []
        self.update_main_labels()

    def update_main_labels(self):
        self.label_7.setText(self.commands[0][0] + ' - ' + self.commands[0][1])
        self.label_9.setText(self.commands[1][0] + ' - ' + self.commands[1][1])
        self.label_8.setText(self.champs[0])
        self.label_10.setText(self.champs[1])

    def update_value(self):
        if self.value:
            pass


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


class ThreadParserOdds(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def get_odds(self):
        urls_pari = []
        heads_pari = []
        urls_xbet = []
        heads_xbet = []
        vilkawidgets = self.window.vilka_wigets
        for wigdet in vilkawidgets:
            url_p, head_p =self.window.parimatch.get_request_value(wigdet.href[0])
            urls_pari.append(url_p)
            heads_pari.append(head_p)
            url_x, head_x = self.window.xbet.get_request_value(wigdet.href[1])
            urls_xbet.append(url_x)
            heads_xbet.append(head_x)
        urls_pari.extend(urls_xbet)
        heads_pari.extend(heads_xbet)
        async_req_urls = urls_pari
        async_req_heads = heads_pari
        responces = async_request.input_reuqests(async_req_urls, async_req_heads)
        responces_pari = responces[:len(responces)/2]
        responces_xbet = responces[len(responces) / 2:]
        value_pari = []
        for resp in responces_pari:
            val_pari = self.window.parimatch.get_value(resp)
            value_pari.append(val_pari)
        value_xbet = []
        for resp in responces_xbet:
            val_xbet = self.window.xbet.get_value(resp)
            value_xbet.append(val_xbet)
        value_pari.extend(value_xbet)
        for wigdet in self.window.vilka_wigets:
            widget.value = []
            for href in wigdet.href:
                if href in urls_pari:
                    widget.value.append(value_pari[urls_pari.index(href)])
            widget.update_value()




    def run(self):
        while True:
            if self.window.vilka_wigets:
                self.get_odds()


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