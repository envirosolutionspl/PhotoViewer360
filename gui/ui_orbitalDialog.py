# -*- coding: utf-8 -*-

# Wygląd okna do przeglądania zdjęć (okno Street View).
# Kolory motywu jasnego/ciemnego są w arkuszu VIEWER_STYLE (właściwość "theme" ustawiana przez ThemeUtils),
# tak samo jak w plikach .ui pozostałych okien wtyczki.

import os

from qgis.PyQt import QtCore, QtGui, QtWidgets
from .. import plugin_dir
from ..utils import QtCompat, ThemeUtils, TranslationUtils

from ..constants import IMAGES_DIRECTORY
from .constants import (
    VIEWER_STYLE,
    VIEWER_ICON_COLORS,
    VIEWER_CLOSE_ICONS,
    VIEWER_DEFAULT_SIZE,
    VIEWER_OPEN_WIDTH_RATIO,
    VIEWER_BUTTON_SIZE,
    VIEWER_ICON_SIZE,
    VIEWER_HEADER_MARGINS,
    VIEWER_HEADER_SPACING,
    VIEWER_TITLE_SPACING,
    VIEWER_TOOLBAR_MARGINS,
    VIEWER_TOOLBAR_SPACING,
    VIEWER_SEPARATOR_SPACING,
    VIEWER_SEPARATOR_INSET,
    VIEWER_BUTTON_GROUPS,
)


