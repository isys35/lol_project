#from threading import Thread
from xbet import XBetParser
from parimatch import ParimatchParser
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
import mainwindow
import frame
import traceback
import sys
from old_parimatch import ParimatchParser
from xbet import XBetParser


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
        self.find_same_matches = ThreadParser(self)
        self.same_matches = ThreadSameMatcth(self, self.find_same_matches)


    def start_find_same_matches(self):
        self.find_same_matches.start()
        self.same_matches.start()


class ThreadParser(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.same_matches = []

    def get_events(self):
        self.window.statusBar().showMessage('получение игр parimatch.com ...')
        events_parimatch = self.window.parimatch.get_events()
        self.window.statusBar().showMessage(f'найдено {len(events_parimatch)} игр ...')
        self.window.label_5.setText(f'{len(events_parimatch)}')
        self.window.statusBar().showMessage('получение игр 1xstavka.ru ...')
        if not events_parimatch:
            self.window.statusBar().showMessage('parimatch.com 0 игр ...')
            return
        events_xbet = self.window.xbet.get_events()
        self.window.statusBar().showMessage(f'найдено {len(events_xbet)} игр ...')
        self.window.label_3.setText(f'{len(events_xbet)}')
        return {'pari':events_parimatch, 'xbet': events_xbet}

    def search_matches(self, events: dict):
        same_matches = []
        for match_p in events['pari']:
            for match_x in events['xbet']:
                if match_p['total_score1'] and match_p['total_score2']:
                    if match_p['total_score1'] == match_x['total_score1'] \
                            and match_p['total_score2'] == match_x['total_score2']:
                        same_matches.append([match_p, match_x])
        self.window.label_3.setText(f'{len(same_matches)}')
        return same_matches

    def run(self):
        while True:
            events = self.get_events()
            self.same_matches = self.search_matches(events)


class ThreadSameMatcth(QThread):
    def __init__(self, window, finded_match):
        super().__init__()
        self.window = window
        self.finded_match = finded_match

    def run(self):
        while True:
            if self.finded_match.same_matches:
                pass




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