import sys
import os
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar,\
    QRadioButton, QGroupBox, QGridLayout
import matplotlib
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")

import pyqtgraph as pg

from load_sp2 import Sp2_loader, LoadHDF5
from plot_2d import TwoD_Plotter
from mpl_canvas_class import MyMplCanvas
from data_treatment import Calc_K_space
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
from generate_maps import VerticalSlitPolarScan
# from new_k_window import K_Window


class ApplicationWindow(QMainWindow):
    ''' Main Application Window '''

    def __init__(self):
        self.hd5mode = False
        self.current_data = []
        self.angle_data = []
        self.angle_extent = []
        self.current_data_k = []
        self.current_data_k = []
        self.current_extent = []
        self.slider_pos = 0
        self.k_space_generated = False
        self.data_are_loaded = False
        self.select_k_space = False
        self.k_data = []
        self.k_extent = []
        self.new_current_data = []
        self.new_current_extent = []
        self._current_labelname = ''
        QMainWindow.__init__(self)
        # self.resize(1000, 600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPyES")

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction(
            '&Load Sp2 Files', self.choose_sp2)
        self.file_menu.addAction(
            '&Load NXS Files', self.choose_nxs)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

        # Set up Mapping Menu
        self.map_menu = QMenu('&Map', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.map_menu)

        # self.map_menu.addAction('&Plot_2D', self.init_k_window)

        # Set up Interaction Menu
        self.interact_menu = QMenu('&2D', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.interact_menu)
        # self.interact_menu.addAction('&Fit_parabola', self.fit_parabola)
        # self.interact_menu.addAction('&Lineprofile', self.lineprofile)

        # Set up Help Menu
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        # Set up subwidgets

        # Set up buttons
        # self.k_button = QPushButton('&Convert to k-space', self)
        # self.k_button.released.connect(self.gen_k_space)

        # Instantiate widgets
        self.main_widget = QWidget(self)

        # self.twoD_widget = TwoD_Plotter(self.main_widget)  # Start 2d plotter
        # self.twoD_label = QLabel()
        # self.twoD_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.twoD_label.setText('')

        # Set up radio buttons

        # self.angle_k_button_group = QGroupBox('Choose Dimensions to work in')
        # self.angle_button = QRadioButton("&Angles", self.main_widget)
        # self.angle_button.setChecked(True)
        # self.angle_button.clicked.connect(self.angle_k_button_state)
        # # self.angle_button.clicked.connect(
        #     lambda: self.angle_k_button_state(self.angle_button))

        # self.k_button = QRadioButton("K-&Space", self.main_widget)
        # self.k_button.clicked.connect(self.angle_k_button_state)
        # self.k_button.toggled.connect(
        #     lambda: self.angle_k_button_state(self.k_button))

        # Instantiate Layout and add widgets
        self.over_layout = QGridLayout(self.main_widget)

        # self.pgplot = pg.PlotWidget()
        # self.imv = pg.ImageView(self.pgplot)
        # self.imv.show()
        # self.over_layout.addWidget(self.pgplot)

        # self.over_layout = QVBoxLayout(self.main_widget)

        # layout.addWidget(t)
        # self.over_layout.addWidget(self.twoD_widget, 1, 0)
        # self.over_layout.addWidget(self.twoD_label,  0, 0)
        # self.over_layout.addWidget(self.pgplot, 0, 1)

        # # Init Parabola Widget and add
        # self.FitParGui = FitParabola(self.twoD_widget.axes, self.main_widget)
        # self.FitParGui.init_widget()
        # self.parabola_widget = self.FitParGui.get_widget()
        # self.over_layout.addWidget(self.parabola_widget, 1, 2)

        # # Init LineProfile Widget and add
        # self.LineProf = LineProfiles(self.twoD_widget, self.main_widget)
        # self.LineProf.init_widget()
        # self.lineprof_widget = self.LineProf.get_widget()
        # self.over_layout.addWidget(self.lineprof_widget, 0, 2)

        # Set up angle and k radio buttons

        # self.radio_layout = QHBoxLayout()

        # self.radio_layout.addWidget(self.angle_button)
        # self.radio_layout.addWidget(self.k_button)

        # self.angle_k_button_group.setLayout(self.radio_layout)
        # self.over_layout.addWidget(self.angle_k_button_group, 2, 0)

        # self.over_layout.addWidget(self.lineprof_widget)

        # self.setLayout(self.over_layout)
        # self.over_layout.addLayout(self, self.over_layout)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # self.lineprofile()  # Start lineprofiles

        self.statusBar().showMessage("Initial Tests", 2000)

    def fileQuit(self):
        ''' Closes current instance '''
        self.close()

    def closeEvent(self, ce):
        ''' Closes current event '''
        self.fileQuit()

    def about(self):
        ''' Prints about '''
        QMessageBox.about(self, "About",
                          """ARPyES""")
        self.vertical_slit_maps()

    def fit_parabola(self):
        # FitPar = FitParabola(self.twoD_widget.fig)
        self.FitParGui = FitParabola(self.twoD_widget.axes, self.main_widget)
        self.FitParGui.init_widget()
        self.parabola_widget = self.FitParGui.get_widget()
        self.over_layout.addWidget(self.parabola_widget, 1, 2)

    def lineprofile(self):
        # FitPar = FitParabola(self.twoD_widget.fig)
        self.LineProf = LineProfiles(self.twoD_widget, self.main_widget)
        self.LineProf.init_widget()
        self.lineprof_widget = self.LineProf.get_widget()
        self.over_layout.addWidget(self.lineprof_widget, 0, 2)

    def angle_k_button_state(self):
        ''' Switch to angle or k space data set '''
        if not self.k_space_generated:
            self.k_space_generated = True
            # QMessageBox.about(self, 'Error',
            #   'Please wait for K-space to finish processing')
        else:
            if self.data_are_loaded:
                self.twoD_widget.instance_counter = 0  # Reset plot
                # if button.text() == '&Angles':
                # if self.angle_button.isChecked():
                self.select_k_space = False
                self.processing_data = self.angle_data
                self.processing_extent = self.angle_extent
                self.update_current_data()

                self.initialize_2D_plot()
                self.update_widgets()
            # else:
            #     self.angle_button.setChecked(True)
            #     QMessageBox.about(self, 'Warning',
            #                       'Please load some data')

    def choose_sp2(self):
        self.sp2 = Sp2_loader()
        many_files = QFileDialog.getOpenFileNames(
            self, 'Select one or more files to open',
            '/home/yannic/Documents/stuff/feb/06/sampl2map/')
        self.loaded_filenames = self.sp2.tidy_up_list(many_files[0])
        self.statusBar().showMessage("Loading Data...", 2000)
        # self.loaded_filenames = ['mos2_2_003.sp2', 'mos2_2_015.sp2']

        self.angle_data, self.angle_extent = self.sp2.read_multiple_sp2(
            self.loaded_filenames)
        self.load_multiple_files()

    def choose_nxs(self):
        self.hd5mode = True
        self.sp2 = Sp2_loader()
        self.sp2.multi_file_mode = True
        location = QFileDialog.getOpenFileNames(
            self, 'Select one NXS file to open',
            '/home/yannic/Documents/PhD/ARPyES/zDisp/SnSe/')
        location = str(location[0][0])
        self.H5loader = LoadHDF5(location)
        self.angle_data, self.angle_extent, self.p_min, self.p_max =\
            self.H5loader.return_data()
        self.load_multiple_files()

    def load_multiple_files(self):
        # self.lineprofile()  # Start lineprofiles
        # self.fit_parabola()

        if not self.sp2.multi_file_mode:
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.new_current_data = self.processing_data
            self.new_current_extent = self.processing_extent

            # self.initialize_2D_plot()
        else:
            stack_size = self.angle_data.shape[-1]
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.update_current_data()

            # self.twoD_slider = self.add_slider(0, stack_size)
            # self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)
            # self.over_layout.addWidget(self.twoD_slider, 3, 0)
            # self.initialize_2D_plot()

            # self.imv.setImage(self.new_current_data)
            # self.over_layout.addWidget()
            # self.pgplot.image(self.new_current_data)
        self.update_widgets()
        if not self.hd5mode:
            self._current_labelname = os.path.basename(
                self.loaded_filenames[0])
            # self.twoD_label.setText(self._current_labelname)
        self.data_are_loaded = True

        self.new_twoD_widget = TwoD_Plotter(self.processing_data,
                                            self.processing_extent,
                                            self.main_widget)
        self.over_layout.addWidget(self.new_twoD_widget, 1, 0)

        # Set data for LineProf
        # self.LineProf.update_data_extent(self.new_current_data,
        #                                  self.new_current_extent)

        # After loading files, instantiate class for data handling
        # self.k_thread = Calc_K_space(
        #     self.angle_data, self.angle_extent)
        # self.k_thread.finished.connect(self.get_k_space)
        # self.statusBar().showMessage("Converting to k-space in background...",
        #                              2000)
        # self.k_thread.start()

    def vertical_slit_maps(self):
        All_maps = VerticalSlitPolarScan(
            self.processing_data, self.processing_extent,
            self.p_min, self.p_max)
        # self.edc = All_maps.EDC(0.0, 0.0, 24, 25, 9, 15, NE=50)
        xmin, xmax, ymin, ymax = -1., 1.6, -1., 1.6
        starttime = time.time()
        # self.k_slice = All_maps.SliceK_E_range(66.16, 67.33, 0.03, 0., 0.,
        #                                        kxmin=xmin, kxmax=xmax, kymin=ymin, kymax=ymax)
        print('Calctime python: {}'.format(time.time()-starttime))
        starttime = time.time()
        self.k_slice = All_maps.slice_K_fortran(66.16, 67.84, 0.03, 0., 0,
                                                kxmin=xmin, kxmax=xmax,
                                                kymin=ymin, kymax=ymax)
        # self.k_slice = All_maps.slice_K_fortran(67.33, 67.33, 0.01, 0., 0,
        #                                         kxmin=xmin, kxmax=xmax,
        #                                         kymin=ymin, kymax=ymax)
        extent_stack = list([[xmin, xmax, ymin, ymax]]) * \
            self.k_slice.shape[-1]
        # fig, ax = matplotlib.pyplot.subplots()

        # ax.imshow(self.k_slice[:, :, 0], extent=[xmin, xmax, ymin, ymax])
        # ax.set_xlim(xmin, xmax)
        # ax.set_ylim(ymin, ymax)
        print('Calctime fortran: {}'.format(time.time()-starttime))
        self.KWin = K_Window(self.k_slice, extent_stack)
        self.KWin.show()

        # # erange = np.linspace(24, 25, len(self.edc))
        # # matplotlib.pyplot.plot(erange, self.edc)
        # matplotlib.pyplot.show()

    def update_current_data(self):
        self.new_current_data = self.processing_data[:, :, self.slider_pos]
        self.new_current_extent = self.processing_extent[self.slider_pos]

    def update_widgets(self):
        pass
        # self.twoD_widget.LineProf.update_data_extent(self.new_current_data,
        #                                              self.new_current_extent)
        # self.twoD_widget.FitParGui.update_parabola()

    def get_k_space(self):
        self.k_data, self.k_extent, self.k_space_generated = self.k_thread.get()
        # self.current_data_k = self.k_data[:, :, self.slider_pos]
        # self.current_extent_k = self.k_extent[self.slider_pos]
        self.statusBar().showMessage("k-space conversion finished!", 2000)

    def initialize_2D_plot(self):
        self.twoD_widget.update_2d_data(self.new_current_data)
        self.twoD_widget.update_2dplot(self.new_current_extent)

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
        if not self.hd5mode:
            self._current_labelname = os.path.basename(
                self.loaded_filenames[self.slider_pos])
            self.twoD_label.setText(self._current_labelname)
        self.update_current_data()
        self.initialize_2D_plot()

        self.update_widgets()


