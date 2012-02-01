#!/usr/bin/env python
#
# Copyright (C) 2012 Jan Pipek (jan.pipek@gmail.com)
# 
# This file may be distributed without limitation.

import sys, re, numpy
from PyQt4 import QtGui, QtCore

COMPANY = "Jan Pipek"
APP_NAME = "scoring_browser"

class DataMatrix:
	def __init__(self, source):
		points = []
		linePattern = re.compile("(\d+),(\d+),(\d+),([0-9.]*)")
		
		for line in source.splitlines():
			match = linePattern.match( line )
			if match:
				x = int( match.group(1) )
				y = int( match.group(2) )
				z = int( match.group(3) )
				val = float( match.group(4) )
				points.append( [x, y, z, val] )
			
		self.sizeX = max( points, key = lambda l: l[0] )[0] + 1
		self.sizeY = max( points, key = lambda l: l[1] )[1] + 1
		self.sizeZ = max( points, key = lambda l: l[2] )[2] + 1
		self.maxValue = max( points, key = lambda l: l[3] )[3]
		
		if len( points ) != self.getSize():
			# Incomplete file probably
			# throw error
			pass
		
		self.matrix = numpy.ndarray( shape = (self.sizeX, self.sizeY, self.sizeZ), dtype=float )
		for p in points:
			self.matrix[p[0], p[1], p[2]] = p[3]

	def getName(self):
		return self.name
	
	def valueAt(self, x, y, z):
		return self.matrix[x, y, z]
		
	def relativeValueAt(self, x, y, z):
		return self.matrix[x, y, z] / self.maxValue
		
	def getSize(self):
		return self.sizeX * self.sizeY + self.sizeZ
		
	def getSizeX(self):
		return self.sizeX
	
	def getSizeY(self):
		return self.sizeY
	
	def getSizeZ(self):
		return self.sizeZ
		
	def getMaxValue(self):
		return self.maxValue

