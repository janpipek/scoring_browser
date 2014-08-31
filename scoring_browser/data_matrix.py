#
# scoring_browser --- Simple Qt application for browsing
# scoring outputs in Geant4
#
# Copyright (C) 2012-2014 Jan Pipek
# (jan.pipek@gmail.com)
#
# This file may be distributed without limitation.
#
import re
import numpy
try:
    import h5py
    HDF5_ENABLED = True
except:
    HDF5_ENABLED = False


class DataMatrix(object):
    """A 3D matrix with data.

    Based on numpy ndarray + a few more methods.
    It can be built from the scoring files made command-based
    Geant4 scoring (either a string of from_file method).

    The indexing is (mostly) forwarded to the inner numpy array.

    * DataMatrix.relative provides a copy of the matrix scaled
    relative to the maximum value (it is stored in the matrix
    after first requested).

    * DataMatrix.reduced() returns a copy of the matrix with values summed
    over volumes of defined size (if division is possible).
    """
    def __init__(self, source=None, header=None):
        self.header = ""
        if source is not None:
            self.data_array = source
            
        if header:
            self.header = header

    def copy(self):
        """Return a copy of the matrix.

        The result will not share memory with the original matrix.
        """
        return DataMatrix(self.data_array.copy())

    def empty(self):
        return not(self.data_array)

    def __add__(self, other):
        """ Add two data matrices. """
        return DataMatrix(self.data_array + other.data_array)

    def __sub__(self, other):
        """ Subtract two data matrices. """
        return DataMatrix(self.data_array - other.data_array)

    def __mul__(self, coefficient):
        """ Multiply DataMatrix by a coefficient. """
        return DataMatrix(self.data_array * coefficient)

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

    def __repr__(self):
        s = "DataMatrix(%d, %d, %d" % self.shape
        if hasattr(self, 'file_name') and self.file_name:
            s += ", file_name=\'%s\'" % self.file_name
        s += ")"
        return s

    def value_at(self, x, y, z):
        return self.data_array[x, y, z]

    def relative_value_at(self, x, y, z):
        return self.relative.value_at(x, y, z)

    @property
    def size(self):
        return self.data_array.size

    @property
    def shape(self):
        return self.data_array.shape

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
            max_ = numpy.nanmax(self.data_array)
            min_ = numpy.nanmin(self.data_array)
            self._maxValue = max(numpy.abs(min_), numpy.abs(max_))
        return self._maxValue

    @property
    def relative(self):
        """ Matrix with all values relative.

        Values normalized to the largest element."""
        if not hasattr(self, "_relative"):
            self._relative = DataMatrix(self.data_array / self.max_value,
                                        header=self.header)
        return self._relative

    def allowed_reductions(self):
        """ Tuple of possible reductions in all dimensions.

        I.e. factors of size along the respective axes."""
        return (
            (i for i in range(1, self.size_x + 1) if self.size_x % i == 0),
            (i for i in range(1, self.size_y + 1) if self.size_y % i == 0),
            (i for i in range(1, self.size_z + 1) if self.size_z % i == 0)
        )

    def reduced(self, indices=(1, 1, 1)):
        """ New matrix with reduced dimensions.

        Each x,y,z-element box is replaced with one element.
        All data in the box are added.
        """
        allowed = self.allowed_reductions()
        if not all([(indices[i] in allowed[i]) for i in range(0, 3)]):
            raise ValueError("Wrong index")
        new_array = numpy.ndarray(shape=(self.size_x / indices[0],
                                         self.size_y / indices[1],
                                         self.size_z / indices[2]),
                                  dtype=float)
        for x in range(0, new_array.shape[0]):
            for y in range(0, new_array.shape[1]):
                for z in range(0, new_array.shape[2]):
                    x0 = x * indices[0]
                    x1 = x0 + indices[0]
                    y0 = y * indices[1]
                    y1 = y0 + indices[1]
                    z0 = z * indices[2]
                    z1 = z0 + indices[2]
                    new_array[x, y, z] = (
                        self.data_array[x0:x1, y0:y1, z0:z1].sum())
        return DataMatrix(new_array, header=self.header)


class DataMatrixLoader(object):
    @staticmethod
    def from_csv(file_name):
        with open(file_name) as f:
            text = f.read()

        points = []
        linePattern = re.compile("(\d+),(\d+),(\d+),([0-9.e\-]*)")
        commentLinePattern = re.compile("#.*")

        for line in text.splitlines():
            # Line with data
            match = linePattern.match(line)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                z = int(match.group(3))
                val = float(match.group(4))
                points.append([x, y, z, val])

            # Line with comments (starting with a "#")
            match = commentLinePattern.match(line)
            if match:
                pass

        sizeX = max(l[0] for l in points) + 1
        sizeY = max(l[1] for l in points) + 1
        sizeZ = max(l[2] for l in points) + 1

        data_array = numpy.ndarray(shape=(sizeX, sizeY, sizeZ),
                                        dtype=float)
        if len(points) != data_array.size:
            raise Exception("Incomplete file.")

        for p in points:
            data_array[p[0], p[1], p[2]] = p[3]

        return DataMatrix(source = data_array)      

    @staticmethod
    def from_hdf5(file_name, path):
        if not HDF5_ENABLED:
            raise Exception("HDF5 library not found => loading disabled.")
        f = h5py.File(file_name)
        print "loaded " + file_name
        data = numpy.array(f.get(path))
        return DataMatrix(source = data)

class DataMatrixSlice2D(object):
    """A 2D slice from a DataMatrix."""

    AXES = ("x", "y", "z")
    PLANES = ("yz", "xz", "xy")

    def __init__(self, matrix, axis_or_plane, index):
        self.matrix = matrix
        if isinstance(axis_or_plane, str):
            self.axis = self.get_axis(axis_or_plane)
        else:
            self.axis = axis_or_plane
        self.index = index

    @classmethod
    def get_axis(cls, axis_or_plane):
        if len(axis_or_plane) == 1:
            return cls.AXES.index(axis_or_plane.lower())
        elif len(axis_or_plane) == 2:
            return cls.PLANES.index(axis_or_plane.lower())
        else:
            raise Exception("You have ")

    @property
    def axis_name(self):
        return self.AXES[self.axis]

    @property
    def plane_name(self):
        return self.PLANES[self.axis]

    @property
    def data(self):
        """View of the underlying numpy data."""
        if self.axis == 0:
            return self.matrix[self.index, :, :]
        elif self.axis == 1:
            return self.matrix[:, self.index, :]
        elif self.axis == 2:
            return self.matrix[:, :, self.index]

    @property
    def shape(self):
        return self.data.shape

    def __getitem__(self, index):
        """Array indexing.

        Delegated to the right slice returned by data.
        """
        return self.data[index]

    def real_index(self, first, second):
        if self.axis == 0:
            return (self.index, first, second)
        elif self.axis == 1:
            return (first, self.index, second)
        elif self.axis == 2:
            return (first, second, self.index)
