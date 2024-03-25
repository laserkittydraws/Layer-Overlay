from PyQt5.QtCore import QObject

from KritaApi import *
from krita import *

EXTENSION_VERSION = '0.1.0'

class LayerOverlayExtension(Extension):

    def __init__(self, parent: QObject):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window: Window):
        pass

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(LayerOverlayExtension(Krita.instance()))