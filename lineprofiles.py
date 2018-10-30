import numpy as np

# import matplotlib.pyplot as plt
# from scipy.constants import hbar, m_e
from scipy.interpolate import interp2d
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    # QApplication,
    QWidget,
    QPushButton,
    # QVBoxLayout,
    # QHBoxLayout,
    # QMenu,
    # QMessageBox,
    # QSizePolicy,
    # QFileDialog,
    # QSlider,
    # QLabel,
    # QScrollBar,
    QRadioButton,
    QGroupBox,
    # QInputDialog,
    QLineEdit,
    QGridLayout,
)

from dragpoints import DraggablePlotExample


class LineProfiles(QWidget):
    """ Attaches stuff for lineprofile to current 2D Plot """

    def __init__(self, twodfig, xprof_ax, yprof_ax, parent, parent_layout):
        # Set up default values
        self.parent_layout = parent_layout
        self.parent = parent
        self.current_hline = False
        self.current_vline = False
        self.cid = False
        self.cid_hover = False
        self.xy_chooser = "x"
        self.breadth = 0.0
        self.free_xy_list = []
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
        """ Disconnect from figure """
        self.ax.figure.canvas.mpl_disconnect(self.cid)
        self.cid = False
        try:
            self.free_plot.disconnect()
            self._figure.canvas.mpl_disconnect(self.click_cid)
            self.ax.figure.mpl.disconnect(self.free_release_cid)
        except ValueError:
            pass

    def init_cursor_active_x(self):
        """ Choose x profile generator """
        self.xy_chooser = "x"
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                "button_press_event", self.on_press
            )

    def init_cursor_active_y(self):
        """ Choose y profile generator """
        self.xy_chooser = "y"
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                "button_press_event", self.on_press
            )

    def on_press(self, event):
        """ Show hline or vline, depending on lineprof chosen """
        if event.button == 3:  # Use right click
            if self.xy_chooser == "x":
                if self.current_hline:
                    self.current_hline.remove()
                self.current_hline = self.ax.axhline(event.ydata)

                x1, y1 = self.lineprofileX(self.data, self.ranges, event.ydata)
                self.xprof_ax.plot(x1, y1, zorder=-1)
                self.xprof_ax.set_xlim(min(x1), max(x1))
                self.xprof_ax.figure.canvas.draw()

            if self.xy_chooser == "y":
                if self.current_vline:
                    self.current_vline.remove()
                self.current_vline = self.ax.axvline(event.xdata)

                x2, y2 = self.lineprofileY(self.data, self.ranges, event.xdata)
                # print(self.x2, self.y2)
                self.yprof_ax.plot(y2, x2, zorder=-1)
                self.yprof_ax.set_ylim(max(x2), min(x2))
                self.yprof_ax.figure.canvas.draw()

            self.ax.figure.canvas.draw()  # redraw

    def free_on_release(self, event):
        """ callback method for mouse release event
        :type event: MouseEvent
        """
        # if event.button == 3 and event.inaxes in [self._axes] and self._dragging_point:

        self.free_plot._update_plot()
        self.free_ax.cla()
        xy1, xy2 = self.free_plot.get_data()
        try:
            outx, outprof = self.lineprofileFree(xy1, xy2, 500)
            self.free_line, = self.free_ax.plot(outx, outprof)
            self.free_ax.figure.canvas.draw()
        except ValueError:
            pass

    def clear_all(self):
        """ Clear Lineprofiles and h,v lines """
        # Remove all lines
        self.xprof_ax.clear()
        self.yprof_ax.clear()
        if self.current_hline:
            self.current_hline.remove()
        if self.current_vline:
            self.current_vline.remove()
        self.current_hline = False
        self.current_vline = False
        try:
            self.free_ax.clear()
            # self.free_ax.cla()
        except:
            pass

        # Redraw to show clearance
        self.twodfig.figure.canvas.draw()
        self.xprof_ax.figure.canvas.draw()
        self.yprof_ax.figure.canvas.draw()

    def init_free_prof(self):
        self.xy_chooser = 'free'
        self.free_plot = DraggablePlotExample(self.ax.figure, self.ax)
        self.free_fig = Figure(figsize=(5, 0.2 * 5), dpi=100, tight_layout=True)
        self.free_ax = self.free_fig.add_subplot(111)
        self.free_canvas = FigureCanvas(self.free_fig)
        self.free_canvas.setMinimumHeight(200)
        self.parent_layout.addWidget(self.free_canvas, 2, 0, 1, 2)
        self.free_release_cid = self.ax.figure.canvas.mpl_connect(
            "button_release_event", self.free_on_release
        )

        # self.plotDraggablePoints([0.1, 0.1], [0.2, 0.2], [0.1, 0.1])

    def processing_data_interpolator(self, data, thisrange):
        """ Generates interpolator """
        data_shape = data.shape
        xvals = np.linspace(thisrange[0], thisrange[1], data_shape[1])
        yvals = np.linspace(thisrange[3], thisrange[2], data_shape[0])
        idata = interp2d(xvals, yvals, data, fill_value=0.0)
        return idata, xvals, yvals

    def lineprofileFree(self, strtpnt: np.array, endpnt: np.array, N: int):
        """
        Returns the line profile along an arbitrary line with N steps
        :param strtpnt: 2-point array [x,y] for starting position
        :param endpnt: 2-point array [x,y] for end position
        :param N: integer on how many steps
        :return: lineprofile as a 1d array
        """
        N = int(N)
        dv = (np.array(endpnt) - np.array(strtpnt)) / N
        profile = [
            self.idata(strtpnt[0] + dv[0] * i, strtpnt[1] + dv[1] * i)[0]
            for i in range(N)
        ]
        return np.linspace(0, 1, N), profile

    def lineprofileX(
        self, data: np.array, current_range: list, yval: float, breadth=0.1
    ):
        """ Returns Lineprofile along X"""
        breadth = self.breadth
        # self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
        #     data, current_range
        # )
        profile = np.sum(
            self.idata(
                self.xvals,
                [yval - 0.5 * breadth + breadth * float(i) / 20.0 for i in range(21)],
            ),
            axis=0,
        )
        return self.xvals, profile

    def lineprofileY(
        self, data: np.array, current_range: list, xval: float, breadth=0.1
    ):
        """ Returns Lineprofile along Y"""
        breadth = self.breadth
        # self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
        #     data, current_range
        # )
        profile = np.sum(
            self.idata(
                [xval - 0.5 * breadth + breadth * float(i) / 20.0 for i in range(21)],
                self.yvals,
            ),
            axis=1,
        )
        # return self.yvals[::-1], self.profile
        return self.yvals, profile

    def get_breadth(self):
        if not self.input_breadth.text() == "":
            self.breadth = float(self.input_breadth.text())
        else:
            self.breadth = 0.0

    def init_widget(self):
        """ Creates widget and layout """
        self.box = QGroupBox("Line Profiles")
        # self.this_layout = QHBoxLayout()
        self.this_layout = QGridLayout()

        # Create Radio Buttond
        self.selectbutton_x = QRadioButton("&X Lineprofile", self)
        self.selectbutton_y = QRadioButton("&Y Lineprofile", self)
        self.selectbutton_free = QRadioButton("&Free Lineprofile", self)
        self.discobutton = QRadioButton("&Stop Selection", self)
        self.discobutton.setChecked(True)

        # Set Tooltips
        self.selectbutton_x.setToolTip('Use Right-Click')
        self.selectbutton_y.setToolTip('Use Right-Click')
        self.selectbutton_free.setToolTip('Use Right-Click')
        
        # self.selectbutton_x = QPushButton('&X Lineprofile', self)
        # self.selectbutton_y = QPushButton('&Y Lineprofile', self)
        self.clearbutton = QPushButton("&Clear", self)

        self.input_breadth = QLineEdit(self)
        self.input_breadth.setPlaceholderText("Breadth")

        self.selectbutton_x.clicked.connect(self.init_cursor_active_x)
        self.selectbutton_y.clicked.connect(self.init_cursor_active_y)
        self.selectbutton_free.clicked.connect(self.init_free_prof)
        self.discobutton.clicked.connect(self.disconnect)
        self.clearbutton.released.connect(self.clear_all)

        self.input_breadth.returnPressed.connect(self.get_breadth)

        self.this_layout.addWidget(self.selectbutton_x, 0, 0)
        self.this_layout.addWidget(self.selectbutton_y, 1, 0)
        self.this_layout.addWidget(self.selectbutton_free, 2, 0)
        self.this_layout.addWidget(self.clearbutton, 0, 1)
        self.this_layout.addWidget(self.input_breadth, 1, 1)
        self.this_layout.addWidget(self.discobutton, 2, 1)

        self.box.setLayout(self.this_layout)

    def get_widget(self):
        """ Returns this widget """
        return self.box

    def update_data_extent(self, data, extent):
        """ Update current data and extent """
        self.data = data
        self.ranges = extent
        self.idata, self.xvals, self.yvals = self.processing_data_interpolator(
            data, extent
        )
        # self.clear_all()

    def get_axes(self):
        return self.xprof_ax, self.yprof_ax
