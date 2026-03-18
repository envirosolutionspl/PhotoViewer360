# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhotoViewer360
                                 A QGIS plugin
 Show local equirectangular images.
                             -------------------
        begin                : 2017-02-17
        copyright            : (C) 2016 All4Gis.
        email                : franka1986@gmail.com
        edited by            : EnviroSolutions Sp z o.o.
        email                : office@envirosolutions.pl
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""

import math
import processing
import os
from os.path import basename
import time
from qgis.core import (
    QgsPointXY,
    QgsProject,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsMessageLog,
    QgsProcessingFeatureSourceDefinition,
    QgsCoordinateReferenceSystem,
    Qgis,
    QgsCoordinateTransform
)
from qgis.gui import QgsRubberBand

from qgis.PyQt.QtCore import (
    QUrl,
    Qt,
    pyqtSignal
)
from qgis.PyQt.QtWidgets import QDockWidget, QFileDialog
from qgis.PyQt.QtGui import QColor
from . import config
from .geom.transformgeom import TransformGeometry
from .gui.UiOrbitalDialog import UiOrbitalDialog
from .utils.qgsutils import qgsutils
# from qgis.PyQt.QtWebKitWidgets import QWebView, QWebPage
# from qgis.PyQt.QtWebKit import QWebSettings
from qgis.PyQt import QtCore
# from PyQt5 import QtNetwork

from .modules.viewer_widget import ViewerWidget
from .utils import MessageUtils

from math import sin, cos, sqrt, atan2, radians
import shutil

try:
    from pydevd import *
except ImportError:
    None


