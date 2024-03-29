from PyQt5.QtCore import Qt
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


class LayerOverlayWidget(QWidget):
    
    layerList: QListWidget
    
    def __init__(self, parent: QWidget | None = ...) -> None:
        flags: Qt.WindowFlags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        super().__init__(parent, flags)
        
        self.setGeometry(200,200,400,200)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10,0,10,10)
        self.setLayout(layout)
        
        gBox = QGroupBox(self)
        gBox.setTitle('Layers')
        gBoxLayout = QVBoxLayout()
        gBox.setLayout(gBoxLayout)
        
        self.layerList = QListWidget()
        activeNode: Node = Krita.instance().activeDocument().activeNode()
        activeNodeLevel = self._getNodeLevel(activeNode)
        
        aboveNode: Node = self._findAboveNode(activeNode)
        aboveNodeLevel = self._getNodeLevel(aboveNode)
        
        belowNode: Node = self._findBelowNode(activeNode)
        belowNodeLevel = self._getNodeLevel(belowNode)
        
        nodeLevelMin = min([activeNodeLevel, aboveNodeLevel, belowNodeLevel])
        activeNodeLevel -= nodeLevelMin
        aboveNodeLevel -= nodeLevelMin
        belowNodeLevel -= nodeLevelMin
        
        aboveNodeItem = self.addItem(self.layerList, aboveNode, aboveNodeLevel)
        activeNodeItem = self.addItem(self.layerList, activeNode, activeNodeLevel)
        belowNodeItem = self.addItem(self.layerList, belowNode, belowNodeLevel)
        
        self.layerList.setCurrentItem(activeNodeItem)
        gBoxLayout.addWidget(self.layerList)
        layout.addWidget(gBox)
        
    def closeWidget(self) -> None:
        self.close()
        
    def launch(self) -> None:
        self.show()
        
    def addItem(self, parent: QListWidget, node: Node, level: int) -> QListWidgetItem:
        item = QListWidgetItem(parent)
        item.setIcon(LAYER_ICONS.get(node.type()))
        item.setText('   '*level + node.name())
        return item
    
    def updateLayers(self) -> None:
        
        self.layerList.clear()
        
        activeNode: Node = Krita.instance().activeDocument().activeNode()
        activeNodeLevel = self._getNodeLevel(activeNode)
        aboveNode: Node = self._findAboveNode(activeNode)
        aboveNodeLevel = self._getNodeLevel(aboveNode)
        belowNode: Node = self._findBelowNode(activeNode)
        belowNodeLevel = self._getNodeLevel(belowNode)
        
        nodeLevelMin = min([activeNodeLevel, aboveNodeLevel, belowNodeLevel])
        activeNodeLevel -= nodeLevelMin
        aboveNodeLevel -= nodeLevelMin
        belowNodeLevel -= nodeLevelMin
        
        aboveNodeItem = self.addItem(self.layerList, aboveNode, aboveNodeLevel)
        activeNodeItem = self.addItem(self.layerList, activeNode, activeNodeLevel)
        belowNodeItem = self.addItem(self.layerList, belowNode, belowNodeLevel)
        
        self.layerList.setCurrentItem(activeNodeItem)
        
    def __findBottomNode(self, node: Node) -> Node:
        if not node.collapsed():
            if (childs := node.childNodes()):
                return self.__findBottomNode(childs[0])
            else:
                return node
        else:
            return node

    def _findAboveNode(self, node: Node) -> Node:
        currIndex = node.index()
        parentNode = node.parentNode()
        numChilds = len(parentNode.childNodes())
        
        if currIndex == numChilds - 1:
                return parentNode
        else:
            return self.__findBottomNode(parentNode.childNodes()[currIndex + 1])
        
    def _findBelowNode(self, node: Node) -> Node:
        currIndex: int = node.index()
        parentNode: Node = node.parentNode()
        
        if (childs := node.childNodes()) and not node.collapsed():
            return childs[-1]
        
        if currIndex == 0:
            return None if node == (belowNode := self._findBelowNode(parentNode)) else belowNode
        
        return parentNode.childNodes()[currIndex - 1]
    
    def _getNodeLevel(self, node: Node) -> int:
        rootNode = Krita.instance().activeDocument().rootNode()
        level = 0
        parent: Node = node
        while (parent := parent.parentNode()) != rootNode: level += 1
        return level