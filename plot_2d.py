import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from mpl_canvas_class import MyMplCanvas
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
from PyQt5 import QtCore
from PyQt5.QtWidgets import QSlider, QFileDialog, QMenu, QLabel


class TwoD_Plotter(MyMplCanvas):
    """ Plots 2D images """

    # def __init__(self, *args, **kwargs):
    def __init__(
        self,
        processing_data,
        processing_extent,
        labellist,
        parent=None,
        width=3,
        height=3,
        dpi=100,
        xlabel="",
        ylabel="",
        appwindow=None,
        labelprefix="",
    ):
        super().__init__(parent, width, height, dpi)
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.labellist = labellist
        self.labelprefix = labelprefix

        self.processing_data, self.processing_extent = (
            processing_data,
            processing_extent,
        )
        stack_size = processing_data.shape[-1]
        self.instance_counter = 0
        self.slider_pos = 0
        self.update_current_data()
        self.update_widgets()
        self.initialize_2D_plot()

        # Add Slider and its Label
        self.twoD_slider = self.add_slider(0, stack_size)
        self.twoD_Label = QLabel(self)
        self.twoD_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)

        # Add LUT Slider
        self.vmax_slider = self.add_slider(0, np.amax(self.processing_data), "vert")
        self.vmax_slider.setSliderPosition(np.amax(self.processing_data))
        self.vmax_label = QLabel("L\nU\nT", self)
        self.vmax_label.setAlignment(QtCore.Qt.AlignCenter)
        self.vmax_slider.valueChanged.connect(self.update_vmax)

        # Add to Layout
        self.main_layout.addWidget(self.twoD_slider)
        self.main_layout.addWidget(self.twoD_Label)
        self.grid_layout.addWidget(self.vmax_slider, 0, 2)
        self.grid_layout.addWidget(self.vmax_label, 0, 3)
        self.set_xylabels()
        self.export_menu = QMenu("&Export Data", parent)
        appwindow.menuBar().addSeparator()
        appwindow.menuBar().addMenu(self.export_menu)
        self.export_menu.addAction("&Save txt", self.save_txt)
        self.export_menu.addAction("&Save Figures", self.save_figs)

    def set_xylabels(self):
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.xprof_ax.set_xlabel(self.xlabel)
        self.xprof_ax.set_ylabel("I [a.u.]")
        self.yprof_ax.set_xlabel(self.ylabel)
        self.yprof_ax.set_ylabel("I [a.u.]")
        self.axes.figure.canvas.update()
        self.xprof_ax.figure.canvas.update()
        self.yprof_ax.figure.canvas.update()

    def update_vmax(self, value):
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        self.twoD_ax.set_clim(0, self.slider_pos)
        self.update_2dplot()

    def update_2dplot(self, extent=None):
        if extent:
            x_range = abs(extent[1] - extent[0])
            e_range = abs(extent[3] - extent[2])
            aspectratio = x_range / e_range
        # print('instance_counter {}'.format(self.instance_counter))
        if self.instance_counter == 0:
            self.instance_counter += 1
            self.axes.cla()
            self.twoD_ax = self.axes.imshow(
                self.twoD_data, extent=extent, aspect=aspectratio, zorder=0
            )

            self.fig.canvas.update()
            self.fig_xax.canvas.update()
            self.fig_yax.canvas.update()

            self.toolbar.update()
            self.canvas.draw()
        else:
            self.twoD_ax.set_data(self.twoD_data)
            self.axes.draw_artist(self.twoD_ax)
            self.axes.figure.canvas.update()
            self.toolbar.update()

    def update_2d_data(self, data):
        self.twoD_data = data

    def compute_initial_figure(self):
        self.twoD_data = np.zeros((10, 10))
        self.axes.imshow(self.twoD_data)
        self.xprof_ax.plot(1, 1)
        self.yprof_ax.plot(1, 1)

    def update_current_data(self):
        self.new_current_data = self.processing_data[:, :, self.slider_pos]
        self.new_current_extent = self.processing_extent[self.slider_pos]
        self.update_widgets()

    def update_widgets(self):
        # pass
        self.LineProf.update_data_extent(self.new_current_data, self.new_current_extent)
        # self.FitParGui.update_parabola()

    def initialize_2D_plot(self):
        self.update_2d_data(self.new_current_data)
        self.update_2dplot(self.new_current_extent)

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

    def twoD_slider_changed(self, value):
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        labelpos = self.labellist[self.slider_pos]
        self.twoD_slider.setToolTip(str(self.slider_pos))
        try:
            self.twoD_Label.setText("{}: {:4f}".format(self.labelprefix, labelpos))
        except:
            self.twoD_Label.setText("{}: {}".format(self.labelprefix, labelpos))
        self.update_current_data()
        self.initialize_2D_plot()

    def save_txt(self):
        td_dat = self.new_current_data
        td_extent = self.new_current_extent
        xprof_ax, yprof_ax = self.LineProf.get_axes()
        location = QFileDialog.getSaveFileName(self, "Choose savename", ".")
        location = str(location[0])
        # TODO: Check with basename stuff for potential endings and remove them

        # Save 1D if they are available
        try:
            last_line = xprof_ax.lines[-1]
            xdat, ydat = last_line.get_data()
            xname = location + "_Xprofile.txt"
            x_header = "X Profile\n{}   Intensity".format(self.xlabel)
            np.savetxt(xname, np.c_[xdat, ydat], header=x_header)
        except:
            print("x error")
        try:
            last_line = yprof_ax.lines[-1]
            xdat, ydat = last_line.get_data()
            yname = location + "_Yprofile.txt"
            y_header = "Y Profile\n{}   Intensity".format(self.ylabel)
            np.savetxt(yname, np.c_[xdat, ydat], header=y_header)
        except:
            print("y error")
        # 2D always available, so save them
        td_name = location + "_2d.txt"
        td_header = "Data shape: {}\n Data extent: {}".format(td_dat.shape, td_extent)
        np.savetxt(td_name, td_dat, header=td_header)

    def save_figs(self):
        location = QFileDialog.getSaveFileName(self, "Choose savename", ".")
        location = str(location[0])
        self.fig.savefig(location + "_2d.png")
        self.fig_xax.savefig(location + "_XProfile.png")
        self.fig_yax.savefig(location + "_YProfile.png")
