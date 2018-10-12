import sys
import os
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar
import matplotlib
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")


# from main_gui import ApplicationWindow


class K_Window(ApplicationWindow):
    ''' Instantiates new window for k data treatment '''

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('K Data Handler')

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

    def fileQuit(self):
        ''' Closes current instance '''
        self.close()
