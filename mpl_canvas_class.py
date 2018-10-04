from __future__ import unicode_literals
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec


# class MyMplCanvas(FigureCanvas):
class MyMplCanvas(QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=10, dpi=100,
                 multifig=False):
        super().__init__()
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if not multifig:
            self.axes = self.fig.add_subplot(111)
        else:
            gs = gridspec.GridSpec(5, 5)
            self.axes = self.fig.add_subplot(gs[0:4, 0:4])  # 2D Data
            self.xprof_ax = self.fig.add_subplot(gs[4, :-1])  # LineProfile X
            self.yprof_ax = self.fig.add_subplot(gs[:-1, 4])  # LineProfile Y

        self.compute_initial_figure()

        self.canvas = FigureCanvas(self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.fig.tight_layout()
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def compute_initial_figure(self):
        pass
