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
import math
import numpy as np

from slice_tab import SliceTab


class TableTab(SliceTab):
    """ Tab with the data table """
    def __init__(self, parent):
        SliceTab.__init__(self, parent)

        self.table = QtGui.QTableWidget()
        self.table.itemSelectionChanged.connect(self.update_statistics)
        self.table.itemChanged.connect(self.on_item_changed)
        self.layout.addWidget(self.table)

        self.options = {
            "notation" : "normal",   # normal | scientific
            "digits" : 5
        }

        for signal in self.all_model_signals:
            signal.connect(self.update_table)
            signal.connect(self.update_statistics)

    def on_item_changed(self, item):
        # TODO: Implement
        pass

    def getCellValue(self, column, row, relative=False):
        '''Get value for the table row & column.

        Takes into account table orientation.
        '''
        index = self.slice.real_index(column, row)
        if relative:
            return self.matrix.relative_value_at(*index)
        else:
            return self.matrix.value_at(*index)

    def format_value(self, value):
        digits = self.options.get("digits", 5)
        if self.options.get("notation", "normal") == "scientific":
            return ("{:." + str(digits) + "e}").format(value)
        else:
            return ("{:." + str(digits) + "f}").format(value)

    def update_cell(self, column, row):
        '''Set value and formatting of a single cell.'''
        relativeValue = self.getCellValue(column, row, relative=True)
        value = self.getCellValue(column, row, relative=False)
        cellWidget = QtGui.QTableWidgetItem()
        if self.relative:
            cellWidget.setText(self.format_value(relativeValue))
            cellWidget.setToolTip(str(relativeValue))
        else:
            cellWidget.setText(self.format_value(value))
            cellWidget.setToolTip(str(value))
        cellWidget.setData(32, value)
        color = QtGui.QColor()
        if np.isnan(relativeValue):
            color.setRgbF(1.0, 1.0, 0.0)
        else:
            if relativeValue > 0:
                color.setHslF(1.0, 1.0, 1.0 - relativeValue)
            else:
                color.setHslF(0.66, 1.0, 1.0 - abs(relativeValue))
            if abs(relativeValue) > 0.33:
                cellWidget.setForeground(QtGui.QColor(255, 255, 255))
            else:
                cellWidget.setForeground(QtGui.QColor(32, 32, 32))
        cellWidget.setBackground(color)
        
        # cellWidget.palette = QtGui.QPalette(color)
        self.table.setItem(row, column, cellWidget)

    def format_stats_number(self, number):
        if number > 10:
            return "{:.1f}".format(number)
        elif number > 1:
            return "{:.2f}".format(number)
        elif number > 0.1:
            return "{:.3f}".format(number)
        elif number > 0.01:
            return "{:.4f}".format(number)
        else:
            return "{:.3e}".format(number)

    def update_statistics(self):
        '''Fill status bar with interesting statistics.

        The statistics summarize selected cells.'''
        data = [self.getCellValue(i.column(), i.row())
                for i in self.table.selectedIndexes()]

        n = len(data)
        total = sum(data)
        text = "count = {}".format(n)
        text += ", total = %s" % self.format_stats_number(total)
        if n > 1:
            mean = total / n
            maximum = max(data)
            minimum = min(data)
            text += ", min = %s" % self.format_stats_number(minimum)
            text += ", mean = %s" % self.format_stats_number(mean)
            text += ", max = %s" % self.format_stats_number(maximum)
            sum_square = sum(((value - mean) ** 2 for value in data))
            stddev = math.sqrt(sum_square / (n - 1))
            text += ", stdev = %s" % self.format_stats_number(stddev)
        self.parent.set_status(text)

    def update_table(self):
        if self.matrix:
            self.table.setColumnCount(self.column_count)
            self.table.setRowCount(self.row_count)

            for row in range(0, self.row_count):
                self.table.setVerticalHeaderItem(
                    row,
                    QtGui.QTableWidgetItem(
                        self.slice.plane_name[1] + " = " + str(row)))
            self.table.setVerticalHeaderItem(self.row_count,
                                             QtGui.QTableWidgetItem("Total"))

            for column in range(0, self.column_count):
                self.table.setHorizontalHeaderItem(
                    column,
                    QtGui.QTableWidgetItem(
                        self.slice.plane_name[0] + " = " + str(column)))
                for row in range(0, self.row_count):
                    self.update_cell(column, row)
        else:
            self.table.setColumnCount(1)
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QtGui.QTableWidgetItem("No data."))
            self.table.setVerticalHeaderItem(0, QtGui.QTableWidgetItem("-"))
            self.table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("-"))
        self.table.update()

    def write_csv(self, fileName):
        if self.matrix:
            with open(fileName, "w") as f:
                for row in range(0, self.row_count):
                    for column in range(0, self.column_count):
                        f.write(str(self.getCellValue(column,
                                                      row, self.relative)))
                        f.write(",")
                    f.write("\n")
