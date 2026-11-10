# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhotoViewer360
                                 A QGIS plugin
 Show local equirectangular images.
                             -------------------
        begin                : 2022-08-08
        copyright            : (C) 2026 by EnviroSolutions Sp z o.o.
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
import re
from qgis.PyQt import QtCore, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QDir, QEvent, QTimer, QUrl
from qgis.PyQt.QtGui import QDesktopServices

from .. import PLUGIN_VERSION
from ..utils import QtCompat, ThemeUtils
from ..constants import (
    FOOTER_LINK_COLORS, FOOTER_LOGOS, HOME_LINK, IMAGES_DIRECTORY, QSS_IMAGES_PREFIX
)

PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))

# Prefiks używany w url(...) arkusza stylów w pliku .ui (strzałka listy, ikony nagłówka).
# Musi być zarejestrowany przed setupUi, inaczej QSS nie znajdzie ikon.
QDir.addSearchPath(QSS_IMAGES_PREFIX, os.path.join(PLUGIN_DIR, IMAGES_DIRECTORY))

FORM_CLASS, _ = uic.loadUiType(os.path.join(PLUGIN_DIR, 'ui', 'first_window_geo360_base.ui'))


class FirstWindowGeo360Dialog(QtWidgets.QDockWidget, FORM_CLASS):
    """Panel dokowany PhotoViewer360 (wybór zdjęć / warstwy / GeoPaczki)."""

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(FirstWindowGeo360Dialog, self).__init__(parent)
        self.setupUi(self)
        # nazwa obiektu - QGIS zapamiętuje po niej położenie panelu
        self.setObjectName('PhotoViewer360Dock')
        self.mQgsFileWidget_search_photo.setOptions(
            QtCompat.qfiledialogShowDirsOnly(QtWidgets)
        )
        # Zakładki na pełną szerokość ramki (documentMode w .ui) - Qt wyłącza wtedy rozciąganie zakładek,
        # więc włączamy je z powrotem; pasek zakładek nie istnieje w pliku .ui
        self.tabWidget_2.tabBar().setExpanding(True)
        self._theme = None
        self._heightFitted = False
        self._applyTheme()
        self._setupLook()

    # ------------------------------- Wygląd -----------------------------------
    def _setupLook(self):
        """Elementy wyglądu, których nie da się opisać w pliku .ui."""
        self.lbl_subtitle.setText('%s · v%s' % (self.lbl_subtitle.text(), PLUGIN_VERSION))
        self.btn_help.clicked.connect(self._openHelp)
        self.btn_close.clicked.connect(self.close)
        # Nagłówek wtyczki jako pasek tytułu panelu - zamiast systemowego paska z nazwą wtyczki
        self.verticalLayout_main.removeWidget(self.header_frame)
        self.setTitleBarWidget(self.header_frame)

    def _applyTheme(self, force=False):
        """Ustawia właściwość "theme" - kolory są zdefiniowane w arkuszu stylów w pliku .ui."""
        theme = 'dark' if ThemeUtils.isDarkTheme() else 'light'
        if theme == self._theme and not force:
            return
        self._theme = theme
        self.setProperty('theme', theme)
        ThemeUtils.repolishAll(self)
        # Linki w stopce: tekst i adres są w .ui (i tłumaczeniu), tu zmienia się tylko kolor
        color = FOOTER_LINK_COLORS[theme]
        for lbl in (self.lbl_email_7, self.label_16):
            lbl.setText(re.sub(r'style="[^"]*"', 'style="text-decoration:underline; color:%s;"' % color, lbl.text()))
        self._setFooterLogo()

    def _setFooterLogo(self):
        """Logo w stopce: zielone na jasnym tle, białe na ciemnym."""
        if self._theme is not None:
            ThemeUtils.setLogo(self.img_es_4, FOOTER_LOGOS[self._theme], self.img_es_4.maximumHeight())

    def showEvent(self, event):
        self._applyTheme()
        self._equalizeTabPages()
        super().showEvent(event)
        # dopiero po pokazaniu znana jest skala ekranu - inaczej logo jest rozpikselowane
        self._setFooterLogo()
        if not self._heightFitted:
            self._heightFitted = True
            # po przeliczeniu layoutów okna głównego
            QTimer.singleShot(0, self._fitOnOpen)

    def _equalizeTabPages(self):
        """Wszystkie zakładki dostają wysokość najwyższej z nich (Wybór zdjęć), żeby przełączanie
        zakładek nie zmieniało rozmiaru panelu."""
        pages = [self.tabWidget_2.widget(i) for i in range(self.tabWidget_2.count())]
        for page in pages:
            page.setMinimumHeight(0)
        height = max(page.sizeHint().height() for page in pages)
        for page in pages:
            page.setMinimumHeight(height)

    def _fitOnOpen(self):
        """Przy otwarciu panel dostaje pełny rozmiar treści, żeby nic nie było ucięte ani zasłonięte.
        Minimum (nie da się zmniejszyć panelu poniżej treści) pilnuje sam Qt - zakładki nie są skracane."""
        main_window = self.parentWidget()
        if self.isFloating() or not isinstance(main_window, QtWidgets.QMainWindow):
            return
        hint = self.sizeHint().expandedTo(self.minimumSizeHint())
        main_window.resizeDocks([self], [hint.width()], QtCore.Qt.Orientation.Horizontal)
        main_window.resizeDocks([self], [hint.height()], QtCore.Qt.Orientation.Vertical)

    def changeEvent(self, event):
        # changeEvent przychodzi już w trakcie setupUi - wtedy _theme jeszcze nie istnieje
        if (event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange)
                and getattr(self, '_theme', None) is not None):
            self._applyTheme()
        super().changeEvent(event)

    def _openHelp(self):
        QDesktopServices.openUrl(QUrl(HOME_LINK))

    def closeEvent(self, event):
        self._heightFitted = False  # po ponownym otwarciu znowu pełna wysokość
        self.closingPlugin.emit()
        event.accept()
