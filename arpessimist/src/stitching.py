import sys
import numpy as np
import os
import glob
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QMenu,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSlider,
    QLabel,
    QComboBox,
    QAction,
    QMessageBox,
)

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from matplotlib.figure import Figure

from .load_sp2 import Sp2_loader
from .sum_ints import SumImages


class StitchWindow(QMainWindow):
    """ Window for Stitching Data"""

    def __init__(self, vertical=False):
        QMainWindow.__init__(self)
        self.statusbar = self.statusBar()
        self.vertical = vertical
        self.instance_counter = 0
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
        self.file_menu.addAction("&Load Data", self.get_figdat_normal)
        self.file_menu.addAction("&Load Map Stitching", self.get_figdat_maps)
        self.file_menu.addAction(
            "&Quit", self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q
        )

        # Set up Summation Menu
        self.summation_menu = QMenu("&Summation", self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.summation_menu)

        self.summation_menu.addAction("&Initialize Summation", self.start_summation)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.summation_menu)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPESsimist - Stitching")

    def get_figdat_normal(self):
        # Choose Data
        LastDir = "."
        if not self.settings.value("LastDir") == None:
            LastDir = self.settings.value("LastDir")
        try:
            many_files = QFileDialog.getOpenFileNames(
                self, "Select one or more files to open", LastDir
            )
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

            LastDir = os.path.dirname(many_files[0][0])
            self.settings.setValue("LastDir", LastDir)
            # Start loading Data
            sp2 = Sp2_loader()
            # loaded_filenames = sp2.tidy_up_list(many_files[0])
            loaded_filenames = many_files[0]
            fignum = len(loaded_filenames)
            figs_data, figs_extents = sp2.read_multiple_sp2(
                loaded_filenames, natsort=False
            )

            self.clear_layout(self.over_layout)
            # Hand over to Stitcher
            self.start_stitcher(fignum, figs_data, figs_extents)

            self.instance_counter += 1

        except ValueError:
            QApplication.restoreOverrideCursor()
            pass
        QApplication.restoreOverrideCursor()

    def get_figdat_maps(self):
        LastDir = '.'
        if not self.settings.value("LastDir") == None:
            LastDir = self.settings.value("LastDir")
        try:
            QMessageBox(
                    QMessageBox.Information,
                    "Stitch 2 Maps",
                    "Two windows will open:<br>"+
                    "1. Select <b>one</b> file from <b>first</b> map<br>"+
                    "2. Select <b>matching</b> file from <b>second</b> map<br>",
                    QMessageBox.Ok 
                    ).exec()

            fp1 = QFileDialog.getOpenFileName(
                    self, "Select left", LastDir
            )[0]
            LastDir = os.path.dirname(fp1)
            fp2 = QFileDialog.getOpenFileName(
                    self, "Select right", LastDir
            )[0]
            loaded_filenames = [fp1, fp2]

            sp2 = Sp2_loader()
            figs_data, figs_extents = sp2.read_multiple_sp2(
                loaded_filenames, natsort=False
            )
            self.clear_layout(self.over_layout)
            # Hand over to Stitcher
            self.start_stitcher(2, figs_data, figs_extents, loaded_filenames)
            

        except ValueError:
            pass

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def start_summation(self):
        SI = SumImages(self.settings, self)

    def start_stitcher(self,fignum, figs_data, figs_extents, filepaths=None):
        Stitcher = Stitch(
            fignum,
            figs_data,
            figs_extents,
            self.over_layout,
            self.figs_layout,
            self.main_widget,
            statusbar=self.statusbar,
            vertical=self.vertical,
            filepaths=filepaths
        )
        if self.instance_counter > 0:
            self.menuBar().removeAction(self.ex_menu_action)
            self.instance_counter = 0

        if self.instance_counter == 0:
            # Export Menu
            self.export_menu = QMenu("&Export", self)
            # self.txt_action = QAction("&Save stitched txt", self.Stitcher.export_data)
            self.export_menu.addAction(
                "&Save stitched txt", Stitcher.export_data
            )
            self.export_menu.addAction(
                "&Save stitched sp2", Stitcher.export_sp2
            )
            self.ex_menu_action = self.menuBar().addMenu(self.export_menu)

            # Stitch 2 Map Menu
            self.map_menu = QMenu("&Stitch_2_Maps", self)
            self.map_menu.addAction(
                    "&Start with current parameters", Stitcher.apply_two_maps)
            self.map_menu_action = self.menuBar().addMenu(self.map_menu)
        self.instance_counter += 1

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
        self,
        fignum,
        figs_data,
        figs_extents,
        layout,
        fig_layout,
        parent=None,
        statusbar=None,
        vertical=False,
        filepaths=None,
    ):
        super().__init__()
        self.parent = parent
        self.fignum = fignum
        self.figs_data = figs_data
        self.figs_extents = figs_extents
        self.half_width = int(self.figs_data.shape[1]/2)
        self.layout = layout
        self.fig_layout = fig_layout
        self.vertical = vertical
        self.filepaths = filepaths
        self.setParent(self.parent)
        self.statusbar = statusbar
        self.is_over_50_count = 0
        self.settings = QtCore.QSettings("Stitching", "StitchWin")
        self.statusbar.showMessage("Finished loading data", 2000)

        # Variables
        self.overlap_percentage = 0
        self.slider_pos = 0
        self.trimmer_pos = 0
        self.figs_data = self.figs_data
        self.figs_data_initial = self.figs_data
        self.colormap = "terrain"
        self.need_redraw_upper = True
        self.lut_avail = False

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
        # Add LUT Slider
        self.lut_slider_pos = np.amax(self.stichted_data)
        self.vmax_slider = self.add_slider(0, 2*np.amax(self.stichted_data))
        self.vmax_slider.setSliderPosition(self.lut_slider_pos)
        self.vmax_label = QLabel(self)
        self.vmax_label.setAlignment(QtCore.Qt.AlignCenter)
        self.vmax_label.setText("LUT")
        self.vmax_slider.valueChanged.connect(self.update_vmax)
        self.lut_avail = True

        if self.vertical:
            self.slider_range = int((self.figs_data[:, :, 0].shape[0]) / 1)
        else:
            self.slider_range = int((self.figs_data[:, :, 0].shape[1]) / 1)
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
        self.layout.addWidget(self.vmax_slider)
        self.layout.addWidget(self.vmax_label)


    def compute_aspect(self, extent, orient="s"):
        x_range = abs(extent[1] - extent[0])
        e_range = abs(extent[3] - extent[2])
        if orient == "s":
            aspectratio = x_range / e_range
        if orient == "h":
            aspectratio = 0.3 * x_range / e_range
        if orient == "v":
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
                subplot_pos = "{}1{}".format(self.fignum, n + 1)
            else:
                subplot_pos = "1{}{}".format(self.fignum, n + 1)
            ax = self.upper_fig.add_subplot(subplot_pos)
            img = ax.imshow(data, extent=extent, aspect=aspectratio, cmap=self.colormap)
            self.upper_images.append(img)
        canvas = FigureCanvas(self.upper_fig)
        # self.fig_layout.addWidget(canvas)
        self.layout.addWidget(canvas)
        canvas.draw_idle()

    def plot_together(self):
        self.fig = Figure(figsize=(10, 10), dpi=100, tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)
        # self.fig_layout.addWidget(self.canvas)
        self.layout.addWidget(self.canvas)
        self.stichted_data = self.stitch_init()

        self.stitched_image = self.ax.imshow(self.stichted_data, cmap=self.colormap)
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

    def update_vmax(self, value):
        if value is not None:
            self.lut_slider_pos = value
        else:
            changed_slider = self.sender()
            self.lut_slider_pos = changed_slider.value()
        self.current_clim = (0, self.lut_slider_pos)
        for n, img in enumerate(self.upper_images):
            img.set_clim(self.current_clim)
            ax = self.upper_fig.axes[n]
            ax.draw_artist(img)

        self.stitched_image.set_clim(self.current_clim)
        self.ax.draw_artist(self.stitched_image)

        self.upper_fig.canvas.update()
        self.canvas.update()

    def update_extents(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        if self.need_redraw_upper:
            init_width = self.figs_data_initial.shape[1]
            current_width = self.figs_data.shape[1]
            ratio = current_width / init_width
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
            aspectratio = self.compute_aspect(self.lower_extent, orient="v")
        else:
            aspectratio = self.compute_aspect(self.lower_extent, orient="h")
        out = self.stitched_image.get_array()

        self.stitched_image = self.ax.imshow(
            out, extent=self.lower_extent, aspect=aspectratio, cmap=self.colormap
        )
        self.ax.set_xlabel(r"Angle [$^\circ{}$]")
        self.ax.set_ylabel(r"Energy [eV]")
        self.canvas.draw_idle()
        if self.lut_avail:
            self.update_vmax(self.lut_slider_pos)
        QApplication.restoreOverrideCursor()

    def stitch_n(self, overlap, drawing=True):

        def stitch(overlap, drawing=True):
            out = 0
            if overlap > 0:
                print('overlap {}'.format(overlap))
                prev_data = None
                for n in range(self.fignum):
                    print('fignum {}'.format(self.fignum))
                    current_data = self.figs_data[:, :, n]

                    #curr_overlap = current_data[:, overlap:]
                    curr_overlap = current_data[:, :overlap]
                    if n == 0:  # Ensure that we start with a left side
                        out = current_data[:, :-overlap]
                    if n == self.fignum - 1:  # If at end
                        data = current_data[:, overlap:]
                    else:
                        data = current_data[:, overlap:-overlap]
                    if n > 0:
                        prev_data = self.figs_data[:, :, n - 1]
                        prev_overlap = prev_data[:, -overlap:]
                        # Renormalize Data
                        sum_prev = np.sum(prev_overlap)
                        sum_curr = np.sum(curr_overlap)
                        ratio = sum_prev / sum_curr
                        self.figs_data[:, :, n - 1] = self.figs_data[:, :, n - 1] / ratio
                        # Linear overlap
                        r_tmp = self.linear_profile(prev_overlap, "r")
                        l_tmp = self.linear_profile(curr_overlap, "l")
                        curr_overlap = l_tmp + r_tmp
                        out = np.hstack((out, curr_overlap))
                    #out = np.hstack((out, data))
                        out = np.hstack((out, data))
                    prev_data = current_data

            else:
                out = self.stitch_init()
            # Always update the dataset
            self.stitched_image.set_data(out)
            if drawing:
                self.ax.draw_artist(self.stitched_image)
                self.ax.figure.canvas.update()
        if self.fignum > 2 and overlap >= self.half_width:
            QMessageBox(
                    QMessageBox.Information,
                    "Alert",
                    "Stitching Overlap >50% for more than 3 figures is<br>"+
                    " not yet supported!",
                    QMessageBox.Ok 
                    ).exec()

        # if overlap >= self.half_width:
            # print('IS OVER')
            # if self.is_over_50_count == 0:
                # stitch(self.half_width)
                # curr_fignum = self.figs_data.shape[-1] - 1
                # self.fignum = curr_fignum
                # curr_data = self.stitched_image.get_array().copy()
                # print('curr data shape {}'.format(curr_data.shape))
                # curr_width = curr_data.shape[-1]
                # print('curr width {}'.format(curr_width))
                # for n in range(curr_fignum):
                    # if n == 0:
                        # self.figs_data = curr_data[:, :int(curr_width/2)]
                    # else:
                        # self.figs_data = np.dstack((self.figs_data,
                            # curr_data[:, int(curr_width/2):]))
                # print(self.figs_data.shape)
            # reduced_overlap = overlap - self.half_width
            # stitch(reduced_overlap, drawing)
            # self.is_over_50_count += 1
        # else:
            # self.is_over_50_count == 0
            # stitch(overlap, drawing)

    def trimmer(self, trimvalue):
        if trimvalue == 0:
            return
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
        self.half_width = int(self.figs_data.shape[1]/2)
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
        # slider_bar.setSingleStep(1)
        stepsize = ((upper - 1) - lower) / 1000
        slider_bar.setSingleStep(stepsize)
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
            self.slider_range = int((self.figs_data[:, :, 0].shape[0]) / 1)
        else:
            self.slider_range = int((self.figs_data[:, :, 0].shape[1]) / 1)
        self.slider.setRange(0, self.slider_range)
        self.slider.setSliderPosition(0)
        self.slider.update()
        self.stitch_n(self.slider_pos)
        QApplication.restoreOverrideCursor()

    def slider_changed(self, value=None):
        if value is None:
            changed_slider = self.sender()
            self.slider_pos = changed_slider.value()
        else:
            self.slider_pos = value
        self.overlap_percentage = self.slider_pos / self.slider_range * 100
        self.Label.setText("Overlap: {:.1f} %".format(self.overlap_percentage))
        self.stitch_n(self.slider_pos)

    def trimmer_changed(self, value):
        self.need_redraw_upper = True
        changed_slider = self.sender()
        self.trimmer_pos = changed_slider.value()
        labelpos = self.trimmer_pos / self.trimmer_range * 100
        self.trim_label.setText("Trim: {:.1f} %".format(labelpos))
        self.trimmer(self.trimmer_pos)

    def apply_two_maps(self):
        trimvalue = self.trimmer_pos
        overlap = self.slider_pos
        loader = Sp2_loader()
        folder1, folder2 = [os.path.dirname(i) for i in self.filepaths]
        files_1 = glob.glob(folder1 + '/*.sp2')
        files_2 = glob.glob(folder2 + '/*.sp2')
        # Choose a savename

        QMessageBox(
                QMessageBox.Information,
                "Stitch 2 Maps",
                "Now choose a <b>directory</b> and <b>name</b> for saving",
                QMessageBox.Ok 
                ).exec()
        location = QFileDialog.getSaveFileName(self, "Choose savename", ".")[0]

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.statusbar.showMessage("Loading dataset 1...", 2000)
        figs_data_left, figs_extents_left  = loader.read_multiple_sp2(files_1)
        self.statusbar.showMessage("Loading dataset 2...", 2000)
        figs_data_right, figs_extents_right = loader.read_multiple_sp2(files_2)
        if len(figs_extents_left) != len(figs_extents_right):
            print('wrong lengths')
            # QAlertbox
            return
        # Define savename

        for n in range(len(figs_extents_left)):
            self.statusbar.showMessage("Stitching data {}...".format(n), 2000)
            # Trim
            left = figs_data_left[:, :, n][:, trimvalue:-trimvalue]
            right = figs_data_right[:, :, n][:, trimvalue:-trimvalue]
            # Add to figs_data
            tmp = left
            self.figs_data = np.dstack((tmp, right))
            #self.slider_range = int((self.figs_data.shape[0]) / 1)
            self.stitch_n(overlap, drawing=False)
            self.slider_changed(overlap)
            data = self.stitched_image.get_array()

            # Save data
            shape = data.shape
            data = np.ravel(data[::-1].T)
            intens = np.sum(data)
            extent = self.lower_extent
            header = (
                "P2\n# ERange\t = {} {} # [eV]\n".format(extent[2], extent[3])
                + "# aRange\t = {} {} # [deg]\n".format(extent[0], extent[1])
                + "{} {} {}".format(shape[0], shape[1], int(intens))
            )
            if '.sp2' in location:
                savename = location.split('.')[0] + '_{}'.format(n) + '.sp2'
            else:
                savename = location + '_{}.sp2'.format(n)
            # TODO: Check if file already exists
            np.savetxt(
                savename,
                data.astype(int),
                fmt="%i",
                header=header,
                footer="P2",
                comments="",
            )
        self.statusbar.showMessage("Finished!", 2000)
        QApplication.restoreOverrideCursor()


    def export_data(self):
        try:
            location = QFileDialog.getSaveFileName(self, "Choose savename", ".")
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            location = str(location[0])
            data = self.stitched_image.get_array()
            shape = data.shape
            data = np.ravel(data[::-1].T)
            extent = self.lower_extent

            header = "Stitched image\nShape: {}\nExtent {}".format(shape, extent)
            np.savetxt(location, data.astype(int), header=header)
        except:
            pass
        QApplication.restoreOverrideCursor()

    def export_sp2(self):
        try:
            location = QFileDialog.getSaveFileName(self, "Choose savename", ".")[0]
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            data = self.stitched_image.get_array()
            shape = data.shape
            data = np.ravel(data[::-1].T)
            intens = np.sum(data)
            extent = self.lower_extent
            header = (
                "P2\n# ERange\t = {} {} # [eV]\n".format(extent[2], extent[3])
                + "# aRange\t = {} {} # [deg]\n".format(extent[0], extent[1])
                + "{} {} {}".format(shape[0], shape[1], int(intens))
            )
            np.savetxt(
                location,
                data.astype(int),
                fmt="%i",
                header=header,
                footer="P2",
                comments="",
            )
        except ValueError:
            pass
        QApplication.restoreOverrideCursor()



if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    gw = StitchWindow()
    gw.show()
    sys.exit(qApp.exec_())
