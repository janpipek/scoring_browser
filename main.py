#!/usr/bin/env python
#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012 Jan Pipek (jan.pipek@gmail.com)
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
from PyQt4 import QtGui, QtCore
from qt4_ui import ApplicationWindow
        
QtCore.QCoreApplication.setApplicationName( "scoring_browser" )
QtCore.QCoreApplication.setOrganizationDomain( "vzdusne.cz" )
QtCore.QCoreApplication.setOrganizationName( "Jan Pipek" )
        
qApp = QtGui.QApplication(sys.argv)
window = ApplicationWindow()
window.show()

if len( sys.argv ) == 2:
    window.readFile( sys.argv[1] )

sys.exit(qApp.exec_())
