# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UiOrbitalDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from .. import plugin_dir


class UiOrbitalDialog(object):
    """Klasa definiująca wygląd okna do przeglądania zdjęć (okno Street View)"""

    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName("orbitalDialog")
        orbitalDialog.resize(563, 375)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(orbitalDialog.sizePolicy().hasHeightForWidth())
        orbitalDialog.setSizePolicy(sizePolicy)

        # dodanie okna ze zdjęciem 
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/ikona_wtyczki.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        orbitalDialog.setWindowIcon(icon)
        orbitalDialog.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ViewerLayout = QtWidgets.QGridLayout()
        self.ViewerLayout.setObjectName("ViewerLayout")
        self.verticalLayout_3.addLayout(self.ViewerLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QtWidgets.QSpacerItem(
            5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)

        # dodanie przycisku służącego do patrzenia w górę
        self.btn_look_up = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_look_up.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_look_up.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/look_up.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_look_up.setIcon(icon8)
        self.btn_look_up.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_look_up)

        # dodanie przycisku służącego do patrzenia w dół
        self.btn_look_down = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_look_down.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_look_down.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/look_down.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_look_down.setIcon(icon9)
        self.btn_look_down.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_look_down)


        # dodanie przycisku służącego do obracania w lewo
        self.btn_turn_left = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_turn_left.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_turn_left.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/turn_left.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_turn_left.setIcon(icon4)
        self.btn_turn_left.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_turn_left)

        # dodanie przycisku służącego do zrobienia raportu graficznego
        self.btn_screenshot = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_screenshot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_screenshot.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/camera.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_screenshot.setIcon(icon1)
        self.btn_screenshot.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_screenshot)

        # dodanie przycisku służącego do obsługi setFullScreen'a
        self.btn_fullScreen = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_fullScreen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_fullScreen.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/full_screen.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_fullScreen.setIcon(icon3)
        self.btn_fullScreen.setCheckable(True)
        self.btn_fullScreen.setObjectName("btn_fullScreen")
        self.horizontalLayout.addWidget(self.btn_fullScreen)

        # dodanie przycisku służącego do obracania w prawo
        self.btn_turn_right = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_turn_right.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_turn_right.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/turn_right.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_turn_right.setIcon(icon5)
        self.btn_turn_right.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_turn_right)

        # dodanie przycisku służącego do przybliżania
        self.btn_zoom_in = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_zoom_in.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_zoom_in.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/zoom_in.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_zoom_in.setIcon(icon6)
        self.btn_zoom_in.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_zoom_in)

        # dodanie przycisku służącego do oddalania
        self.btn_zoom_out = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_zoom_out.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_zoom_out.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(plugin_dir + "/images/zoom_out.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_zoom_out.setIcon(icon7)
        self.btn_zoom_out.setObjectName("btn_screenshot")
        self.horizontalLayout.addWidget(self.btn_zoom_out)

        spacerItem1 = QtWidgets.QSpacerItem(
            5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem1)

        self.verticalLayout_3.addLayout(self.horizontalLayout)
        orbitalDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(orbitalDialog)
        
        # obsługa wciśnięć przycisków w oknie przeglądania zdjęć
        self.btn_fullScreen.clicked["bool"].connect(orbitalDialog.setFullScreen)
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
        orbitalDialog.setWindowTitle(
            _translate("orbitalDialog", "PhotoViewer360")
        )
