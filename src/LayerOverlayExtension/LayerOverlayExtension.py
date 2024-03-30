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
    layerOverlayIsVisible = False

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
            self.activeWindow: Window = self.kritaInst.activeWindow()
            self.activeWindow.activeViewChanged.connect(self.updateView)
            
            self.kritaInst.action('activateNextLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activateNextSiblingLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activatePreviousLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activatePreviousSiblingLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('view_show_canvas_only').triggered.connect(self.updateLayerOverlayPosition)
    
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
        
    def updateLayerOverlayLayers(self) -> None:
        if self.layerOverlayIsVisible:
            self.layerOverlay.updateLayers()
            
    def updateLayerOverlayPosition(self) -> None:
        if self.layerOverlayIsVisible:
            self.layerOverlay.updatePosition()
        
    def showLayerOverlay(self) -> None:
        if self.layerOverlay is None:
            self.layerOverlay = LayerOverlayWidget(Krita.instance().activeWindow().qwindow())
            self.layerOverlay.launch()
            self.layerOverlayIsVisible = True
        elif self.layerOverlayIsVisible:
            self.layerOverlay.close()
            self.layerOverlayIsVisible = False
        else:
            self.layerOverlay.launch()
            self.layerOverlayIsVisible = True

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(LayerOverlayExtension(Krita.instance()))