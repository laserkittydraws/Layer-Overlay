from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QLabel, QStyle, QCommonStyle

from .KritaApi import *
from krita import *

from .LayerOverlayWidget import *

EXTENSION_VERSION = '0.1.0'

class LayerOverlayExtension(Extension):
    
    kritaInst: Krita = Krita.instance()
    notifier: Notifier = kritaInst.notifier()
    activeWindow: Window
    activeWindowUpdated: bool = False
    
    view: View
    views: list[View]
    
    layerOverlay: LayerOverlayWidget = None

    def __init__(self, parent: QMainWindow):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        
        # setup signals
        self.notifier.viewCreated.connect(self.updateViews)
        self.notifier.viewClosed.connect(self.updateViews)
        self.notifier.windowCreated.connect(self.updateActiveWindow)
        

    
    def createActions(self, window: Window) -> None:
        axn = window.createAction('testid', 'Test Action', 'Tools/Scripts')
        axn.triggered.connect(self.showLayerOverlay)
        
    def updateActiveWindow(self) -> None:
        if not self.activeWindowUpdated:
            self.activeWindow = self.kritaInst.activeWindow()
            self.activeWindow.activeViewChanged.connect(self.updateView)
            
            self.kritaInst.action('activateNextLayer').triggered.connect(self.updateLayerOverlay)
            self.kritaInst.action('activatePreviousLayer').triggered.connect(self.updateLayerOverlay)
    
    def updateViews(self) -> None:
        self.views = Krita.instance().activeWindow().views()
        
    def updateView(self) -> None:
        self.view = Krita.instance().activeWindow().activeView()
    
    def test(self) -> None:
        x = QMessageBox(
            QMessageBox.Icon.Question,
            'Test title',
            'Test text',
            QMessageBox.StandardButton.Ok
        )
        x.exec_()
        
    def updateLayerOverlay(self) -> None:
        if self.layerOverlay is not None:
            self.layerOverlay.updateLayers()
        
    def showLayerOverlay(self) -> None:
        if self.layerOverlay is None:
            self.layerOverlay = LayerOverlayWidget(Krita.instance().activeWindow().qwindow())
            self.layerOverlay.launch()
        else:
            self.layerOverlay.closeWidget()
            self.layerOverlay = None

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(LayerOverlayExtension(Krita.instance()))