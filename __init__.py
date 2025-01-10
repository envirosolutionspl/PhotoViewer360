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
import sys, os

try:
    sys.path.append("C:\eclipse\plugins\org.python.pydev.core_8.3.0.202104101217\pysrc")
    sys.path.append(
        "/home/fragalop/eclipse/plugins/org.python.pydev.core_8.3.0.202104101217/pysrc"
    )
    from pydevd import *
except ImportError:
    None

plugin_dir = os.path.dirname(__file__)
exifread_path = os.path.join(plugin_dir, 'libs', 'ExifRead-3.0.0')

def classFactory(iface):
    from .Geo360 import Geo360

    return Geo360(iface)
