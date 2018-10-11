import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
matplotlib.use("Qt5Agg")
from mpl_canvas_class import MyMplCanvas
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
from PyQt5 import QtCore
from PyQt5.QtWidgets import QSlider


class TwoD_Plotter(MyMplCanvas):
    ''' Plots 2D images '''

    # def __init__(self, *args, **kwargs):
    def __init__(self, processing_data, processing_extent, parent=None, width=5, height=6, dpi=100,
                 multifig=True):
        super().__init__(parent, width, height, dpi,
                         multifig)
        self.processing_data, self.processing_extent = processing_data, processing_extent
        stack_size = processing_data.shape[-1]
        self.instance_counter = 0
        self.slider_pos = 0
        self.update_current_data()
        self.initialize_2D_plot()
        self.twoD_slider = self.add_slider(0, stack_size)
        self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)

    def update_2dplot(self, extent=None):
        ''' Really slow at the moment, due to having three axis
        in here. Have to use blitting '''
        if extent:
            x_range = abs(extent[1] - extent[0])
            e_range = abs(extent[3] - extent[2])
            aspectratio = x_range/e_range
        # print('instance_counter {}'.format(self.instance_counter))
        if self.instance_counter == 0:
            print('zero instance')
            self.instance_counter += 1
            self.axes.cla()
            self.twoD_ax = self.axes.imshow(self.twoD_data,
                                            extent=extent,
                                            aspect=aspectratio,
                                            zorder=0)

            self.fig.canvas.update()
            self.fig_xax.canvas.update()
            self.fig_yax.canvas.update()

            self.toolbar.update()
            self.canvas.draw()
        else:
            self.twoD_ax.set_data(self.twoD_data)
            # self.axes.draw_artist(self.twoD_ax)
            self.axes.figure.canvas.update()
            # self.axes.figure.canvas.flush_events()
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

    def update_widgets(self):
        # pass
        self.LineProf.update_data_extent(self.new_current_data,
                                         self.new_current_extent)
        # self.FitParGui.update_parabola()

    def initialize_2D_plot(self):
        self.update_2d_data(self.new_current_data)
        self.update_2dplot(self.new_current_extent)

    def add_slider(self, lower: int, upper: int):
        slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        slider_bar.setRange(lower, upper-1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        return slider_bar

    def twoD_slider_changed(self, value):
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        # if not self.hd5mode:
        #     self._current_labelname = os.path.basename(
        #         self.loaded_filenames[self.slider_pos])
        # self.twoD_label.setText(self._current_labelname)
        self.update_current_data()
        self.initialize_2D_plot()

        self.update_widgets()
