#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from slice_tab import SliceTab

from PyQt4 import QtGui, QtCore
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # Needed to enable 3D plotting
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class ChartTab(SliceTab):
    def __init__(self, parent):
        SliceTab.__init__(self, parent)

        self.is_3d = False

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget( self.canvas )

        self.threeDCheckBox = QtGui.QCheckBox( "3D" ) 
        self.toolBar.addSeparator()
        self.toolBar.addWidget( self.threeDCheckBox )

        for signal in self.all_model_signals:
            signal.connect(self.update_chart)
        self.threeDCheckBox.stateChanged.connect(self.on_3D_check_box_change)

        self.update_chart()

    def on_3D_check_box_change(self, state):
        self.is_3d = (state == QtCore.Qt.Checked)
        self.update_chart()

    def _plot_2d(self, X, Y, Z):
        axes = self.figure.add_subplot(111)

        axes.contour(Y, X, Z)
        axes.set_ylim(reversed(axes.get_ylim()))

        axes.set_xlabel(self.slice.plane_name[0])
        axes.set_ylabel(self.slice.plane_name[1])

    def _plot_3d(self, X, Y, Z):
        axes = self.figure.add_subplot(111, projection='3d')
        plot = axes.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=matplotlib.cm.coolwarm, linewidth=0, antialiased=False)
        self.figure.colorbar(plot, shrink=0.5)

        axes.set_xlabel(self.slice.plane_name[1])
        axes.set_ylabel(self.slice.plane_name[0])

    def update_chart(self):
        self.figure.clear()
        if self.matrix:
            x = np.arange(self.slice.shape[0])
            y = np.arange(self.slice.shape[1])
            X, Y = np.meshgrid(x, y)

            if self.is_3d:
                self._plot_3d(X, Y, self.slice.data)
            else:
                self._plot_2d(X, Y, self.slice.data)
        self.canvas.draw()
            
