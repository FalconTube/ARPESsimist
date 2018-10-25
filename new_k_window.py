from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import \
    QMainWindow, QWidget, QGridLayout, QMenu
from plot_2d import TwoD_Plotter


class K_Window(QMainWindow):
    ''' Instantiates new window for k data treatment '''

    def __init__(self, k_stack, k_extent, labellist, labelprefix):
        QMainWindow.__init__(self)
        # super.__init__(self)
        self.setWindowTitle('K Data Handler')
        self.setWindowIcon(QIcon('logo_black.png'))

        # Set up File Menu
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)
        self.k_win_widget = QWidget(self)
        self.k_k_widget = TwoD_Plotter(
            k_stack, k_extent, labellist, self.k_win_widget, appwindow=self,
            labelprefix=labelprefix)  # Start 2d plotter
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
