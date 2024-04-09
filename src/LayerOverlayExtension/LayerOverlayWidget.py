from PyQt5.QtCore import Qt, QPoint, QRect
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
        self.oldCanvasPosition = canvas.mapToGlobal(QPoint(0, 0))
        self.oldCanvasSize = canvas.rect()
        
        self.updatePosition()
        
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
        self.show()
        
    def _addItem(self, parent: QListWidget, node: Node, level: int) -> QListWidgetItem:
        if node:
            item = QListWidgetItem(parent)
            item.setIcon(LAYER_ICONS.get(node.type(), LAYER_ICONS.get('paintlayer')))
            itemName = '    '*level + node.name()
            stringTruncation = '...' if len(itemName) > 30 else ''
            itemName = itemName[0:30] + stringTruncation
            item.setText(itemName)
            return item
        return None
    
    def updateLayers(self) -> None:
        
        """updates the layers in the layer overlay widget
        """
        
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
        
    
    # NODE TRAVERSAL FUNCTIONS
        
    def _findBottomNode(self, node: Node) -> Node:
        
        """recursively search for the bottom node in the current tree view

        Returns:
            Node: the bottom most node in the current tree view
        """
        
        if not node.collapsed():
            if (childs := node.childNodes()):
                return self._findBottomNode(childs[0])
            else:
                return node
        else:
            return node

    def _findAboveNode(self, node: Node) -> Node:
        
        """returns the node above the specified node in the current tree view
        
        Args:
            node (Node): node above which to find the above node

        Returns:
            Node: node above specified node
        """
        
        currIndex = node.index()
        parentNode = node.parentNode()
        numChilds = len(parentNode.childNodes())
        rootNode = Krita.instance().activeDocument().rootNode()
        
        if currIndex == numChilds - 1:
            return parentNode if parentNode != rootNode else None
        else:
            return self._findBottomNode(parentNode.childNodes()[currIndex + 1])
        
    def _findBelowNodeClimb(self, node: Node) -> Node:
        
        """recursively searches for the node below the specified node given an arbitrary amount of nesting

        Args:
            node (Node): node below which to find the below node
        
        Returns:
            Node: the node below the specified node in the current tree view
        """
        
        currIndex: int = node.index()    
        parentNode: Node = node.parentNode()
        rootNode: Node = Krita.instance().activeDocument().rootNode()
        
        if node == rootNode:
            return None
        if parentNode.childNodes()[0] == node:
            return self._findBelowNodeClimb(parentNode)
        else:
            return parentNode.childNodes()[currIndex - 1]
        
    def _findBelowNode(self, node: Node) -> Node:
        
        """finds the node below the specified node in the current tree view

        Args:
            node (Node): node below which to find the below node

        Returns:
            Node: the node below the specified node in the current tree view
        """
        
        if (childs := node.childNodes()) and not node.collapsed():
            return childs[-1]
        
        return self._findBelowNodeClimb(node)
    
    def _getNodeLevel(self, node: Node) -> int:
        
        """returns how deep in the tree the node is

        Args:
            node (Node): node to find the tree depth of

        Returns:
            int: tree depth of the node
        """
        
        rootNode = Krita.instance().activeDocument().rootNode()
        level = 0
        parent: Node = node
        while (parent := parent.parentNode()) not in [rootNode, None]: level += 1
        return level
    
    
    # MOUSE FUNCTIONS
    
    def mousePressEvent(self, event: QMouseEvent):
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta: QPoint = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()