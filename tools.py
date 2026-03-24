from . import plugin_dir
from qgis.gui import QgsMapToolIdentify

from qgis.PyQt.QtGui import QCursor, QPixmap
from .utils import QgsMapUtils
from .constants import UI_SMALL_CURSOR_PATH

class SelectTool(QgsMapToolIdentify):
    """Obsługa wybrania zdjęcia z mapy projektu (wybór punktu)"""

    def __init__(self, iface, parent=None, query_layer=None):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.query_layer = query_layer
        self.parent = parent

        small_image = plugin_dir + UI_SMALL_CURSOR_PATH

        self.cursor = QCursor(
            QPixmap(small_image)
        )

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, event):
        pp = event.pixelPoint()
        found_features = self.identify(
            pp.x(), pp.y(), [self.query_layer], self.TopDownAll
        )
        if len(found_features) > 0:

            feature = found_features[0].mFeature
            # Zoom To Feature
            QgsMapUtils.zoomToFeature(self.canvas, self.query_layer, feature.id())
            self.parent.createNewViewer(features_id=feature.id(), layer=self.query_layer)
