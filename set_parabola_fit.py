import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.widgets import Button
from scipy.optimize import curve_fit
from scipy.constants import hbar, m_e

from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar,\
    QRadioButton, QGroupBox, QTextEdit


class FitParabola(QWidget):
    ''' Class for fitting of parabola and getting effective electron mass '''

    def __init__(self, fig, parent):
        super().__init__()
        # self.setParent(parent)
        self.thisax = fig
        self.init_plot()

    def disconnect(self):
        self.thisax.figure.canvas.mpl_disconnect(self.cid)

    def init_cursor_active(self):
        print('Selection called')
        self.cid = self.thisax.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)

    def init_plot(self):
        self.xpoints = []
        self.ypoints = []
        self.plotline, = self.thisax.plot(self.xpoints, self.ypoints, 'rx')
        # self.plotline, = self.thisax.plot(self.xpoints, self.ypoints, 'rx', zorder=-1)

    def on_press(self, event):
        if event.button == 3:  # Use right click
            self.xpoints.append(event.xdata)
            self.ypoints.append(event.ydata)
            # self.thisax.plot(self.xpoints, self.ypoints,  'rx', zorder=-1)

            self.plotline.set_data(self.xpoints, self.ypoints)
            # self.plotline.figure.canvas.flush_events()
            self.plotline.figure.canvas.draw()

    def clear_all(self):
        # Remove all lines
        self.xpoints = []
        self.ypoints = []
        self.plotline.set_data(self.xpoints, self.ypoints)
        self.out_fit.set_data(self.xpoints, self.ypoints)
        # Redraw to show clearance

        self.thisax.figure.canvas.draw()

    def perform_fit(self):
        try:
            self.popt, self.pcov = curve_fit(
                self.fitfunction, self.xpoints, self.ypoints)
        except:
            QMessageBox.about(self, "Error",
                              """Could not Fit parabola""")
        self.draw_fit(self.popt)
        e_mass = self.calculateEffectiveMass(self.popt[0])
        eff_e_mass = e_mass/m_e
        self.text_field.setText('m_eff/m_e: {:.2e}'.format(eff_e_mass))

    def draw_fit(self, popt):
        lower = min(self.xpoints)
        upper = max(self.xpoints)
        xvals = np.linspace(lower, upper, 100)
        yvals = [self.fitfunction(x, popt[0], popt[1], popt[2]) for x in xvals]
        self.out_fit, = self.thisax.plot(xvals, yvals, 'r', lw=2)
        self.thisax.figure.canvas.draw()

    def fitfunction(self, x, a, b, c):
        return a*(x-c)**2 + b

    def calculateEffectiveMass(self, parameter):
        test = hbar**2 * 16.021766 / (2*m_e)
        return test/parameter

    def init_widget(self):
        # self.parabola_widget = QWidget(self)

        self.box = QGroupBox('Fit Parabola')
        self.parabola_layout = QHBoxLayout()

        self.fitbutton = QPushButton('&Fit Parabola', self)
        self.selectbutton = QPushButton('&Select Points', self)
        self.clearbutton = QPushButton('&Clear', self)
        self.discobutton = QPushButton('&Stop Selection', self)
        self.text_field = QTextEdit(self)
        self.text_field.setReadOnly(True)
        self.text_field.setPlaceholderText('Eff mass [eV]')

        self.fitbutton.released.connect(self.perform_fit)
        self.selectbutton.released.connect(self.init_cursor_active)
        self.clearbutton.released.connect(self.clear_all)
        self.discobutton.released.connect(self.disconnect)

        self.parabola_layout.addWidget(self.fitbutton)
        self.parabola_layout.addWidget(self.selectbutton)
        self.parabola_layout.addWidget(self.clearbutton)
        self.parabola_layout.addWidget(self.discobutton)
        self.parabola_layout.addWidget(self.text_field)

        self.box.setLayout(self.parabola_layout)

    def get_widget(self):
        return self.box

    def update_parabola(self):
        self.init_plot()
