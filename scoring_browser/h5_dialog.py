from PyQt4 import QtGui, QtCore
import h5py

class H5Dialog(QtGui.QDialog):
    def fill_item(self, hdf5_item, tree_item):
        for key, item in hdf5_item.items():
            new_item = QtGui.QTreeWidgetItem()
            new_item.setText(0, key)
            tree_item.addChild(new_item)
            if isinstance(item, h5py.Dataset):
                new_item.setText(1, "x".join([str(i) for i in item.shape]))
                new_item.setData(0, 32, QtCore.QVariant(item.name))
            else:
                self.fill_item(item, new_item)         

    def __init__(self, parent, file_name):
        super(H5Dialog, self).__init__(parent)
        self.setModal(True)

        f = h5py.File(file_name)

        # Tree Widget
        def on_item_selection_change():
            if len(self.tree_widget.selectedItems()):
                item = self.tree_widget.selectedItems()[0]
                data = item.data(0, 32)
                if data.toString():
                    self.ok_button.setDisabled(False)
                    self._path = str(data.toString())
                    return
            self.ok_button.setDisabled(True)
            self._path = None

        self.tree_widget = QtGui.QTreeWidget()
        self.tree_widget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tree_widget.setHeaderHidden(False)
        self.tree_widget.setIndentation(10)
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(("Data set", "Dimension"))
        self.tree_root = QtGui.QTreeWidgetItem()
        self.setWindowTitle(file_name)
        self.tree_root.setText(0, "/")
        self.tree_widget.addTopLevelItem(self.tree_root)      
        self.fill_item(f, self.tree_root)
        self.tree_widget.expandAll()
        self.tree_widget.itemSelectionChanged.connect(on_item_selection_change)

        # Button
        def on_ok_click():
            self.accept()

        self.ok_button = QtGui.QPushButton()
        self.ok_button.setDisabled(True)
        self.ok_button.setText("Use selected data set")
        self.ok_button.clicked.connect(on_ok_click)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)
        self._path = None
        f.close()

    @property
    def path(self):
        return self._path
