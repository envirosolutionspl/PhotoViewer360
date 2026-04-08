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
import os

from qgis.PyQt.QtCore import Qt, QCoreApplication, QSettings, QThread, QTranslator, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QMessageBox,
    QProgressBar,
    QToolBar,
)
from qgis.core import *
from qgis.PyQt import QtWidgets
import processing

from .utils import MessageUtils, QtCompat, TranslationUtils

from .Geo360Dialog import Geo360Dialog
from .gui.first_window_geo360_dialog import FirstWindowGeo360Dialog

from .constants import (
    GPKG_FILTER_EXTENSION,
    TEMPORATORY_FILES_LIST,
    GPKP_COLUMNS_CHECK,
    GPKP_COLUMNS_ADD_LIST,
    GPKP_COLUMNS_DICT,
    GPKP_COLUMNS_DELETE_LIST,
    COLUMN_NAME,
    COLUMN_YAW,
    ENV_MENU_NAME,
    DEFAULT_YAW_DEGREES,
    DUPLICATES_PREVIEW_LIMIT,
    PROGRESS,
    UI_PLUGIN_ICON_PATH,
    UI_TARGET_ICON_PATH,
    QGIS_SETTINGS_KEYS,
    QGIS_FEED_MIN_VERSION_INT,
)

from collections import defaultdict
from pathlib import Path
from .tools import SelectTool
from .qgis_feed import QgisFeedDialog
import importlib.util

from . import PLUGIN_VERSION as plugin_version
from . import PLUGIN_NAME as plugin_name

from . import plugin_dir, temp_dir

