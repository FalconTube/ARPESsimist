from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from .progbar_ui import Ui_Form


class ProgressBar(QtWidgets.QDialog, Ui_Form):
    def __init__(self, desc=None, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setupUi(self)
        self.show()

        if desc != None:
            self.setDescription(desc)

    def setValue(self, val):  # Sets value
        self.progressBar.setProperty("value", val)

    def setDescription(self, desc):  # Sets Pbar window title
        self.setWindowTitle(desc)


def main():
    # A new instance of QApplication
    app = QtWidgets.QApplication(sys.argv)
    # We set the form to be our MainWindow (design)
    form = ProgressBar("pbar")
    app.exec_()
