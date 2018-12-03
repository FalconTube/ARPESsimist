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
    QComboBox,
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


class StitchWindow(QMainWindow):
    """ Window for Stitching Data"""

    def __init__(self, vertical=False):
        QMainWindow.__init__(self)
        self.vertical = vertical
        self.settings = QtCore.QSettings("Stitching", "StitchWin")
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            self.resize(960, 1080)
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))
        # Instantiate widgets
        self.main_widget = QWidget(self)

        # Main Layout
        # if self.vertical:
        self.figs_layout = QHBoxLayout()
        # else:
        self.over_layout = QVBoxLayout(self.main_widget)
        self.over_layout.addLayout(self.figs_layout)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # File Menu
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction("&Load Data", self.get_figdat)
        self.file_menu.addAction(
            "&Quit", self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q
        )

        self.menuBar().addMenu(self.file_menu)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPESsimist - Stitching")

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
        # Hand over to Stitcher
        self.Stitcher = Stitch(
            fignum, figs_data, figs_extents, self.over_layout,
            self.figs_layout, self.main_widget, vertical=self.vertical
        )
        # Export Menu
        self.export_menu = QMenu("&Export", self)
        self.export_menu.addAction("&Save stitched txt", self.Stitcher.export_data)
        self.menuBar().addMenu(self.export_menu)

    def fileQuit(self):
        """ Closes current instance """
        self.close()

    def closeEvent(self, ce):
        """ Closes current event """
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        self.fileQuit()


