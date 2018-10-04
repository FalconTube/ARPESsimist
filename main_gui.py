import sys
import os
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar,\
    QRadioButton, QGroupBox
import matplotlib
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")

from load_sp2 import Sp2_loader
from plot_2d import TwoD_Plotter
from mpl_canvas_class import MyMplCanvas
from data_treatment import Calc_K_space
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
# from new_k_window import K_Window


class ApplicationWindow(QMainWindow):
    ''' Main Application Window '''

    def __init__(self):
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
            '&Load Files', self.load_multiple_files)
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
        self.interact_menu.addAction('&Fit_parabola', self.fit_parabola)
        self.interact_menu.addAction('&Lineprofile', self.lineprofile)

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

        self.twoD_widget = TwoD_Plotter(self.main_widget)  # Start 2d plotter
        self.twoD_label = QLabel()
        self.twoD_label.setAlignment(QtCore.Qt.AlignCenter)
        self.twoD_label.setText('')

        # Set up radio buttons

        self.angle_k_button_group = QGroupBox('Choose Dimensions to work in')
        self.angle_button = QRadioButton("&Angles", self.main_widget)
        self.angle_button.setChecked(True)
        self.angle_button.clicked.connect(self.angle_k_button_state)
        # self.angle_button.clicked.connect(
        #     lambda: self.angle_k_button_state(self.angle_button))

        self.k_button = QRadioButton("K-&Space", self.main_widget)
        self.k_button.clicked.connect(self.angle_k_button_state)
        # self.k_button.toggled.connect(
        #     lambda: self.angle_k_button_state(self.k_button))

        # Instantiate Layout and add widgets
        self.main_layout = QVBoxLayout(self.main_widget)
        # layout.addWidget(t)
        self.main_layout.addWidget(self.twoD_widget)
        self.main_layout.addWidget(self.twoD_label)

        # Set up angle and k radio buttons

        self.radio_layout = QHBoxLayout()

        self.radio_layout.addWidget(self.angle_button)
        self.radio_layout.addWidget(self.k_button)

        self.angle_k_button_group.setLayout(self.radio_layout)
        self.main_layout.addWidget(self.angle_k_button_group)

        # self.main_layout.addWidget(self.lineprof_widget)

        # self.setLayout(self.main_layout)

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

    def fit_parabola(self):
        # FitPar = FitParabola(self.twoD_widget.fig)
        self.FitParGui = FitParabola(self.twoD_widget.axes, self.main_widget)
        self.FitParGui.init_widget()
        self.parabola_widget = self.FitParGui.get_widget()
        self.main_layout.addWidget(self.parabola_widget)

    def lineprofile(self):
        # FitPar = FitParabola(self.twoD_widget.fig)
        self.LineProf = LineProfiles(self.twoD_widget, self.main_widget)
        self.LineProf.init_widget()
        self.lineprof_widget = self.LineProf.get_widget()
        self.main_layout.addWidget(self.lineprof_widget)

    def angle_k_button_state(self):
        ''' Switch to angle or k space data set '''
        if not self.k_space_generated:
            QMessageBox.about(self, 'Error',
                              'Please wait for K-space to finish processing')
        else:
            if self.data_are_loaded:
                self.twoD_widget.instance_counter = 0  # Reset plot
                # if button.text() == '&Angles':
                if self.angle_button.isChecked():
                    print('angle')
                    self.select_k_space = False
                    self.processing_data = self.angle_data
                    self.processing_extent = self.angle_extent
                    self.update_current_data()
                # if button.text() == 'K-&Space':
                if self.k_button.isChecked():
                    print('kspace')
                    self.select_k_space = True
                    self.processing_data = self.k_data
                    self.processing_extent = self.k_extent
                    self.update_current_data()
                self.initialize_2D_plot()
                self.update_widgets()
            else:
                self.angle_button.setChecked(True)
                QMessageBox.about(self, 'Warning',
                                  'Please load some data')

    def load_multiple_files(self):
        self.lineprofile()  # Start lineprofiles
        self.fit_parabola()
        self.sp2 = Sp2_loader()
        many_files = QFileDialog.getOpenFileNames(
            self, 'Select one or more files to open',
            '/home/yannic/Documents/stuff/feb/06/sampl2map/')
        self.loaded_filenames = self.sp2.tidy_up_list(many_files[0])
        self.statusBar().showMessage("Loading Data...", 2000)
        # self.loaded_filenames = ['mos2_2_003.sp2', 'mos2_2_015.sp2']

        self.angle_data, self.angle_extent = self.sp2.read_multiple_sp2(
            self.loaded_filenames)

        if not self.sp2.multi_file_mode:
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.new_current_data = self.processing_data
            self.new_current_extent = self.processing_extent

            self.initialize_2D_plot()
        else:
            stack_size = self.angle_data.shape[-1]
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.update_current_data()

            self.twoD_slider = self.add_slider(0, stack_size)
            self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)
            self.main_layout.addWidget(self.twoD_slider)
            self.initialize_2D_plot()
        self.update_widgets()
        self._current_labelname = os.path.basename(
            self.loaded_filenames[0])
        self.twoD_label.setText(self._current_labelname)
        self.data_are_loaded = True

        # Set data for LineProf
        # self.LineProf.update_data_extent(self.new_current_data,
        #                                  self.new_current_extent)

        # After loading files, instantiate class for data handling
        self.k_thread = Calc_K_space(
            self.angle_data, self.angle_extent)
        self.k_thread.finished.connect(self.get_k_space)
        self.statusBar().showMessage("Converting to k-space in background...",
                                     2000)
        self.k_thread.start()

    def update_current_data(self):
        self.new_current_data = self.processing_data[:, :, self.slider_pos]
        self.new_current_extent = self.processing_extent[self.slider_pos]

    def update_widgets(self):
        self.LineProf.update_data_extent(self.new_current_data,
                                         self.new_current_extent)
        self.FitParGui.update_parabola()

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
        self._current_labelname = os.path.basename(
            self.loaded_filenames[self.slider_pos])
        self.update_current_data()
        self.initialize_2D_plot()
        self.twoD_label.setText(self._current_labelname)
        self.update_widgets()


# class K_Window(ApplicationWindow):
#     ''' Instantiates new window for k data treatment '''

#     def __init__(self, kdata_stack, k_ranges_stack):
#         # QMainWindow.__init__(self)
#         super().__init__()
#         self.kdata_stack, self.k_ranges_stack = kdata_stack, k_ranges_stack
#         self.current_data_k = self.kdata_stack[:, :, self.slider_pos]
#         self.current_extent_k = self.k_ranges_stack[self.slider_pos]
#         self.setWindowTitle('K Data Handler')

#         # Set up File Menu
#         self.file_menu = QMenu('&File', self)
#         self.file_menu.addAction('&Quit', self.fileQuit,
#                                  QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

#         self.menuBar().addMenu(self.file_menu)

#         # Instantiate widgets
#         self.sub_widget = QWidget(self)
#         self.k_plotter = TwoD_Plotter(self.sub_widget)

#         # Instantiate layouts
#         self.main_layout = QVBoxLayout(self.sub_widget)
#         # layout.addWidget(t)
#         self.main_layout.addWidget(self.k_plotter)
#         # self.main_layout.addWidget(self.twoD_label)

#         self.initialize_2D_plot()


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
