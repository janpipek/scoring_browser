#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
from PyQt4 import QtGui, QtCore
from data_matrix import DataMatrixSlice2D

class SliceTab(QtGui.QWidget):
    matrix_changed = QtCore.pyqtSignal(name='matrixChanged')
    plane_changed = QtCore.pyqtSignal(name='planeChanged')
    slice_index_changed = QtCore.pyqtSignal(name='sliceIndexChanged')
    relative_changed = QtCore.pyqtSignal(name='relativeChanged')

    def __init__(self, parent):
        # Initialize
        self.parent = parent
        QtGui.QWidget.__init__( self )

        # Set matrix
        self._matrix = None
        self._slice_index = 0
        self._plane = "xy"
        self._relative = False

        self.initialize_ui()

    @property
    def all_model_signals(self):
        return (self.matrix_changed, self.plane_changed,
            self.slice_index_changed, self.relative_changed)

    def initialize_ui(self):
        # More GUI
        self.layout = QtGui.QVBoxLayout( self )
        self.setLayout( self.layout )

        self.toolBar = QtGui.QToolBar()
        
        self.relativeCheckBox = QtGui.QCheckBox( "Relative Values" ) 
        
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
        
        self.toolBar.addWidget( self.xyRadio )
        self.toolBar.addWidget( self.yzRadio )
        self.toolBar.addWidget( self.xzRadio )
        
        self.toolBar.addSeparator()
        
        self.sliceIndexSlider = QtGui.QSlider( QtCore.Qt.Horizontal )
        self.sliceIndexSlider.setPageStep( 1 )
        
        
        self.toolBar.addWidget( self.sliceIndexSlider )
        
        self.sliceIndexLabel = QtGui.QLabel()
        self.toolBar.addWidget( self.sliceIndexLabel )

        self.layout.addWidget( self.toolBar )

        # Helper function for radio buttons signals
        def set_plane(plane):
            def _set_plane(t):
                if t:
                    self.plane = plane
            return _set_plane

        # Connect all signals
        self.xyRadio.toggled.connect(set_plane("xy"))
        self.yzRadio.toggled.connect(set_plane("yz"))
        self.xzRadio.toggled.connect(set_plane("xz")) 
        self.relativeCheckBox.stateChanged.connect( self.on_relative_checkbox_changed )
        self.sliceIndexSlider.valueChanged.connect( self.on_slider_value_changed )

        for signal in self.all_model_signals:
            signal.connect(self.update_slider)

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        if self._matrix != value:
            self._matrix = value
            self.matrix_changed.emit()

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, value):
        if self._plane != value:
            self._plane = value
            self.plane_changed.emit()

    @property
    def slice_index(self):
        return self._slice_index

    @slice_index.setter
    def slice_index(self, value):
        if self._slice_index != value:
            self._slice_index = value
            self.slice_index_changed.emit()

    @property
    def relative(self):
        return self._relative

    @relative.setter
    def relative(self, value):
        if self._relative != value:
            self._relative = value
            self.relative_changed.emit()
        
    @property
    def column_count(self):
        return self.slice.shape[0]

    @property
    def row_count(self):
        return self.slice.shape[1]
           
    @property 
    def plane_count(self):
        return self.matrix.shape[self.slice.axis]

    @property
    def slice(self):
        return DataMatrixSlice2D(self.matrix, self.plane, self.slice_index)   

    def on_slider_value_changed(self, value):
        self.slice_index = value

    def on_relative_checkbox_changed(self, state):
        self.relative = (state == QtCore.Qt.Checked)

    def update_slider(self):
        if self.matrix:
            plane_count = self.plane_count #self.matrix.shape[self.slice.axis]
            self.sliceIndexSlider.setMaximum(plane_count - 1)
            if self.slice_index >= plane_count:
                self.slice_index = plane_count - 1            
            self.sliceIndexLabel.setText( self.slice.axis_name + " = " + str( self.slice_index ) )
        else:
            self.sliceIndexSlider.setMaximum( 0 )
            self.slice_index = 0            
            self.sliceIndexLabel.setText( self.slice.axis_name + " = " + str( 0 ) )     