class K_Window(QMainWindow):
    ''' Instantiates new window for k data treatment '''

    def __init__(self, k_stack, k_extent):
        QMainWindow.__init__(self)
        # super.__init__(self)
        self.setWindowTitle('K Data Handler')

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)
        self.k_win_widget = QWidget(self)
        self.k_k_widget = TwoD_Plotter(
            k_stack, k_extent, self.k_win_widget
        )  # Start 2d plotter
        self.over_layout = QGridLayout(self.k_win_widget)
        self.over_layout.addWidget(self.k_k_widget, 1, 0)
        self.k_win_widget.setFocus()
        self.setCentralWidget(self.k_win_widget)
        # self.k_k_label = QLabel()
        # self.k_k_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.k_k_label.setText('')
        # self.k_k_widget.update_2d_data(k_stack)
        # self.k_k_widget.update_2dplot(k_extent)

    def fileQuit(self):
        ''' Closes current instance '''
        self.close()


if __name__ == '__main__':
    # test = Sp2_loader()
    # stack, ranges = test.read_multiple_sp2(
    #     ['mos2_2_003.sp2', 'mos2_2_015.sp2'])
    # handler = HandleNielsSpectra(stack, ranges)
    # out, extent = handler.convert_all_to_k()

    # sys.exit()
    qApp = QApplication(sys.argv)

    aw = ApplicationWindow()
    # aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
