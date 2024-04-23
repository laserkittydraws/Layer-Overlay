from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QGroupBox, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from .KritaApi import *
from krita import *

from .mlemLayerView import mlemLayerView

startPosScale: float = 0.02

class mlemWidget(QWidget):
    
    layerView: mlemLayerView
    canvasOnlyMode: bool
    oldCanvasPosition: QPoint
    oldCanvasSize: QRect
    
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        
        self.setFixedSize(400, 175)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        
        self.canvasOnlyMode = False
        canvas: QWidget = Krita.instance().activeWindow().qwindow().findChild(QWidget,'view_0')
        self.oldCanvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        self.oldCanvasSize = canvas.rect()
        
        self.updatePosition()
        
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10,10,10,10)
        
        title = QLabel('Layer Overlay')
        
        self.layerView = mlemLayerView(self)
        self.updateLayers()
        
        self.layout().addWidget(title)
        self.layout().addWidget(self.layerView)
        
    def closeWidget(self) -> None:
        self.close()
        
    def launch(self) -> None:
        self.updateLayers()
        self.show()
        
    def updateLayers(self) -> None:
        self.layerView.updateLayers()
        
    def updatePosition(self) -> None:
        
        """updates the position of the layer overlay widget
        """
        
        canvas: QWidget = Krita.instance().activeWindow().qwindow().findChild(QWidget,'view_0')
        canvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        
        relPosXScale = (self.pos().x() - self.oldCanvasPosition.x()) / self.oldCanvasSize.width()
        relPosX = relPosXScale * canvas.width()
        relPosYScale: float
        if not self.canvasOnlyMode:
            relPosYScale = (self.pos().y() - (self.oldCanvasPosition.y() / 2)) / self.oldCanvasSize.height()
        else:
            relPosYScale = (self.pos().y() - self.oldCanvasPosition.y()) / self.oldCanvasSize.height()
        relPosY = relPosYScale * canvas.height()
        
        newPos = min(
            int(startPosScale * canvas.width()),
            int(startPosScale * canvas.height())
        )
        
        newPosX = relPosX if relPosX >= newPos else newPos
        newPosY = relPosY if relPosY >= newPos else newPos
        
        self.oldPos = self.pos()
        if self.canvasOnlyMode:
            self.move(int(newPosX) + canvasPosition.x(), int(newPosY) + int(canvasPosition.y() / 2))
        else:
            self.move(int(newPosX) + canvasPosition.x(), int(newPosY) + canvasPosition.y())
        self.canvasOnlyMode = not self.canvasOnlyMode
        self.oldCanvasSize = canvas.rect()
        self.oldCanvasPosition = canvasPosition
    
    def mousePressEvent(self, event: QMouseEvent):
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta: QPoint = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()