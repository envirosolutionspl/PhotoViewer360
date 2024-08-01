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


from qgis.gui import QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, QSettings, QThread, QVariant, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QCursor, QPixmap
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressBar, QApplication, QToolBar, QWidget
from qgis.core import *
from PyQt5 import QtWidgets, QtCore
import processing

from . import plugin_dir
from .Geo360Dialog import Geo360Dialog
from PhotoViewer360.gui.first_window_geo360_dialog import FirstWindowGeo360Dialog
import PhotoViewer360.config as config
from PhotoViewer360.utils.log import log
from PhotoViewer360.utils.qgsutils import qgsutils
from functools import partial
from collections import defaultdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import time, os
from pathlib import Path
import exifread
from .tools import SelectTool

try:
    from pydevd import *
except ImportError:
    None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class Geo360:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        self.config = None
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.project=QgsProject.instance()
        threadcount = QThread.idealThreadCount()

    
        # use all available cores and parallel rendering
        QgsApplication.setMaxThreads(threadcount)
        QSettings().setValue("/qgis/parallel_rendering", True)
        # OpenCL acceleration
        QSettings().setValue("/core/OpenClEnabled", True)
        self.orbitalViewer = None
        self.server = None
        self.actions = []
        self.make_server()

        self.dlg = FirstWindowGeo360Dialog()
        self.settings = QgsSettings()
        self.useLayer = ""
        self.is_press_button = False

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u"&PhotoViewer360")
        self.layer = None
        self.mapTool = None


        # toolbar
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, "PhotoViewer360")

        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u"PhotoViewer360")
            self.toolbar.setObjectName(u"PhotoViewer360")

        # noinspection PyMethodMayBeStatic

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("PhotoViewer360", message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None,
    ):

        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            # self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)
        
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Dodanie narzędzia PhotoViewer360"""

        log.initLogging()

        # Dodanie narzędzia PhotoViewer360
        self.action = self.add_action(
            icon_path=QIcon(plugin_dir + "/images/ikona_wtyczki.svg"),
            text=u"PhotoViewer360",
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # Dodanie narzędzia PhotoViewer360 aktywacja
        self.action_activate= self.add_action(
            icon_path=QIcon(plugin_dir + "/images/target.png"),
            text=u"PhotoViewer360 aktywacja",
            callback=self.activate,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
        )

        # will be set False in run()
        self.first_start = True

        # self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu(u"&PhotoViewer360", self.action)

        #self.action_activate.triggered.connect(self.activate)
        self.iface.addPluginToMenu(u"&PhotoViewer360", self.action_activate)

        # eventy

        # obsługa zdarzeń wciśnięć przycisków w oknie PhotoViewer360
        self.dlg.fromLayer_btn.clicked.connect(self.fromLayer_btn_clicked)
        self.dlg.fromPhotos_btn.clicked.connect(self.fromPhotos_btn_clicked)
        self.dlg.fromGPKG_btn.clicked.connect(self.fromGPKG_btn_clicked)

        # obsługa ścieżek do plików/folderów w oknie PhotoViewer360
        self.dlg.mQgsFileWidget_save_gpkg.setFilter(config.GPKG_FILTER_EXTENSTION)


        # obsługa wybrania warstwy z projektu w oknie PhotoViewer360
        self.dlg.mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.dlg.mapLayerComboBox.setShowCrs(True)

        # obsługa usunięcia warstwy w oknie PhotoViewer360
        self.project.layerRemoved.connect(self.layerRemoved)

    def unload(self):
        """Załadowanie narzędzi PhotoViewer360"""

        # zamykanie otwartych okien wtyczki i dezaktywacja celownika
        self.action_activate.setEnabled(False)
        self.iface.actionPan().trigger()

        if self.orbitalViewer != None:
            self.orbitalViewer.close()

        if self.dlg != None:
            self.dlg.close()  

        # ponowne załadowanie narzędzi
        for action in self.actions:
            self.iface.removePluginMenu(
                u"&PhotoViewer360",
                action)
            self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)
            self.close_server()

        # remove the toolbar
        del self.toolbar

    def close_server(self):
        """Close Local server"""

        # Close server
        if self.server is not None:
            self.server.shutdown()
            time.sleep(1)
            self.server.server_close()
            while self.server_thread.is_alive():
                self.server_thread.join()
            self.server = None

    def make_server(self):
        """Create Local server"""

        # Close server
        self.close_server()
        # Create Server
        directory = (
                QgsApplication.qgisSettingsDirPath().replace("\\", "/")
                + config.server_directory
        )

        try:
            self.server = ThreadingHTTPServer(
                (config.IP, config.PORT),
                partial(QuietHandler, directory=directory),
            )
            self.server_thread = Thread(
                target=self.server.serve_forever,
                name="http_server",
            )
            self.server_thread.daemon = True
            print("Serving at port: %s" % self.server.server_address[1])
            time.sleep(1)
            self.server_thread.start()
        except Exception:
            print("Server Error")

    def run(self):
        """Run after pressing the plugin"""

        # wywołanie okna "PhotoViewer360" po wciśnięciu ikony aparatu
        self.dlg.show()

    def click_feature(self):
        """Obsługa wybrania punktu na mapie"""

        lys = self.project.mapLayers().values()

        for layer in lys:
            if layer.name() == self.useLayer:
                self.layer = layer
                break

        self.mapTool = SelectTool(self.iface, parent=self, queryLayer=self.layer)
        self.iface.mapCanvas().setMapTool(self.mapTool)

    def activate(self):
        """Obsługa narzędzia PhotoViewer360 aktywacja (powrót do wybrania punktu na mapie)"""

        layer = self.dlg.mapLayerComboBox.currentText()
        layer = self.project.mapLayersByName(layer.split(" ")[0])[0]
        self.iface.messageBar().pushMessage("Informacja", "Korzystasz z warstwy: " + self.useLayer, level=Qgis.Info, duration=-1)
        self.layer = layer
        self.mapTool = SelectTool(self.iface, parent=self, queryLayer=self.layer)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.click_feature()

    def fromLayer_btn_clicked(self):
        """Obsługa przycisku "Przeglądaj" do wybrania warstwy z projektu QGIS"""

        self.is_press_button = True
        self.action_activate.setEnabled(True)
        good_layer = False
        layerName = self.dlg.mapLayerComboBox.currentText()
        self.useLayer = layerName

        try:
            self.layer = self.project.mapLayersByName(layerName.split(" ")[0])[0]

            # zdiagnozowanie czy wybrana wartwa została utworzona przez wtyczkę PhotoViewer360 (poprzez znalezienie kolumny "sciezka_zdjecie")
            for field in self.layer.fields():
                if field.name() == "sciezka_zdjecie":
                    good_layer = True

            if good_layer == True:
                self.mapTool = SelectTool(self.iface, parent=self, queryLayer=self.layer)
                self.iface.mapCanvas().setMapTool(self.mapTool)
                self.dlg.hide()
                self.click_feature()
            else:
                self.iface.messageBar().pushCritical("Ostrzeżenie:",
                                                     "Podana warstwa punktowa nie zawiera geotagowanych zdjęć")
                return False

        except IndexError:
            self.iface.messageBar().pushCritical("Ostrzeżenie:",
                                                 "Nie wskazano warstwy geopackage z geotagowanymi zdjęciami")
            return False

    def create_gpkg(self, photo_path, gpkg_path):
        """Stworzenie GeoPaczki na bazie wskazanego folderu ze zdjęciami oraz późniejsza jej modyfikacja"""

        # Processing feedback
        def progress_changed(progress):
            """Funkcja pokazująca progres podczas pracy narzędzia "Importuj geotagowane zdjęcia" """
            try:
                self.progress.setValue(5 + int(progress*34/100))
                QApplication.processEvents()
            except RuntimeError:
                pass

        try:
            self.progress.setValue(5)
        except RuntimeError:
            pass
                
        gpkg_path = os.path.join(gpkg_path)

        try:
            f = QgsProcessingFeedback()
            f.progressChanged.connect(progress_changed)

            # uruchomienie narzędzia "Importuj geotagowane zdjęcia"
            processing.run(
                "native:importphotos",
                {
                "FOLDER": photo_path,
                "RECURSIVE": False,
                "OUTPUT":gpkg_path,
                },
                feedback=f
            )

        except:
            print("Tool Import Geotagged Photos failed!")

        try:
            self.progress.setValue(40)

        except RuntimeError:
            pass

        gpkg_name = Path(gpkg_path).stem

        # stworzenie warstwy z utworzonej GeoPaczki
        vlayer = QgsVectorLayer(gpkg_path, gpkg_name, "ogr")

        if not vlayer.isValid():
            print("Layer failed to load!")
        else:
            # start edycji GeoPaczki
            vlayer.startEditing()

            # dodanie nowych kolumn do warstwy
        
            field_type=QVariant.String
            generated_fature_list=[QgsField(x,field_type) for x in config.GPKP_COLUMNS_ADD_LIST]
            vlayer.dataProvider().addAttributes(generated_fature_list)
            vlayer.updateFields()

            # modyfikacja już utworzonych kolumn (zmiana nazwy lub całkowite usunięcie atrybutu)
            for field_idx,field in enumerate(vlayer.fields()):
                GPKP_COLUMNS_CHANGE_DICT=defaultdict(str,config.GPKP_COLUMNS_CHANGE_DICT)
                if GPKP_COLUMNS_CHANGE_DICT[field.name()]:
                    new_value=GPKP_COLUMNS_CHANGE_DICT[field.name()]
                    old_value=field.name()
                    self.rename_name_field(vlayer, old_value, new_value)
                if field.name() in config.GPKP_COLUMNS_DELETE_LIST:
                    vlayer.dataProvider().deleteAttributes([field_idx])
                    vlayer.updateFields()

            features = vlayer.getFeatures()
            number_of_features = vlayer.featureCount()
            time_progress = 0

            # modyfikacja wartości atrybutów
            for feature in features:

                time_progress += 1
                try:
                    self.progress.setValue(45+int(int(50*time_progress)/number_of_features))
                    QApplication.processEvents()
                except RuntimeError:
                    pass
                
                # uzupełnienie wartości dla atrybutów: nr_drogi, nazwa_ulicy, numer_odcinka, kilometraz
                nazwa_zdjecia = feature["nazwa_zdjecia"]

                try:
                    nr_drogi = nazwa_zdjecia.split("_")[0]
                    nazwa_ulicy = nazwa_zdjecia.split("_")[1]
                    numer_odcinka = nazwa_zdjecia.split("_")[2]
                    kilometraz = nazwa_zdjecia.split("_")[3]

                except IndexError:
                    nr_drogi = nazwa_zdjecia
                    nazwa_ulicy = None
                    numer_odcinka = None
                    kilometraz = None
                                                               
                vlayer.dataProvider().changeAttributeValues(
                    {feature.id(): {vlayer.dataProvider().fieldNameMap()["nr_drogi"]: nr_drogi}})
                vlayer.dataProvider().changeAttributeValues(
                    {feature.id(): {vlayer.dataProvider().fieldNameMap()["nazwa_ulicy"]: nazwa_ulicy}})
                vlayer.dataProvider().changeAttributeValues(
                    {feature.id(): {vlayer.dataProvider().fieldNameMap()["numer_odcinka"]: numer_odcinka}})
                vlayer.dataProvider().changeAttributeValues(
                    {feature.id(): {vlayer.dataProvider().fieldNameMap()["kilometraz"]: kilometraz}})

                # uzupełnienie wartości dla atrybutu azymut, w przypadku braku danych o azymucie w metadanych zdjęcia
                azymut_value = feature["azymut"]

                if str(azymut_value) == "NULL":
                    vlayer.dataProvider().changeAttributeValues(
                        {feature.id(): {vlayer.dataProvider().fieldNameMap()["azymut"]: 310}})
                else:
                    pass    

                # uzupełnienie wartości dla atrybutu data_wykonania
                data_value = feature["data_wykonania"]

                if str(data_value) == "NULL":
                    sciezka_zdjecie_value = feature["sciezka_zdjecie"]
                    sciezka_zdjecie_value = sciezka_zdjecie_value.replace("\\", "/")
                    sciezka_zdjecie_open = open(sciezka_zdjecie_value, "rb")
                    tags = exifread.process_file(sciezka_zdjecie_open)
                    self.dataTime = tags["EXIF DateTimeOriginal"]
                    vlayer.dataProvider().changeAttributeValues(
                        {feature.id(): {
                            vlayer.dataProvider().fieldNameMap()["data_wykonania"]: str(self.dataTime)}})
                    sciezka_zdjecie_open.close()

        try:
            self.progress.setValue(95)
        except RuntimeError:
            pass

        vlayer.commitChanges()
        return vlayer

    def usuniecie_wartosci_gpkg(self, gpkg_path):
        """Usunięcie wszystkich obiektów w warstwie"""

        lys = self.project.mapLayers().values()

        for layer in lys:
            if layer.name() == gpkg_path.split("\\")[-1].split(".")[0]:
                layer.startEditing()

                for feat in layer.getFeatures():
                    layer.deleteFeature(feat.id())
                layer.commitChanges()

        try:
            self.progress.setValue(5)
        except RuntimeError:
            pass

    def polaczenie_warstw(self, gpkg_path, overwrite):
        """Połączenie dwóch Geopaczek (starego gpkg i gpkg z nowymi obiektami)"""

        lys = self.project.mapLayers().values()
        for layer in lys:
            if layer.name() == gpkg_path.split("\\")[-1].split(".")[0]:
                layer.startEditing()

                for sourcefeat in overwrite.getFeatures():
                    newfeat = QgsFeature()
                    newfeat.setGeometry(sourcefeat.geometry())
                    newfeat.setAttributes(sourcefeat.attributes())
                    idx = overwrite.fields().indexFromName("fid")

                    if idx is not None:  # check if there is an "fid" attribute
                        newfeat[idx] = None  # clear attribute

                    layer.addFeature(newfeat)
                layer.commitChanges()

        self.useLayer = str(layer.name())

    def dopisanie_plik_button_clicked(self, photo_path, gpkg_path):
        """Obsługa wyboru przycisku dopisania danych do GeoPaczki"""

        try:
            self.progress.setValue(2)
        except RuntimeError:
            pass

        vlayer_overwrite = self.create_gpkg(photo_path, os.path.join(plugin_dir, "temporary_files", "overwrite.gpkg"))
        self.polaczenie_warstw(gpkg_path, vlayer_overwrite)

    def usuwanie_duplikatow(self, gpkg_path):
        """uruchomienie narzędzia do wykrywania duplikatów w warstwie po wybranych atrybutach"""

        duplicate = processing.run(
            "native:removeduplicatesbyattribute",
            {
                "INPUT": gpkg_path,
                "FIELDS": [
                    "nazwa_zdjecia",
                    "długosc geog",
                    "szerokosc geog",
                    "data_wykonania",
                ],
                "OUTPUT": plugin_dir + "/temporary_files/no_duplicates.gpkg",
                "DUPLICATES": plugin_dir + "/temporary_files/duplicates.gpkg"
            }
        )

        if duplicate["DUPLICATE_COUNT"] > 0:    # obsługa wykrycia duplikatów w warstwie

            self.usuniecie_wartosci_gpkg(gpkg_path)

            try:
                self.progress.setValue(96)
            except RuntimeError:
                pass

            layer_no_duplicate = QgsVectorLayer(duplicate["OUTPUT"], "no_duplicate", "ogr")
            self.polaczenie_warstw(gpkg_path, layer_no_duplicate)

            try:
                self.progress.setValue(98)
            except RuntimeError:
                pass

            # przygotowanie informacji o zduplikowanych zdjęciach
            sciezka_zdjecie_list = []
            layer_duplicate = QgsVectorLayer(duplicate["DUPLICATES"], "duplicate", "ogr")

            for feat_duplic in layer_duplicate.getFeatures():
                sciezka_zdjecie_value = feat_duplic["nazwa_zdjecia"]
                sciezka_zdjecie_list.append(sciezka_zdjecie_value)

            if len(sciezka_zdjecie_list) <= 20:
                lista_zdjec = str(sciezka_zdjecie_list)
            else:
                lista_zdjec = str(sciezka_zdjecie_list[0:19]) + " ... "

            # wyświetlenie okna z informacją duplikatach
            msgbox = QMessageBox(QMessageBox.Information, "Ostrzeżenie:",
                                    f"Usunięto {duplicate['DUPLICATE_COUNT']} duplikatów.\n\n"
                                    f"Duplikaty stwierdzono na podstawie atrybutów: "
                                    f"nazwa_zdjecia, długosc geog, szerokosc geog, data_wykonania.\n\n"
                                    f"Stwierdzono duplikaty zdjęć: \n"
                                    f"{lista_zdjec}")
            msgbox.exec_()

    def fromPhotos_btn_clicked(self):
        """Obsługa przycisku "Importuj" do stworzenia GeoPaczki z geotagowanych zdjęć z wybranego folderu """

        self.is_press_button = True
        self.action_activate.setEnabled(True)

        photo_path = self.dlg.mQgsFileWidget_search_photo.filePath()
        if not self.checkSavePath(photo_path):
            return False
        
                # sprawdzenie, czy w folderze ze zdjęciami są pliki zdjęć (.jpg)
        files = os.listdir(photo_path)
        rozszerzenia = []

        for file in files:
            rozszerzenie = file.split(".")
            rozszerzenia.append(rozszerzenie[-1])
            

        if ("jpg" not in rozszerzenia):
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:", "We wskazanym folderze ze zdjęciami brak plików z rozszerzeniem .jpg").exec_()
            return False

        gpkg_path = self.dlg.mQgsFileWidget_save_gpkg.filePath()
        # sprawdzenie rozszerzenia pliku wpisanego przez użytkownika
        if gpkg_path.find(".gpkg") == -1:
            gpkg_path = gpkg_path + ".gpkg"

        # stworzenie paska postępu
        progressMessageBar = self.iface.messageBar().createMessage("Postęp importowania " + gpkg_path.split("\\")[-1] + "...")
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if not gpkg_path or gpkg_path == "": # obsługa nie wskazania ściężki zapisu GeoPaczki
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:", "Nie wskazano wskazano miejsca zapisu plików").exec_()
            return False

        elif os.path.exists(gpkg_path): # obsługa wskazania już istnięjącego pliku Geopaczki

            # stworzenie okienka wyboru przy sytuacji istnienia gpkg
            msgBox = QMessageBox(QMessageBox.Information, "Informacja",
                                 "Plik już istnieje.\n"
                                 "Czy chcesz stworzyć nowy plik (stary plik GPKG zostanie usunięty)?\n"
                                 "Czy chcesz dopisać dane do starego pliku?")

            nowy_plik_button = msgBox.addButton("Nowy plik", QtWidgets.QMessageBox.ApplyRole)
            dopisanie_plik_button = msgBox.addButton("Dopisanie do pliku", QtWidgets.QMessageBox.ApplyRole)
            anuluj_button = msgBox.addButton("Anuluj", QtWidgets.QMessageBox.ResetRole)
            msgBox.exec_()

            if msgBox.clickedButton() == nowy_plik_button:  # obsługa przycisku do stworzenia nowego pliku gpkg (dane z istniejącego pliku zostaną skasowane)
                progressMessageBar.layout().addWidget(self.progress)
                self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)

                try:
                    self.progress.setValue(0)
                except RuntimeError:
                    pass

                self.usuniecie_wartosci_gpkg(gpkg_path)
                self.dopisanie_plik_button_clicked(photo_path, gpkg_path)

            elif msgBox.clickedButton() == dopisanie_plik_button:  # obsługa przycisku do dodania nowych danych do pliku gpkg (do danych z istniejącego pliku zostaną dopisane nowe)
                progressMessageBar.layout().addWidget(self.progress)
                self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)

                try:
                    self.progress.setValue(0)
                except RuntimeError:
                    pass

                self.dopisanie_plik_button_clicked(photo_path, gpkg_path)
                self.usuwanie_duplikatow(gpkg_path)

            elif msgBox.clickedButton() == anuluj_button:   # obsługa anulowania zdarzenia
                return False
            else:
                pass

            # dodanie zmodyfikawanej warstwy gpkg do projektu
            lys = self.project.mapLayers().values()

            for layer in lys:
                if (layer.name() == Path(gpkg_path).stem):
                    self.project.removeMapLayers([layer.id()])

            layer = QgsVectorLayer(gpkg_path, Path(gpkg_path).stem, "ogr")
            self.project.addMapLayer(layer)
            self.useLayer = str(layer.name())

            try:
                self.progress.setValue(100)
            except RuntimeError:
                pass

            # ukrycie okna PhotoViewer360
            self.dlg.hide()
            self.click_feature()

        else: # obsługa wskazania ścieżki zapisu gpkg (bez komplikacji)
            progressMessageBar.layout().addWidget(self.progress)
            self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
            self.progress.setValue(0)
            vlayer = self.create_gpkg(photo_path, gpkg_path)
            self.project.addMapLayer(vlayer)
            self.useLayer = str(vlayer.name())

            try:
                self.progress.setValue(100)
            except RuntimeError:
                pass

            self.dlg.hide()
            self.click_feature()

    def fromGPKG_btn_clicked(self):
        """Obsługa przycisku "Przeglądaj" do wczytania już istniejącej GeoPaczki nie wczytanej w projekcie QGIS 
        (GeoPaczka musi być utworzona przez tą wtyczkę) """

        self.is_press_button = True
        self.action_activate.setEnabled(True)

        gpkg_path = os.path.join(self.dlg.mQgsFileWidget_search_gpkg.filePath())
        if not self.checkSavePath(gpkg_path):
            return False
        gpkg_name = Path(gpkg_path).stem

        vlayer = QgsVectorLayer(gpkg_path, gpkg_name, "ogr")
        if not vlayer.isValid():
            print("Layer failed to load!")
            return False

        self.project.addMapLayer(vlayer)

        self.useLayer = vlayer.name()
        self.dlg.hide()
        self.click_feature()

    def rename_name_field(self, rlayer, oldname, newname):
        """Funkcja zmieniająca nazwy atrybutów w warstwie"""

        findex = rlayer.dataProvider().fieldNameIndex(oldname)
        if findex != -1:
            rlayer.dataProvider().renameAttributes({findex: newname})
            rlayer.updateFields()

    def createNewViewer(self, featuresId=None, layer=None):
        """Funkcja uruchamia plik Geo360Dialog.py, który jest odpowiedzialny za obsługę okna StreetView (okna ze zdjęciami oraz nawigacją)"""

        self.featuresId = featuresId
        self.canvas.refresh()

        self.orbitalViewer = Geo360Dialog(
            self.iface,
            featuresId=featuresId,
            layer=layer,
            name_layer=self.useLayer,
            parent=self,
        )

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.orbitalViewer)

    def layerRemoved(self):
        """Obsługa usunięcia warstwy z projektu QGIS"""

        lys = self.project.mapLayers().values()
        layers_name = []

        for one_layer in lys:
            layers_name.append(one_layer.name())

        if (self.useLayer not in layers_name):
            self.action_activate.setEnabled(False)
            self.iface.actionPan().trigger()

            if self.orbitalViewer != None:
                self.orbitalViewer.close()

    def checkSavePath(self, path):
        """Funkcja sprawdza czy ścieżka jest poprawna i zwraca Boolean"""

        if not path or path == "":
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:", "Nie wskazano ścieżki do pliku/folderu").exec_()
            return False
        elif not os.path.exists(path):
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:", "Wskazano nieistniejącą ścieżkę do odczytu plików/folderu").exec_()
            return False
        else:
            return True
