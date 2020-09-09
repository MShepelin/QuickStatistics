from PyQt5 import QtCore, QtGui, QtWidgets
import sip

class TableFilterWidget(QtWidgets.QWidget):
    def __init__(self, steps=5, *args, **kwargs):
        super(TableFilterWidget, self).__init__(*args, **kwargs)

        self.owner = None

        font = QtGui.QFont()
        font.setPointSize(16)

        layout = QtWidgets.QHBoxLayout()

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setContentsMargins(-1, 4, -1, -1)
        self.vertical_layout.setSpacing(10)

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.vertical_layout.setContentsMargins(0, 4, 0, 0)
        self.vertical_layout.setSpacing(10)

        self.label_column = QtWidgets.QLabel(self)
        self.label_column.setText("Колонка")
        self.label_column.setFont(font)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.label_column.sizePolicy().hasHeightForWidth())
        self.label_column.setSizePolicy(size_policy)

        self.combo_box = QtWidgets.QComboBox(self)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.combo_box.sizePolicy().hasHeightForWidth())
        self.combo_box.setSizePolicy(size_policy)
        self.combo_box.setMinimumSize(QtCore.QSize(120, 50))

        spacer_item = QtWidgets.QSpacerItem(20, 120, QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.MinimumExpanding)

        self.vertical_layout.addWidget(self.label_column)
        self.vertical_layout.addWidget(self.combo_box)
        self.vertical_layout.addItem(spacer_item)
        layout.addLayout(self.vertical_layout)

        self.vertical_layout_2 = QtWidgets.QVBoxLayout()
        self.vertical_layout_2.setContentsMargins(0, 10, 0, 0)
        self.vertical_layout_2.setSpacing(10)

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setText("Значения, которые должны присутствовать:")
        self.vertical_layout_2.addWidget(self.label_2)
        self.list_needed_values = QtWidgets.QListWidget(self)
        self.list_needed_values.setMinimumSize(QtCore.QSize(0, 20))
        self.vertical_layout_2.addWidget(self.list_needed_values)
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setText("Доступные значения")
        self.vertical_layout_2.addWidget(self.label_4)
        self.list_view = QtWidgets.QListWidget(self)
        self.list_view.setMinimumSize(QtCore.QSize(0, 20))
        self.list_view.setObjectName("listView")
        self.vertical_layout_2.addWidget(self.list_view)

        layout.addLayout(self.vertical_layout_2)

        self.delete_button = QtWidgets.QPushButton("Удалить")
        self.delete_button.clicked.connect(self.custom_destroy)

        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.list_view.itemDoubleClicked.connect(self.move_to_needed_values)
        self.list_needed_values.itemDoubleClicked.connect(self.move_to_list_view)

    def set_owner(self, new_owner):
        self.owner = new_owner

    def custom_destroy(self):
        if self.owner is None:
            raise Exception("Owner and list of other TableFilterWidget must be set before destroying")
        self.owner.removeWidget(self)
        sip.delete(self)

    def move_to_needed_values(self, item):
        self.list_needed_values.addItem(item.clone())
        self.list_view.takeItem(self.list_view.currentIndex().row())

    def move_to_list_view(self, item):
        self.list_view.addItem(item.clone())
        self.list_needed_values.takeItem(self.list_needed_values.currentIndex().row())
