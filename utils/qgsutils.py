"""
/***************************************************************************
 Geo360 viewer Plugin
 ***************************************************************************/
"""

from qgis.core import Qgis as QGis
from qgis.gui import QgsRubberBand
from qgis.utils import iface
from qgis.core import (
    QgsPointXY,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsRectangle,
)
from .log import log

try:
    from pydevd import *
except ImportError:
    None


class qgsutils(object):
    @staticmethod
    def convertProjection(x, y, from_crs, to_crs):
        """Convert Coordinates EPSG"""
        crsSrc = QgsCoordinateReferenceSystem(from_crs)
        crsDest = QgsCoordinateReferenceSystem(to_crs)
        xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        pt = xform.transform(QgsPointXY(x, y))
        return pt

    @staticmethod
    def getAttributeFromFeature(feature, columnName):
        """Get Attribute from feature"""
        return feature.attribute(columnName)

    @staticmethod
    def zoomToFeature(canvas, layer, ide):
        """Zoom to feature by Id"""
        if layer:
            for feature in layer.getFeatures():
                if feature.id() == ide:
                    # Transform Point
                    actual_point = feature.geometry().asPoint()
                    proj_point = qgsutils.convertProjection(
                        actual_point.x(),
                        actual_point.y(),
                        layer.crs().authid(),
                        canvas.mapSettings().destinationCrs().authid(),
                    )
                    x = proj_point.x()
                    y = proj_point.y()
                    # rect = QgsRectangle(x*0.99998, y*0.99998, x*1.00002, y*1.00002) # zakres zoom w przypadku przybliżenia do punktu
                    rect = QgsRectangle(x, y, x, y)
                    canvas.setExtent(rect)
                    canvas.refresh()
                    return True
        return False

    @staticmethod
    def showUserAndLogMessage(
        before, text="", level=QGis.Info, duration=3, onlyLog=False
    ):
        """Show user & log info/warning/error messages"""
        if not onlyLog:
            iface.messageBar().popWidget()
            iface.messageBar().pushMessage(before, text, level=level, duration=duration)
        if level == QGis.Info:
            log.info(text)
        elif level == QGis.Warning:
            log.warning(text)
        elif level == QGis.Critical:
            log.error(text)
        return

    @staticmethod
    def getToFeature(layer, ide):
        """Get To feature by ID"""
        if layer:
            for feature in layer.getFeatures():
                if feature.id() == ide:
                    return feature
        return False
