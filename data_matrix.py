#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
import re, numpy

class DataMatrix:
    def __init__(self, source=None):
        if source == None:
            pass
        elif isinstance(source, numpy.ndarray):
            self.matrix = source
        else:
            points = []
            linePattern = re.compile("(\d+),(\d+),(\d+),([0-9.e\-]*)")
            
            for line in source.splitlines():
                match = linePattern.match( line )
                if match:
                    x = int( match.group(1) )
                    y = int( match.group(2) )
                    z = int( match.group(3) )
                    val = float( match.group(4) )
                    points.append( [x, y, z, val] )
                
            sizeX = max( points, key = lambda l: l[0] )[0] + 1
            sizeY = max( points, key = lambda l: l[1] )[1] + 1
            sizeZ = max( points, key = lambda l: l[2] )[2] + 1
            
            self.matrix = numpy.ndarray( shape = (sizeX, sizeY, sizeZ), dtype=float )
            if len( points ) != self.getSize():
                raise Exception("Incomplete file")
            
            for p in points:
                self.matrix[p[0], p[1], p[2]] = p[3]
    
    @staticmethod
    def fromFile(fileName):
        with open(fileName) as f:
            text = f.read()
            return DataMatrix( text )
            
    def __add__(self, other):
        return DataMatrix( self.matrix + other.matrix )
        
    def __sub__(self, other):
        return DataMatrix( self.matrix - other.matrix )

    def getName(self):
        return self.name
    
    def valueAt(self, x, y, z):
        return self.matrix[x, y, z]
        
    def relativeValueAt(self, x, y, z):
        return self.relative().valueAt(x, y, z)
        
    def getSize(self):
        return self.matrix.size
        
    def getSizeX(self):
        return self.matrix.shape[0]
    
    def getSizeY(self):
        return self.matrix.shape[1]
    
    def getSizeZ(self):
        return self.matrix.shape[2]
        
    def getMaxValue(self):
        if not hasattr(self, "_maxValue"):
            self._maxValue = self.matrix.max()
        return self._maxValue

    def allowedReductions(self):
        """ Tuple of possible reductions in all dimensions (i.e. factors of size along the axis) """
        return (
            (i for i in range(1, self.getSizeX() + 1 ) if self.getSizeX() % i == 0),
            (i for i in range(1, self.getSizeY() + 1 ) if self.getSizeY() % i == 0),
            (i for i in range(1, self.getSizeZ() + 1 ) if self.getSizeZ() % i == 0)
        )

    def relative(self):
        """ Matrix with all values relative (normalized to the largest element) """
        if not hasattr( self, "_relative"):
            self._relative = DataMatrix(self.matrix / self.getMaxValue())
        return self._relative

    def reduce(self, indices = (1, 1, 1)):
        """ New matrix with reduced dimensions (each x,y,z-element box is replaced with one element) """
        allowed = self.allowedReductions()
        if not all( [(indices[i] in allowed[i]) for i in range(0, 3)]):
            raise ValueError("Wrong index")
        new_array = numpy.ndarray( shape = (self.getSizeX() / indices[0], self.getSizeY() / indices[1], self.getSizeZ() / indices[2]), dtype=float )
        for x in range(0, new_array.shape[0]):
            for y in range(0, new_array.shape[1]):
                for z in range(0, new_array.shape[2]):
                    x0 = x * indices[0]; x1 = x0 + indices[0]
                    y0 = y * indices[1]; y1 = y0 + indices[1]
                    z0 = z * indices[2]; z1 = z0 + indices[2]
                    new_array[x, y, z] = ( self.matrix[ x0:x1, y0:y1, z0:z1 ].sum())
        return DataMatrix(new_array)