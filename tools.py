from . import plugin_dir
from qgis.gui import QgsMapToolIdentify
from PyQt5.QtGui import QCursor, QPixmap
from .utils.qgsutils import qgsutils
from .constants import IMAGE_SMALL_CURSOR


class SelectTool(QgsMapToolIdentify):
    """Obsługa wybrania zdjęcia z mapy projektu (wybór punktu)"""

    def __init__(self, iface, parent=None, queryLayer=None):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.queryLayer = queryLayer
        self.parent = parent

        small_image = plugin_dir + IMAGE_SMALL_CURSOR

        self.cursor = QCursor(
            QPixmap(small_image)
        )

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, event):
        found_features = self.identify(
            event.x(), event.y(), [self.queryLayer], self.TopDownAll
        )
        if len(found_features) > 0:

            feature = found_features[0].mFeature
            # Zoom To Feature
            qgsutils.zoomToFeature(self.canvas, self.queryLayer, feature.id())
            self.parent.createNewViewer(featuresId=feature.id(), layer=self.queryLayer)