class UiOrbitalDialog(object):
    """Klasa definiująca wygląd okna do przeglądania zdjęć (okno Street View)"""

    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName("orbitalDialog")
        orbitalDialog.resize(*VIEWER_DEFAULT_SIZE)
        sizePolicy = QtWidgets.QSizePolicy(
            QtCompat.qsizepolicyExpanding(QtWidgets),
            QtCompat.qsizepolicyExpanding(QtWidgets),
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(orbitalDialog.sizePolicy().hasHeightForWidth())
        orbitalDialog.setSizePolicy(sizePolicy)

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(os.path.join(plugin_dir, IMAGES_DIRECTORY, "ikona_wtyczki.svg")),
            QtCompat.qiconModeNormal(QtGui),
            QtCompat.qiconStateOff(QtGui),
        )
        orbitalDialog.setWindowIcon(icon)
        orbitalDialog.setFeatures(QtCompat.qdockwidgetAllFeatures(QtWidgets))
        orbitalDialog.setStyleSheet(VIEWER_STYLE)
        self._viewer_theme = None

        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)

        # nagłówek - używany jako pasek tytułu panelu (zamiast systemowego paska z nazwą wtyczki)
        self.header_frame = QtWidgets.QFrame(orbitalDialog)
        self.header_frame.setObjectName("header_frame")
        header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(*VIEWER_HEADER_MARGINS)
        header_layout.setSpacing(VIEWER_HEADER_SPACING)
        title_layout = QtWidgets.QVBoxLayout()
        title_layout.setSpacing(VIEWER_TITLE_SPACING)
        self.lbl_viewer_title = QtWidgets.QLabel(self.header_frame)
        self.lbl_viewer_title.setObjectName("lbl_viewer_title")
        self.lbl_viewer_subtitle = QtWidgets.QLabel(self.header_frame)
        self.lbl_viewer_subtitle.setObjectName("lbl_viewer_subtitle")
        title_layout.addWidget(self.lbl_viewer_title)
        title_layout.addWidget(self.lbl_viewer_subtitle)
        header_layout.addLayout(title_layout, 1)
        self.btn_viewer_close = QtWidgets.QToolButton(self.header_frame)
        self.btn_viewer_close.setObjectName("btn_viewer_close")
        self.btn_viewer_close.setAutoRaise(True)
        self.btn_viewer_close.setIconSize(QtCore.QSize(VIEWER_ICON_SIZE, VIEWER_ICON_SIZE))
        self.btn_viewer_close.setCursor(QtGui.QCursor(QtCompat.qcursorShapePointingHand(QtCore)))
        header_layout.addWidget(self.btn_viewer_close)
        orbitalDialog.setTitleBarWidget(self.header_frame)

        # okno ze zdjęciem (widget OpenGL dodawany w Geo360Dialog.updateViewer)
        self.viewer_frame = QtWidgets.QFrame(self.dockWidgetContents)
        self.viewer_frame.setObjectName("viewer_frame")
        self.ViewerLayout = QtWidgets.QGridLayout(self.viewer_frame)
        self.ViewerLayout.setObjectName("ViewerLayout")
        self.ViewerLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.addWidget(self.viewer_frame, 1)

        # pasek przycisków sterujących
        self.toolbar_frame = QtWidgets.QFrame(self.dockWidgetContents)
        self.toolbar_frame.setObjectName("toolbar_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.toolbar_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(*VIEWER_TOOLBAR_MARGINS)
        self.horizontalLayout.setSpacing(VIEWER_TOOLBAR_SPACING)
        self.horizontalLayout.addStretch(1)
        self._viewer_buttons = []
        for group_index, group in enumerate(VIEWER_BUTTON_GROUPS):
            if group_index > 0:
                separator = QtWidgets.QFrame(self.toolbar_frame)
                separator.setProperty("role", "separator")
                separator.setFixedSize(1, VIEWER_BUTTON_SIZE - VIEWER_SEPARATOR_INSET)
                self.horizontalLayout.addSpacing(VIEWER_SEPARATOR_SPACING)
                self.horizontalLayout.addWidget(separator)
                self.horizontalLayout.addSpacing(VIEWER_SEPARATOR_SPACING)
            for object_name, icon_file, _tooltip in group:
                button = QtWidgets.QPushButton(self.toolbar_frame)
                button.setObjectName(object_name)
                button.setCursor(QtGui.QCursor(QtCompat.qcursorShapePointingHand(QtCore)))
                button.setFixedSize(VIEWER_BUTTON_SIZE, VIEWER_BUTTON_SIZE)
                button.setIconSize(QtCore.QSize(VIEWER_ICON_SIZE, VIEWER_ICON_SIZE))
                setattr(self, object_name, button)
                self._viewer_buttons.append((button, icon_file))
                self.horizontalLayout.addWidget(button)
        self.horizontalLayout.addStretch(1)
        self.verticalLayout_3.addWidget(self.toolbar_frame)

        orbitalDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(orbitalDialog)
        self.applyViewerTheme()

        # obsługa wciśnięć przycisków w oknie przeglądania zdjęć
        self.btn_viewer_close.clicked.connect(orbitalDialog.close)
        self.btn_fullscreen.clicked["bool"].connect(orbitalDialog.fullScreen)
        self.btn_screenshot.clicked.connect(orbitalDialog.getScreenShot)

        self.btn_turn_left.pressed.connect(orbitalDialog.turnLeft)
        self.btn_turn_right.pressed.connect(orbitalDialog.turnRight)
        self.btn_turn_left.released.connect(orbitalDialog.turnStop)
        self.btn_turn_right.released.connect(orbitalDialog.turnStop)

        self.btn_zoom_in.pressed.connect(orbitalDialog.zoomIn)
        self.btn_zoom_out.pressed.connect(orbitalDialog.zoomOut)
        self.btn_zoom_in.released.connect(orbitalDialog.zoomStop)
        self.btn_zoom_out.released.connect(orbitalDialog.zoomStop)

        self.btn_look_up.pressed.connect(orbitalDialog.lookUp)
        self.btn_look_down.pressed.connect(orbitalDialog.lookDown)
        self.btn_look_up.released.connect(orbitalDialog.lookStop)
        self.btn_look_down.released.connect(orbitalDialog.lookStop)

        QtCore.QMetaObject.connectSlotsByName(orbitalDialog)

    def retranslateUi(self, orbitalDialog):
        orbitalDialog.setWindowTitle(TranslationUtils.tr("PhotoViewer360"))
        self.lbl_viewer_title.setText(TranslationUtils.tr("Panoramic photo preview"))
        self.btn_viewer_close.setToolTip(TranslationUtils.tr("Close preview"))
        for group in VIEWER_BUTTON_GROUPS:
            for object_name, _icon_file, tooltip in group:
                getattr(self, object_name).setToolTip(TranslationUtils.tr(tooltip))

    def setViewerSubtitle(self, text):
        """Podpis w nagłówku - nazwa wyświetlanego zdjęcia."""
        self.lbl_viewer_subtitle.setText(text)
        self.lbl_viewer_subtitle.setVisible(bool(text))

    def applyViewerTheme(self, force=False):
        """Motyw jasny/ciemny: kolory z VIEWER_STYLE, ikony przycisków przemalowane na kolor motywu."""
        theme = 'dark' if ThemeUtils.isDarkTheme() else 'light'
        if theme == self._viewer_theme and not force:
            return
        self._viewer_theme = theme
        self.setProperty('theme', theme)
        ThemeUtils.repolishAll(self)
        dpr = self.devicePixelRatioF()
        for button, icon_file in self._viewer_buttons:
            button.setIcon(ThemeUtils.tintedIcon(icon_file, VIEWER_ICON_COLORS[theme], VIEWER_ICON_SIZE, dpr))
        self.btn_viewer_close.setIcon(
            QtGui.QIcon(os.path.join(plugin_dir, IMAGES_DIRECTORY, VIEWER_CLOSE_ICONS[theme]))
        )

    def fitViewerOnOpen(self):
        """Przy pierwszym otwarciu okno ze zdjęciem zajmuje część szerokości okna QGIS (VIEWER_OPEN_WIDTH_RATIO),
        żeby zdjęcie i wszystkie przyciski były od razu dobrze widoczne."""
        main_window = self.parentWidget()
        if self.isFloating() or not isinstance(main_window, QtWidgets.QMainWindow):
            return
        width = max(self.minimumSizeHint().width(), int(main_window.width() * VIEWER_OPEN_WIDTH_RATIO))
        main_window.resizeDocks([self], [width], QtCore.Qt.Orientation.Horizontal)
