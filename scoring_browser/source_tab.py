#
# scoring_browser --- Simple Qt application for browsing
# scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek
# (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from PyQt4 import QtGui


class SourceTab(QtGui.QWidget):
    """ Tab displaying the file source."""
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QVBoxLayout(self)
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)

    def setText(self, text):
        self.textEdit.setText(text)
