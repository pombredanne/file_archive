import sys

try:
    import sip

    api2_classes = [
            'QData', 'QDateTime', 'QString', 'QTextStream',
            'QTime', 'QUrl', 'QVariant',
            ]
    for cl in api2_classes:
        sip.setapi(cl, 2)

    from PyQt4 import QtCore, QtGui
except ImportError:
    sys.stderr.write("PyQt4 is required by 'file_archive view'\n")
    sys.exit(3)


def _(s, disambiguation=None, **kwargs):
    if kwargs:
        s = s.format(**kwargs)
    return QtCore.QCoreApplication.translate(
            'file_archive.viewer',
            s,
            disambiguation,
            QtCore.QCoreApplication.UnicodeUTF8)


class SearchError(Exception):
    """Error while querying the file store.
    """


class StoreViewerWindow(QtGui.QMainWindow):
    def __init__(self, store):
        QtGui.QMainWindow.__init__(self)

        self.store = store

        searchbar = QtGui.QHBoxLayout()

        self._input = QtGui.QLineEdit()
        self._input.setPlaceholderText(_(u"Enter query here"))
        self._input.returnPressed.connect(self._search)
        searchbar.addWidget(self._input)

        searchbutton = QtGui.QPushButton(_(u"Search"))
        searchbutton.clicked.connect(self._search)
        searchbar.addWidget(searchbutton)

        results = QtGui.QHBoxLayout()

        self._result_tree = QtGui.QTreeWidget()
        results.addWidget(self._result_tree)

        buttons = QtGui.QVBoxLayout()
        but1 = QtGui.QPushButton(_(u"Buttons"))
        but1.setEnabled(False)
        buttons.addWidget(but1)
        but2 = QtGui.QPushButton(_(u"go here"))
        buttons.addWidget(but2)
        but2.setEnabled(False)
        results.addLayout(buttons)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(searchbar)
        layout.addLayout(results)

        widget = QtGui.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _search(self):
        error = None

        query = self._input.text()
        query = query.split()

        if len(query) == 1 and all(o not in query[0] for o in '=<>'):
            h = query[0]
            try:
                entries = [self.store.get(h)]
            except KeyError:
                error = _(u"{h} not found", h=h)

        else:
            try:
                entries = self._search_conditions(query)
            except SearchError, e:
                error = e.message

        self._result_tree.clear()

        if error is not None:
            w = QtGui.QTreeWidgetItem([error])
            w.setForeground(0, QtGui.QColor(255, 0, 0))
            self._result_tree.addTopLevelItem(w)
        else:
            pass # TODO : display results

    def _search_condition(self, query):
        pass # TODO : search from a string


def run_viewer(store):
    application = QtGui.QApplication([])

    window = StoreViewerWindow(store)
    window.show()

    application.exec_()
    sys.exit(0)
