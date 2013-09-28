#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from PyQt4 import QtGui, QtCore

from data_matrix import DataMatrix
import math

""" Tab displaying the file source """
class SourceTab(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__( self )
        layout =  QtGui.QVBoxLayout( self )
        self.textEdit = QtGui.QTextEdit() 
        self.textEdit.setReadOnly( True )
        layout.addWidget( self.textEdit )
    
    def setText(self, text):
        self.textEdit.setText( text )
        
""" Tab with the data table """
class TableTab(QtGui.QWidget):
    def __init__(self, parent):
        self.parent = parent

        QtGui.QWidget.__init__( self )
        layout =  QtGui.QVBoxLayout( self )
        self.setLayout( layout )
        
        self.table = QtGui.QTableWidget()
        self.table.itemSelectionChanged.connect( self.update_statistics )
        
        self.toolBar = QtGui.QToolBar()
        
        self.relativeCheckBox = QtGui.QCheckBox( "Relative Values" )
        self.relativeCheckBox.stateChanged.connect( self.on_relative_checkbox_changed )
        
        self.toolBar.addWidget( self.relativeCheckBox )
        
        self.toolBar.addSeparator()
        
        self.toolBar.addWidget( QtGui.QLabel("Plane: ") )
        
        buttonGroup = QtGui.QButtonGroup()
        
        self.xyRadio = QtGui.QRadioButton("XY")
        self.xyRadio.setChecked( True )
        
        self.yzRadio = QtGui.QRadioButton("YZ")
        self.xzRadio = QtGui.QRadioButton("XZ")
        
        buttonGroup.addButton( self.xyRadio )
        buttonGroup.addButton( self.yzRadio )
        buttonGroup.addButton( self.xzRadio )
        
        self.xyRadio.toggled.connect( lambda t: t and self.set_plane("xy"))
        self.yzRadio.toggled.connect( lambda t: t and self.set_plane("yz"))
        self.xzRadio.toggled.connect( lambda t: t and self.set_plane("xz"))
        
        self.toolBar.addWidget( self.xyRadio )
        self.toolBar.addWidget( self.yzRadio )
        self.toolBar.addWidget( self.xzRadio )
        
        
        self.toolBar.addSeparator()
        
        
        self.slider = QtGui.QSlider( QtCore.Qt.Horizontal )
        self.slider.setPageStep( 1 )
        self.slider.valueChanged.connect( self.on_slider_value_changed )
        
        self.toolBar.addWidget( self.slider )
        
        self.zValueLabel = QtGui.QLabel()
        self.toolBar.addWidget( self.zValueLabel )
        
        # w.setLayout( vLayout)
        
        layout.addWidget( self.toolBar )
        layout.addWidget( self.table )
    
        self.z = 0
        self.relative = False
        self.matrix = None
        self.set_plane( "xy" )       
        
    def on_slider_value_changed(self, value):
        self.z = value
        self.update_slider()
        self.update_table()
        self.update_statistics()
        
    def update_slider(self):
        if self.matrix:
            self.slider.setMaximum( self.plane_count - 1)
            self.zValueLabel.setText( self.axis + " = " + str( self.z ) )
        else:
            self.slider.setMaximum( 0 )
            self.zValueLabel.setText( self.axis + " = " + str( 0 ) )
        
    def on_relative_checkbox_changed(self, state ):
        if state == QtCore.Qt.Checked:
            self.relative = True
        else:
            self.relative = False
        self.update_table()
        
    def set_plane(self, plane):
        self.plane = plane
        # self.z = 0
        if self.plane == "xy":
            self.axis = "z"
        elif self.plane == "yz":
            self.axis = "x"
        else:
            self.axis = "y"
        self.update_slider()
        self.update_table()
    
    @property
    def horizontal_axis(self):
        return self.plane[0]
    
    @property
    def vertical_axis(self):
        return self.plane[1]
        
    @property
    def row_count(self):
        if self.plane == "xy":
            return self.matrix.size_y
        else:
            return self.matrix.size_z
        
    @property
    def column_count(self):
        if self.plane == "yz":
            return self.matrix.size_y
        else:
            return self.matrix.size_x
           
    @property 
    def plane_count(self):
        if self.plane == "xy":
            return self.matrix.size_z
        elif self.plane == "yz":
            return self.matrix.size_x
        else:
            return self.matrix.size_y           
    
    def getCellValue(self, column, row, relative=False):
        '''Get value for the table row & column.

        Takes into account table orientation.
        '''
        if self.plane == "xy":
            x = column
            y = row
            z = self.z
        elif self.plane == "yz":
            x = self.z
            y = column
            z = row
        elif self.plane == "xz":
            x = column
            y = self.z 
            z = row
        if relative:
            return self.matrix.relative_value_at(x, y, z)
        else:
            return self.matrix.value_at(x, y, z)

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
            self.table.setColumnCount( self.column_count )
            self.table.setRowCount( self.row_count)
            
            for row in range(0, self.row_count ):
                self.table.setVerticalHeaderItem( row, QtGui.QTableWidgetItem( self.vertical_axis + " = " + str(row) ))
            self.table.setVerticalHeaderItem( self.row_count, QtGui.QTableWidgetItem("Total"))

            for column in range(0, self.column_count ):
                self.table.setHorizontalHeaderItem( column, QtGui.QTableWidgetItem( self.horizontal_axis + " = " + str(column) ))
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
                        
        
    def set_matrix(self, matrix):
        self.matrix = matrix
        if matrix == None:
            self.z = 0
        elif self.z >= self.plane_count:
            self.z = self.plane_count - 1
        self.update_table()
        self.update_slider()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.tabs = QtGui.QTabWidget(self)
        
        self.tableTab = TableTab(self)
        self.tabs.addTab(self.tableTab, "Data Table")
        self.tableTab.set_matrix( None )     
        
        self.sourceTab = SourceTab()
        self.tabs.addTab(self.sourceTab, "Source")

        self.setCentralWidget( self.tabs )
        self.setWindowTitle("Scoring Output Browser")
        
        self.build_menu()
        
        self.set_status("Ready")
        self.restore_settings()
        
    def build_menu(self):
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.open_file, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.close, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('E&xport Table as CSV', self.export_csv, QtCore.Qt.CTRL + QtCore.Qt.Key_X)
        self.menuBar().addMenu(self.file_menu)

        self.tools_menu = QtGui.QMenu('&Tools', self)
        self.tools_menu.addAction('&Reduce Matrix', self.show_reduction_dialog, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.tools_menu)
        
    def set_matrix(self, matrix):
        self.matrix = matrix
        self.tableTab.set_matrix( matrix )

    def show_reduction_dialog( self ):
        dialog = QtGui.QDialog( self )
        dialog.setWindowTitle("Reduce Matrix")

        layout = QtGui.QVBoxLayout()
        dialog.setLayout( layout )

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
                matrix = self.matrix.reduce((x, y, z))
                self.set_matrix( matrix )
                dialog.close()
            except ValueError:
                pass

        button = QtGui.QPushButton("Proceed")
        button.clicked.connect( onButtonClick )      
        
        layout.addWidget(button)

        dialog.show()
        self.set_matrix( DataMatrix( self.matrix.matrix ) )
    
    def open_file(self):
        """ Invoke file open dialog and read the selected file """  
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select Data File")
        if fileName:
            self.read_file(fileName)     

    def export_csv(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Select CSV File")
        if fileName:
            self.tableTab.write_csv( fileName )
    
    def read_file(self, fileName):
        self.set_status( "Opening " + fileName + "...")
    #try:
        with open(fileName) as f:
            text = f.read()
            self.sourceTab.setText( text )
            matrix = DataMatrix( text )
        self.set_status( "Successfully read " + fileName )
        self.setWindowTitle("Scoring Output Browser (" + fileName + ")")
    #except:
        # matrix = None           
        # self.set_status( "Error reading file." )
        self.set_matrix( matrix )
    
    def set_status(self, text):
        """ Display a status message """
        self.statusBar().showMessage(text)
        
    def closeEvent( self, event):
         settings = QtCore.QSettings();
         settings.setValue("window/geometry", self.saveGeometry())
         settings.setValue("window/state", self.saveState())
         QtGui.QMainWindow.closeEvent(self, event)
    
    def restore_settings( self ):
        """ Restore settings about window geometry from the saved settings"""
        try:
            settings = QtCore.QSettings()
            self.restoreGeometry(settings.value("window/geometry"))
            self.restoreState(settings.value("window/state"))
        except:
            pass
