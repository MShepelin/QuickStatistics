import sys
import matplotlib.pyplot as plt
import matplotlib as mlib
from support import Constants as Const
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

mlib.use('Qt5Agg')


class HistWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, height=Const.default_graph_height):
        super(HistWidget, self).__init__(parent)

        # Visualisation properties
        self.height = height

        # Draw empty canvas
        self.data = None
        self.ax = None
        self.canvas = FigureCanvasQTAgg(mlib.figure.Figure(figsize=(4, height)))
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas.draw()

        self.vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vlayout)

        title_label = QtWidgets.QLabel("Графики сравнения по колонке")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        self.column_setup = QtWidgets.QHBoxLayout()
        self.combo_box = QtWidgets.QComboBox(self)

        self.button = QtWidgets.QPushButton("Выбрать колонку сравнения")
        self.button.clicked.connect(self.update_data)
        self.column_setup.addWidget(self.button)
        self.column_setup.addWidget(self.combo_box)

        self.vlayout.addWidget(title_label)
        self.vlayout.addLayout(self.column_setup)
        self.vlayout.addWidget(self.canvas)

    def set_data(self, data):
        # data can be changed outside and affect this object
        # so when update_data is called user gets view of data in it's current state
        self.data = data

        self.combo_box.clear()
        self.combo_box.addItems(self.data.columns)

    def update_data(self):
        if self.ax is not None:
            self.canvas.figure.delaxes(self.ax)

        self.ax = self.canvas.figure.add_axes(Const.default_graph_positioning, projection=None)

        bins = self.data[str(self.combo_box.currentText())].nunique()
        self.ax.hist(self.data[str(self.combo_box.currentText())].astype('str'), bins=bins, edgecolor='black',
                     linewidth=1.2)

        self.canvas.draw()
        self.canvas.resize_event()


class SumWidget(HistWidget):
    def __init__(self, parent=None, height=Const.default_graph_height):
        super(SumWidget, self).__init__(parent, height)

        self.num_box = QtWidgets.QComboBox(self)

        num_label = QtWidgets.QLabel("Суммировать по:")

        self.column_setup.addWidget(num_label)
        self.column_setup.addWidget(self.num_box)

        self.button.disconnect()
        self.button.clicked.connect(self.update_num_data)

    def set_data(self, data):
        super(SumWidget, self).set_data(data)

        self.num_box.clear()
        self.num_box.addItems(self.data.columns)

    def update_num_data(self):
        if (self.data[str(self.num_box.currentText())].dtype not in [
            'float32', 'float64', 'int32', 'int64'] or
                self.num_box.currentText() == self.combo_box.currentText()):
            # Print error message
            print("ERROR")
            return

        data_num = self.data.groupby(
            str(self.combo_box.currentText()))[[str(self.num_box.currentText())]].sum().reset_index()

        if self.ax is not None:
            self.canvas.figure.delaxes(self.ax)

        self.ax = self.canvas.figure.add_axes(Const.default_graph_positioning, projection=None)

        self.ax.plot(data_num[str(self.combo_box.currentText())],
                     data_num[str(self.num_box.currentText())])

        self.ax.set_xlabel(str(self.combo_box.currentText()), fontsize=Const.default_fontsize)
        self.ax.set_ylabel(str(self.num_box.currentText()), fontsize=Const.default_fontsize)
        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(Const.details_fontsize)
        for tick in self.ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(Const.details_fontsize)

        self.canvas.draw()
        self.canvas.resize_event()
