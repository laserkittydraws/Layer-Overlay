from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QLabel, QStyle, QCommonStyle

from .KritaApi import *
from krita import *

EXTENSION_VERSION = '0.1.0'

class LayerOverlayExtension(Extension):
    
    kritaInst: Krita = Krita.instance()
    notifier: Notifier = kritaInst.notifier()
    activeWindow: Window
    activeWindowUpdated: bool = False
    
    view: View
    views: list[View]

    def __init__(self, parent: QMainWindow):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        
        
        # setup signals
        self.notifier.viewCreated.connect(self.updateViews)
        self.notifier.viewClosed.connect(self.updateViews)
        self.notifier.windowCreated.connect(self.updateActiveWindow)
        

    def createActions(self, window: Window):
        axn = window.createAction('testid', 'Test Action', 'Tools/Scripts')
        axn.triggered.connect(self.test2)
        
    def updateActiveWindow(self):
        if not self.activeWindowUpdated:
            self.activeWindow = self.kritaInst.activeWindow()
            self.activeWindow.activeViewChanged.connect(self.updateView)
    
    def updateViews(self):
        self.views = Krita.instance().activeWindow().views()
        
    def updateView(self):
        self.view = Krita.instance().activeWindow().activeView()
    
    def test(self):
        x = QMessageBox(
            QMessageBox.Icon.Question,
            'Test title',
            'Test text',
            QMessageBox.StandardButton.Ok
        )
        x.exec_()
        
    def test2(self):
        x = QWidget(Krita.instance().activeWindow().qwindow())
        x.setGeometry(200,200,400,400)
        x.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        x.setAutoFillBackground(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        x.setLayout(layout)
        
        y = QLabel('lorem ipsum')
        layout.addWidget(y)
        
        x.show()

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(LayerOverlayExtension(Krita.instance()))