class Stitch(QWidget):
    def __init__(
        self, fignum, figs_data, figs_extents, layout, fig_layout, parent=None, vertical=False
    ):
        super().__init__()
        self.parent = parent
        self.fignum = fignum
        self.figs_data = figs_data
        self.figs_extents = figs_extents
        self.layout = layout
        self.fig_layout = fig_layout
        self.vertical = vertical
        self.setParent(self.parent)

        # Variables
        self.overlap_percentage = 0
        self.slider_pos = 0
        self.figs_data = self.figs_data
        self.figs_data_initial = self.figs_data
        self.colormap = "terrain"
        self.need_redraw_upper = True

        # Call plots
        self.plot_separate()
        self.plot_together()
        self.update_extents()

        # Init toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.cb = QComboBox()
        self.cb.addItem("terrain")
        self.cb.addItem("viridis")
        self.cb.addItem("plasma")
        self.cb.addItem("inferno")
        self.cb.addItem("magma")
        self.cb.addItem("Greys")
        self.toolbar.addWidget(self.cb)
        self.cb.currentIndexChanged.connect(self.update_colormap)

        self.layout.addWidget(self.toolbar)

        # Add sliders
        if self.vertical:
            self.slider_range = int((self.figs_data[:, :, 0].shape[0]) / 2)
        else:
            self.slider_range = int((self.figs_data[:, :, 0].shape[1]) / 2)
        self.slider = self.add_slider(0, self.slider_range)
        self.slider.setSliderPosition(0)
        self.Label = QLabel(self)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Overlap: 0.0 %")
        self.slider.valueChanged.connect(self.slider_changed)
        self.slider.sliderReleased.connect(self.update_extents)

        self.trimmer_range = int((self.figs_data[:, :, 0].shape[1]) / 4)
        self.trimmmer_slider = self.add_slider(0, self.trimmer_range)
        self.trimmmer_slider.setSliderPosition(0)
        self.trim_label = QLabel(self)
        self.trim_label.setAlignment(QtCore.Qt.AlignCenter)
        self.trim_label.setText("Trim: 0.0 %")
        self.trimmmer_slider.valueChanged.connect(self.trimmer_changed)
        self.trimmmer_slider.sliderReleased.connect(self.update_extents)
        self.trimmmer_slider.sliderReleased.connect(self.update_lower)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.trimmmer_slider)
        self.layout.addWidget(self.trim_label)

    def compute_aspect(self, extent, orient='s'):
        x_range = abs(extent[1] - extent[0])
        e_range = abs(extent[3] - extent[2])
        if orient == 's':
            aspectratio = x_range / e_range
        if orient == 'h':
            aspectratio = 0.3 * x_range / e_range
        if orient == 'v':
            aspectratio = x_range / (0.3 * e_range)
        return aspectratio

    def plot_separate(self):
        # self.upper_fig = Figure(figsize=(10, 10), dpi=100, tight_layout=True)
        self.upper_fig = Figure(figsize=(10, 10), dpi=100)
        self.upper_images = []
        for n in range(self.fignum):
            data = self.figs_data[:, :, n]
            extent = self.figs_extents[n]

            aspectratio = self.compute_aspect(extent)

            if self.vertical:
                subplot_pos = "{}1{}".format(self.fignum, n+1)
            else:
                subplot_pos = "1{}{}".format(self.fignum, n + 1)
            ax = self.upper_fig.add_subplot(subplot_pos)
            img = ax.imshow(data, extent=extent, aspect=aspectratio, cmap=self.colormap)
            self.upper_images.append(img)
        canvas = FigureCanvas(self.upper_fig)
        self.fig_layout.addWidget(canvas)
        canvas.draw_idle()

    def plot_together(self):
        self.fig = Figure(figsize=(10, 10), dpi=100, tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)
        self.fig_layout.addWidget(self.canvas)

        stichted = self.stitch_init()

        self.stitched_image = self.ax.imshow(stichted, cmap=self.colormap)
        self.canvas.update()
        self.canvas.draw_idle()
        self.show()

    def stitch_init(self):
        for n in range(self.fignum):
            data = self.figs_data[:, :, n]
            if n == 0:
                out = data
            else:
                if self.vertical:
                    out = np.vstack((out, data))
                else:
                    out = np.hstack((out, data))
        return out

    def update_extents(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        if self.need_redraw_upper:
            init_width = self.figs_data_initial.shape[1]
            current_width = self.figs_data.shape[1]
            ratio = current_width / init_width
            # new_extents = []
            # Upper axes
            for n, i in enumerate(self.figs_extents):
                left = i[0] * ratio
                right = i[1] * ratio
                yl = i[2]
                yu = i[3]
                this_extent = [left, right, yl, yu]

                # new_extents.append(this_extent)
                self.figs_extents[n] = this_extent
                aspectratio = self.compute_aspect(this_extent)
                ax = self.upper_fig.axes[n]
                current_dat = self.upper_images[n].get_array()
                self.upper_images[n] = ax.imshow(
                    current_dat,
                    extent=this_extent,
                    aspect=aspectratio,
                    cmap=self.colormap,
                )
            self.upper_fig.canvas.draw_idle()
        # else:
        #     new_extents = self.figs_extents
        self.need_redraw_upper = False

        # Lower axis
        if self.vertical:
            self.figs_extents[0] = self.figs_extents[0][::-1]
        self.lower_extent = []
        left = self.figs_extents[0][0]

        for n, i in enumerate(self.figs_extents[0]):
            if n == 1:
                right = i
                width = right - left
                end = left + self.fignum * width
                self.lower_extent.append(end)
            else:
                self.lower_extent.append(i)
        if self.overlap_percentage > 0:
            self.lower_extent = self.calc_overlap_extent(self.lower_extent)
        if self.vertical:
            self.figs_extents[0] = self.figs_extents[0][::-1]
            self.lower_extent = self.lower_extent[::-1]
        if self.vertical:
            aspectratio = self.compute_aspect(self.lower_extent, orient='v')
        else:
            aspectratio = self.compute_aspect(self.lower_extent, orient='h')
        out = self.stitched_image.get_array()

        self.stitched_image = self.ax.imshow(
            out, extent=self.lower_extent, aspect=aspectratio, cmap=self.colormap
        )
        self.ax.set_xlabel(r"Angle [$^\circ{}$]")
        self.ax.set_ylabel(r"Energy [eV]")
        self.canvas.draw_idle()
        QApplication.restoreOverrideCursor()

    def stitch(self, overlap):
        out = 0
        self.overlap = overlap
        if overlap > 0:
            prev_data = None
            for n in range(self.fignum):
                current_data = self.figs_data[:, :, n]
                if self.vertical:
                    current_data = current_data.T
                

                l_over = current_data[:, :overlap]
                if n == 0:  # Ensure that we start with a left side
                    out = l_over
                    data = current_data[:, overlap:-overlap]
                if n == self.fignum - 1:  # If at end
                    data = current_data[:, overlap:]
                else:
                    data = current_data[:, overlap:-overlap]
                if n > 0:
                    l_tmp = self.linear_profile(l_over, "l")
                    # prev_data = self.figs_data[:, -overlap:, n-1]
                    prev_data = prev_data[:, -overlap:]
                    r_tmp = self.linear_profile(prev_data, "r")
                    l_over = l_tmp + r_tmp
                    if self.vertical:
                        print('VERTICAL')
                        # print('lover')
                        # print(out.shape)
                        # print(l_over.shape)
                        out = np.vstack((out, l_over))
                    else:
                        out = np.hstack((out, l_over))
                prev_data = current_data
                # print('###########')
                # print(out.shape)
                # print(data.shape)
                if self.vertical:
                    out = np.vstack((out, data))
                else:
                    out = np.hstack((out, data))
        else:
            out = self.stitch_init()
        self.stitched_image.set_data(out)
        self.ax.draw_artist(self.stitched_image)
        self.ax.figure.canvas.update()

    def trimmer(self, trimvalue):
        for n, ax in enumerate(self.upper_fig.axes):
            trimmed_data_range = self.figs_data_initial[:, :, n]
            trimmed_data = trimmed_data_range[:, trimvalue:-trimvalue]
            self.upper_images[n].set_data(trimmed_data)
            ax.draw_artist(self.upper_images[n])
            if n == 0:
                tmp = trimmed_data
            else:
                tmp = np.dstack((tmp, trimmed_data))
        self.figs_data = tmp
        self.upper_fig.canvas.update()

    def linear_profile(self, data, pos="r"):
        upper = data.shape[1]
        res = np.zeros(data.shape)
        if pos == "r":
            if upper > 0:
                slope = -1 / upper
            else:
                slope = 0
            offset = 1
        if pos == "l":
            if upper > 0:
                slope = 1 / upper
            else:
                slope = 0
            offset = 0
        for n, i in enumerate(data.T):
            f = (slope * n + offset) * i
            res[:, n] = f
        return res

    def calc_overlap_extent(self, extent_in):
        lower = extent_in[0]
        upper = extent_in[1]
        perc = self.overlap_percentage / 100  #  Only goes to 50% overlap
        n = self.fignum
        one = (upper - lower) / n
        diff = one * perc
        upper = upper - ((n - 1) * diff)
        extent_in[1] = upper
        return extent_in

    def add_slider(self, lower: int, upper: int):
        slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        slider_bar.setRange(lower, upper - 1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        slider_bar.setToolTip("0")
        return slider_bar

    def update_colormap(self):
        current_map = self.cb.currentText()
        self.colormap = current_map
        for n, ax in enumerate(self.upper_fig.axes):
            img = self.upper_images[n]
            img.set_cmap(current_map)
            ax.draw_artist(img)
        self.stitched_image.set_cmap(current_map)
        self.ax.draw_artist(self.stitched_image)
        self.update_all()

    def update_all(self):
        self.upper_fig.canvas.update()
        self.canvas.update()

    def update_lower(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if self.vertical:
            self.slider_range = int((self.figs_data[:, :, 0].shape[0]) / 2)
        else:
            self.slider_range = int((self.figs_data[:, :, 0].shape[1]) / 2)
        self.slider.setRange(0, self.slider_range)
        self.slider.setSliderPosition(0)
        self.slider.update()
        self.stitch(self.slider_pos)
        QApplication.restoreOverrideCursor()

    def slider_changed(self, value):
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        self.overlap_percentage = self.slider_pos / self.slider_range * 50
        self.Label.setText("Overlap: {:.1f} %".format(self.overlap_percentage))
        self.stitch(self.slider_pos)

    def trimmer_changed(self, value):
        self.need_redraw_upper = True
        changed_slider = self.sender()
        self.trimmer_pos = changed_slider.value()
        labelpos = self.trimmer_pos / self.trimmer_range * 100
        self.trim_label.setText("Trim: {:.1f} %".format(labelpos))
        self.trimmer(self.trimmer_pos)

    def update_vmax(self, value):
        changed_slider = self.sender()
        self.lut_slider_pos = changed_slider.value()
        self.current_clim = (0, self.lut_slider_pos)
        self.twoD_ax.set_clim(self.current_clim)
        self.update_2dplot()

    def export_data(self):
        location = QFileDialog.getSaveFileName(self, "Choose savename", ".")
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        location = str(location[0])
        data = self.stitched_image.get_array()
        shape = data.shape
        data = np.ravel(data)
        extent = self.lower_extent

        header = "Stitched image\nShape: {}\nExtent {}".format(shape, extent)
        np.savetxt(location, data, header=header)
        QApplication.restoreOverrideCursor()


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    gw = StitchWindow(True)
    gw.show()
    sys.exit(qApp.exec_())
