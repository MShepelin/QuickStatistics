from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from support.TableFilterWidget import TableFilterWidget
import pandas as pd


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.DataFrame()):
        QtCore.QAbstractTableModel.__init__(self)
        self._df = df # ! not df.copy() !

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._df.columns[column]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget            = QtWidgets.QWidget()
        self.scroll            = QtWidgets.QScrollArea()
        self.vertical_box      = QtWidgets.QVBoxLayout()
        self.open_table_button = QtWidgets.QPushButton("Загрузить таблицу")
        self.model = None

        # Table view
        self.table_view        = QtWidgets.QTableView(self.widget)

        # Part specifiers
        self.specifiers_title  = QtWidgets.QLabel("Выбрать часть таблицы")
        self.add_specifier     = QtWidgets.QPushButton("Добавить фильтр")
        self.filters_list      = list()
        self.filters_zone      = QtWidgets.QVBoxLayout()
        self.use_filters       = QtWidgets.QPushButton("Использовать фильтр")

        self.initUI()

    def add_filter(self):
        test_widget = TableFilterWidget()
        test_widget.setMaximumSize(QtCore.QSize(16777215, 300))
        test_widget.set_owner(self.filters_zone)

        test_widget.combo_box.addItems(self.model._df.columns)
        test_widget.combo_box.currentIndexChanged.connect(lambda i: self.combobox_set(test_widget, i))
        self.combobox_set(test_widget, 0)

        self.filters_zone.addWidget(test_widget)
        self.filters_list.append(test_widget)

    def initUI(self):
        self.table_view.setMinimumHeight(300)

        self.open_table_button.clicked.connect(self.open_table)
        self.vertical_box.addWidget(self.open_table_button)

        self.widget.setLayout(self.vertical_box)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(512, 128, 1024, 512)
        self.setWindowTitle('Quick Statistics')
        self.show()

        self.table_view.setMaximumHeight(300)
        self.table_view.hide()

        self.specifiers_title.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.specifiers_title.setAlignment(QtCore.Qt.AlignCenter)

        self.add_specifier.clicked.connect(self.add_filter)
        self.add_specifier.hide()

        self.use_filters.clicked.connect(self.parse_filters)
        self.use_filters.hide()

        self.vertical_box.addLayout(self.filters_zone)

    def register_search_function(self):
        self.vertical_box.addWidget(self.specifiers_title)
        self.vertical_box.addWidget(self.add_specifier)

        self.specifiers_title.show()
        self.add_specifier.show()

        self.vertical_box.addWidget(self.use_filters)
        self.use_filters.show()

    def unregister_search_function(self):
        self.vertical_box.removeWidget(self.specifiers_title)

        for filter_widget in self.filters_list:
            filter_widget.custom_destroy()
        self.filters_list = []

        self.specifiers_title.hide()

        self.vertical_box.removeWidget(self.add_specifier)
        self.add_specifier.hide()

        self.vertical_box.removeWidget(self.use_filters)
        self.use_filters.hide()

    def register_table(self, dataframe):
        self.model = PandasModel(dataframe)
        self.table_view.setModel(self.model)

        self.vertical_box.addWidget(self.table_view)
        self.table_view.show()

        self.register_search_function()

    def unregister_table(self):
        self.unregister_search_function()
        self.vertical_box.removeWidget(self.table_view)
        self.table_view.hide()

    def open_table(self):
        self.unregister_table()

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Table", filter="Table files (*.xlsx)")

        if file_name:
            self.register_table(pd.read_excel(file_name))

    def combobox_set(self, target_widget, i):
        target_widget.list_view.clear()
        target_widget.list_needed_values.clear()
        for value in self.model._df[target_widget.combo_box.itemText(i)].unique():
            item = QtWidgets.QListWidgetItem()
            item.setText(str(value))
            target_widget.list_view.addItem(item)

    def parse_filters(self):
        #++++ add ability to refresh table
        for filter_widget in self.filters_list:
            column = filter_widget.combo_box.currentText()
            values_list = []
            for i in range(filter_widget.list_needed_values.count()):
                values_list.append(filter_widget.list_needed_values.item(i).text())

            self.model._df = self.model._df[self.model._df[column].isin(values_list)]

        self.table_view.model().layoutChanged.emit()
