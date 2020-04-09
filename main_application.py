from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
import mainwindow
import sys
from xbet_grab import XBetGrab
from parimatch_grab import ParimatchGrab


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parimatch_grab = ParimatchGrab()
        self.xbet_grab = XBetGrab()
        self.update_games = UpdaterGames(self.parimatch_grab, self.xbet_grab)
        self.update_games.start()


class UpdaterGames(QThread):
    def __init__(self, parimatch, xbet):
        super().__init__()
        self.parimatch_grab = parimatch
        self.xbet_grab = xbet

    def get_games(self):
        self.parimatch_grab.get_games()
        self.xbet_grab.get_games()

    def run(self):
        while True:
            self.get_games()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()