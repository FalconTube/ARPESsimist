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


class TwoD_Plotter(MyMplCanvas):
    ''' Plots 2D images '''

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.instance_counter = 0

    def update_2dplot(self):
        if self.instance_counter == 0:
            self.instance_counter += 1
            self.axes.cla()
            self.thisax = self.axes.imshow(self.twoD_data)
            self.toolbar.update()
            self.canvas.draw()
        else:
            self.thisax.set_data(self.twoD_data)
            self.toolbar.update()
            self.canvas.draw()

    def update_2d_data(self, data):
        self.twoD_data = data

    def compute_initial_figure(self):
        self.twoD_data = np.zeros((10, 10))
        self.axes.imshow(self.twoD_data)
