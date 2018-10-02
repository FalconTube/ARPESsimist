import sys
import os
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel, QScrollBar,\
    QRadioButton
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
# from new_k_window import K_Window


class ApplicationWindow(QMainWindow):
    ''' Main Application Window '''

    def __init__(self):
        self.current_data = 0
        self.data_stack = range(1)
        self.current_data_k = 0
        self.current_data_k = range(1)
        self.current_extent = None
        self.slider_pos = 0
        self.k_space_generated = False
        self.data_are_loaded = False
        self.select_k_space = False
        self.k_data = False
        self._current_labelname = ''
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPyES")

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction(
            '&Load Files', self.load_multiple_files)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

        # Set up K-Data Menu
        self.k_menu = QMenu('&Map', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.k_menu)

        self.k_menu.addAction('&Plot_2D', self.init_k_window)

        # Set up Help Menu
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        # Set uo radio buttons
        self.angle_button = QRadioButton("Angles")
        self.angle_button.setChecked(True)
        self.angle_button.toggled.connect(
            lambda: self.angle_k_button_state(self.angle_button))

        self.k_button = QRadioButton("K-Space")
        self.k_button.toggled.connect(
            lambda: self.angle_k_button_state(self.k_button))

        # Set up buttons
        # self.k_button = QPushButton('&Convert to k-space', self)
        # self.k_button.released.connect(self.gen_k_space)

        # Instantiate widgets
        self.main_widget = QWidget(self)
        # t = One_Dim_Canvas(self.main_widget)
        self.twoD_label = QLabel()
        self.twoD_label.setText('')
        self.twoD_widget = TwoD_Plotter(self.main_widget)
        # self.twoD_slider = self.add_slider(0, 2)
        # self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)

        # Instantiate Layout and add widgets
        self.main_layout = QVBoxLayout(self.main_widget)
        # layout.addWidget(t)
        self.main_layout.addWidget(self.twoD_widget)
        self.main_layout.addWidget(self.twoD_label)

        # Set up angle and k radio buttons
        radio_layout = QHBoxLayout()

        radio_layout.addWidget(self.angle_button)
        radio_layout.addWidget(self.k_button)
        self.main_layout.addLayout(radio_layout)

        # self.setLayout(self.main_layout)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

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

    def angle_k_button_state(self, button):
        # print('pressed')
        # print(button.text())
        self.twoD_widget.instance_counter = 0  # Reset plot
        if button.text() == '&Angles':
            if button.isChecked():
                self.select_k_space = False
        if button.text() == 'K-&Space':
            if button.isChecked():
                self.select_k_space = True
        self.initialize_2D_plot()

    def init_k_window(self):
        ''' Created new window for k data handling '''
        if self.data_are_loaded:
            if self.k_space_generated:
                self.KWin = K_Window(self.k_data, self.k_range)
                self.KWin.show()
            else:
                QMessageBox.about(self, 'Warning',
                                  'Please wait for k-space to be processed')
        else:

            QMessageBox.about(self, 'Warning',
                              'Please load data')

    def load_multiple_files(self):
        self.sp2 = Sp2_loader()
        many_files = QFileDialog.getOpenFileNames(
            self, 'Select one or more files to open',
            '/home/yannic/Documents/stuff/feb/06/sampl2map/')
        self.loaded_filenames = self.sp2.tidy_up_list(many_files[0])
        self.statusBar().showMessage("Loading Data...", 2000)

        self.data_stack, self.stack_extent = self.sp2.read_multiple_sp2(
            self.loaded_filenames)

        if not self.sp2.multi_file_mode:
            self.current_data = self.data_stack
            self.current_extent = self.stack_extent
            self.initialize_2D_plot()
        else:
            self.stack_size = self.data_stack.shape[-1]
            self.current_data = self.data_stack[:, :, 0]
            self.current_extent = self.stack_extent[0]

            self.twoD_slider = self.add_slider(0, self.stack_size)
            self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)
            self.main_layout.addWidget(self.twoD_slider)
            self.initialize_2D_plot()
        self._current_labelname = os.path.basename(
            self.loaded_filenames[0])
        self.twoD_label.setText(self._current_labelname)
        self.data_are_loaded = True

        # After loading files, instantiate class for data handling
        self.k_thread = Calc_K_space(
            self.data_stack, self.stack_extent)
        self.k_thread.finished.connect(self.get_k_space)
        self.statusBar().showMessage("Converting to k-space in background...",
                                     2000)
        self.k_thread.start()

    def get_k_space(self):
        self.k_data, self.k_extent, self.k_space_generated = self.k_thread.get()
        self.current_data_k = self.k_data[:, :, self.slider_pos]
        self.current_extent_k = self.k_extent[self.slider_pos]
        self.statusBar().showMessage("k-space conversion finished!", 2000)

    def initialize_2D_plot(self):
        if self.select_k_space:
            self.twoD_widget.update_2d_data(self.current_data_k)
            self.twoD_widget.update_2dplot(self.current_extent_k)
        else:
            self.twoD_widget.update_2d_data(self.current_data)
            self.twoD_widget.update_2dplot(self.current_extent)

    def add_slider(self, lower: int, upper: int):
        # slider_bar = QScrollBar(QtCore.Qt.Horizontal, self)
        # slider_bar.setRange(lower, upper-1)
        slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        slider_bar.setRange(lower, upper-1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        return slider_bar

    def twoD_slider_changed(self, value):
        # if self.k_space_generated:
        #     use_data = self._da
        changed_slider = self.sender()
        self.slider_pos = changed_slider.value()
        self._current_labelname = os.path.basename(
            self.loaded_filenames[self.slider_pos])
        self.current_data = self.data_stack[:, :, self.slider_pos]
        self.current_extent = self.stack_extent[self.slider_pos]
        try:
            self.current_data_k = self.k_data[:, :, self.slider_pos]
            self.current_extent_k = self.k_extent[self.slider_pos]
        except:
            pass
        self.initialize_2D_plot()
        self.twoD_label.setText(self._current_labelname)


class K_Window(ApplicationWindow):
    ''' Instantiates new window for k data treatment '''

    def __init__(self, kdata_stack, k_ranges_stack):
        # QMainWindow.__init__(self)
        super().__init__()
        self.kdata_stack, self.k_ranges_stack = kdata_stack, k_ranges_stack
        self.current_data_k = self.kdata_stack[:, :, self.slider_pos]
        self.current_extent_k = self.k_ranges_stack[self.slider_pos]
        self.setWindowTitle('K Data Handler')

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

        # Instantiate widgets
        self.sub_widget = QWidget(self)
        self.k_plotter = TwoD_Plotter(self.sub_widget)

        # Instantiate layouts
        self.main_layout = QVBoxLayout(self.sub_widget)
        # layout.addWidget(t)
        self.main_layout.addWidget(self.k_plotter)
        # self.main_layout.addWidget(self.twoD_label)

        self.initialize_2D_plot()


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
