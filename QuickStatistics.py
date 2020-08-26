from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys
from support import MainMenu, TableFilterWidget

def main():
    app = QApplication(sys.argv)
    form = MainMenu.MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()