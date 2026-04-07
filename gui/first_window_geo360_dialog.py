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
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from ..utils import QtCompat

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'first_window_geo360_base.ui'))

class FirstWindowGeo360Dialog(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        """Constructor."""
        super(FirstWindowGeo360Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.mQgsFileWidget_search_photo.setOptions(
            QtCompat.qfiledialogShowDirsOnly(QtWidgets)
        )
        #self.folder_fileWidget.setStorageMode(QgsFileWidget.GetDirectory)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
