from PyQt5.QtWidgets import QListView, QWidget
from PyQt5.QtCore import QAbstractListModel

# TODO all of it

class CustomListItem(QWidget): ...

class CustomListModel(QAbstractListModel): ...

class CustomListView(QListView):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.setModel(CustomListModel())