# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'first_window_geo360_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName("main")
        main.setWindowModality(QtCore.Qt.NonModal)
        main.resize(600, 280)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main.sizePolicy().hasHeightForWidth())
        main.setSizePolicy(sizePolicy)
        main.setMinimumSize(QtCore.QSize(600, 280))
        main.setMaximumSize(QtCore.QSize(600, 280))
        main.setFocusPolicy(QtCore.Qt.NoFocus)
        main.setSizeGripEnabled(False)
        main.setModal(False)
        self.lbl_title = QtWidgets.QLabel(main)
        self.lbl_title.setGeometry(QtCore.QRect(0, 10, 600, 20))
        self.lbl_title.setMinimumSize(QtCore.QSize(600, 20))
        self.lbl_title.setMaximumSize(QtCore.QSize(600, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_title.setObjectName("lbl_title")
        self.tabWidget_2 = QtWidgets.QTabWidget(main)
        self.tabWidget_2.setEnabled(True)
        self.tabWidget_2.setGeometry(QtCore.QRect(10, 50, 581, 211))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tabWidget_2.setMinimumSize(QtCore.QSize(0, 0))
        self.tabWidget_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget_2.setFocusPolicy(QtCore.Qt.TabFocus)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab2.sizePolicy().hasHeightForWidth())
        self.tab2.setSizePolicy(sizePolicy)
        self.tab2.setObjectName("tab2")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 561, 161))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.mQgsFileWidget_search_photo = QgsFileWidget(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mQgsFileWidget_search_photo.sizePolicy().hasHeightForWidth())
        self.mQgsFileWidget_search_photo.setSizePolicy(sizePolicy)
        self.mQgsFileWidget_search_photo.setStorageMode(QgsFileWidget.GetDirectory)
        self.mQgsFileWidget_search_photo.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        self.mQgsFileWidget_search_photo.setObjectName("mQgsFileWidget_search_photo")
        self.verticalLayout_2.addWidget(self.mQgsFileWidget_search_photo)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.mQgsFileWidget_save_gpkg = QgsFileWidget(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mQgsFileWidget_save_gpkg.sizePolicy().hasHeightForWidth())
        self.mQgsFileWidget_save_gpkg.setSizePolicy(sizePolicy)
        self.mQgsFileWidget_save_gpkg.setFileWidgetButtonVisible(True)
        self.mQgsFileWidget_save_gpkg.setUseLink(False)
        self.mQgsFileWidget_save_gpkg.setFullUrl(False)
        self.mQgsFileWidget_save_gpkg.setStorageMode(QgsFileWidget.SaveFile)
        self.mQgsFileWidget_save_gpkg.setObjectName("mQgsFileWidget_save_gpkg")
        self.verticalLayout_2.addWidget(self.mQgsFileWidget_save_gpkg)
        self.fromPhotos_btn = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.fromPhotos_btn.setObjectName("fromPhotos_btn")
        self.verticalLayout_2.addWidget(self.fromPhotos_btn)
        self.tabWidget_2.addTab(self.tab2, "")
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab1.sizePolicy().hasHeightForWidth())
        self.tab1.setSizePolicy(sizePolicy)
        self.tab1.setObjectName("tab1")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab1)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 561, 121))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.mapLayerComboBox = QgsMapLayerComboBox(self.verticalLayoutWidget)
        self.mapLayerComboBox.setObjectName("mapLayerComboBox")
        self.verticalLayout.addWidget(self.mapLayerComboBox)
        self.fromLayer_btn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fromLayer_btn.sizePolicy().hasHeightForWidth())
        self.fromLayer_btn.setSizePolicy(sizePolicy)
        self.fromLayer_btn.setObjectName("fromLayer_btn")
        self.verticalLayout.addWidget(self.fromLayer_btn)
        self.tabWidget_2.addTab(self.tab1, "")
        self.tab3 = QtWidgets.QWidget()
        self.tab3.setEnabled(True)
        self.tab3.setObjectName("tab3")
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.tab3)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(10, 10, 561, 121))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_5.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_11 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_5.addWidget(self.label_11)
        self.mQgsFileWidget_search_gpkg = QgsFileWidget(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mQgsFileWidget_search_gpkg.sizePolicy().hasHeightForWidth())
        self.mQgsFileWidget_search_gpkg.setSizePolicy(sizePolicy)
        self.mQgsFileWidget_search_gpkg.setObjectName("mQgsFileWidget_search_gpkg")
        self.verticalLayout_5.addWidget(self.mQgsFileWidget_search_gpkg)
        self.fromGPKG_btn = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fromGPKG_btn.sizePolicy().hasHeightForWidth())
        self.fromGPKG_btn.setSizePolicy(sizePolicy)
        self.fromGPKG_btn.setObjectName("fromGPKG_btn")
        self.verticalLayout_5.addWidget(self.fromGPKG_btn)
        self.tabWidget_2.addTab(self.tab3, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.tab)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(160, 0, 411, 181))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 371, 87))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.lbl_copyrights_2 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_copyrights_2.setFont(font)
        self.lbl_copyrights_2.setTextFormat(QtCore.Qt.RichText)
        self.lbl_copyrights_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_copyrights_2.setOpenExternalLinks(True)
        self.lbl_copyrights_2.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lbl_copyrights_2.setObjectName("lbl_copyrights_2")
        self.gridLayout.addWidget(self.lbl_copyrights_2, 3, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.lbl_email_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_email_3.setFont(font)
        self.lbl_email_3.setTextFormat(QtCore.Qt.RichText)
        self.lbl_email_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_email_3.setOpenExternalLinks(True)
        self.lbl_email_3.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lbl_email_3.setObjectName("lbl_email_3")
        self.gridLayout.addWidget(self.lbl_email_3, 2, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.verticalLayoutWidget_3)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 20, 371, 21))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_14 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_14.setFont(font)
        self.label_14.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 0, 0, 1, 1)
        self.lbl_copyrights_3 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_copyrights_3.setFont(font)
        self.lbl_copyrights_3.setTextFormat(QtCore.Qt.RichText)
        self.lbl_copyrights_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_copyrights_3.setOpenExternalLinks(True)
        self.lbl_copyrights_3.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lbl_copyrights_3.setObjectName("lbl_copyrights_3")
        self.gridLayout_3.addWidget(self.lbl_copyrights_3, 0, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 171, 181))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_12 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_12.setMaximumSize(QtCore.QSize(122, 122))
        self.label_12.setText("")
        self.label_12.setPixmap(QtGui.QPixmap("../images/logo2.png"))
        self.label_12.setScaledContents(True)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.tab, "")

        self.retranslateUi(main)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "PhotoViewer360 - ustawienia"))
        self.lbl_title.setText(_translate("main", "Wybierz dane do przeglądania zdjęć panoramicznych"))
        self.label_3.setText(_translate("main", "Wybierz folder ze zdjęciami z georeferencją i azymutem"))
        self.label.setText(_translate("main", "Wybierz ścieżkę zapisu paczki GeoPackage z warstwą punktową zdjęć"))
        self.fromPhotos_btn.setText(_translate("main", "Importuj"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab2), _translate("main", "Wybór zdjęć"))
        self.label_2.setText(_translate("main", "Wybierz warstwę wektorową"))
        self.fromLayer_btn.setText(_translate("main", "Przeglądaj"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab1), _translate("main", "Wybór warstwy w QGIS"))
        self.label_11.setText(_translate("main", "Wybierz plik GeoPackage utworzony za pomocą wtyczki PhotoViewer360"))
        self.fromGPKG_btn.setText(_translate("main", "Przeglądaj"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab3), _translate("main", "Wybór warstwy punktowej GPKG"))
        self.groupBox.setTitle(_translate("main", "Informacje o wtyczce"))
        self.label_6.setText(_translate("main", "Wersja wtyczki:"))
        self.label_8.setText(_translate("main", "1.0"))
        self.label_5.setText(_translate("main", "Nazwa wtyczki:"))
        self.lbl_copyrights_2.setText(_translate("main", "<html><head/><body><p><a href=\"http://www.envirosolutions.pl/\"><span style=\" text-decoration: underline; color:#0000ff;\">EnviroSolutions Sp. z o.o.</span></a></p></body></html>"))
        self.label_7.setText(_translate("main", "Twórca:"))
        self.label_9.setText(_translate("main", "PhotoViewer360"))
        self.label_4.setText(_translate("main", "Właściciel:"))
        self.lbl_email_3.setText(_translate("main", "<html><head/><body><p><a href=\"https://klaster.pro\"><span style=\" text-decoration: underline; color:#0000ff;\">KLASTER Robert M.</span></a></p></body></html>"))
        self.groupBox_2.setTitle(_translate("main", "Dokumentacja"))
        self.label_14.setText(_translate("main", "Instrukcja użytkownika:"))
        self.lbl_copyrights_3.setText(_translate("main", "<html><head/><body><p><a href=\"https://github.com/envirosolutionspl/PhotoViewer360/blob/master/README.md\"><span style=\" text-decoration: underline; color:#0000ff;\">Plik README</span></a></p></body></html>"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab), _translate("main", "Informacje"))
from qgsfilewidget import QgsFileWidget
from qgsmaplayercombobox import QgsMapLayerComboBox