class Geo360:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        self.iface = iface
        self.translator = None
        locale_full = QSettings().value("locale/userLocale", "en") or "en"
        locale = locale_full[:2] if len(locale_full) >= 2 else "en"
        locale_path = os.path.join(plugin_dir, "i18n", f"photoviewer360_{locale}.qm")
        if os.path.isfile(locale_path):
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

        self.canvas = self.iface.mapCanvas()
        self.project = QgsProject.instance()
        thread_count = QThread.idealThreadCount()
        self.settings = QgsSettings() 
        self.exifread_path = os.path.join(plugin_dir, 'libs', 'exifread_3_0_0')

        if Qgis.QGIS_VERSION_INT >= QGIS_FEED_MIN_VERSION_INT:
            from .qgis_feed import QgisFeed

            self.selected_industry = self.settings.value(
                "selected_industry", None
            )
            show_dialog = self.settings.value(
                "showDialog", True, type=bool
            )

            if self.selected_industry is None and show_dialog:
                self.showBranchSelectionDialog()

            select_indust_session = self.settings.value(
                "selected_industry"
            )

            self.feed = QgisFeed(selected_industry=select_indust_session, plugin_name=plugin_name)
            self.feed.initFeed()
    
        # use all available cores and parallel rendering
        QgsApplication.setMaxThreads(thread_count)
        QSettings().setValue(QGIS_SETTINGS_KEYS["PARALLEL_RENDERING"], True)
        # OpenCL acceleration
        QSettings().setValue(QGIS_SETTINGS_KEYS["OPENCL_ENABLED"], True)
        self.orbital_viewer = None

        self.dlg = FirstWindowGeo360Dialog()
        self.use_layer = ""
        self.is_press_button = False

        self.actions = []
        self.menu = "&" + TranslationUtils.tr(ENV_MENU_NAME)
        self.layer = None
        self.map_tool = None

        # toolbar
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, ENV_MENU_NAME)

        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(ENV_MENU_NAME)
            self.toolbar.setObjectName(ENV_MENU_NAME)

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
        return TranslationUtils.tr(message)

    def addAction(
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

    def importExifread(self):
        """Sprawdza dostępność biblioteki 'exifread'"""

        exifread_spec = importlib.util.find_spec('exifread')
        
        if os.path.exists(self.exifread_path):
            MessageUtils.pushLogInfo(TranslationUtils.tr("Found local version of the 'exifread' library."))
            MessageUtils.pushLogInfo(TranslationUtils.tr("Using local version of the 'exifread' library."))
            return True  

        elif exifread_spec is not None:
            from exifread import processFile
            MessageUtils.pushLogInfo(TranslationUtils.tr("Found 'exifread' library in QGIS"))
            return True  
        
        else:
            from .libs.exifread_3_0_0.exifread import processFile
            MessageUtils.pushLogCritical(
                TranslationUtils.tr("Local 'exifread' library not found. Please install the library.")
            )
            MessageUtils.pushCritical(
                self.iface,
                TranslationUtils.tr(
                    "'exifread' library not found - plugin may not function correctly. Please install the library.",
                ),
            )
            return False        
        

    def initGui(self):
        """Dodanie narzędzia PhotoViewer360"""

        # Dodanie narzędzia PhotoViewer360
        self.action = self.addAction(
            icon_path=QIcon(plugin_dir + UI_PLUGIN_ICON_PATH),
            text=plugin_name,

            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # Dodanie narzędzia PhotoViewer360 aktywacja
        self.action_activate= self.addAction(
            icon_path=QIcon(plugin_dir + UI_TARGET_ICON_PATH),
            text=f"{plugin_name} {TranslationUtils.tr('activation')}",
            callback=self.activate,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
        )

        # will be set False in run()
        self.first_start = True
        
        # informacje o wersji
        self.dlg.setWindowTitle('%s %s' % (plugin_name, plugin_version))
        self.dlg.label_8.setText('%s' % (plugin_version))
        self.dlg.label_9.setText(plugin_name)
        self.dlg.lbl_pluginVersion_3.setText('%s %s' % (plugin_name, plugin_version))
        ##TODO docelowo ma być wsparcie dla poniższeko komponentu i dolny pasek wtyczki
        #self.dlg.lbl_pluginVersion.setText('%s %s' % (plugin_name, plugin_version))

        # eventy

        # obsługa zdarzeń wciśnięć przycisków w oknie PhotoViewer360
        self.dlg.fromLayer_btn.clicked.connect(self.fromLayer_btn_clicked)
        self.dlg.fromPhotos_btn.clicked.connect(self.importPhotos)
        self.dlg.fromGPKG_btn.clicked.connect(self.browseGpkg)

        # obsługa ścieżek do plików/folderów w oknie PhotoViewer360
        self.dlg.mQgsFileWidget_save_gpkg.setFilter(TranslationUtils.tr(GPKG_FILTER_EXTENSION))


        # obsługa wybrania warstwy z projektu w oknie PhotoViewer360
        self.dlg.mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.dlg.mapLayerComboBox.setShowCrs(True)

        # obsługa usunięcia warstwy w oknie PhotoViewer360
        self.project.layerRemoved.connect(self.layerRemoved)

    def unload(self):
        """Załadowanie narzędzi PhotoViewer360"""

        if self.translator is not None:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None

        # zamykanie otwartych okien wtyczki i dezaktywacja celownika
        self.action_activate.setEnabled(False)
        self.iface.actionPan().trigger()

        if self.orbital_viewer is not None:
            self.orbital_viewer.close()

        if self.dlg != None:
            self.dlg.close()  

        # ponowne załadowanie narzędzi
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)

        # usuwanie katalogu plików tymczasowych
        for nazwa_pliku_tymczasowego in TEMPORATORY_FILES_LIST:
            try:
                os.remove(os.path.join(temp_dir, nazwa_pliku_tymczasowego))
            except OSError as e:
                pass

        # remove the toolbar
        del self.toolbar
        
    def run(self):
        """Run after pressing the plugin"""
        # Sprawdzenie dostępności biblioteki 'exifread'
        if not self.importExifread():
            return 
        # wywołanie okna "PhotoViewer360" po wciśnięciu ikony aparatu
        self.dlg.show()

    def showBranchSelectionDialog(self):
        self.qgisfeed_dialog = QgisFeedDialog()

        if QtCompat.dialogExec(self.qgisfeed_dialog) == QDialog.Accepted:
            self.selected_branch = self.qgisfeed_dialog.combo_box.currentText()
            
            #Zapis w QGIS3.ini
            self.settings.setValue("selected_industry", self.selected_branch)  
            self.settings.setValue("showDialog", False) 

    def clickPointOnMapFeature(self):
        """Obsługa wybrania punktu na mapie"""

        lys = self.project.mapLayers().values()

        for layer in lys:
            if layer.name() == self.use_layer:
                self.layer = layer
                break

        self.map_tool = SelectTool(self.iface, parent=self, query_layer=self.layer)
        self.iface.mapCanvas().setMapTool(self.map_tool)

    def activate(self):
        """Obsługa narzędzia PhotoViewer360 aktywacja (powrót do wybrania punktu na mapie)"""

        layer = self.dlg.mapLayerComboBox.currentText()
        layer = self.project.mapLayersByName(layer.split(" ")[0])[0]
        MessageUtils.pushMessage(
            self.iface,
            TranslationUtils.tr("Using layer: {layer}").format(layer=self.use_layer),
        )
        self.layer = layer
        self.map_tool = SelectTool(self.iface, parent=self, query_layer=self.layer)
        self.iface.mapCanvas().setMapTool(self.map_tool)
        self.clickPointOnMapFeature()

    def fromLayer_btn_clicked(self):
        """Obsługa przycisku "Przeglądaj" do wybrania warstwy z projektu QGIS"""

        self.is_press_button = True
        good_layer = False
        layer_name = self.dlg.mapLayerComboBox.currentText()
        self.use_layer = layer_name

        try:
            self.layer = self.project.mapLayersByName(layer_name.split(" ")[0])[0]

            # zdiagnozowanie czy wybrana wartwa została utworzona przez wtyczkę PhotoViewer360 (poprzez znalezienie kolumny "sciezka_zdjecie")
            for field in self.layer.fields():
                if field.name() == COLUMN_NAME:
                    good_layer = True

            if good_layer:
                self.map_tool = SelectTool(self.iface, parent=self, query_layer=self.layer)
                self.iface.mapCanvas().setMapTool(self.map_tool)
                self.dlg.hide()
                self.clickPointOnMapFeature()
            else:
                MessageUtils.pushMessageBoxWarning(
                    self.dlg,
                    TranslationUtils.tr("Warning"),
                    TranslationUtils.tr("The selected point layer does not contain geotagged photos"),
                )
                return False

        except IndexError:
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr("No GeoPackage layer with geotagged photos selected"),
            )
            return False
        
        self.action_activate.setEnabled(True)

    def createGpkg(self, photo_path, gpkg_path):
        """Stworzenie GeoPaczki na bazie wskazanego folderu ze zdjęciami oraz późniejsza jej modyfikacja"""

        # Processing feedback
        def progressChanged(progress):
            """Funkcja pokazująca progres podczas pracy narzędzia "Importuj geotagowane zdjęcia" """
            try:
                self.progress.setValue(PROGRESS["IMPORT_START"] + int(progress * (PROGRESS["IMPORT_AFTER_TOOL"] - PROGRESS["IMPORT_START"]) / 100))
                QApplication.processEvents()
            except RuntimeError:
                MessageUtils.pushLogWarning(
                    TranslationUtils.tr("Failed to update dialog window.")
                )

        try:
            self.progress.setValue(PROGRESS["IMPORT_START"])
        except RuntimeError:
            MessageUtils.pushLogWarning(
                TranslationUtils.tr("Failed to update dialog window.")
            )
                
        gpkg_path = os.path.join(gpkg_path)

        try:
            f = QgsProcessingFeedback()
            f.progressChanged.connect(progressChanged)

            # uruchomienie narzędzia "Importuj geotagowane zdjęcia"
            processing.run(
                "native:importphotos",
                {
                "FOLDER": photo_path,
                "RECURSIVE": False,
                "OUTPUT": gpkg_path,
                },
                feedback=f
            )

        except Exception as exc:
            MessageUtils.pushLogCritical(
                TranslationUtils.tr(
                    "Failed to import photos using the 'native:importphotos' tool. Error: {err}"
                ).format(err=exc)
            )

        try:
            self.progress.setValue(PROGRESS["IMPORT_AFTER_TOOL"])
        except RuntimeError:
            MessageUtils.pushLogWarning(
                TranslationUtils.tr("Failed to update dialog window.")
            )

        gpkg_name = Path(gpkg_path).stem

        # stworzenie warstwy z utworzonej GeoPaczki
        vlayer = QgsVectorLayer(gpkg_path, gpkg_name, "ogr")

        if not vlayer.isValid():
            MessageUtils.pushLogCritical(
                TranslationUtils.tr("Failed to load layer after loading the GeoPackage.")
            )
        else:
            # start edycji GeoPaczki
            vlayer.startEditing()

            # dodanie nowych kolumn do warstwy
        
            # field_type = QMetaType.Type.QString
            field_type = QVariant.String
            generated_fature_list=[QgsField(x,field_type) for x in GPKP_COLUMNS_ADD_LIST]
            vlayer.dataProvider().addAttributes(generated_fature_list)
            vlayer.updateFields()

            # modyfikacja już utworzonych kolumn (zmiana nazw atrybutów)
            for field_idx,field in enumerate(vlayer.fields()):
                GPKP_COLUMNS_CHANGE_DICT_local = defaultdict(str, GPKP_COLUMNS_DICT)
                if GPKP_COLUMNS_CHANGE_DICT_local[field.name()]:
                    new_value=GPKP_COLUMNS_CHANGE_DICT_local[field.name()]
                    old_value=field.name()
                    self.renameNameField(vlayer, old_value, new_value)

            # usuwanie zbędnych atrybutów z GeoPaczki, które powstały podczas processingu
            is_cleaned = False
            while not is_cleaned:
                is_cleaned = True
                for field_idx,field in enumerate(vlayer.fields()):        
                    if field.name() in GPKP_COLUMNS_DELETE_LIST:
                        is_cleaned = False
                        vlayer.dataProvider().deleteAttributes([field_idx])
                        vlayer.updateFields()
                        break

            features = vlayer.getFeatures()
            number_of_features = vlayer.featureCount()
            progressbar_div = int(number_of_features / (PROGRESS["IMPORT_ATTRIBUTES_DONE"] - PROGRESS["IMPORT_AFTER_TOOL"]))
            if progressbar_div == 0: 
                progressbar_div = 1
            time_progress = 0

            # modyfikacja wartości atrybutów
            field_map = vlayer.dataProvider().fieldNameMap()
            for feature in features:
                time_progress += 1
                # aktualizowanie paska postępu tylko, kiedy ma to sens
                if time_progress % progressbar_div == 0:
                    try:
                        progress_attr = PROGRESS["IMPORT_AFTER_TOOL"] + int(
                            (PROGRESS["IMPORT_ATTRIBUTES_DONE"] - PROGRESS["IMPORT_AFTER_TOOL"])
                            * time_progress
                            / number_of_features
                        )
                        self.progress.setValue(progress_attr)
                        QApplication.processEvents()
                    except RuntimeError:
                        MessageUtils.pushLogWarning(
                            TranslationUtils.tr("Failed to update dialog window.")
                        )
                
                # uzupełnienie wartości dla atrybutów: nr_drogi, nazwa_ulicy, numer_odcinka, kilometraz
                nazwa_zdjecia = feature[GPKP_COLUMNS_DICT["filename"]]
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

                vlayer.dataProvider().changeAttributeValues({
                        feature.id(): {
                            field_map[GPKP_COLUMNS_ADD_LIST[0]]: nr_drogi,
                            field_map[GPKP_COLUMNS_ADD_LIST[1]]: nazwa_ulicy,
                            field_map[GPKP_COLUMNS_ADD_LIST[2]]: numer_odcinka,
                            field_map[GPKP_COLUMNS_ADD_LIST[3]]: kilometraz
                            }
                    })
                # uzupełnienie wartości dla atrybutu azymut, w przypadku braku danych o azymucie w metadanych zdjęcia
                azymut_value = feature[COLUMN_YAW]

                if str(azymut_value) == "NULL" or azymut_value is None:
                    vlayer.dataProvider().changeAttributeValues(
                        {feature.id(): {vlayer.dataProvider().fieldNameMap()[COLUMN_YAW]: DEFAULT_YAW_DEGREES}})
                    MessageUtils.pushLogWarning(
                        TranslationUtils.tr(
                            "Invalid input data. Setting default value for 'azimuth' attribute at fid: {fid}."
                        ).format(fid=feature.id())
                    )

                # uzupełnienie wartości dla atrybutu data_wykonania
                data_value = feature[GPKP_COLUMNS_DICT["timestamp"]]
                if str(data_value) == "NULL" or data_value is None:
                    sciezka_zdjecie_value = feature[COLUMN_NAME]
                    sciezka_zdjecie_value = sciezka_zdjecie_value.replace("\\", "/")
                    sciezka_zdjecie_open = open(sciezka_zdjecie_value, "rb")
                    tags = processFile(sciezka_zdjecie_open)
                    self.dataTime = tags["EXIF DateTimeOriginal"]
                    vlayer.dataProvider().changeAttributeValues(
                        {feature.id(): {
                            field_map[GPKP_COLUMNS_DICT["timestamp"]]: str(self.dataTime)}})
                    sciezka_zdjecie_open.close()

        try:
            self.progress.setValue(PROGRESS["IMPORT_ATTRIBUTES_DONE"])
        except RuntimeError:
            pass

        vlayer.commitChanges()
        return vlayer

    def usuniecieWartosciGpkg(self, gpkg_path):
        """Usunięcie wszystkich obiektów w warstwie"""

        vlayer = QgsVectorLayer(gpkg_path, Path(gpkg_path).stem, "ogr")
        if not vlayer.isValid():
            MessageUtils.pushLogCritical(f"Niepowodzenie podczas ladowania warstwy do wyczyszczenia: {gpkg_path}")
            return

        if not vlayer.startEditing():
            MessageUtils.pushLogCritical(f"Niepowodzenie podczas rozpoczecia edycji warstwy: {gpkg_path}")
            return

        for feat in vlayer.getFeatures():
            vlayer.deleteFeature(feat.id())

        if not vlayer.commitChanges():
            MessageUtils.pushLogCritical(f"Niepowodzenie podczas zapisu zmian przy czyszczeniu warstwy: {gpkg_path}")
            vlayer.rollBack()
            return
        try:
            self.progress.setValue(PROGRESS["IMPORT_START"])
        except RuntimeError:
            pass

    def polaczenieWarstw(self, gpkg_path, overwrite):
        """Połączenie dwóch Geopaczek (starego gpkg i gpkg z nowymi obiektami)"""

        vlayer = QgsVectorLayer(gpkg_path, Path(gpkg_path).stem, "ogr")
        if not vlayer.isValid():
            MessageUtils.pushLogCritical(
                f"Niepowodzenie podczas ladowania warstwy do polaczenia: {gpkg_path}"
            )
            return

        if not vlayer.startEditing():
            MessageUtils.pushLogCritical(
                f"Niepowodzenie podczas rozpoczecia edycji warstwy: {gpkg_path}"
            )
            return

        idx = vlayer.fields().indexFromName("fid")
        for sourcefeat in overwrite.getFeatures():
            newfeat = QgsFeature()
            newfeat.setGeometry(sourcefeat.geometry())
            newfeat.setAttributes(sourcefeat.attributes())

            if idx != -1:
                newfeat[idx] = None

            vlayer.addFeature(newfeat)

        if not vlayer.commitChanges():
            MessageUtils.pushLogCritical(
                f"Niepowodzenie podczas zapisu zmian przy laczeniu warstw: {gpkg_path}"
            )
            vlayer.rollBack()
            return

        self.use_layer = str(vlayer.name())

    def dopisaniePlikButtonClicked(self, photo_path, gpkg_path):
        """Obsługa wyboru przycisku dopisania danych do GeoPaczki"""

        try:
            self.progress.setValue(PROGRESS["IMPORT_START"] // 2)
        except RuntimeError:
            pass
          
        vlayer_overwrite = self.createGpkg(photo_path, os.path.join(temp_dir, TEMPORATORY_FILES_LIST[0]))
        self.polaczenieWarstw(gpkg_path, vlayer_overwrite)

    def _gpkgFields(self, *keys):
        """
        Zwraca nazwy pól (kolumn) z GeoPackage na podstawie GPKP_COLUMNS_DICT.
        """
        if not keys:
            return list(GPKP_COLUMNS_DICT.values())
        return [GPKP_COLUMNS_DICT[key] for key in keys]

    def usuwanieDuplikatow(self, gpkg_path):

        """uruchomienie narzędzia do wykrywania duplikatów w warstwie po wybranych atrybutach"""

        duplicate = processing.run(
            "native:removeduplicatesbyattribute",
            {
                "INPUT": gpkg_path,
                "FIELDS": self._gpkgFields(),
                "OUTPUT": os.path.join(temp_dir, TEMPORATORY_FILES_LIST[2]),
                "DUPLICATES": os.path.join(temp_dir, TEMPORATORY_FILES_LIST[1])
            }
        )

        if duplicate["DUPLICATE_COUNT"] > 0:    # obsługa wykrycia duplikatów w warstwie

            self.usuniecieWartosciGpkg(gpkg_path)

            try:
                self.progress.setValue(PROGRESS["DUPLICATES_BEFORE_MERGE"])
            except RuntimeError:
                pass

            layer_no_duplicate = QgsVectorLayer(duplicate["OUTPUT"], "no_duplicate", "ogr")
            self.polaczenieWarstw(gpkg_path, layer_no_duplicate)

            try:
                self.progress.setValue(PROGRESS["DUPLICATES_AFTER_MERGE"])
            except RuntimeError:
                pass

            # przygotowanie informacji o zduplikowanych zdjęciach
            sciezka_zdjecie_list = []
            layer_duplicate = QgsVectorLayer(duplicate["DUPLICATES"], "duplicate", "ogr")

            for feat_duplic in layer_duplicate.getFeatures():
                sciezka_zdjecie_value = feat_duplic[GPKP_COLUMNS_DICT["filename"]]
                sciezka_zdjecie_list.append(sciezka_zdjecie_value)

            if len(sciezka_zdjecie_list) <= DUPLICATES_PREVIEW_LIMIT:
                lista_zdjec = str(sciezka_zdjecie_list)
            else:
                lista_zdjec = str(sciezka_zdjecie_list[0:DUPLICATES_PREVIEW_LIMIT-1]) + " ... "

            # wyświetlenie okna z informacją duplikatach
            MessageUtils.pushMessageBoxInfo(
                self.iface.mainWindow(),
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr(
                    "Removed {count} duplicates. Duplicates were identified based on attributes: photo_name, longitude, latitude, capture_date. Duplicate photos: {lista}"
                ).format(count=duplicate["DUPLICATE_COUNT"], lista=lista_zdjec),
            )

    def importPhotos(self):
        """Obsługa przycisku "Importuj" do stworzenia GeoPaczki z geotagowanych zdjęć z wybranego folderu """

        self.is_press_button = True

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
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr("No .jpg files were found in the selected photo folder"),
            )
            return False

        gpkg_path = self.dlg.mQgsFileWidget_save_gpkg.filePath()

        # stworzenie paska postępu
        progress_message_bar = self.iface.messageBar().createMessage(
            TranslationUtils.tr("Import inprogress {name}...").format(
                name=gpkg_path.split("\\")[-1]
            )
        )
        self.progress = QProgressBar()
        self.progress.setMaximum(PROGRESS["COMPLETE"])
        self.progress.setAlignment(QtCompat.alignmentLeftVcenter(Qt))

        if not gpkg_path or gpkg_path == "": # obsługa nie wskazania ściężki zapisu GeoPaczki
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr(
                    "No output GeoPackage (.gpkg) file was specified. This file is required by the QGIS layer manager. Operation cancelled."
                ),
            )
            return False
        
        # sprawdzanie, czy plik nie jest używany przez inny proces zewnętrzny lub przez istniejącą warstwę 
        if os.path.exists(gpkg_path):
            try:
                os.rename(gpkg_path, gpkg_path)
            except OSError as e:
                MessageUtils.pushMessageBoxWarning(
                    self.dlg,
                    TranslationUtils.tr("Warning"),
                    TranslationUtils.tr(
                        "The specified GeoPackage file is in use by another process or an existing layer. Operation aborted."
                    ),
                )
                return False

        # sprawdzenie rozszerzenia pliku wpisanego przez użytkownika
        if Path(gpkg_path).suffix.lower() != ".gpkg":
            gpkg_path = gpkg_path + ".gpkg"

        elif os.path.exists(gpkg_path): # obsługa wskazania już istnięjącego pliku Geopaczki

            # stworzenie okienka wyboru przy sytuacji istnienia gpkg
            msgBox = QMessageBox(self.dlg)
            msgBox.setIcon(QtCompat.qmessageboxInformationIcon())
            msgBox.setWindowTitle(TranslationUtils.tr("Information"))
            msgBox.setText(
                TranslationUtils.tr(
                    "File already exists.\n"
                    "Do you want to create a new file (the existing GPKG file will be deleted)?\n"
                    "Or append data to the existing file?"
                )
            )

            zatwierdz_role = QtCompat.qmessageboxApplyRole(QtWidgets)
            anuluj_role = QtCompat.qmessageboxResetRole(QtWidgets)

            nowy_plik_button = msgBox.addButton(TranslationUtils.tr("New file"), zatwierdz_role)
            dopisanie_plik_button = msgBox.addButton(TranslationUtils.tr("Append data"), zatwierdz_role)
            anuluj_button = msgBox.addButton(TranslationUtils.tr("Cancel"), anuluj_role)
            QtCompat.dialogExec(msgBox)

            if msgBox.clickedButton() == nowy_plik_button:  # obsługa przycisku do stworzenia nowego pliku gpkg (dane z istniejącego pliku zostaną skasowane)
                progress_message_bar.layout().addWidget(self.progress)
                self.iface.messageBar().pushWidget(progress_message_bar, Qgis.Info)

                try:
                    self.progress.setValue(0)
                except RuntimeError:
                    pass

                self.usuniecieWartosciGpkg(gpkg_path)
                self.dopisaniePlikButtonClicked(photo_path, gpkg_path)

            elif msgBox.clickedButton() == dopisanie_plik_button:  # obsługa przycisku do dodania nowych danych do pliku gpkg (do danych z istniejącego pliku zostaną dopisane nowe)
                progress_message_bar.layout().addWidget(self.progress)
                self.iface.messageBar().pushWidget(progress_message_bar, Qgis.Info)

                try:
                    self.progress.setValue(0)
                except RuntimeError:
                    pass

                self.dopisaniePlikButtonClicked(photo_path, gpkg_path)
                self.usuwanieDuplikatow(gpkg_path)

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
            self.use_layer = str(layer.name())

            try:
                self.progress.setValue(PROGRESS["COMPLETE"])
            except RuntimeError:
                pass

            # ukrycie okna PhotoViewer360
            self.dlg.hide()
            self.action_activate.setEnabled(True)
            self.clickPointOnMapFeature()

        else: # obsługa wskazania ścieżki zapisu gpkg (bez komplikacji)
            progress_message_bar.layout().addWidget(self.progress)
            self.iface.messageBar().pushWidget(progress_message_bar, Qgis.Info)
            self.progress.setValue(0)
            vlayer = self.createGpkg(photo_path, gpkg_path)
            self.project.addMapLayer(vlayer)
            self.use_layer = str(vlayer.name())

            try:
                self.progress.setValue(PROGRESS["COMPLETE"])
            except RuntimeError:
                pass

            self.dlg.hide()
            self.clickPointOnMapFeature()

    def browseGpkg(self):
        """Obsługa przycisku "Przeglądaj" do wczytania już istniejącej GeoPaczki nie wczytanej w projekcie QGIS 
        (GeoPaczka musi być utworzona przez tą wtyczkę) """

        self.is_press_button = True

        gpkg_path = os.path.join(self.dlg.mQgsFileWidget_search_gpkg.filePath())
        if not self.checkSavePath(gpkg_path):
            return False
        gpkg_name = Path(gpkg_path).stem

        vlayer = QgsVectorLayer(gpkg_path, gpkg_name, "ogr")
        if not vlayer.isValid():
            MessageUtils.pushLogCritical(
                TranslationUtils.tr(
                    "Failed to load layer from existing GeoPackage: {path}"
                ).format(path=gpkg_path)
            )
            return False
        
        # sprawdzanie poprawności GeoPaczki, pliki powstałe poza wtyczką są odrzucane
        col_name = GPKP_COLUMNS_CHECK[0]
        try:
            for feature in vlayer.getFeatures():
                for name in GPKP_COLUMNS_CHECK:
                    col_name = name
                    atrybut = feature.attribute(name)
                break
        except KeyError:
            MessageUtils.pushLogWarning(
                TranslationUtils.tr(
                    "Required attribute not found in the selected GeoPackage file: {col}"
                ).format(col=col_name)
            )
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr(
                    "The selected file does not contain the required attributes. The file may be corrupted or created using another tool."
                ),
            )
            self.action_activate.setEnabled(False)
            return False

        self.project.addMapLayer(vlayer)

        self.use_layer = vlayer.name()
        self.dlg.hide()
        self.action_activate.setEnabled(True)
        self.clickPointOnMapFeature()

        return True

    def renameNameField(self, rlayer, oldname, newname):
        """Funkcja zmieniająca nazwy atrybutów w warstwie"""

        findex = rlayer.dataProvider().fieldNameIndex(oldname)
        if findex != -1:
            rlayer.dataProvider().renameAttributes({findex: newname})
            rlayer.updateFields()

    def createNewViewer(self, features_id=None, layer=None):
        """Funkcja uruchamia plik Geo360Dialog.py, który jest odpowiedzialny za obsługę okna StreetView (okna ze zdjęciami oraz nawigacją)"""

        self.features_id = features_id
        self.canvas.refresh()

        pozycja_dockwidget = QtCompat.rightDockwidgetArea(Qt)

        if self.orbital_viewer is not None:
            self.orbital_viewer.updateViewerDialog(
                features_id=features_id,
                layer=layer,
                name_layer=self.use_layer,
            )
        else:
            self.orbital_viewer = Geo360Dialog(
                self.iface,
                features_id=features_id,
                layer=layer,
                name_layer=self.use_layer,
                parent=self,
            )
            self.iface.addDockWidget(pozycja_dockwidget, self.orbital_viewer)

    def layerRemoved(self):
        """Obsługa usunięcia warstwy z projektu QGIS"""

        lys = self.project.mapLayers().values()
        layers_name = []

        for one_layer in lys:
            layers_name.append(one_layer.name())

        if (self.use_layer not in layers_name):
            self.action_activate.setEnabled(False)
            self.iface.actionPan().trigger()

            if self.orbital_viewer is not None:
                self.orbital_viewer.close()

    def checkSavePath(self, path):
        """Funkcja sprawdza czy ścieżka jest poprawna i zwraca Boolean"""

        if not path or path == "":
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr("No file/folder path specified"),
            )
            return False
        elif not os.path.exists(path):
            MessageUtils.pushMessageBoxWarning(
                self.dlg,
                TranslationUtils.tr("Warning"),
                TranslationUtils.tr("Specified path for reading files/folder does not exist"),
            )
            return False
        else:
            return True
