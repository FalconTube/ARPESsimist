import numpy as np

# import matplotlib.pyplot as plt
# from scipy.constants import hbar, m_e
from scipy.interpolate import interp2d
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import RectangleSelector

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

import matplotlib.pyplot as plt

from dragpoints import DraggablePlotExample
from edc_fitting import EDCfitter
from lmfit.models import PseudoVoigtModel
from lmfit.models import LorentzianModel
from lmfit.models import LinearModel
from lmfit.models import GaussianModel
from scipy.signal import savgol_filter



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
            # self.free_plot._figure.canvas.mpl_disconnect(self.click_cid)
            self.ax.figure.mpl.disconnect(self.free_release_cid)
            self.ax.figure.mpl.disconnect(self.rect_cid)
        except:
            pass

    def init_cursor_active_x(self):
        """ Choose x profile generator """
        self.xy_chooser = "x"
        self.disconnect()
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                "button_press_event", self.on_press
            )

    def init_cursor_active_y(self):
        """ Choose y profile generator """
        self.xy_chooser = "y"
        self.disconnect()
        if not self.cid:
            self.cid = self.ax.figure.canvas.mpl_connect(
                "button_press_event", self.on_press
            )

    def on_press(self, event):
        """ Show hline or vline, depending on lineprof chosen """
        if event.button == 3:  # Use right click
            if self.xy_chooser == "x":
                if self.current_hline:
                    try:
                        self.current_hline.remove()
                    except:
                        pass
                self.current_hline = self.ax.axhline(event.ydata, color="#ff7f0e")

                x1, y1 = self.lineprofileX(self.data, self.ranges, event.ydata)
                self.xprof_ax.relim()
                self.xprof_ax.plot(x1, y1, zorder=-1)
                # self.xprof_ax.set_xlim(min(x1), max(x1))
                self.xprof_ax.figure.canvas.draw()

            if self.xy_chooser == "y":
                if self.current_vline:
                    try:
                        self.current_vline.remove()
                    except:
                        pass
                self.current_vline = self.ax.axvline(event.xdata, color="#ff7f0e")

                x2, y2 = self.lineprofileY(self.data, self.ranges, event.xdata)
                # print(self.x2, self.y2)
                self.yprof_ax.relim()
                self.yprof_ax.plot(y2, x2, zorder=-1)
                # self.yprof_ax.set_ylim(min(x2), max(x2))
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
        self.line_remover(self.xprof_ax)
        self.line_remover(self.yprof_ax)

        if self.current_hline:
            self.current_hline.remove()
        if self.current_vline:
            self.current_vline.remove()
        self.current_hline = False
        self.current_vline = False
        try:
            self.free_plot.clear_line()
        except:
            pass
        try:
            self.free_ax.cla()
        except:
            pass

        # Redraw to show clearance
        self.twodfig.figure.canvas.draw()
        self.xprof_ax.figure.canvas.draw()
        self.yprof_ax.figure.canvas.draw()
        self.free_ax.figure.canvas.draw()

    def line_remover(self, axis):
        """ Somehow cannot just iterate over all lines,
        must do it with while loop. Strange but works... """
        while len(axis.lines) > 0:
            for line in axis.lines:
                line.remove()

    def init_free_prof(self):
        self.xy_chooser = "free"
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
        return self.yvals[::-1], profile
        # return self.yvals, profile

    def get_breadth(self):
        if not self.input_breadth.text() == "":
            self.breadth = float(self.input_breadth.text())
        else:
            self.breadth = 0.0

    def init_rectangle(self):
        def line_select_callback(eclick, erelease):
            "eclick and erelease are the press and release events"
            self.rect_x1, self.rect_y1 = eclick.xdata, eclick.ydata
            self.rect_x2, self.rect_y2 = erelease.xdata, erelease.ydata

        def toggle_selector(event):
            print(" Key pressed.")
            if event.key in ["Q", "q"] and toggle_selector.RS.active:
                print(" RectangleSelector deactivated.")
                toggle_selector.RS.set_active(False)
            if event.key in ["A", "a"] and not toggle_selector.RS.active:
                print(" RectangleSelector activated.")
                toggle_selector.RS.set_active(True)

        # drawtype is 'box' or 'line' or 'none'
        toggle_selector.RS = RectangleSelector(
            self.ax,
            line_select_callback,
            drawtype="box",
            useblit=False,
            button=[1, 3],  # don't use middle button
            #    minspanx=5, minspany=5,
            spancoords="data",
            interactive=True,
        )
        self.rect_cid = self.ax.figure.canvas.mpl_connect(
            "key_press_event", toggle_selector
        )

    def find_maxima(self):
        max_x = []
        max_y = []
        x_pos = np.logical_and(self.rect_x1 < self.xvals, self.xvals < self.rect_x2)
        y_pos = np.logical_and(self.rect_y1 < self.yvals, self.yvals < self.rect_y2)
        x_range = self.xvals[x_pos]
        y_range = self.yvals[y_pos]
        # print(x_range, y_range)
        fig = plt.figure()
        for n, i in enumerate(y_range):
            print(n/len(y_range)*100)
            raw_lineprof = self.idata(x_range, i)
            lineprof = savgol_filter(raw_lineprof, 51, 2)
            plt.plot(x_range, raw_lineprof, marker='.', linestyle=None)
            plt.plot(x_range, lineprof, marker=None, linestyle='-')
            pos_max = np.argmax(lineprof)
            max_x.append(x_range[pos_max])
            max_y.append(i)
            # self.fit_profile(x_range, lineprof)
        lim_before = self.ax.get_ylim()
        max_line = self.ax.scatter(
            max_x, max_y, s=50, facecolor="none", color="b", zorder=3
        )
        # Have to reset the ylim, don't know why this happens
        self.ax.set_ylim(lim_before)
        self.ax.figure.canvas.draw()  # redraw
        plt.show()
    
    def find_maxima_fit(self):
        max_x = []
        max_y = []
        x_pos = np.logical_and(self.rect_x1 < self.xvals, self.xvals < self.rect_x2)
        y_pos = np.logical_and(self.rect_y1 < self.yvals, self.yvals < self.rect_y2)
        x_range = self.xvals[x_pos]
        y_range = self.yvals[y_pos]
        # print(x_range, y_range)
        for n, i in enumerate(y_range):
            print(n/len(y_range)*100)
            lineprof = self.idata(x_range, i)
            # pos_max = np.argmax(lineprof)
            center = self.fit_profile(x_range, lineprof)
            max_x.append(center)
            max_y.append(i)
            
        lim_before = self.ax.get_ylim()
        max_line = self.ax.scatter(
            max_x, max_y, s=50, facecolor="none", color="r", zorder=3
        )
        # Have to reset the ylim, don't know why this happens
        self.ax.set_ylim(lim_before)
        self.ax.figure.canvas.draw()  # redraw

        # finder = EDCfitter(self.idata)
    
    def fit_profile(self, x, y):
        # pseudovoigt = PseudoVoigtModel()
        fitmod = GaussianModel()
        
        background = LinearModel()
        mod = fitmod + background
        # mod = VoigtModel()
        # mod = LorentzianModel()
        pars = fitmod.guess(y, x=x)
        linpars = background.guess(y, x=x)
        allpars = pars + linpars
        out = mod.fit(y, allpars, x=x)
        center = out.values['center']
        return center


    def init_widget(self):
        """ Creates widget and layout """
        self.box = QGroupBox("Line Profiles")
        # self.this_layout = QHBoxLayout()
        self.this_layout = QGridLayout()

        # Create Radio Buttons
        self.selectbutton_x = QRadioButton("&X Lineprofile", self)
        self.selectbutton_y = QRadioButton("&Y Lineprofile", self)
        self.selectbutton_free = QRadioButton("&Free Lineprofile", self)
        self.selectbutton_rectangle = QRadioButton("&Select Rectangle", self)
        self.discobutton = QRadioButton("&Stop Selection", self)
        self.discobutton.setChecked(True)
        self.clearbutton = QPushButton("&Clear", self)
        self.maximabutton = QPushButton("&Find Maxima", self)
        self.maximabutton_fit = QPushButton("&Find Maxima Fitting", self)

        self.input_breadth = QLineEdit(self)
        self.input_breadth.setPlaceholderText("Breadth")

        # Set Tooltips
        self.selectbutton_x.setToolTip("Use Right-Click")
        self.selectbutton_y.setToolTip("Use Right-Click")
        self.selectbutton_free.setToolTip("Use Right-Click")

        self.selectbutton_x.clicked.connect(self.init_cursor_active_x)
        self.selectbutton_y.clicked.connect(self.init_cursor_active_y)
        self.selectbutton_free.clicked.connect(self.init_free_prof)
        self.selectbutton_rectangle.clicked.connect(self.init_rectangle)
        self.discobutton.clicked.connect(self.disconnect)
        self.clearbutton.released.connect(self.clear_all)
        self.maximabutton.released.connect(self.find_maxima)
        self.maximabutton_fit.released.connect(self.find_maxima_fit)

        self.input_breadth.returnPressed.connect(self.get_breadth)

        self.this_layout.addWidget(self.selectbutton_x, 0, 0)
        self.this_layout.addWidget(self.selectbutton_y, 1, 0)
        self.this_layout.addWidget(self.selectbutton_free, 2, 0)
        self.this_layout.addWidget(self.selectbutton_rectangle, 3, 0)
        self.this_layout.addWidget(self.clearbutton, 0, 1)
        self.this_layout.addWidget(self.input_breadth, 1, 1)
        self.this_layout.addWidget(self.discobutton, 2, 1)
        self.this_layout.addWidget(self.maximabutton, 3, 1)
        self.this_layout.addWidget(self.maximabutton_fit, 4, 1)

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
