from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from support.TableFilterWidget import TableFilterWidget
from support.BarplotsWidget import BarplotsWidget
import pandas as pd
import sip


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.DataFrame()):
        QtCore.QAbstractTableModel.__init__(self)
        self.model_dataframe = df # ! not df.copy() !

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.model_dataframe.columns[column]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return str(self.model_dataframe.iloc[index.row(), index.column()])
        return None

    def rowCount(self, parent=None):
        return self.model_dataframe.shape[0]

    def columnCount(self, parent=None):
        return self.model_dataframe.shape[1]


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Main sections
        self.widget            = QtWidgets.QWidget()
        self.scroll            = QtWidgets.QScrollArea()
        self.vertical_box      = QtWidgets.QVBoxLayout()
        self.table_and_filters = QtWidgets.QHBoxLayout()
        self.open_table_button = QtWidgets.QPushButton("Загрузить таблицу")
        self.chosen_table      = None
        self.model             = None

        # Table view
        self.table_layout      = QtWidgets.QVBoxLayout()
        self.table_view        = QtWidgets.QTableView(self.widget)
        self.add_filter        = QtWidgets.QPushButton("Добавить фильтр")
        self.use_filters       = QtWidgets.QPushButton("Использовать фильтры")
        self.remove_filters    = QtWidgets.QPushButton("Отменить фильтры")

        # Filters
        self.filters_title      = QtWidgets.QLabel("Добавление фильтров")
        self.filters_list       = list()
        self.filters_widget     = QtWidgets.QWidget(self.widget)
        self.filters_scroll     = QtWidgets.QScrollArea()
        self.filters_zone       = QtWidgets.QVBoxLayout(self.filters_widget)

        # Barplots
        self.barplots_title     = QtWidgets.QLabel("Графики сравнения по колонке")
        self.barplot            = BarplotsWidget(self, width=5, height=5, dpi=100)

        self.initUI()

    def initUI(self):
        # Setup appearance
        self.table_view.setMinimumHeight(300)
        self.table_view.setMaximumHeight(300)
        self.open_table_button.clicked.connect(self.open_table)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.filters_title.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.filters_title.setAlignment(QtCore.Qt.AlignCenter)
        self.add_filter.clicked.connect(self.add_filter_function)
        self.use_filters.clicked.connect(self.parse_filters)
        self.remove_filters.clicked.connect(self.forget_filters)
        self.setGeometry(512, 128, 1024, 512)
        self.setWindowTitle('Quick Statistics')

        # Configure parents and children
        self.setCentralWidget(self.scroll)
        self.widget.setLayout(self.vertical_box)
        self.scroll.setWidget(self.widget)

        self.vertical_box.addWidget(self.open_table_button)
        self.vertical_box.addLayout(self.table_and_filters)
        self.table_and_filters.addLayout(self.table_layout)
        #++++ add other tasks

        self.filters_widget.setLayout(self.filters_zone)
        self.filters_scroll.setWidget(self.filters_widget)
        self.filters_scroll.setWidgetResizable(True)
        self.filters_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.filters_zone.addWidget(self.filters_title)

        self.barplots_title.setAlignment(QtCore.Qt.AlignCenter)
        self.barplot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # Hide unneeded widgets
        self.filters_widget.hide()
        self.table_view.hide()
        self.add_filter.hide()
        self.use_filters.hide()
        self.remove_filters.hide()
        self.barplot.hide()
        self.barplots_title.hide()

        self.show()

    def add_filter_function(self):
        test_widget = TableFilterWidget()
        test_widget.setMaximumSize(QtCore.QSize(16777215, 300))
        test_widget.set_owner(self.filters_zone)

        test_widget.combo_box.addItems(self.model.model_dataframe.columns)
        test_widget.combo_box.currentIndexChanged.connect(lambda i: self.combobox_set(test_widget, i))
        self.combobox_set(test_widget, 0)

        self.filters_zone.addWidget(test_widget)
        self.filters_list.append(test_widget)

    def register_filters(self):
        self.table_and_filters.addWidget(self.filters_scroll)

        self.table_layout.addWidget(self.add_filter)
        self.table_layout.addWidget(self.use_filters)
        self.table_layout.addWidget(self.remove_filters)

        self.filters_widget.show()
        self.add_filter.show()
        self.remove_filters.show()
        self.use_filters.show()

    def unregister_filters(self):
        self.table_and_filters.removeWidget(self.filters_widget)

        for filter_widget in self.filters_list:
            filter_widget.custom_destroy()
        self.filters_list = []

        self.table_layout.removeWidget(self.add_filter)
        self.table_layout.removeWidget(self.use_filters)
        self.table_layout.removeWidget(self.remove_filters)

        self.remove_filters.hide()
        self.add_filter.hide()
        self.use_filters.hide()
        self.filters_widget.hide()

    def register_table(self, dataframe):
        self.chosen_table = dataframe.copy()
        self.model = PandasModel(dataframe)
        self.table_view.setModel(self.model)

        self.table_layout.addWidget(self.table_view)
        self.table_view.show()

        self.register_filters()
        self.register_column_barplot()

    def unregister_table(self):
        self.unregister_column_barplot()
        self.unregister_filters()

        self.table_layout.removeWidget(self.table_view)
        self.table_view.hide()

    def open_table(self):
        self.unregister_table()

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Table", filter="Table files (*.xlsx)")
        if file_name:
            self.register_table(pd.read_excel(file_name))

    def combobox_set(self, target_widget, i):
        target_widget.list_view.clear()
        target_widget.list_needed_values.clear()
        for value in self.model.model_dataframe[target_widget.combo_box.itemText(i)].unique():
            item = QtWidgets.QListWidgetItem()
            item.setText(str(value))
            target_widget.list_view.addItem(item)

    def parse_filters(self):
        self.forget_filters()

        index = 0
        while (index < len(self.filters_list)):
            filter_widget = self.filters_list[index]
            if sip.isdeleted(filter_widget):
                self.filters_list[index], self.filters_list[len(self.filters_list) - 1] = \
                    self.filters_list[len(self.filters_list) - 1], self.filters_list[index]
                self.filters_list.pop(len(self.filters_list) - 1)
                continue

            column = filter_widget.combo_box.currentText()
            values_list = []
            for i in range(filter_widget.list_needed_values.count()):
                values_list.append(filter_widget.list_needed_values.item(i).text())

            self.model.model_dataframe = self.model.model_dataframe[
                self.model.model_dataframe[column].isin(values_list)]
            index += 1

    def set_barplot(self):
        self.barplot.axes.plot([0, 1, 2, 3], [5, 6, 2, 6])

    def forget_filters(self):
        self.model.model_dataframe = self.chosen_table
        self.table_view.model().layoutChanged.emit()

    def register_column_barplot(self):
        self.vertical_box.addWidget(self.barplots_title)
        self.vertical_box.addWidget(self.barplot)
        self.barplot.show()
        self.barplots_title.show()

    def unregister_column_barplot(self):
        self.vertical_box.removeWidget(self.barplots_title)
        self.vertical_box.removeWidget(self.barplot)
        self.barplot.hide()
        self.barplots_title.hide()
