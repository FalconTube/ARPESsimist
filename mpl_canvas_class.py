from __future__ import unicode_literals
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout, QGridLayout,\
    QSlider
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles


# class MyMplCanvas(FigureCanvas):
class MyMplCanvas(QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        super().__init__()
        self.parent = parent
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig_xax = Figure(figsize=(width, 0.2*height), dpi=dpi)
        self.fig_yax = Figure(figsize=(0.2*width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)  # 2D Data
        self.xprof_ax = self.fig_xax.add_subplot(111)  # LineProfile X
        self.yprof_ax = self.fig_yax.add_subplot(111)  # LineProfile Y

        self.compute_initial_figure()

        self.canvas = FigureCanvas(self.fig)

        # print('Setting size policy')
        # self.canvas.setSizePolicy(QSizePolicy.Expanding)
        # print('Finished with size policy')
        sizePolicy = QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        self.x_canvas = FigureCanvas(self.fig_xax)
        self.y_canvas = FigureCanvas(self.fig_yax)
        self.canvas.setSizePolicy(sizePolicy)
        # self.canvas.updateGeometry(self)
        # self.x_canvas.setSizePolicy(QSizePolicy.Preferred)
        # self.y_canvas.setSizePolicy(QSizePolicy.Preferred)
        self.setParent(self.parent)
        # self.canvas.setSizePolicy(self,
        #                           QSizePolicy.Expanding,
        #                           QSizePolicy.Expanding)
        # self.canvas.updateGeometry(self)

        self.fig.tight_layout()
        self.toolbar = NavigationToolbar(self.canvas, self)

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

    def compute_initial_figure(self):
        pass

    def fit_parabola(self):
        self.FitParGui = FitParabola(self.axes, self)
        self.FitParGui.init_widget()
        self.parabola_widget = self.FitParGui.get_widget()
        self.main_layout.addWidget(self.parabola_widget)

    def lineprofile(self):
        self.LineProf = LineProfiles(self.axes, self.xprof_ax, self.yprof_ax,
                                     self.parent)
        self.LineProf.init_widget()
        self.lineprof_widget = self.LineProf.get_widget()
        self.grid_layout.addWidget(self.lineprof_widget, 1, 1)

    def add_slider(self, lower: int, upper: int):
        slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        slider_bar.setRange(lower, upper-1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        return slider_bar
