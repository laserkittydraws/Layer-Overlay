from PyQt5.QtWidgets import QMessageBox

from .KritaApi import *
from krita import *

from .LayerOverlayWidget import *

EXTENSION_VERSION = '0.2.0'

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
        axn = window.createAction('toggleLayerOverlay', 'Toggle Layer Overlay', 'Tools/Scripts')
        axn.triggered.connect(self.showLayerOverlay)
        
    def updateActiveWindow(self) -> None:
        if not self.activeWindowUpdated:
            self.activeWindow: Window = self.kritaInst.activeWindow()
            self.activeWindow.activeViewChanged.connect(self.updateView)
            
            # navigating layers
            self.kritaInst.action('activateNextLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activateNextSiblingLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activatePreviousLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('activatePreviousSiblingLayer').triggered.connect(self.updateLayerOverlayLayers)
            
            # misc
            self.kritaInst.action('merge_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('duplicatelayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('flatten_image').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('remove_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('RenameCurrentLayer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('paste_layer_from_clipboard').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('new_from_visible').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('move_layer_down').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('move_layer_up').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('cut_layer_clipboard').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('copy_selection_to_new_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('cut_selection_to_new_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('split_alpha_into_mask').triggered.connect(self.updateLayerOverlayLayers)
            
            # convert layer to...
            self.kritaInst.action('convert_to_filter_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('convert_to_paint_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('convert_to_selection_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('convert_to_transparency_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('convert_to_file_layer').triggered.connect(self.updateLayerOverlayLayers)
            
            # import layer as...
            self.kritaInst.action('import_layer_as_filter_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('import_layer_as_paint_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('import_layer_as_selection_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('import_layer_as_transparency_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('import_layer_from_file').triggered.connect(self.updateLayerOverlayLayers)
            
            # create new layer actions
            self.kritaInst.action('add_new_clone_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_colorize_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_file_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_fill_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_adjustment_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_filter_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_group_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_selection_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_paint_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_transform_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_transparency_mask').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('add_new_shape_layer').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('new_from_visible').triggered.connect(self.updateLayerOverlayLayers)
            
            # grouping of layers
            self.kritaInst.action('create_quick_group').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('quick_ungroup').triggered.connect(self.updateLayerOverlayLayers)
            self.kritaInst.action('create_quick_clipping_group').triggered.connect(self.updateLayerOverlayLayers)
            
            
            # canvas only mode switching
            self.kritaInst.action('view_show_canvas_only').triggered.connect(self.updateLayerOverlayPosition)
    
    # MARK: UI FUNCTIONS
    
    def updateViews(self) -> None:
        self.views = Krita.instance().activeWindow().views()
        if not self.views and self.layerOverlayIsVisible:
            self.layerOverlay.destroy()
        
    def updateView(self) -> None:
        self.view = Krita.instance().activeWindow().activeView()
        if self.layerOverlay:
            self.layerOverlay.updateLayers()
    
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
        if self.layerOverlay is not None:
            self.layerOverlay.updatePosition()
        
    def showLayerOverlay(self) -> None:
        if self.views:
            if self.layerOverlay is None:
                self.layerOverlay = LayerOverlayWidget(Krita.instance().activeWindow().qwindow())
                self.layerOverlay.launch()
                self.layerOverlayIsVisible = True
            elif self.layerOverlayIsVisible:
                self.layerOverlay.closeWidget()
                self.layerOverlayIsVisible = False
            else:
                self.layerOverlay.launch()
                self.layerOverlayIsVisible = True

Krita.instance().addExtension(LayerOverlayExtension(Krita.instance()))