#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from PyQt4 import QtGui
import math

from slice_tab import SliceTab

""" Tab with the data table """
class TableTab(SliceTab):
    def __init__(self, parent):
        SliceTab.__init__(self, parent)
        
        self.table = QtGui.QTableWidget()
        self.table.itemSelectionChanged.connect( self.update_statistics )
        self.table.itemChanged.connect( self.on_item_changed )
        self.layout.addWidget( self.table )

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

    def update_cell(self, column, row):
        '''Set value and formatting of a single cell.'''
        relativeValue = self.getCellValue( column, row, relative=True)
        value = self.getCellValue( column, row, relative=False)
        cellWidget = QtGui.QTableWidgetItem()
        if self.relative:
            cellWidget.setText( str(relativeValue) )
        else:
            cellWidget.setText( str(value) )    
        cellWidget.setData( 32, value )
        color = QtGui.QColor()
        color.setHslF( 1.0, 1.0, 1.0 - relativeValue)
        cellWidget.setBackground( color )
        if relativeValue > 0.33:
            cellWidget.setForeground( QtGui.QColor( 255, 255, 255) )
        else:
            cellWidget.setForeground( QtGui.QColor( 32, 32, 32) )
        # cellWidget.palette = QtGui.QPalette( color )
        self.table.setItem(row, column, cellWidget )    

    def format_number( self, number ):
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

    def update_statistics( self ):
        '''Fill status bar with interesting statistics about selected values.'''
        data = [ self.getCellValue(i.column(), i.row()) for i in self.table.selectedIndexes() ]

        n = len(data)
        total = sum(data)
        text = "count = {}".format(n)
        text += ", total = %s" % self.format_number(total)
        if n > 1:
            mean = total / n
            maximum = max(data)
            minimum = min(data)
            text += ", min = %s" % self.format_number(minimum)
            text += ", mean = %s" % self.format_number(mean)
            text += ", max = %s" % self.format_number(maximum)
            sum_square = sum(( (value - mean) ** 2 for value in data ))
            stddev = math.sqrt( sum_square / (n - 1) )
            text += ", stdev = %s" % self.format_number(stddev)
        self.parent.set_status(text)
        
    def update_table(self):
        if self.matrix:
            self.table.setColumnCount( self.slice.shape[0] ) #self.column_count
            self.table.setRowCount( self.slice.shape[1]) # self.row_count)
            
            for row in range(0, self.row_count ):
                self.table.setVerticalHeaderItem( row, QtGui.QTableWidgetItem( self.slice.plane_name[1] + " = " + str(row) ))
            self.table.setVerticalHeaderItem( self.row_count, QtGui.QTableWidgetItem("Total"))

            for column in range(0, self.column_count ):
                self.table.setHorizontalHeaderItem( column, QtGui.QTableWidgetItem( self.slice.plane_name[0] + " = " + str(column) ))
                for row in range(0, self.row_count ):
                    self.update_cell(column, row)                    
        else:
            self.table.setColumnCount( 1 )
            self.table.setRowCount( 1 )
            self.table.setItem(0, 0, QtGui.QTableWidgetItem( "No data." ) ) 
            self.table.setVerticalHeaderItem( 0, QtGui.QTableWidgetItem( "-" ))
            self.table.setHorizontalHeaderItem( 0, QtGui.QTableWidgetItem( "-" ))
        self.table.update()
        
    def write_csv(self, fileName):
        if self.matrix:
            with open(fileName, "w") as f:
                for row in range(0, self.row_count ):
                    for column in range(0, self.column_count ):
                        f.write( str( self.getCellValue( column, row, self.relative ) ) )
                        f.write(",")
                    f.write( "\n" ) 