class Plot2DTab(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__( self )

class EditTab(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__( self )
		layout =  QtGui.QVBoxLayout( self )
		self.textEdit = QtGui.QTextEdit() 
		self.textEdit.setReadOnly( True )
		layout.addWidget( self.textEdit )
	
	def setText(self, text):
		self.textEdit.setText( text )
		
class TableTab(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__( self )
		layout =  QtGui.QVBoxLayout( self )
		self.setLayout( layout )
		
		self.table = QtGui.QTableWidget()
		
		self.toolBar = QtGui.QToolBar()
		
		self.relativeCheckBox = QtGui.QCheckBox( "Relative" )
		self.relativeCheckBox.stateChanged.connect( self.onRelativeCheckBoxChanged )
		
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
		
		self.xyRadio.toggled.connect( lambda t: t and self.setPlane("xy"))
		self.yzRadio.toggled.connect( lambda t: t and self.setPlane("yz"))
		self.xzRadio.toggled.connect( lambda t: t and self.setPlane("xz"))
		
		self.toolBar.addWidget( self.xyRadio )
		self.toolBar.addWidget( self.yzRadio )
		self.toolBar.addWidget( self.xzRadio )
		
		
		self.toolBar.addSeparator()
		
		
		self.slider = QtGui.QSlider( QtCore.Qt.Horizontal )
		self.slider.valueChanged.connect( self.onSliderValueChanged )
		
		self.toolBar.addWidget( self.slider )
		
		self.zValueLabel = QtGui.QLabel()
		self.toolBar.addWidget( self.zValueLabel )
		
		# w.setLayout( vLayout)
		
		layout.addWidget( self.toolBar )
		layout.addWidget( self.table )
	
		self.z = 0
		self.relative = False
		self.matrix = None
		self.setPlane( "xy" )		
		
	def onSliderValueChanged(self, value):
		self.z = value
		self.updateSlider()
		self.updateTable()
		
	def updateSlider(self):
		if self.matrix:
			self.slider.setMaximum( self.getPlaneCount() - 1)
			self.zValueLabel.setText( self.axis + " = " + str( self.z ) )
		else:
			self.slider.setMaximum( 0 )
			self.zValueLabel.setText( self.axis + " = " + str( 0 ) )
		
	def onRelativeCheckBoxChanged(self, state ):
		if state == QtCore.Qt.Checked:
			self.relative = True
		else:
			self.relative = False
		self.updateTable()
		
	def setPlane(self, plane):
		self.plane = plane
		# self.z = 0
		if self.plane == "xy":
			self.axis = "z"
		elif self.plane == "yz":
			self.axis = "x"
		else:
			self.axis = "y"
		self.updateSlider()
		self.updateTable()
			
	def horizontalAxis(self):
		return self.plane[0]
	
	def verticalAxis(self):
		return self.plane[1]
		
	def getRowCount(self):
		if self.plane == "xy":
			return self.matrix.getSizeY()
		else:
			return self.matrix.getSizeZ()
		
	def getColumnCount(self):
		if self.plane == "yz":
			return self.matrix.getSizeY()
		else:
			return self.matrix.getSizeX()
			
	def getPlaneCount(self):
		if self.plane == "xy":
			return self.matrix.getSizeZ()
		elif self.plane == "yz":
			return self.matrix.getSizeX()
		else:
			return self.matrix.getSizeY()			
		
	def updateCell(self, column, row):
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
		relativeValue = self.matrix.relativeValueAt(x, y, z)
		value = self.matrix.valueAt(x, y, z)
		cellWidget = QtGui.QTableWidgetItem()
		if self.relative:
			cellWidget.setText( str(relativeValue) )
		else:
			cellWidget.setText( str(value) )	
		color = QtGui.QColor()
		color.setHslF( 1.0, 1.0, 1.0 - relativeValue)
		cellWidget.setBackground( color )
		if relativeValue > 0.33:
			cellWidget.setForeground( QtGui.QColor( 255, 255, 255) )
		# cellWidget.palette = QtGui.QPalette( color )
		self.table.setItem(row, column, cellWidget )	
		
		
	def updateTable(self):
		if self.matrix:
			self.table.setColumnCount( self.getColumnCount() )
			self.table.setRowCount( self.getRowCount() )
			
			for row in range(0, self.getRowCount() ):
				self.table.setVerticalHeaderItem( row, QtGui.QTableWidgetItem( self.verticalAxis() + " = " + str(row) ))
			
			for column in range(0, self.getColumnCount() ):
				self.table.setHorizontalHeaderItem( column, QtGui.QTableWidgetItem( self.horizontalAxis() + " = " + str(column) ))
				
				for row in range(0, self.getRowCount() ):
					self.updateCell(column, row)
					
		else:
			self.table.setColumnCount( 1 )
			self.table.setRowCount( 1 )
			self.table.setItem(0, 0, QtGui.QTableWidgetItem( "No data." ) )	

		
	def setMatrix(self, matrix):
		self.matrix = matrix
		self.updateTable()
		self.updateSlider()

class ApplicationWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.tabs = QtGui.QTabWidget(self)
		
		self.tableTab = TableTab()
		self.tabs.addTab(self.tableTab, "Data Table")
		self.tableTab.setMatrix( None )		
		
		self.plot2DTab = Plot2DTab()
		# self.tabs.addTab(self.plot2DTab, "2D Plot")
		
		self.editTab = EditTab()
		self.tabs.addTab(self.editTab, "Source")

		self.setCentralWidget( self.tabs )
		self.setWindowTitle("Scoring Output Browser")
		
		self.buildMenu()
		
		self.setStatus("Ready")
		self.restoreSettings()
		
	def buildMenu(self):
		self.file_menu = QtGui.QMenu('&File', self)
		self.file_menu.addAction('&Open', self.openFile, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
		self.file_menu.addAction('&Quit', self.close, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
		self.menuBar().addMenu(self.file_menu)
		
	def setMatrix(self, matrix):
		self.matrix = matrix
		self.tableTab.setMatrix( matrix )
		
	def openFile(self):
		fileName = QtGui.QFileDialog.getOpenFileName(self, "Select Data File")
		self.readFile(fileName)
	
	def readFile(self, fileName):
		self.setStatus( "Opening " + fileName + "...")
		try:
			with open(fileName) as f:
				text = f.read()
				self.editTab.setText( text )
				matrix = DataMatrix( text )
			self.setStatus( "Successfully read " + fileName )
			self.setWindowTitle("Scoring Output Browser (" + fileName + ")")
		except:
			matrix = None			
			self.setStatus( "Error reading file." )
		self.setMatrix( matrix )
	
	""" Display a status message """
	def setStatus(self, text):
		self.statusBar().showMessage(text)
		
	def closeEvent( self, event):
		 settings = QtCore.QSettings(COMPANY, APP_NAME);
		 settings.setValue("window/geometry", self.saveGeometry());
		 settings.setValue("window/state", self.saveState());
		 QtGui.QMainWindow.closeEvent(self, event);
	
	""" Restore settings about window geometry from the saved settings"""
	def restoreSettings( self ):
		try:
			settings = QtCore.QSettings(COMPANY, APP_NAME);
			self.restoreGeometry(settings.value("window/geometry"))
			self.restoreState(settings.value("window/state"))
		except:
			pass
		
qApp = QtGui.QApplication(sys.argv)
window = ApplicationWindow()
window.show()

if len( sys.argv ) == 2:
	window.readFile( sys.argv[1] )

sys.exit(qApp.exec_())
