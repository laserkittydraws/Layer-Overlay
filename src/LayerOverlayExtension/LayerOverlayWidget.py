from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton




class LayerOverlayWidget(QWidget):
    
    def __init__(self, parent: QWidget | None = ...) -> None:
        flags: Qt.WindowFlags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        super().__init__(parent, flags)
        
        self.setGeometry(200,200,400,400)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        
        y = QLabel('lorem ipsum')
        layout.addWidget(y)
        
        z = QPushButton('Close', self)
        z.clicked.connect(self.closeWidget)
        layout.addWidget(z)
        
    def closeWidget(self) -> None:
        self.close()
        
    def launch(self) -> None:
        self.show()