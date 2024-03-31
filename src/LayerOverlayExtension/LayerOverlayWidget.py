from PyQt5.QtCore import Qt, QPointF, QPoint, QRect
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QListWidget, QListWidgetItem
# from PyQt5.QtGui import QIcon

from .KritaApi import *
from krita import *

LAYER_ICONS = {
    'paintlayer': Krita.instance().icon('paintLayer'),
    'grouplayer': Krita.instance().icon('groupLayer'),
    'filterlayer': Krita.instance().icon('filterLayer'),
    'filtermask': Krita.instance().icon('filterLayer'),
    'filllayer': Krita.instance().icon('fillLayer'),
    'filelayer': Krita.instance().icon('fileLayer'),
    'clonelayer': Krita.instance().icon('cloneLayer'),
    'vectorlayer': Krita.instance().icon('vectorLayer')
}

startPosScale: float = 0.02

class LayerOverlayWidget(QWidget):
    
    layerList: QListWidget
    canvasOnlyMode: bool
    oldCanvasPosition: QPoint
    oldCanvasSize: QRect
    
    def __init__(self, parent: QWidget | None = ...) -> None:
        flags: Qt.WindowFlags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        super().__init__(parent, flags)
        
        self.setFixedSize(400, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        
        self.canvasOnlyMode = False
        
        canvas: QWidget = Krita.instance().activeWindow().qwindow().findChild(QWidget,'view_0')
        canvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        self.oldCanvasPosition = canvasPosition
        self.oldCanvasSize = canvas.rect()
        startPos = min(
            int(startPosScale * canvas.width()),
            int(startPosScale * canvas.height())
        )
        
        self.move(startPos + canvasPosition.x(), startPos + canvasPosition.y())
        self.oldPos = self.pos()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10,0,10,10)
        self.setLayout(layout)
        
        gBox = QGroupBox(self)
        gBox.setTitle('Layers')
        gBoxLayout = QVBoxLayout()
        gBox.setLayout(gBoxLayout)
        
        self.layerList = QListWidget()
        self.updateLayers()
        
        gBoxLayout.addWidget(self.layerList)
        layout.addWidget(gBox)
        
    def closeWidget(self) -> None:
        self.close()
        
    def launch(self) -> None:
        self.updateLayers()
        canvas: QWidget = Krita.instance().activeWindow().qwindow().findChild(QWidget,'view_0')
        canvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        startPos = min(
            int(startPosScale * canvas.width()),
            int(startPosScale * canvas.height())
        )
        
        if not self.canvasOnlyMode:
            self.move(startPos + canvasPosition.x(), startPos + canvasPosition.y())
        else:
            self.move(startPos + canvasPosition.x(), startPos + int(canvasPosition.y() / 2))
        self.show()
        
    def _addItem(self, parent: QListWidget, node: Node, level: int) -> QListWidgetItem:
        if node:
            item = QListWidgetItem(parent)
            item.setIcon(LAYER_ICONS.get(node.type(), LAYER_ICONS.get('paintlayer')))
            itemName = '    '*level + node.name()
            dotAppend = '...' if len(itemName) > 30 else ''
            itemName = itemName[0:30] + dotAppend
            item.setText(itemName)
            return item
        return None
    
    def updateLayers(self) -> None:
        
        self.layerList.clear()
        
        activeNode: Node = Krita.instance().activeDocument().activeNode()
        activeNodeLevel = 999 if activeNode is None else self._getNodeLevel(activeNode)
        aboveNode: Node = self._findAboveNode(activeNode)
        aboveNodeLevel = 999 if aboveNode is None else self._getNodeLevel(aboveNode)
        belowNode: Node = self._findBelowNode(activeNode)
        belowNodeLevel = 999 if belowNode is None else self._getNodeLevel(belowNode)
        aboveAboveNode: Node
        aboveAboveNodeLevel: int
        if belowNode is None and aboveNode is not None:
            aboveAboveNode = self._findAboveNode(aboveNode)
            aboveAboveNodeLevel = 999 if aboveNode is None else self._getNodeLevel(aboveAboveNode)
        belowBelowNode: Node
        belowBelowNodeLevel: int
        if aboveNode is None and belowNode is not None:
            belowBelowNode= self._findBelowNode(belowNode)
            belowBelowNodeLevel = 999 if belowNode is None else self._getNodeLevel(belowBelowNode)
        
        nodeLevelMin = min([activeNodeLevel, aboveNodeLevel, belowNodeLevel])
        activeNodeLevel -= nodeLevelMin
        aboveNodeLevel -= nodeLevelMin
        belowNodeLevel -= nodeLevelMin
        
        if belowNode is None and aboveNode is not None:
            self._addItem(self.layerList, aboveAboveNode, aboveAboveNodeLevel)
        aboveNodeItem = self._addItem(self.layerList, aboveNode, aboveNodeLevel)
        activeNodeItem = self._addItem(self.layerList, activeNode, activeNodeLevel)
        belowNodeItem = self._addItem(self.layerList, belowNode, belowNodeLevel)
        if aboveNode is None and belowNode is not None:
            self._addItem(self.layerList, belowBelowNode, belowBelowNodeLevel)
        
        self.layerList.setCurrentItem(activeNodeItem)
        
    def updatePosition(self) -> None:
        canvas: QWidget = Krita.instance().activeWindow().qwindow().findChild(QWidget,'view_0')
        canvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        
        startPos = min(
            int(startPosScale * canvas.width()),
            int(startPosScale * canvas.height())
        )
        
        self.canvasOnlyMode = not self.canvasOnlyMode
        if not self.canvasOnlyMode:
            self.move(startPos + canvasPosition.x(), startPos + canvasPosition.y())
        else:
            self.move(startPos + canvasPosition.x(), startPos + int(canvasPosition.y() / 2))
        
    def _findBottomNode(self, node: Node) -> Node:
        if not node.collapsed():
            if (childs := node.childNodes()):
                return self._findBottomNode(childs[0])
            else:
                return node
        else:
            return node

    def _findAboveNode(self, node: Node) -> Node:
        currIndex = node.index()
        parentNode = node.parentNode()
        numChilds = len(parentNode.childNodes())
        rootNode = Krita.instance().activeDocument().rootNode()
        
        if currIndex == numChilds - 1:
            return parentNode if parentNode != rootNode else None
        else:
            return self._findBottomNode(parentNode.childNodes()[currIndex + 1])
        
    def _findBelowNodeClimb(self, node: Node) -> Node:
        currIndex: int = node.index()    
        parentNode: Node = node.parentNode()
        rootNode: Node = Krita.instance().activeDocument().rootNode()
        if node == rootNode:
            return None
        if parentNode.childNodes()[0] == node:
            return self._findBelowNodeClimb(parentNode)
        else:
            return parentNode.childNodes()[node.index() - 1]
        
    def _findBelowNode(self, node: Node) -> Node:
        currIndex: int = node.index()
        parentNode: Node = node.parentNode()
        rootNode = Krita.instance().activeDocument().rootNode()
        
        if (childs := node.childNodes()) and not node.collapsed():
            return childs[-1]
        
        return self._findBelowNodeClimb(node)
    
    def _getNodeLevel(self, node: Node) -> int:
        rootNode = Krita.instance().activeDocument().rootNode()
        level = 0
        parent: Node = node
        while (parent := parent.parentNode()) not in [rootNode, None]: level += 1
        return level
    
    # TODO uncomment after figure out scaling transformation between canvas only view and not
    # def mousePressEvent(self, event: QMouseEvent):
    #     self.oldPos = event.globalPos()
    
    # def mouseMoveEvent(self, event: QMouseEvent) -> None:
    #     delta: QPoint = event.globalPos() - self.oldPos
    #     self.move(self.x() + delta.x(), self.y() + delta.y())
    #     self.oldPos = event.globalPos()