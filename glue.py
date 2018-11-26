import sys
import numpy as np
import time
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QMenu,
    QMessageBox,
    QFileDialog,
    QGridLayout,
    QDialog,
    QInputDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSlider,
    QLabel,
)

# from PyQt5.QtGui import QIcon, QScreen, QPixmap

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# from mpl_canvas_class import MyMplCanvas
from load_sp2 import Sp2_loader


class GlueWindow(QMainWindow):
    """ Window for Glueing Data"""

    def __init__(self):
        QMainWindow.__init__(self)
        self.settings = QtCore.QSettings("Glue", "GlueWin")
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))
        # Instantiate widgets
        self.main_widget = QWidget(self)

        # Main Layout
        self.over_layout = QVBoxLayout(self.main_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction("&Get Figures", self.get_figdat)
        self.file_menu.addAction(
            "&Quit", self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q
        )
        self.menuBar().addMenu(self.file_menu)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # self.get_figdat(fignum)

    def get_figdat(self):
        # Choose Data
        LastDir = "."
        if not self.settings.value("LastDir") == None:
            LastDir = self.settings.value("LastDir")

        many_files = QFileDialog.getOpenFileNames(
            self, "Select one or more files to open", LastDir
        )
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        LastDir = os.path.dirname(many_files[0][0])
        self.settings.setValue("LastDir", LastDir)
        # Start loading Data
        sp2 = Sp2_loader()
        loaded_filenames = sp2.tidy_up_list(many_files[0])
        fignum = len(loaded_filenames)
        figs_data, figs_extents = sp2.read_multiple_sp2(loaded_filenames)
        QApplication.restoreOverrideCursor()
        # Hand over to Gluer
        self.Gluer = Glue(
            fignum, figs_data, figs_extents, self.over_layout, self.main_widget
        )

        # self.over_layout.addLayout(self.Gluer)

    def fileQuit(self):
        """ Closes current instance """
        self.close()

    def closeEvent(self, ce):
        """ Closes current event """
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        self.fileQuit()


# class Glue(QWidget, GlueWindow):
class Glue(QWidget):
    def __init__(self, fignum, figs_data, figs_extents, layout, parent=None):
        super().__init__()
        self.parent = parent
        self.fignum = fignum
        self.figs_data = figs_data
        self.figs_extents = figs_extents
        self.layout = layout
        self.setParent(self.parent)

        # Variables
        self.overlap = 0

        # Call funcs
        self.plot_separate()
        self.plot_together()

        self.slider_range = int((self.figs_data[:, :, 0].shape[1]) / 2)
        self.slider = self.add_slider(0, self.slider_range)
        self.slider.setSliderPosition(0)
        self.Label = QLabel(self)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.slider.valueChanged.connect(self.slider_changed)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.Label)
        # self.slider.sliderReleased.connect(self.update_widgets)

    def plot_separate(self):
        fig = Figure(figsize=(10, 10), dpi=100, tight_layout=True)
        for n in range(self.fignum):
            data = self.figs_data[:, :, n]
            extent = self.figs_extents[n]

            x_range = abs(extent[1] - extent[0])
            e_range = abs(extent[3] - extent[2])
            aspectratio = x_range / e_range

            subplot_pos = "1{}{}".format(self.fignum, n + 1)
            ax = fig.add_subplot(subplot_pos)
            img = ax.imshow(data, extent=extent, aspect=aspectratio, cmap="terrain")
        canvas = FigureCanvas(fig)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(2)
        # self.canvas.setMinimumHeight(200)
        canvas.setSizePolicy(sizePolicy)
        self.layout.addWidget(canvas)
        # self.ax.get_yaxis().set_visible(False)
        canvas.update()
        canvas.draw()
        self.show()

    def plot_together(self):
        self.fig = Figure(figsize=(10, 10), dpi=100, tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)
        self.layout.addWidget(self.canvas)

        stichted = self.stich_init()

        self.stiched_image = self.ax.imshow(stichted, cmap="terrain")
        self.canvas.update()
        self.canvas.draw()
        self.show()

    def stich_init(self):
        for n in range(self.fignum):
            data = self.figs_data[:, :, n]
            extent = self.figs_extents[n]
            if n == 0:
                out = data
            else:
                out = np.hstack((out, data))
        return out

    def stich(self, overlap):
        out = 0
        for n in range(self.fignum):
            l_over = self.figs_data[:, :overlap, n]
            if n == 0:  # Ensure that we start with a left side
                out = l_over
                data = self.figs_data[:, overlap:-overlap, n]
            if n == self.fignum - 1:  # If at end
                data = self.figs_data[:, overlap:, n]
            else:
                data = self.figs_data[:, overlap:-overlap, n]
            if n > 0:
                l_tmp = self.linear_profile(l_over, "l")
                prev_data = self.figs_data[:, -overlap:, n - 1]
                r_tmp = self.linear_profile(prev_data, "r")
                l_over = l_tmp + r_tmp
                out = np.hstack((out, l_over))

            out = np.hstack((out, data))
        self.stiched_image.set_data(out)
        self.ax.draw_artist(self.stiched_image)
        self.ax.figure.canvas.update()

    def linear_profile(self, data, pos="r"):
        upper = data.shape[1]
        res = np.zeros(data.shape)
        if pos == "r":
            slope = -1 / upper
            offset = 1
        if pos == "l":
            slope = 1 / upper
            offset = 0
        for n, i in enumerate(data.T):
            f = (slope * n + offset) * i
            res[:, n] = f
        return res

    def add_slider(self, lower: int, upper: int, orient="hor"):
        if orient == "hor":
            slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        else:
            slider_bar = QSlider(QtCore.Qt.Vertical, self)
        slider_bar.setRange(lower, upper - 1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        slider_bar.setToolTip("0")
        return slider_bar

    def slider_changed(self, value):
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        labelpos = self.slider_pos / self.slider_range * 100
        self.Label.setText("{:.1f} %".format(labelpos))
        self.stich(self.slider_pos)


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    gw = GlueWindow()
    gw.show()
    sys.exit(qApp.exec_())
