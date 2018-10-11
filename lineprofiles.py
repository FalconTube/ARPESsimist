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
    QRadioButton, QGroupBox, QInputDialog, QLineEdit


class LineProfiles(QWidget):
    ''' Attaches stuff for lineprofile to current 2D Plot '''

    def __init__(self, twodfig, xprof_ax, yprof_ax, parent):
        # Set up default values
        self.current_hline = False
        self.current_vline = False
        self.cid = False
        self.cid_hover = False
        self.xy_chooser = 'x'
        self.breadth = 0.0
        # MyMplCanvas.__init__(self)
        super().__init__()
        # self.setParent(parent)
        self.data = 0
        self.ranges = 0

        # Get fig and axes
        self.twodfig = twodfig
        self.ax = self.twodfig.axes
        self.xprof_ax = xprof_ax
        self.yprof_ax = yprof_ax

    def disconnect(self):
        ''' Disconnect from figure '''
        self.ax.figure.canvas.mpl_disconnect(self.cid)
        self.cid = False

    def init_cursor_active_x(self):
        ''' Choose x profile generator '''
        self.xy_chooser = 'x'
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                'button_press_event', self.on_press)

    def init_cursor_active_y(self):
        ''' Choose y profile generator '''
        self.xy_chooser = 'y'
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                'button_press_event', self.on_press)

    def on_press(self, event):
        ''' Show hline or vline, depending on lineprof chosen '''
        if event.button == 3:  # Use right click
            if self.xy_chooser == 'x':
                if self.current_hline:
                    self.current_hline.remove()
                self.current_hline = self.ax.axhline(event.ydata)

                self.xpoints, self.ypoints = \
                    self.lineprofileX(self.data, self.ranges, event.ydata)
                self.xprof_ax.plot(self.xpoints, self.ypoints, zorder=-1)
                self.xprof_ax.figure.canvas.draw()

            if self.xy_chooser == 'y':
                if self.current_vline:
                    self.current_vline.remove()
                self.current_vline = self.ax.axvline(event.xdata)

                self.xpoints, self.ypoints = \
                    self.lineprofileY(self.data, self.ranges, event.xdata)
                self.yprof_ax.plot(self.ypoints, self.xpoints, zorder=-1)
                self.yprof_ax.figure.canvas.draw()

            self.ax.figure.canvas.draw()  # redraw

    def clear_all(self):
        ''' Clear Lineprofiles and h,v lines '''
        # Remove all lines
        self.xprof_ax.clear()
        self.yprof_ax.clear()
        if self.current_hline:
            self.current_hline.remove()
        if self.current_vline:
            self.current_vline.remove()
        self.current_hline = False
        self.current_vline = False

        # Redraw to show clearance
        # self.ax.figure.canvas.draw()
        self.twodfig.figure.canvas.draw()

    def processing_data_interpolator(self, data, thisrange):
        ''' Generates interpolator '''
        data_shape = data.shape
        xvals = np.linspace(thisrange[0], thisrange[1], data_shape[1])
        yvals = np.linspace(thisrange[3], thisrange[2], data_shape[0])
        idata = interp2d(xvals, yvals, data, fill_value=0.0)
        return idata, xvals, yvals

    def lineprofileX(self, data: np.array, current_range: list,
                     yval: float, breadth=0.1):
        ''' Returns Lineprofile along X'''
        breadth = self.breadth
        self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
            data, current_range)
        self.profile = np.sum(self.idata(self.xvals, [
            yval - 0.5*breadth + breadth*float(i)/20.
            for i in range(21)]), axis=0)
        return self.xvals, self.profile

    def lineprofileY(self, data: np.array, current_range: list,
                     xval: float, breadth=0.1):
        ''' Returns Lineprofile along Y'''
        breadth = self.breadth
        self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
            data, current_range)
        self.profile = np.sum(self.idata([
            xval - 0.5*breadth + breadth*float(i)/20.
            for i in range(21)], self.yvals), axis=1)
        return self.yvals[::-1], self.profile

    def get_breadth(self):
        if not self.input_breadth.text() == '':
            self.breadth = float(self.input_breadth.text())
            print(self.breadth)
        else:
            self.breadth = 0.0

    def init_widget(self):
        ''' Creates widget and layout '''
        self.box = QGroupBox('LineProfileX')
        self.this_layout = QHBoxLayout()

        self.selectbutton_x = QPushButton('&X Lineprofile', self)
        self.selectbutton_y = QPushButton('&Y Lineprofile', self)
        self.clearbutton = QPushButton('&Clear', self)
        self.discobutton = QPushButton('&Stop Selection', self)
        self.input_breadth = QLineEdit(self)
        self.input_breadth.setPlaceholderText('Breadth')

        self.selectbutton_x.released.connect(self.init_cursor_active_x)
        self.selectbutton_y.released.connect(self.init_cursor_active_y)
        self.clearbutton.released.connect(self.clear_all)
        self.discobutton.released.connect(self.disconnect)
        self.input_breadth.returnPressed.connect(self.get_breadth)

        self.this_layout.addWidget(self.selectbutton_x)
        self.this_layout.addWidget(self.selectbutton_y)
        self.this_layout.addWidget(self.clearbutton)
        self.this_layout.addWidget(self.discobutton)
        self.this_layout.addWidget(self.input_breadth)

        self.box.setLayout(self.this_layout)

    def get_widget(self):
        ''' Returns this widget '''
        return self.box

    def update_data_extent(self, data, extent):
        ''' Update current data and extent '''
        self.data = data
        self.ranges = extent
        self.clear_all()
