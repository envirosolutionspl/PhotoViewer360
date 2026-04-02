# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UiOrbitalDialog.ui'
#
# Adapted for Qt5 / Qt6 compatibility using QtCompat
#
# WARNING! Manual compatibility adjustments added.

import os

from qgis.PyQt import QtCore, QtGui, QtWidgets
from .. import plugin_dir
from ..utils import QtCompat

from ..constants import IMAGES_DIRECTORY


class UiOrbitalDialog(object):
    """Klasa definiująca wygląd okna do przeglądania zdjęć (okno Street View)"""

    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName("orbitalDialog")
        orbitalDialog.resize(563, 375)
        sizePolicy = QtWidgets.QSizePolicy(
            QtCompat.qsizepolicyExpanding(QtWidgets),
            QtCompat.qsizepolicyExpanding(QtWidgets),
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(orbitalDialog.sizePolicy().hasHeightForWidth())
        orbitalDialog.setSizePolicy(sizePolicy)

        # dodanie okna ze zdjęciem
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/ikona_wtyczki.svg"),
            QtCompat.qiconModeNormal(QtGui),
            QtCompat.qiconStateOff(QtGui),
        )
        orbitalDialog.setWindowIcon(icon)
        orbitalDialog.setFeatures(QtCompat.qdockwidgetAllFeatures(QtWidgets))
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ViewerLayout = QtWidgets.QGridLayout()
        self.ViewerLayout.setObjectName("ViewerLayout")
        self.verticalLayout_3.addLayout(self.ViewerLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(
            QtCompat.qlayoutSizeConstraintFixedSize(QtWidgets)
        )
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QtWidgets.QSpacerItem(
            5,
            20,
            QtCompat.qsizepolicyExpanding(QtWidgets),
            QtCompat.qsizepolicyMinimum(QtWidgets),
        )
        self.horizontalLayout.addItem(spacerItem)

        def setButton(object_name, image_file_name):
            button = QtWidgets.QPushButton(self.dockWidgetContents)
            button.setCursor(QtGui.QCursor(QtCompat.qcursorShapePointingHand(QtCore)))
            button.setText("")
            q_icon = QtGui.QIcon()
            q_icon.addPixmap(
                QtGui.QPixmap(os.path.join(plugin_dir, IMAGES_DIRECTORY, image_file_name)),
                QtCompat.qiconModeNormal(QtGui),
                QtCompat.qiconStateOff(QtGui),
            )
            button.setIcon(q_icon)
            button.setObjectName(object_name)
            return button
        
        # dodanie przycisku służącego do patrzenia w górę
        self.btn_look_up = setButton("btn_look_up", "look_up.svg")
        self.horizontalLayout.addWidget(self.btn_look_up)

        # dodanie przycisku służącego do patrzenia w dół
        self.btn_look_down = setButton("btn_look_down", "look_down.svg")
        self.horizontalLayout.addWidget(self.btn_look_down)

        # dodanie przycisku służącego do obracania w lewo
        self.btn_turn_left = setButton("btn_turn_left", "turn_left.svg")
        self.horizontalLayout.addWidget(self.btn_turn_left)

        # dodanie przycisku służącego do zrobienia raportu graficznego
        self.btn_screenshot = setButton("btn_screenshot", "camera.svg")
        self.horizontalLayout.addWidget(self.btn_screenshot)

        # dodanie przycisku służącego do obsługi fullscreen'a
        self.btn_fullscreen = setButton("btn_fullscreen", "full_screen.svg")
        self.horizontalLayout.addWidget(self.btn_fullscreen)

        # dodanie przycisku służącego do obracania w prawo
        self.btn_turn_right = setButton("btn_turn_right", "turn_right.svg")
        self.horizontalLayout.addWidget(self.btn_turn_right)

        # dodanie przycisku służącego do przybliżania
        self.btn_zoom_in = setButton("btn_zoom_in", "zoom_in.svg")
        self.horizontalLayout.addWidget(self.btn_zoom_in)

        # dodanie przycisku służącego do oddalania
        self.btn_zoom_out = setButton("btn_zoom_out", "zoom_out.svg")
        self.horizontalLayout.addWidget(self.btn_zoom_out)

        spacerItem1 = QtWidgets.QSpacerItem(
            5,
            20,
            QtCompat.qsizepolicyExpanding(QtWidgets),
            QtCompat.qsizepolicyMinimum(QtWidgets),
        )
        self.horizontalLayout.addItem(spacerItem1)

        self.verticalLayout_3.addLayout(self.horizontalLayout)
        orbitalDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(orbitalDialog)

        # obsługa wciśnięć przycisków w oknie przeglądania zdjęć
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
        _translate = QtCore.QCoreApplication.translate
        orbitalDialog.setWindowTitle(_translate("orbitalDialog", "PhotoViewer360"))
