from __future__ import unicode_literals
import matplotlib

# Make sure that we are using QT5
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QSlider,
    QComboBox,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
import matplotlib.pyplot as plt

# matplotlib.rcParams['toolbar'] = 'toolmanager'



# class MyMplCanvas(FigureCanvas):
class MyMplCanvas(QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        super().__init__()
        self.parent = parent
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.fig_xax = Figure(figsize=(width, 0.2 * height), dpi=dpi, tight_layout=True)
        self.fig_yax = Figure(figsize=(0.2 * width, height), dpi=dpi, tight_layout=True)

        self.axes = self.fig.add_subplot(111)  # 2D Data
        # self.axes.invert_xaxis()
        self.xprof_ax = self.fig_xax.add_subplot(111, sharex=self.axes)  # LineProfile X
        self.yprof_ax = self.fig_yax.add_subplot(111, sharey=self.axes)  # LineProfile Y

        self.compute_initial_figure()

        self.canvas = FigureCanvas(self.fig)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        self.x_canvas = FigureCanvas(self.fig_xax)
        self.x_canvas.setMinimumHeight(200)
        # xPolicy = QSizePolicy(QSizePolicy.Minimum())
        self.y_canvas = FigureCanvas(self.fig_yax)
        self.canvas.setSizePolicy(sizePolicy)

        self.setParent(self.parent)

        self.toolbar = NavigationToolbar(self.canvas, self)
        # self.toolbar = MyToolBar(self.canvas, self)
        
        self.cb = QComboBox()
        self.cb.addItem("terrain")
        self.cb.addItem("viridis")
        self.cb.addItem("plasma")
        self.cb.addItem("inferno")
        self.cb.addItem("magma")
        self.cb.addItem("Greys")
        self.toolbar.addWidget(self.cb)
        # thisslider = QSlider(QtCore.Qt.Horizontal, self)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toolbar)
        # self.data_slider = self.add_slider(0, 1)
        self.grid_layout = QGridLayout(self)
        self.main_layout.addLayout(self.grid_layout)

        self.grid_layout.addWidget(self.canvas, 0, 0)
        self.grid_layout.addWidget(self.x_canvas, 1, 0)
        self.grid_layout.addWidget(self.y_canvas, 0, 1)
        # self.fit_parabola()
        self.lineprofile()
        self.show()

    # def set_message(self, s):
    #     self.message.emit(s)
    #     if self.coordinates:
    #         self.locLabel.setText(s)

    def compute_initial_figure(self):
        pass

    def fit_parabola(self):
        self.FitParGui = FitParabola(self.axes, self)
        self.FitParGui.init_widget()
        self.parabola_widget = self.FitParGui.get_widget()
        self.main_layout.addWidget(self.parabola_widget)

    def lineprofile(self):
        self.LineProf = LineProfiles(
            self.axes, self.xprof_ax, self.yprof_ax, self.parent, self.grid_layout
        )
        self.LineProf.init_widget()
        self.lineprof_widget = self.LineProf.get_widget()
        self.grid_layout.addWidget(self.lineprof_widget, 1, 1)
