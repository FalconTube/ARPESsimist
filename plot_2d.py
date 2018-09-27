import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from mpl_canvas_class import MyMplCanvas


class TwoD_Plotter(FigureCanvas):
    ''' Plots 2D images '''

    def __init__(self, parent=None, width=3, height=3, dpi=100):
        self.instance_counter = 0
        self.axtitle = 'test'
        self.twoD_data = np.zeros((10, 10))
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title = self.axtitle
        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.toolbar = NavigationToolbar(self, self)
        # self.vbl = QVBoxLayout()
        # self.vbl.addWidget(self.figure.canvas)
        # self.vbl.addWidget(self.toolbar)
        # self.setLayout(self.vbl)

        self.axes.imshow(self.twoD_data)

    def update_2dplot(self):
        if self.instance_counter == 0:
            self.instance_counter += 1
            self.axes.cla()
            self.thisax = self.axes.imshow(self.twoD_data)
            self.toolbar.update()
            self.draw()
        else:
            self.thisax.set_data(self.twoD_data)
            self.toolbar.update()
            self.draw()

    def update_2d_data(self, data):
        self.twoD_data = data
