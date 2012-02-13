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
        if not source:
            pass
        else:
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
            
    def __add__(self, other):
        pass
        
    def __sub__(self, other):
        pass

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
