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

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class HistogramTab(QtGui.QWidget):
    """ Tab displaying the histogram of values."""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

        self.update_histogram()

    @property
    def matrix(self):
        if not hasattr(self, "_matrix"):
            return None
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix = value
        self.update_histogram()

    def update_histogram(self):
        self.figure.clear()
        if self.matrix:
            steps = 100
            axis = self.figure.add_subplot(111)
            data = np.histogram(self.matrix.data_array, steps)
            # print data
            y = data[0]
            x = data[1][:-1] # data[1][1:]

            bar_width = float(data[1][-1] - data[1][0]) / steps

            axis.bar(x, y, align="center", width=bar_width)
        self.canvas.draw()


    #def setText(self, text):
    #    self.textEdit.setText(text)
