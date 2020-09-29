import sys
import matplotlib as plt
import seaborn as sns
import pandas as pd
plt.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class BarplotsWidget(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super(BarplotsWidget, self).__init__(parent)

        self.data = data # !not data.copy()

        grid = sns.FacetGrid(data)
        grid.map(sns.histplot, data.columns[0])
        self.canvas = FigureCanvasQTAgg(grid.fig)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas.draw()

        self.vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vlayout)

        title_label = QtWidgets.QLabel("Графики сравнения по колонке")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        column_setup = QtWidgets.QHBoxLayout()
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(data.columns)
        button = QtWidgets.QPushButton("Выбрать колонку")
        button.clicked.connect(self.update_data)
        column_setup.addWidget(button)
        column_setup.addWidget(self.combo_box)

        self.vlayout.addWidget(title_label)
        self.vlayout.addLayout(column_setup)
        self.vlayout.addWidget(self.canvas)

    def update_data(self):
        grid = sns.FacetGrid(self.data)
        grid.map(sns.histplot, str(self.combo_box.currentText()))
        self.canvas.figure = grid.fig
        self.canvas.draw()
        # call something so that canvas resizes itself using SizePolicy
