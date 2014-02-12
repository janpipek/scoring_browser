#
# scoring_browser --- Simple Qt application for browsing scoring outputs in Geant4
#
# Copyright (C) 2012 Jan Pipek (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
import re, numpy

class DataMatrix:
    """A 3D matrix with data.

    Based on numpy ndarray + a few more methods.
    It can be built from the scoring files made command-based
    Geant4 scoring (either a string of from_file method).

    The indexing is (mostly) forwarded to the inner numpy array.
    
    * DataMatrix.relative provides a copy of the matrix scaled
    relative to the maximum value (it is stored in the matrix
    after first requested).
    
    * DataMatrix.reduced returns a copy of the matrix with values summed
    over volumes of defined size (if division is possible).
    """
    def __init__(self, source=None, header=None):
        self.header = ""
        if source == None:
            pass
        elif isinstance(source, numpy.ndarray):
            self.data_array = source
        else:
            points = []
            linePattern = re.compile("(\d+),(\d+),(\d+),([0-9.e\-]*)")
            commentLinePattern = re.compile("#.*")
            
            for line in source.splitlines():
                match = linePattern.match( line )
                if match:
                    x = int( match.group(1) )
                    y = int( match.group(2) )
                    z = int( match.group(3) )
                    val = float( match.group(4) )
                    points.append( [x, y, z, val] )

                match = commentLinePattern.match( line )
                if match:
                    self.header += line + "\n"
                
            sizeX = max( l[0] for l in points ) + 1 #, key = lambda l: l[0] )[0] + 1
            sizeY = max( points, key = lambda l: l[1] )[1] + 1
            sizeZ = max( points, key = lambda l: l[2] )[2] + 1
            
            self.data_array = numpy.ndarray( shape = (sizeX, sizeY, sizeZ), dtype=float )
            if len( points ) != self.size:
                raise Exception("Incomplete file")
            
            for p in points:
                self.data_array[p[0], p[1], p[2]] = p[3]
        if header:
            self.header = header
    
    @staticmethod
    def from_file(file_name):
        """Read the matrix from scoring file."""
        with open(file_name) as f:
            text = f.read()
            return DataMatrix( text )

    def to_file(self, file):
        """Write the matrix to a scoring file."""
        file.write(self.header)
            
    def __add__(self, other):
        return DataMatrix( self.data_array + other.data_array )
        
    def __sub__(self, other):
        return DataMatrix( self.data_array - other.data_array )

    def __getitem__(self, index):
        """ Array indexing.

        If the index is 4-elements long and the last one is "True",
        relative value is taken.
        """
        if not hasattr(index, "__len__"):
            return self.data_array[index]
        if len(index) == 4 and index[3]:
            m = self.relative
        else:
            m = self
        return m.data_array.__getitem__(index[0:3])

    def __setitem__(self, index, value):
        self.data_array.__setitem__(index, value)
    
    def value_at(self, x, y, z):
        return self.data_array[x, y, z]
        
    def relative_value_at(self, x, y, z):
        return self.relative.value_at(x, y, z)
        
    @property
    def size(self):
        return self.data_array.size
     
    @property   
    def size_x(self):
        return self.data_array.shape[0]
    
    @property
    def size_y(self):
        return self.data_array.shape[1]
    
    @property
    def size_z(self):
        return self.data_array.shape[2]
      
    @property
    def max_value(self):
        if not hasattr(self, "_maxValue"):
            self._maxValue = self.data_array.max()
        return self._maxValue

    @property
    def relative(self):
        """ Matrix with all values relative (normalized to the largest element) """
        if not hasattr( self, "_relative"):
            self._relative = DataMatrix(self.data_array / self.max_value, header=self.header)
        return self._relative        

    def allowed_reductions(self):
        """ Tuple of possible reductions in all dimensions.

        I.e. factors of size along the respective axes."""
        return (
            (i for i in range(1, self.size_x + 1 ) if self.size_x % i == 0),
            (i for i in range(1, self.size_y + 1 ) if self.size_y % i == 0),
            (i for i in range(1, self.size_z + 1 ) if self.size_z % i == 0)
        )

    def reduced(self, indices = (1, 1, 1)):
        """ New matrix with reduced dimensions.

        Each x,y,z-element box is replaced with one element."""
        allowed = self.allowed_reductions()
        if not all( [(indices[i] in allowed[i]) for i in range(0, 3)]):
            raise ValueError("Wrong index")
        new_array = numpy.ndarray( shape = (self.size_x / indices[0], self.size_y / indices[1], self.size_z / indices[2]), dtype=float )
        for x in range(0, new_array.shape[0]):
            for y in range(0, new_array.shape[1]):
                for z in range(0, new_array.shape[2]):
                    x0 = x * indices[0]; x1 = x0 + indices[0]
                    y0 = y * indices[1]; y1 = y0 + indices[1]
                    z0 = z * indices[2]; z1 = z0 + indices[2]
                    new_array[x, y, z] = ( self.data_array[ x0:x1, y0:y1, z0:z1 ].sum())
        return DataMatrix(new_array, header=self.header)