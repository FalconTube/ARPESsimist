import sys
import os
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QMenu,
    QMessageBox,
    QFileDialog,
    QGridLayout,
    QDialog,
)
from PyQt5.QtGui import QIcon
# import qdarkstyle


# import matplotlib
# from matplotlib.backends.backend_qt5agg \
#     import FigureCanvasQTAgg as FigureCanvas,\
#     NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
# matplotlib.use("Qt5Agg")


from load_sp2 import Sp2_loader, LoadHDF5
from plot_2d import TwoD_Plotter
from mpl_canvas_class import MyMplCanvas
from data_treatment import Calc_K_space
from set_parabola_fit import FitParabola
from lineprofiles import LineProfiles
from generate_maps import VerticalSlitPolarScan, ThreadingKMaps
from ask_map_parameters import MapParameterBox
from new_k_window import K_Window


class ApplicationWindow(QMainWindow):
    """ Main Application Window """

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
        self.new_twoD_widget = False
        self.k_data = []
        self.k_extent = []
        self.new_current_data = []
        self.new_current_extent = []
        self._current_labelname = ""
        self.p_min = False
        QMainWindow.__init__(self)

        self.resize(950, 950)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("ARPESsimist")
        iconpath = os.path.relpath('logo_black.png')
        self.setWindowIcon(QIcon(iconpath))
        # self.setWindowIcon(QtCore.Qt.QIcon('logo.png'))

        # Set up File Menu
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction("&Load Sp2 Files", self.choose_sp2)
        self.file_menu.addAction("&Load NXS Files", self.choose_nxs)
        self.file_menu.addAction(
            "&Quit", self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q
        )

        self.menuBar().addMenu(self.file_menu)

        # Set up Mapping Menu
        self.map_menu = QMenu("&Map", self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.map_menu)

        self.map_menu.addAction("&3D-Map Polar", self.polar_maps)
        self.map_menu.addAction("&3D-Map Azimuth", self.azi_maps)

        # Set up Interaction Menu
        # self.interact_menu = QMenu('&2D', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.interact_menu)

        # Set up Help Menu
        self.help_menu = QMenu("&Help", self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction("&About", self.about)

        # Instantiate widgets
        self.main_widget = QWidget(self)

        # Instantiate Layout and add widgets
        self.over_layout = QGridLayout(self.main_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Welcome to ARPyES", 2000)

    def fileQuit(self):
        """ Closes current instance """
        self.close()

    def closeEvent(self, ce):
        """ Closes current event """
        self.fileQuit()

    def about(self):
        """ Prints about """
        QMessageBox.about(self, "About", """ARPyES""")

    def angle_k_button_state(self):
        """ Switch to angle or k space data set """
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
        self.p_min = None
        many_files = QFileDialog.getOpenFileNames(
            self,
            "Select one or more files to open",
            "/home/yannic/Documents/PhD/ARPyES/zDisp/azimap/",
        )
        try:
            self.sp2 = Sp2_loader()
            self.loaded_filenames = self.sp2.tidy_up_list(many_files[0])
            self.statusBar().showMessage("Loading Data...", 2000)
            self.angle_data, self.angle_extent = self.sp2.read_multiple_sp2(
                self.loaded_filenames
            )
            self.load_multiple_files()
        except:
            pass

    def choose_nxs(self):
        self.p_min = None
        try:
            location = QFileDialog.getOpenFileNames(
                self,
                "Select one NXS file to open",
                "/home/yannic/Documents/PhD/ARPyES/zDisp/SnSe/",
            )

            location = str(location[0][0])
            self.statusBar().showMessage("Loading Data...", 2000)
            self.hd5mode = True
            self.sp2 = Sp2_loader()
            self.sp2.multi_file_mode = True
            self.H5loader = LoadHDF5(location)
            self.angle_data, self.angle_extent, self.p_min, self.p_max = (
                self.H5loader.return_data()
            )

            self.loaded_filenames = range(self.angle_data.shape[0])
            self.load_multiple_files()
        except:
            pass

    def load_multiple_files(self):
        if self.new_twoD_widget:
            self.new_twoD_widget.deleteLater()
        if not self.sp2.multi_file_mode:
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.new_current_data = self.processing_data
            self.new_current_extent = self.processing_extent

        else:
            stack_size = self.angle_data.shape[-1]
            self.processing_data = self.angle_data  # Start with angle data
            self.processing_extent = self.angle_extent
            self.update_current_data()

        # self.update_widgets()
        if not self.hd5mode:
            self._current_labelname = os.path.basename(self.loaded_filenames[0])
            # self.twoD_label.setText(self._current_labelname)
        self.data_are_loaded = True
        self.new_twoD_widget = TwoD_Plotter(
            self.processing_data,
            self.processing_extent,
            self.loaded_filenames,
            self.main_widget,
            xlabel=r"Angle [$^\circ{}$]",
            ylabel="Energy [eV]",
            appwindow=self,
            labelprefix="Dataset",
        )
        self.over_layout.addWidget(self.new_twoD_widget, 1, 0)

    def thread_polar_maps(self):
        xmin, xmax, ymin, ymax = -1.0, 1.6, -1.0, 1.6
        self.kmap_thread = ThreadingKMaps(
            self.processing_data,
            self.processing_extent,
            self.p_min,
            self.p_max,
            66.16,
            67.84,
            0.01,
            0.0,
            0,
            kxmin=xmin,
            kxmax=xmax,
            kymin=ymin,
            kymax=ymax,
        )

        self.kmap_thread.finished.connect(self.kmap_thread.get)
        self.kmap_thread.start()
        # extent_stack = list([[xmin, xmax, ymin, ymax]]) * \
        #     self.k_slice.shape[-1]

        # self.KWin = K_Window(self.k_slice, extent_stack)
        # self.KWin.show()

    def gen_maps(self):
        if self.p_min:
            parameters = MapParameterBox(pol_available=True)
        else:
            parameters = MapParameterBox(pol_available=False)
        if parameters.exec_() == parameters.Accepted:
            outvalues = parameters.get_values()
            self.statusBar().showMessage(
                "Generating Map. This will take a couple seconds...", 2000
            )
            if not self.p_min:
                ksteps, esteps, pol_off, angle_off, tilt, azi, kxmin, kxmax, kymin, kymax, self.p_min, self.p_max = (
                    outvalues
                )
            else:
                print(outvalues)
                ksteps, esteps, pol_off, angle_off, tilt, azi, kxmin, kxmax, kymin, kymax = (
                    outvalues
                )

            # Check if data will overflow memory
            self.check_ram_usage()

            All_maps = VerticalSlitPolarScan(
                self.processing_data,
                self.processing_extent,
                self.p_min,
                self.p_max,
                angle_offset=angle_off,
                kxmin=kxmin,
                kxmax=kxmax,
                kymin=kymin,
                kymax=kymax,
            )
            print(ksteps)
            ke_slice, ky_slice, kx_slice, kxmin, kxmax, kymin, kymax, kx_list, ky_list, E_list = All_maps.slice_K_fortran(
                ksteps, esteps, azi, tilt, self.use_azi
            )

            extent_stack_E = list([[kxmin, kxmax, kymax, kymin]]) * ke_slice.shape[-1]
            extent_stack_ky = (
                list([[kxmin, kxmax, min(E_list), max(E_list)]]) * ky_slice.shape[-1]
            )
            extent_stack_kx = (
                list([[kxmin, kxmax, min(E_list), max(E_list)]]) * kx_slice.shape[-1]
            )

            self.KEWin = K_Window(
                ke_slice,
                extent_stack_E,
                E_list,
                labelprefix="Energy [eV]",
                xlabel=r"kx [$\mathrm{\AA^{-1}}$]",
                ylabel=r"ky [$\mathrm{\AA^{-1}}$]",
            )
            self.KEWin.show()

            self.KyWin = K_Window(
                ky_slice,
                extent_stack_ky,
                kx_list,
                labelprefix="Kx",
                xlabel=r"ky [$\mathrm{\AA^{-1}}$]",
                ylabel="E [eV]",
            )
            self.KyWin.show()

            self.KxWin = K_Window(
                kx_slice,
                extent_stack_kx,
                ky_list,
                labelprefix="Ky",
                xlabel=r"kx [$\mathrm{\AA^{-1}}$]",
                ylabel="E [eV]",
            )
            self.KxWin.show()
        self.p_min = None

    def polar_maps(self):
        self.use_azi = False
        self.gen_maps()

    def azi_maps(self):
        self.use_azi = True
        self.gen_maps()

    def update_current_data(self):
        self.new_current_data = self.processing_data[:, :, self.slider_pos]
        self.new_current_extent = self.processing_extent[self.slider_pos]

    def check_ram_usage(self):
        ram_usage = (
            np.product(self.processing_data.shape) * 8 * 1e-9
        )  # Convert to RAM usage in GB for single array
        ram_usage *= 4  # Three times for spline, once for data
        if ram_usage > 2.0:  # TODO: Is 2GB a good value?
            # Prevent from too high RAM usage
            reduced_ram = (
                np.product(self.processing_data[::2, ::2, ::2].shape) * 8 * 1e-9 * 4
            )  # Convert to RAM usage in GB for single array

            ram_question = (
                "Your dataset is very large. Map transformation "
                + "will therefore use {:.2f} GB RAM. Should I only use every second ".format(
                    ram_usage
                )
                + "value and reduce RAM usage to {} GB? This should not ".format(
                    reduced_ram
                )
                + "impact the accuracy of the interpolation! "
                + "<b>(Highly recommended on machines with le 8 GB RAM)</b> "
            )
            if (
                QMessageBox.Yes
                == QMessageBox(
                    QMessageBox.Information,
                    "High RAM usage",
                    ram_question,
                    QMessageBox.Yes | QMessageBox.No,
                ).exec()
            ):
                self.processing_data = self.processing_data[::2, ::2, ::2]


if __name__ == "__main__":
    # test = Sp2_loader()
    # stack, ranges = test.read_multiple_sp2(
    #     ['mos2_2_003.sp2', 'mos2_2_015.sp2'])
    # handler = HandleNielsSpectra(stack, ranges)
    # out, extent = handler.convert_all_to_k()

    # sys.exit()
    qApp = QApplication(sys.argv)
    # qApp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


    aw = ApplicationWindow()
    # aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
