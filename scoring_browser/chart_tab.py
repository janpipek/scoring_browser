#
# scoring_browser --- Simple Qt application for browsing
# scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek
# (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from slice_tab import SliceTab

from PyQt4 import QtGui, QtCore
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   # Needed to enable 3D plotting
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class ChartTab(SliceTab):
    def __init__(self, parent):
        SliceTab.__init__(self, parent)

        self.is_3d = False

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)

        self.threeDCheckBox = QtGui.QCheckBox("3D")
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.threeDCheckBox)

        self.options = {
            "contour_labels" : True
        }

        for signal in self.all_model_signals:
            signal.connect(self.update_chart)
        self.threeDCheckBox.stateChanged.connect(self.on_3D_check_box_change)

        if hasattr(parent, "options_menu"):
            parent.options_menu.addAction('&Chart Options', self.show_options_dialog)   

        self.update_chart()

    def show_options_dialog(self):
        dialog = ChartOptionsDialog(self)
        dialog.show()

    def on_3D_check_box_change(self, state):
        self.is_3d = (state == QtCore.Qt.Checked)
        self.update_chart()

    def _plot_2d(self, X, Y, Z):
        axes = self.figure.add_subplot(111)

        contours = self.options.get("contours", 5)

        cs = axes.contour(Y, X, Z, contours)
        axes.set_ylim(reversed(axes.get_ylim()))

        axes.set_xlabel(self.slice.plane_name[0])
        axes.set_ylabel(self.slice.plane_name[1])

        if self.options.get("contour_labels"):
            axes.clabel(cs, fontsize=9, inline=1)

    def _plot_3d(self, X, Y, Z):
        axes = self.figure.add_subplot(111, projection='3d')
        plot = axes.plot_surface(X, Y, Z, rstride=1, cstride=1,
                                 cmap=matplotlib.cm.coolwarm, linewidth=0,
                                 antialiased=False)
        self.figure.colorbar(plot, shrink=0.5)

        axes.set_xlabel(self.slice.plane_name[1])
        axes.set_ylabel(self.slice.plane_name[0])

    def update_chart(self):
        self.figure.clear()
        if self.matrix:
            x = np.arange(self.slice.shape[1])
            y = np.arange(self.slice.shape[0])
            X, Y = np.meshgrid(x, y)

            if self.is_3d:
                self._plot_3d(X, Y, self.slice.data)
            else:
                self._plot_2d(X, Y, self.slice.data)
        self.canvas.draw()

class ChartOptionsDialog(QtGui.QDialog):
    def __init__(self, parent):
        def onSaveClicked():
            parent.options["contours"] = [float(s) for s in contours_text.text().split(" ")]
            # print parent.options
            parent.update_chart()
            self.close()

        super(ChartOptionsDialog, self).__init__(parent)
        self.setWindowTitle("Chart Options")
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)        

        # Contours
        contours_text = QtGui.QLineEdit()
        if 'contours' in parent.options:
            contours_text.setText(" ".join((str(contour) for contour in parent.options["contours"])))

        layout.addWidget(QtGui.QLabel("Contours (space-separated)"))
        layout.addWidget(contours_text)

        button = QtGui.QPushButton("Save")
        button.clicked.connect(onSaveClicked)
        layout.addWidget(button)


        # dialog = QtGui.QDialog(self)
        # dialog.setWindowTitle("Reduce Matrix")

        # layout = QtGui.QVBoxLayout()
        # dialog.setLayout(layout)

        # xtext = QtGui.QLineEdit()
        # ytext = QtGui.QLineEdit()
        # ztext = QtGui.QLineEdit()

        # layout.addWidget(QtGui.QLabel("Reduction in X Axis"))
        # layout.addWidget(xtext)

        # layout.addWidget(QtGui.QLabel("Reduction in Y Axis"))
        # layout.addWidget(ytext)

        # layout.addWidget(QtGui.QLabel("Reduction in Z Axis"))
        # layout.addWidget(ztext)

        # def onButtonClick():
        #     try:
        #         x = int(xtext.text())
        #         y = int(ytext.text())
        #         z = int(ztext.text())
        #         matrix = self.matrix.reduced((x, y, z))
        #         self.set_matrix(matrix)
        #         dialog.close()
        #     except ValueError:
        #         pass

        # button = QtGui.QPushButton("Proceed")
        # button.clicked.connect(onButtonClick)

        # layout.addWidget(button)

        # dialog.show()
        # self.set_matrix(self.matrix.copy())  # ???