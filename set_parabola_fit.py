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
        self.setParent(parent)
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
        self.text_field.setText('{:.2e}'.format(e_mass))

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
        self.text_field.setPlaceholderText('Effective e-mass [eV]')

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

# class PointPeaks(object):
#     def __init__(self, fig):
#         self.hbar = 6.582e-16
#         self.me = 9.11e-31

#         self.FIG = fig
#         # self.thisax = self.FIG.add_subplot(111)
#         self.AX = self.FIG.get_axes()[0]
#         self.AX.grid(b=False)
#         plt.subplots_adjust(bottom=0.2)
#         self.AddPoints = True
#         self.axFit = plt.axes([0.1, 0.05, 0.1, 0.075])
#         self.axPnts = plt.axes([0.25, 0.05, 0.15, 0.075])
#         self.axRvrt = plt.axes([0.45, 0.05, 0.15, 0.075])
#         self.axUndo = plt.axes([0.65, 0.05, 0.15, 0.075])
#         self.bUndo = Button(self.axUndo, "Undo")
#         self.bUndo.on_clicked(self.undo)
#         self.bPnts = Button(self.axPnts, 'Add Points')
#         self.bPnts.on_clicked(self.add_points_Button)
#         self.bFit = Button(self.axFit, 'Fit')
#         self.bFit.on_clicked(self.fit)
#         self.bRvrt = Button(self.axRvrt, 'Revert')
#         self.bRvrt.on_clicked(self.revert)
#         self.cid = self.FIG.canvas.mpl_connect(
#             'button_press_event', self.onclick)
#         self.POPT = []
#         self.scat = self.AX.scatter([], [], c='b', s=50)
#         self.FIT, = self.AX.plot([], [], 'r', lw=2)

#         self.Xpoints = []
#         self.Ypoints = []

#     def add_background(self, image, xvals, yvals):
#         self.AX.imshow(image, extent=[xvals[0], xvals[1], yvals[0], yvals[1]],
#                        cmap=plt.get_cmap(
#             'Greys')0, aspect='auto', vmax=0.7)
#         self.AX.set_xlim(xvals[0], xvals[1])
#         self.AX.set_ylim(yvals[0], yvals[1])

#     def calculateEffectiveMass(self, parameter):
#         test = self.hbar**2 * 16.021766 / (2.*self.me)
#         return test/parameter

#     def undo(self, event):
#         if self.Xpoints:
#             self.Xpoints = self.Xpoints[:-1]
#             self.Ypoints = self.Ypoints[:-1]
#             self.update()

#     def add_points_Button(self, event):
#         self.AddPoints = not self.AddPoints
#         print(self.AddPoints)

#     def revert(self, event):
#         print("reverted")
#         self.Xpoints = []
#         self.Ypoints = []
#         self.update()

#     def update(self):
#         self.scat.remove()
#         try:
#             self.FIT.remove()
#         except:
#             pass
#         # for i in range(len(self.Xpoints)):
#         self.scat = self.AX.scatter(self.Xpoints, self.Ypoints, c='b', s=50)
#         plt.draw()

#     def fit(self, event):
#         print("fitting")
#         self.update()
#         popt, pcov = curve_fit(self.fitfunction, self.Xpoints, self.Ypoints)
#         self.draw_fit(popt=popt)
#         self.POPT = popt
#         print(self.calculateEffectiveMass(popt[0]), popt)

#     def draw_fit(self, popt):
#         xstart, xstop = self.AX.get_xlim()
#         xvals = np.linspace(xstart, xstop, 1000)
#         yvals = [self.fitfunction(x, popt[0], popt[1], popt[2]) for x in xvals]
#         self.FIT, = self.AX.plot(xvals, yvals, 'r', lw=2)
#         plt.draw()

#     def onclick(self, event):
#         # if event.inaxes != self.AX: return
#         if event.button == 3 and self.AddPoints:
#             if event.xdata and event.ydata:
#                 self.Xpoints.append(event.xdata)
#                 self.Ypoints.append(event.ydata)

#             self.update()
#             print(self.Xpoints)

#     def fitfunction(self, x, a, b, c):
#         return a*(x-c)**2 + b


# # imagelocation = 'SnSe_0_5Natrium_GY.txt'
# # image = np.loadtxt('./data/'+imagelocation)[::-1, :]
# # image = np.nan_to_num(image)
# # image /= np.amax(image)

# # fig = plt.figure()
# # ax = fig.add_subplot(111)
# # P = PointPeaks(fig)
# # # P.add_background(image, (-1.358,0.268), (-0.64,0.06)) # SnSeGY 1% Na
# # P.add_background(image, (-0.97724891, 0.26275109),
# #                  (-1.0880539, 0.15543628))  # SnSeGZ 1% Na
# # # P.add_background(image, (-1.2390191, 0.40264375),(-0.64417124,0.057998611)) # SnSeGY 0.5%Na
# # # P.add_background(image, (-0.97305498, 0.24869896),(-1.1994113,0.044078944)) # SnSeGZ 0.5%Na


# # plt.show()
