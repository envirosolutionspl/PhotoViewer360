from . import plugin_dir
from qgis.gui import QgsMapToolIdentify
from PyQt5.QtGui import QCursor, QPixmap
from .utils.qgsutils import qgsutils
#from PIL import Image, ImageQt
#from PIL import Image


class SelectTool(QgsMapToolIdentify):
    """Obsługa wybrania zdjęcia z mapy projektu (wybór punktu)"""

    def __init__(self, iface, parent=None, queryLayer=None):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        # print("QgsMapToolIdentify: ", QgsMapToolIdentify)
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.queryLayer = queryLayer
        self.parent = parent

        # stworzenie kursora/celownika do wybierania obiektu na mapie
        ############### Nowy QGIS na nowego PIL który działa poprawnie tylko na PYQT6 stąd ominięcie edycji cursora
        #image = Image.open(plugin_dir + "/images/celownik.png")
        #size = 28, 28
        #image.thumbnail(size)
        #image_qt = ImageQt.ImageQt(image)
        small_image=plugin_dir + "/images/small_celownik.png"

        self.cursor = QCursor(
            QPixmap(small_image)
            #QPixmap.fromImage(image_qt)
        )

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, event):
        found_features = self.identify(
            event.x(), event.y(), [self.queryLayer], self.TopDownAll
        )
        # print(event.x(), event.y())
        if len(found_features) > 0:

            feature = found_features[0].mFeature
            # Zoom To Feature
            qgsutils.zoomToFeature(self.canvas, self.queryLayer, feature.id())
            self.parent.createNewViewer(featuresId=feature.id(), layer=self.queryLayer)