class Geo360Dialog(QDockWidget, UiOrbitalDialog):
    """Geo360 Dialog Class"""
    _x = 0.0
    _y = 0.0
    _id = -1
    _coordinates = []
    _index = ""
    is_window_full_screen = False

    def setXYId(self, coordinates):
        """definiuje wartości parametrów do przekazania do JS"""
        self._coordinates = coordinates

    @QtCore.pyqtSlot(str, str, str)
    def setXYtoPython(self, x, y, index):
        """definiuje wartości parametrów do przekazania do Python'a """
        self.clickHotspot([x, y, index])

    @QtCore.pyqtSlot(result=list)
    def getPhotoDetails(self):
        return [self._coordinates]

    @QtCore.pyqtSlot(result=list)
    def getHotSpotDetailsToPython(self):
        return [self._x, self._y, self._index]

    def clickHotspot(self, coordinate_hotspot):
        """Odbiór sygnału po kliknięciu w Hotspot"""
        newId = int(coordinate_hotspot[2])
        self.reloadView(newId)

    def __init__(self, iface, features_id=None, layer=None, name_layer="", parent = None):

        QDockWidget.__init__(self)

        self.setupUi(self)

        # zapisanie danych z konstruktora
        self.iface = iface
        self.features_id = features_id
        self.layer = layer
        self.use_layer = name_layer
        self.parent = parent
        
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self.canvas = self.iface.mapCanvas()

        # kierunek zdjęcia
        self.bearing = None
        self.bearing_current = None
        self.current_direction = None
        self.yaw = None
        self.old_bering = None
        self.new_bering = None

        # dane zdjecia
        self.data_wykonania = "" 
        self.nr_drogi = ""
        self.nazwa_ulicy = "NULL"
        self.numer_odcinka = ""
        self.kilometraz = ""

        # opcja FullScreen
        self.is_window_full_screen = False
        self.normal_window_state = None
        
        # elementy rysowania obserwatora na mapie (podgląd kierunku)
        self.actual_point_dx = None
        self.actual_point_sx = None
        self.actual_point_orientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry
        )
        self.position_dx = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )
        self.position_int = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )
        self.position_sx = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )

        self.selected_features = qgsutils.getToFeature(self.layer, self.features_id)

        self.gl_widget = None

        # otrzymanie ściezki do zdjęcia z warstwy  
        self.is_current_image_exists = False
        self.current_image, self.is_current_image_exists = self.getImagePathFromLayer()

        if self.is_current_image_exists is False:
            MessageUtils.pushLogInfo("Nie znaleziono pliku JPG skojarzonego ze wskazanym punktem.")

        # pobranie danych z warstwy potrzebnych do wyświetlenia dymka
        self.copyInfoAboutFile()

        # dodanie okna Street View (okna ze zdjeciem) do Layout'u ui_orbitalDialog'u
        self.updateViewer()
        
        # ustawienie RubberBand
        self.resetQgsRubberBand()
        self.setQgsRubberBandPosition()
    
    def __del__(self):
        """dekonstruktor, uruchamia się przy zamknięciu okna"""
        self.resetQgsRubberBand()

    def updateViewerDialog(self, features_id=None, layer=None, name_layer=""):
        """
        Aktualizacja okna viewera po wybraniu nowego źródła danych
        """
        self.use_layer = name_layer
        self.layer = layer
        self.features_id = features_id
        self.selected_features = qgsutils.getToFeature(self.layer, self.features_id)

        # resetowanie RubberBand
        self.resetQgsRubberBand()

        # otrzymanie ściezki do zdjęcia i zaczytanie nowych danych
        self.current_image, self.is_current_image_exists = self.getImagePathFromLayer()
        self.copyInfoAboutFile()

        # ustawienie RubberBand jeśli ma się co wyświetlać
        if self.is_current_image_exists:
            self.setQgsRubberBandPosition()

        self.updateViewer()
        

    def updateViewer(self):
        """ Funkcja odpowiadająca za załadowanie lub aktualizację okna Street View (okna ze zdjęciem) """

        # TODO Komunikat na nasze
        qgsutils.showUserAndLogMessage(u"Information: ", u"Create viewer", onlyLog=True)

        geom = self.selected_features.geometry()
        x = geom.asPoint().x()
        y = geom.asPoint().y()
        azymut = self.selected_features.attributes()[4]

        if self.gl_widget is not None: 
            # Wgranie do widgetu danych dla dymka
            self.gl_widget.setDataAboutPhoto(
                self.current_image, self.data_wykonania, self.nr_drogi, self.nazwa_ulicy, self.numer_odcinka, self.kilometraz
            ) 
            self.getPointsToHotspot()
            # Ustawienie danych geometrycznych i wymuszenie aktualizacji okna
            self.gl_widget.updateViewerWigdet(
                azymut, 0.0, x, y
            )
            
        else:
            # Utworzenie widgetu wraz ze wszystkimi danymi potrzebnymi do poprawnego wyswietlenia
            self.gl_widget = ViewerWidget(
                self, self.iface,
                azymut, 0.0, x, y,
                self.current_image, self.data_wykonania, self.nr_drogi, self.nazwa_ulicy, self.numer_odcinka, self.kilometraz
            )
            # while self.gl_widget.is_widget_loaded:
            #    time.sleep(10)
            self.getPointsToHotspot()
            self.ViewerLayout.addWidget(self.gl_widget, 1, 0)

        MessageUtils.pushLogInfo("Zaktualizowano Widget OpenGL.'")
                

    def copyInfoAboutFile(self):
        """ 
        Pobieranie danych o zdjęciu z warstwy do zmiennych klasy.
                
        """

        MessageUtils.pushLogInfo("Wczytywanie danych punktu z warstwy...")

        # Copy image in local folder
        a = self.current_image
        name_img = basename(a)
        
        # zebranie danych potrzebnych do wyświetlenia informacji o zdjęciu
        self.data_wykonania = "" 
        self.nr_drogi = ""
        self.nazwa_ulicy = "NULL"
        self.numer_odcinka = ""
        self.kilometraz = ""
        for feature in self.layer.getFeatures():
            if feature.attributes()[2] == name_img.replace(".jpg",""):
                dateTime = feature.attributes()[7]
                self.data_wykonania = str(dateTime.toString(Qt.DateFormat.ISODate)).replace("T", " ")
                self.nr_drogi = str(feature.attributes()[8])
                self.nazwa_ulicy = str(feature.attributes()[9])
                self.numer_odcinka = str(feature.attributes()[10])
                self.kilometraz = str(feature.attributes()[11])
        if self.nazwa_ulicy == "NULL":
            MessageUtils.pushLogInfo("Wczytywanie danych punktu z warstwy... Dane niekompletne.")
        else:
            MessageUtils.pushLogInfo("Wczytywanie danych punktu z warstwy... Sukces.")

    def getPointsToHotspot(self):
        """Wybranie z warstwy hotspotów na podstawie utworzonego 15 metrowego buforu"""

        self.layer.select(self.selected_features.id())

        features = self.layer.selectedFeatures()
        for feat in features:
            geom = feat.geometry()
            x_punktu = geom.asPoint().x()
            y_punktu = geom.asPoint().y()

        # przeliczenie do układu EPSG: 2180
        selected_feature_2180 = processing.run(
            "native:reprojectlayer", {
                'INPUT': QgsProcessingFeatureSourceDefinition(
                    self.layer.name(),
                    selectedFeaturesOnly=True,
                    featureLimit=-1,
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                ),
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
                'OPERATION': '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 +x_0=500000 +y_0=-5300000 +ellps=GRS80',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
        )

        # stworzenie bufora o promieniu 15m
        bufor_2180 = processing.run(
            "native:buffer", {
                'INPUT': list(selected_feature_2180.values())[0],
                'DISTANCE': 15,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
        )

        # wybranie z wartwy punktów, które znajdują się w buforze
        processing.run(
            "native:selectbylocation",
            {
                'INPUT': self.layer.name(),
                'PREDICATE': 0,
                'INTERSECT': list(bufor_2180.values())[0],
                'METHOD': 0
            }
        )

        """Pobranie współrzędnych dla zdjęcia oraz dla punktów znajdujących się w buforze (hotspotów)"""
        # współrzędne w układzie EPSG:4326

        list_of_attribute_list = []

        for feat in self.layer.selectedFeatures():
            geom = feat.geometry()
            x = geom.asPoint().x()
            y = geom.asPoint().y()

            azymut = feat.attributes()[4]
            index_feature = feat.id()
            azymut_metadane = str(azymut).replace(",",".")

            # obliczenie azymutu na podstawie, którego będziemy identyfikować czy punkt jest aktualnie wyświetlanym zdjęciem
            centr = QgsPointXY(float(x), float(y))
            pkt = QgsPointXY(float(x_punktu), float(y_punktu))
            azymut_obliczony = centr.azimuth(pkt)

            # obliczenie dystansu pomiędzy zdjeciem a punktami w buforze
            distance = self.distanceFunction(y_punktu, y, x_punktu, x)

            # ustawienie pod jakim kątem ma się wyświetlać zdjęcie w js
            # jeśli jest to pierwszy kliknięty hotspot to zdjęcie będzie miało kierunek jazdy samochodu
            if self.yaw is None:
                self.yaw_actual = 0
            else:
                self.yaw_actual = 0 + self.old_bering - self.new_bering + self.yaw * (-180/math.pi)
                # kąt self.yaw_actual jest liczony od kąta północy (sprowadzenie do układu globalnego) 

            # dodanie parametrów do listy (potem wysłanej do Java Scriptu)
            # list_of_attribute_list.append(str(x) + ' ' + str(y) + ' ' + azymut_metadane + ' ' + str(index_feature) + ' ' + str(azymut_obliczony) + ' ' + str(distance) + ' ' + str(self.yaw_actual*(math.pi/180)).replace(",","."))
            list_of_attribute_list.append({
                    'x' : x,
                    'y' : y,
                    'azymut' : azymut*(math.pi/180),
                    'fid' : index_feature,
                    'azymut_obliczony' : azymut_obliczony*(math.pi/180),
                    'distance' : distance,
                    'yaw_actual' : self.yaw_actual*(math.pi/180)
                })

            # wyzerowanie kąta o jaki mamy obrócić zdjęcie od północy
            self.yaw_actual = 0

            # usunięcie zaznaczenia selekcji
            self.layer.removeSelection() 

        # połączenie z Java Scriptem oraz przekazanie parametrów potrzebnych do wyświetlenia hotspotów
        # self.setXYId(coordinates=list_of_attribute_list)
        if self.gl_widget is not None: 
            # Wczytanie danych dla dymka
            self.gl_widget.setHotSpots(coordinates=list_of_attribute_list)

        # przypisanie do zmiennej "self.old_bering" azumtu poprzedniego punktu z hotspot'a
        self.old_bering  = self.new_bering

    def getImagePathFromLayer(self):
        """
        Funkcja pobiera ścieżkę do pliku z wybranej warstwy QGIS

        Returns:
            (str, boolean): Zwraca nazwę pliku z warstwy oraz informację, czy plik istnieje  
        """

        self.new_bering = self.selected_features.attribute(config.COLUMN_YAW)

        try:
            path = qgsutils.getAttributeFromFeature(
                self.selected_features,
                config.COLUMN_NAME,
            )
            if not os.path.isabs(path):  # Relative Path to Project
                path_project = QgsProject.instance().readPath("./")
                path = os.path.normpath(os.path.join(path_project, path))

        except Exception:
            qgsutils.showUserAndLogMessage(u"Information: ", u"Column not found.")
            return

        qgsutils.showUserAndLogMessage(u"Information: ", str(path), onlyLog=True)
        path_exists = os.path.exists(path)
        return path, path_exists
        
    def distanceFunction(self, lat1, lat2, lon1, lon2):
        """Funkcja obliczająca dystans punktami"""

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))
        R = 6373.0
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c * 1000

        return distance

    def reloadView(self, new_id):
        """
        Odświeżenie widoku zdjęcia po kliknięciu Hot Spota
        
        Parameters:
            int: FeatureID, dla którego zostanie zaktualizowany widok
        """

        self.features_id = new_id
        self.selected_features = qgsutils.getToFeature(self.layer, new_id)

        # przypisanie danych z poprzedniego hotspotu do nowych zmiennych
        self.current_direction = self.bearing_current # w celu zachowania kierunku radaru
        
        # resetowanie RubberBand
        self.resetQgsRubberBand()

        # otrzymanie ściezki do zdjęcia i zaczytanie nowych danych
        self.current_image, self.is_current_image_exists = self.getImagePathFromLayer()
        self.copyInfoAboutFile()

        # ustawienie RubberBand jeśli ma się co wyświetlać
        if self.is_current_image_exists:
            self.setQgsRubberBandPosition()

        self.updateViewer()

        # zoom do punktu po wybraniu hotspot'u
        qgsutils.zoomToFeature(self.canvas, self.layer, new_id)

    def keyPressEvent(self, event):
        """Funkcja odpowiedzialna za wykrycie użycia przycisku ESC"""
        if event.key() == Qt.Key_Escape:
            self.gl_widget.showNormal()  # po przyciśnięciu ESC, wychodzimy z trybu FullSreen
            self.setWindowState(self.normal_window_state)
            self.setFloating(False)
            self.is_window_full_screen = False

    def setFullScreen(self):
        """Funkcja odpowiedzialna za przycisk do przeglądania zdjęć w trybie pełnoekranowym"""

        if not self.isWindowFullScreen:
            self.setFloating(True)
            self.normal_window_state = self.windowState()
            self.setWindowState(Qt.WindowState.WindowFullScreen)
            self.gl_widget.showFullScreen()
            self.is_window_full_screen = True

        else:
            self.gl_widget.showNormal()
            self.setWindowState(self.normalWindowState)
            self.setFloating(False)
            self.is_window_full_screen = False

    def getScreenShot(self):
        """Funkcja odpowiedzialna za przycisk do robienia raportu graficznego"""

        image_path, extencion = QFileDialog.getSaveFileName(
            self.gl_widget,
            "Wskaż lokalizacje zrzutu ekranu",
            "",
            "PNG(*.png);;JPEG(*.jpg)",
        )

        # gdy użytkownik nie wskaże pliku -> nic nie rób
        if not image_path:
            return
        
        self.gl_widget.setScreenShotMode(True)
        pixmap = self.gl_widget.grab()
        self.gl_widget.setScreenShotMode(False)
        pixmap.save(image_path)
        os.startfile(image_path)
        #image.show()

    def updateOrientation(self, yaw=None):
        """Zaktualizowanie kierunku/orinetacji zdjęcia"""
        # funkcja wywoływana w trakcie obrotu zdjęcia

        # zdefiniowanie kierunku radaru na mapie
        if self.current_direction is not None: # warunek wywołany po użyciu hotspotu, zachowanie kierunku radaru
            self.bearing = str(self.bearing_current * -180 / math.pi)
        else: # warunek wywołany po wybraniu punktu na mapie, kierunek radaru wzięty z tabeli atrybutów
            self.bearing = self.selected_features.attribute(config.COLUMN_YAW)

        original_point = self.selected_features.geometry().asPoint()

        self.actual_point_dx = qgsutils.convertProjection(
            original_point.x(),
            original_point.y(),
            self.layer.crs().authid(),
            self.canvas.mapSettings().destinationCrs().authid(),
        ) 
      
        try:
            self.actual_point_orientation.reset()
        except Exception:
            pass

        # stworzenie radaru na mapie (pokazuje skierowanie zdjęcia)
        self.actual_point_orientation = QgsRubberBand(
            self.iface.mapCanvas(),
            QgsWkbTypes.LineGeometry,
        )

        if hasattr(Qt, "GlobalColor"):
            self.actual_point_orientation.setColor(Qt.GlobalColor.magenta)
        else:
            self.actual_point_orientation.setColor(Qt.magenta)
        self.actual_point_orientation.setWidth(3)

        # zdefiniowanie punktów radaru

        # lewy punkt
        CS = self.canvas.mapUnitsPerPixel() * 18
        A2x = self.actual_point_dx.x() - CS
        A2y = self.actual_point_dx.y() + CS
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A2x),
                float(A2y)
            )
        )

        # dolny punkt radaru
        CS = self.canvas.mapUnitsPerPixel() * 22
        A1x = self.actual_point_dx.x()
        A1y = self.actual_point_dx.y()
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A1x),
                float(A1y)
            )
        )

        # prawy punkt
        CS = self.canvas.mapUnitsPerPixel() * 18
        A3x = self.actual_point_dx.x() + CS
        A3y = self.actual_point_dx.y() + CS
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A3x),
                float(A3y)
            )
        )

        # następne punkty łuku strzałki
        CS = self.canvas.mapUnitsPerPixel() * 18
        A4x = self.actual_point_dx.x() + CS * 0.75
        A4y = self.actual_point_dx.y() + CS * 1.25
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A4x),
                float(A4y)
            )
        )

        CS = self.canvas.mapUnitsPerPixel() * 18
        A44x = self.actual_point_dx.x() + CS * 0.50
        A44y = self.actual_point_dx.y() + CS * 1.45
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A44x),
                float(A44y)
            )
        )

        CS = self.canvas.mapUnitsPerPixel() * 18
        A444x = self.actual_point_dx.x() + CS * 0.25
        A444y = self.actual_point_dx.y() + CS * 1.55
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A444x),
                float(A444y)
            )
        )

        # górny punkt łuku radaru
        CS = self.canvas.mapUnitsPerPixel() * 18
        A5x = self.actual_point_dx.x()
        A5y = self.actual_point_dx.y() + CS * 1.6
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A5x),
                float(A5y)
            )
        )

        # następne punkty łuku radaru
        CS = self.canvas.mapUnitsPerPixel() * 18
        A6x = self.actual_point_dx.x() - CS * 0.25
        A6y = self.actual_point_dx.y() + CS * 1.55
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A6x),
                float(A6y)
            )
        )

        CS = self.canvas.mapUnitsPerPixel() * 18
        A66x = self.actual_point_dx.x() - CS * 0.50
        A66y = self.actual_point_dx.y() + CS * 1.45
        self.actual_point_orientation.addPoint(
            QgsPointXY(
                float(A66x),
                float(A66y)
            )
        )

        CS = self.canvas.mapUnitsPerPixel() * 18
        A666x = self.actual_point_dx.x() - CS * 0.75
        A666y = self.actual_point_dx.y() + CS * 1.25
        self.actual_point_orientation.addPoint(QgsPointXY(float(A666x), float(A666y)))

        # punkt kończący strzałkę
        CS = self.canvas.mapUnitsPerPixel() * 18
        Ax = self.actual_point_dx.x() - CS
        Ay = self.actual_point_dx.y() + CS
        self.actual_point_orientation.addPoint(QgsPointXY(float(Ax), float(Ay)))

        # zdefiniowanie kierunku zdjęcia
        if self.current_direction is not None: # warunek spełniony po wybraniu kolejnego hotspotu
            angle = self.bearing_current
        elif yaw is not None: # warunek dla przypadku, gdy obróciliśmy zdjęcie w oknie (kąt yaw - kąt o jaki obróciliśmy zdjęcie względem kierunku jazdy samochodu)
            self.yaw = yaw * math.pi / -180 # kąt o jaki obrócono zdjęcie, potrzeby do ustawienia zdjęcia w odpowiednim kierunku w następnym hotspocie
            self.bearing_current = float(self.bearing + yaw) * math.pi / -180 # kąt potrzebny do zachowania kierunku radaru w następnym hotspocie
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180
            self.bearing_current = float(self.bearing) * math.pi / -180
        
        self.current_direction = None

        tmp_geom = self.actual_point_orientation.asGeometry()

        self.rotate_tool = TransformGeometry()
        epsg = self.canvas.mapSettings().destinationCrs().authid()

        self.dumLayer = QgsVectorLayer(
            "Point?crs=" + epsg,
            "temporary_points",
            "memory"
        )

        self.actual_point_orientation.setToGeometry(
            self.rotate_tool.rotate(
                tmp_geom,
                self.actual_point_dx,
                angle
            ),
            self.dumLayer
        )

    def setQgsRubberBandPosition(self):
        """ustawienie pozycji RubberBand (rysunku łuku)"""

        # Transform Point
        original_point = self.selected_features.geometry().asPoint()
        self.actual_point_dx = qgsutils.convertProjection(
            original_point.x(),
            original_point.y(),
            "EPSG:4326",
            self.canvas.mapSettings().destinationCrs().authid(),
        )

        self.position_dx = QgsRubberBand(
            self.iface.mapCanvas(),
            QgsWkbTypes.PointGeometry,
        )

        self.position_dx.setWidth(6)
        self.position_dx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position_dx.setIconSize(6)
        self.position_dx.setColor(QColor(0, 102, 153))

        self.position_sx = QgsRubberBand(
            self.iface.mapCanvas(),
            QgsWkbTypes.PointGeometry,
        )

        self.position_sx.setWidth(5)
        self.position_sx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position_sx.setIconSize(4)
        self.position_sx.setColor(QColor(0, 102, 153))

        self.position_int = QgsRubberBand(
            self.iface.mapCanvas(),
            QgsWkbTypes.PointGeometry,
        )

        self.position_int.setWidth(5)
        self.position_int.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position_int.setIconSize(3)
        if hasattr(Qt, "GlobalColor"):
            self.position_int.setColor(Qt.GlobalColor.white)
        else:
            self.position_int.setColor(Qt.white)

        self.position_dx.addPoint(self.actual_point_dx)
        self.position_sx.addPoint(self.actual_point_dx)
        self.position_int.addPoint(self.actual_point_dx)

    def closeEvent(self, _):
        """Zamknięcie okna ze zdjęciem (street view)"""

        self.resetQgsRubberBand()
        self.canvas.refresh()
        self.iface.actionPan().trigger()
        self.parent.orbital_viewer = None

    def resetQgsRubberBand(self):
        """Usunięcie łuku wskazującego kierunek zdjęcia"""

        try:
            self.position_sx.reset()
            self.position_int.reset()
            self.position_dx.reset()
            self.actual_point_orientation.reset()
        except Exception:
            print("exception remove rubbeband")
            None
