#
# scoring_browser --- Simple Qt application for browsing
# scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek
# (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from PyQt4 import QtGui, QtCore

from data_matrix import DataMatrix

from table_tab import TableTab
from source_tab import SourceTab


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.tabs = QtGui.QTabWidget(self)

        self.tableTab = TableTab(self)
        self.tabs.addTab(self.tableTab, "Data Table")

        self.sourceTab = SourceTab()
        self.tabs.addTab(self.sourceTab, "Source")

        try:
            # matplotlib needed
            from chart_tab import ChartTab
            self.chartTab = ChartTab(self)
            self.tabs.addTab(self.chartTab, "Chart")
        except:
            raise

        self.setCentralWidget(self.tabs)
        self.setWindowTitle("Scoring Output Browser")

        self.build_menu()

        self.set_status("Ready")
        self.restore_settings()

    def build_menu(self):
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.open_file,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.close,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('E&xport Table as CSV',
                                 self.export_csv,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_X)
        self.menuBar().addMenu(self.file_menu)

        self.tools_menu = QtGui.QMenu('&Tools', self)
        self.tools_menu.addAction('&Reduce Matrix',
                                  self.show_reduction_dialog,
                                  QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.tools_menu)

    def set_matrix(self, matrix):
        self.matrix = matrix
        self.tableTab.matrix = matrix
        if hasattr(self, "chartTab"):
            self.chartTab.matrix = matrix

    def show_reduction_dialog(self):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Reduce Matrix")

        layout = QtGui.QVBoxLayout()
        dialog.setLayout(layout)

        xtext = QtGui.QLineEdit()
        ytext = QtGui.QLineEdit()
        ztext = QtGui.QLineEdit()

        layout.addWidget(QtGui.QLabel("Reduction in X Axis"))
        layout.addWidget(xtext)

        layout.addWidget(QtGui.QLabel("Reduction in Y Axis"))
        layout.addWidget(ytext)

        layout.addWidget(QtGui.QLabel("Reduction in Z Axis"))
        layout.addWidget(ztext)

        def onButtonClick():
            try:
                x = int(xtext.text())
                y = int(ytext.text())
                z = int(ztext.text())
                matrix = self.matrix.reduced((x, y, z))
                self.set_matrix(matrix)
                dialog.close()
            except ValueError:
                pass

        button = QtGui.QPushButton("Proceed")
        button.clicked.connect(onButtonClick)

        layout.addWidget(button)

        dialog.show()
        self.set_matrix(self.matrix.copy())  # ???

    def open_file(self):
        """ Invoke file open dialog and read the selected file """
        file_name = QtGui.QFileDialog.getOpenFileName(self, "Select Data File")
        if file_name:
            self.read_file(file_name)

    def export_csv(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self, "Select CSV File")
        if file_name:
            self.tableTab.write_csv(file_name)

    def read_file(self, file_name):
        self.set_status("Opening " + file_name + "...")
        try:
            with open(file_name) as f:
                text = f.read()
                self.sourceTab.setText(text)
                matrix = DataMatrix(text)
            self.set_status("Successfully read " + file_name)
            self.setWindowTitle("Scoring Output Browser (" + file_name + ")")
        except:
            matrix = None
            self.set_status("Error reading file.")
        self.set_matrix(matrix)

    def set_status(self, text):
        """ Display a status message."""
        self.statusBar().showMessage(text)

    def closeEvent(self, event):
        settings = QtCore.QSettings()
        settings.setValue("window/geometry", self.saveGeometry())
        settings.setValue("window/state", self.saveState())
        QtGui.QMainWindow.closeEvent(self, event)

    def restore_settings(self):
        """ Restore settings about window geometry from the saved settings"""
        try:
            settings = QtCore.QSettings()
            self.restoreGeometry(settings.value("window/geometry"))
            self.restoreState(settings.value("window/state"))
        except:
            pass
