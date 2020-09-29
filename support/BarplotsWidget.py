import sys
import matplotlib.pyplot as plt
import matplotlib as mlib
import seaborn as sns
import pandas as pd
mlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class HistWidget(QtWidgets.QWidget):
    def __init__(self, data, parent=None, height=4):
        super(HistWidget, self).__init__(parent)

        self.data = data # !not data.copy()
        self.height = height

        self.canvas = FigureCanvasQTAgg(mlib.figure.Figure(figsize=(1, height)))
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas.draw()

        self.vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vlayout)

        title_label = QtWidgets.QLabel("Графики сравнения по колонке")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        self.column_setup = QtWidgets.QHBoxLayout()
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(data.columns)
        self.button = QtWidgets.QPushButton("Выбрать колонку сравнения")
        self.button.clicked.connect(self.update_data)
        self.column_setup.addWidget(self.button)
        self.column_setup.addWidget(self.combo_box)

        self.vlayout.addWidget(title_label)
        self.vlayout.addLayout(self.column_setup)
        self.vlayout.addWidget(self.canvas)

    def update_data(self):
        fig, ax = plt.subplots()
        bins = self.data[str(self.combo_box.currentText())].nunique()
        ax.hist(self.data[str(self.combo_box.currentText())].astype('str'), bins=bins, edgecolor='black', linewidth=1.2)

        self.canvas.figure = fig
        self.canvas.draw()
        # call something so that canvas resizes itself using SizePolicy


class SumWidget(HistWidget):
    def __init__(self, data, parent=None, height=4):
        super(SumWidget, self).__init__(data, parent, height)

        self.num_box = QtWidgets.QComboBox(self)
        self.num_box.addItems(data.columns)

        num_label = QtWidgets.QLabel("Суммировать по:")

        self.column_setup.addWidget(num_label)
        self.column_setup.addWidget(self.num_box)

        self.button.disconnect()
        self.button.clicked.connect(self.update_num_data)

    def update_num_data(self):
        if (self.data[str(self.num_box.currentText())].dtype not in [
            'float32', 'float64', 'int32', 'int64'] or
                self.num_box.currentText() == self.combo_box.currentText()):
            # print error message
            print("ERROR")
            return

        data_num = self.data.groupby(
            str(self.combo_box.currentText()))[[str(self.num_box.currentText())]].sum().reset_index()

        fig, ax = plt.subplots()
        bins = self.data[str(self.combo_box.currentText())].nunique()
        ax.hist(self.data[str(self.combo_box.currentText())].astype('str'), bins=bins, edgecolor='black', linewidth=1.2)

        self.canvas.figure = fig
        self.canvas.draw()
