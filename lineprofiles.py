import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.widgets import Button
from scipy.optimize import curve_fit
from scipy.constants import hbar, m_e
from scipy.interpolate import interp2d

from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar,\
    QRadioButton, QGroupBox

from mpl_canvas_class import MyMplCanvas


class LineProfiles(MyMplCanvas):
    ''' Attaches stuff for lineprofile to current 2D Plot '''

    def __init__(self, data, ranges, twodfig, parent):
        self.current_hline = False
        self.current_vline = False
        self.cid = False
        self.cid_hover = False
        self.xy_chooser = 'x'
        MyMplCanvas.__init__(self)
        self.setParent(parent)
        self.data = data
        self.ranges = ranges
        self.ax = twodfig.add_subplot(111)
        self.axes.remove()
        self.xprof_ax = self.fig.add_subplot(211)
        self.yprof_ax = self.fig.add_subplot(212)

        self.init_plot()

    def disconnect(self):
        self.ax.figure.canvas.mpl_disconnect(self.cid)
        self.cid = False

    def init_cursor_active_x(self):
        self.xy_chooser = 'x'
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                'button_press_event', self.on_press)

    def init_cursor_active_y(self):
        self.xy_chooser = 'y'
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                'button_press_event', self.on_press)

    def init_mouse_hover(self):
        self.cid_hover = self.ax.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_hover)

    def init_plot(self):
        self.xpoints = []
        self.ypoints = []
        self.xline, = self.xprof_ax.plot(self.xpoints, self.ypoints)
        self.yline, = self.yprof_ax.plot(self.xpoints, self.ypoints)

    # def on_hover(self, event):
    #     self.current_hline = self.ax.axhline(event.ydata,
    #                                          color='r',  zorder=-1)
    #     self.xpoints, self.ypoints = \
    #         self.lineprofileX(self.data, self.ranges, event.ydata)
    #     # print(self.xpoints, self.ypoints)
    #     # self.axes.plot(self.xpoints, self.ypoints)
    #     self.line.set_data(self.xpoints, self.ypoints)
    #     self.axes.figure.canvas.draw()
    #     self.ax.figure.canvas.draw()
    #     # self.line.remove()
    #     # self.current_hline.remove()

    def on_press(self, event):
        if event.button == 3:  # Use right click

            if self.xy_chooser == 'x':
                if self.current_hline:
                    self.current_hline.remove()
                self.current_hline = self.ax.axhline(event.ydata)

                self.xpoints, self.ypoints = \
                    self.lineprofileX(self.data, self.ranges, event.ydata)
                self.xprof_ax.plot(self.xpoints, self.ypoints, zorder=-1)

            if self.xy_chooser == 'y':
                if self.current_vline:
                    self.current_vline.remove()
                self.current_vline = self.ax.axvline(event.xdata)

                self.xpoints, self.ypoints = \
                    self.lineprofileY(self.data, self.ranges, event.xdata)
                self.yprof_ax.plot(self.xpoints, self.ypoints, zorder=-1)

            # self.axes.plot(self.xpoints, self.ypoints)
            self.xprof_ax.figure.canvas.draw()
            self.ax.figure.canvas.draw()

    def clear_all(self):
        # Remove all lines
        self.xprof_ax.clear()
        self.yprof_ax.clear()
        # Redraw to show clearance
        self.ax.figure.canvas.draw()
        self.xprof_ax.figure.canvas.draw()
        # self.yprof_ax.figure.canvas.draw()

    def processing_data_interpolator(self, data, thisrange):
        ''' Generates interpolator '''
        data_shape = data.shape
        xvals = np.linspace(thisrange[0], thisrange[1], data_shape[1])
        yvals = np.linspace(thisrange[3], thisrange[2], data_shape[0])
        idata = interp2d(xvals, yvals, data, fill_value=0.0)
        return idata, xvals, yvals

    def lineprofileX(self, data: np.array, current_range: list,
                     yval: float, breadth=0.1):
        """
        returns the lineprofile along the x direction
        for a given y value with a broadening breadth
        :param yval: float
        :param breadth: float
        :return: xvalues, profile both as 1d arrays
        """
        self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
            data, current_range)
        self.profile = np.sum(self.idata(self.xvals, [
            yval - 0.5*breadth + breadth*float(i)/20.
            for i in range(21)]), axis=0)
        return self.xvals, self.profile

    def lineprofileY(self, data: np.array, current_range: list,
                     xval: float, breadth=0.1):
        """
        returns the lineprofile along the x direction
        for a given y value with a broadening breadth
        :param xval: float
        :param breadth: float
        :return: yvalues, profile both as 1d arrays
        """
        self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
            data, current_range)
        self.profile = np.sum(self.idata([
            xval - 0.5*breadth + breadth*float(i)/20.
            for i in range(21)], self.yvals), axis=1)
        return self.yvals[::-1], self.profile

    def init_widget(self):
        # self.parabola_widget = QWidget(self)

        self.box = QGroupBox('LineProfileX')
        self.this_layout = QHBoxLayout()

        self.selectbutton_x = QPushButton('&X Lineprofile', self)
        self.selectbutton_y = QPushButton('&Y Lineprofile', self)
        self.clearbutton = QPushButton('&Clear', self)
        self.discobutton = QPushButton('&Stop Selection', self)

        self.selectbutton_x.released.connect(self.init_cursor_active_x)
        self.selectbutton_y.released.connect(self.init_cursor_active_y)
        self.clearbutton.released.connect(self.clear_all)
        self.discobutton.released.connect(self.disconnect)

        self.this_layout.addWidget(self.selectbutton_x)
        self.this_layout.addWidget(self.selectbutton_y)
        self.this_layout.addWidget(self.clearbutton)
        self.this_layout.addWidget(self.discobutton)

        self.box.setLayout(self.this_layout)

    def get_widget(self):
        return self.box
