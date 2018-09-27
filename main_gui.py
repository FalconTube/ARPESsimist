import sys
import os
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import \
    QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,\
    QMenu, QMessageBox, QSizePolicy, QFileDialog, QSlider, QLabel
import matplotlib
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")

from load_sp2 import Sp2_loader
from plot_2d import TwoD_Plotter
from mpl_canvas_class import MyMplCanvas


class ApplicationWindow(QMainWindow):
    ''' Main Application Window '''

    def __init__(self):
        self._current_data = 0
        self._current_data_stack = range(1)
        self._current_labelname = ''
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPyES")

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Load Single File', self.load_single_file)
        self.file_menu.addAction(
            '&Load Multiple Files', self.load_multiple_files)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

        # Set up Plot Menu
        self.plot_menu = QMenu('&Plotting', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.plot_menu)

        # self.plot_menu.addAction('&Plot_2D', self.initialize_2D_plot)

        # Set up Help Menu
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        # Set up buttons
        self.init_2d_button = QPushButton('&Init 2D Plot', self)
        self.init_2d_button.released.connect(self.initialize_2D_plot)

        # Instantiate widgets
        self.main_widget = QWidget(self)
        # t = One_Dim_Canvas(self.main_widget)
        self.twoD_label = QLabel()
        self.twoD_label.setText('Test')
        self.twoD_widget = TwoD_Plotter(self.main_widget)
        # self.twoD_slider = self.add_slider(0, 2)
        # self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)

        # Instantiate Layout and add widgets
        self.layout = QVBoxLayout(self.main_widget)
        # layout.addWidget(t)
        self.layout.addWidget(self.twoD_label)
        self.layout.addWidget(self.twoD_widget)
        self.layout.addWidget(self.init_2d_button)
        # self.layout.addWidget(self.twoD_slider)
        # self.addToolBar(NavigationToolbar(t, self))
        # self.toolbar = NavigationToolbar(self.twoD_widget, self)
        # self.addToolBar(self.toolbar)

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
                          """ARPyES"""
                          )

    def load_single_file(self):
        self.sp2 = Sp2_loader()
        single_file = QFileDialog.getOpenFileName(
            self, 'Select a single file to open', '.')
        self.single_filename = single_file[0]
        self._current_data = self.sp2.read_sp2(self.single_filename)

    def load_multiple_files(self):
        self.sp2 = Sp2_loader()
        many_files = QFileDialog.getOpenFileNames(
            self, 'Select one or more files to open', '.')
        self.loaded_filenames = many_files[0]
        self._current_data_stack = self.sp2.read_multiple_sp2(
            self.loaded_filenames)
        self.stack_size = self._current_data_stack.shape[-1]
        self._current_data = self._current_data_stack[:, :, 0]
        print(self.stack_size)
        self.twoD_slider = self.add_slider(0, self.stack_size)
        self.twoD_slider.valueChanged.connect(self.twoD_slider_changed)
        self.layout.addWidget(self.twoD_slider)

    def initialize_2D_plot(self):
        self.twoD_widget.update_2d_data(self._current_data)
        self.twoD_widget.update_2dplot()
        self.loaded_filenames

    def add_slider(self, lower: int, upper: int):
        slider_bar = QSlider(QtCore.Qt.Horizontal, self)
        slider_bar.setRange(lower, upper-1)
        slider_bar.setTickInterval(5)
        slider_bar.setSingleStep(1)
        slider_bar.setPageStep(10)
        return slider_bar

    def twoD_slider_changed(self, value):
        changed_slider = self.sender()
        slider_pos = changed_slider.value()
        self._current_labelname = os.path.basename(
            self.loaded_filenames[slider_pos])
        self._current_data = self._current_data_stack[:, :, slider_pos]
        self.twoD_widget.update_2d_data(self._current_data)
        self.twoD_widget.update_2dplot()
        self.twoD_label.setText(self._current_labelname)


if __name__ == '__main__':
    qApp = QApplication(sys.argv)

    aw = ApplicationWindow()
    # aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
