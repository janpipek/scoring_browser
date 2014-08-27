#!/usr/bin/env python
#
# scoring_browser --- Simple Qt application for browsing
# scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
# Requires:
#   - numpy
#   - PyQt4
#
# Tested on:
#   Linux, Python 2.7, 3.2

import sys
import os
from PyQt4 import QtGui, QtCore
from qt4_ui import ApplicationWindow

QtCore.QCoreApplication.setApplicationName("scoring_browser")
QtCore.QCoreApplication.setOrganizationDomain("vzdusne.cz")
QtCore.QCoreApplication.setOrganizationName("Jan Pipek")

qApp = QtGui.QApplication(sys.argv)

icon_dir = os.path.dirname(os.path.realpath(__file__))
icon_file = os.path.join(icon_dir, 'images/icon.png')

qApp.setWindowIcon(QtGui.QIcon(icon_file))
window = ApplicationWindow()
window.show()

if len(sys.argv) >= 2:
    if sys.argv[1].endswith("h5"):
        if len(sys.argv) >= 3:
            window.read_file_hdf5(sys.argv[1], sys.argv[2])
        else:
            print "Please, specify dataset name."
            sys.exit(-1)
    else:
        window.read_file_csv(sys.argv[1])

sys.exit(qApp.exec_())
