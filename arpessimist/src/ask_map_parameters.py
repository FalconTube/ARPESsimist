from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QVBoxLayout,
)


class MapParameterBox(QDialog):
    """ Initiates Box for user input of Map parameters """

    def __init__(self, saved_values=None, pol_available=False):
        print('invals {}'.format(saved_values))
        super().__init__()
        self.pol_available = pol_available
        self.saved_values = saved_values
        self.init_box()
        self.init_buttons()

    def init_buttons(self):
        buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.over_layout.addWidget(buttonbox)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

    def init_box(self):
        self.over_layout = QVBoxLayout(self)

        self.lay = QGridLayout(self)

        if self.saved_values == None:
            # Define LineEdit Fields
            ksteps = QLineEdit("0.01", self)
            esteps = QLineEdit("0.005", self)
            tilt = QLineEdit("0.0", self)
            angle_off = QLineEdit("0.0", self)
            azi = QLineEdit("0.0", self)
            kxmin = QLineEdit("-1.0", self)
            kxmax = QLineEdit("1.0", self)
            kymin = QLineEdit("-1.0", self)
            kymax = QLineEdit("1.0", self)
        else:
            # TODO This seems like a really stupid way to do, but dont know
            # how to do better...
            ksteps = QLineEdit(str(self.saved_values[0]), self)
            esteps = QLineEdit(str(self.saved_values[1]), self)
            tilt = QLineEdit(str(self.saved_values[2]), self)
            angle_off = QLineEdit(str(self.saved_values[3]), self)
            azi = QLineEdit(str(self.saved_values[4]), self)
            kxmin = QLineEdit(str(self.saved_values[5]), self)
            kxmax = QLineEdit(str(self.saved_values[6]), self)
            kymin = QLineEdit(str(self.saved_values[7]), self)
            kymax = QLineEdit(str(self.saved_values[8]), self)


        # Define Labels
        ksteps_label = QLabel("K Stepsize", self)
        esteps_label = QLabel("Energy Stepsize", self)
        #pol_off_label = QLabel("Polar Offset", self)
        tilt_label = QLabel("Tilt Angle", self)
        angle_off_label = QLabel("Polar Offset", self)
        azi_label = QLabel("Azimuth Angle", self)
        kxmin_label = QLabel("Kx Min", self)
        kxmax_label = QLabel("Kx Max", self)
        kymin_label = QLabel("Ky Min", self)
        kymax_label = QLabel("Ky Max", self)

        # Add Edits
        self.lay.addWidget(ksteps, 0, 1)
        self.lay.addWidget(esteps, 1, 1)
        self.lay.addWidget(tilt, 2, 1)
        self.lay.addWidget(angle_off, 3, 1)
        self.lay.addWidget(azi, 4, 1)
        self.lay.addWidget(kxmin, 5, 1)
        self.lay.addWidget(kxmax, 6, 1)
        self.lay.addWidget(kymin, 7, 1)
        self.lay.addWidget(kymax, 8, 1)

        # Add Labels
        self.lay.addWidget(ksteps_label, 0, 0)
        self.lay.addWidget(esteps_label, 1, 0)
        self.lay.addWidget(tilt_label, 2, 0)
        self.lay.addWidget(angle_off_label, 3, 0)
        self.lay.addWidget(azi_label, 4, 0)
        self.lay.addWidget(kxmin_label, 5, 0)
        self.lay.addWidget(kxmax_label, 6, 0)
        self.lay.addWidget(kymin_label, 7, 0)
        self.lay.addWidget(kymax_label, 8, 0)

        if not self.pol_available:
            if self.saved_values == None:
                pol_min = QLineEdit("0.0", self)
                pol_max = QLineEdit("20.0", self)
            else:
                pol_min = QLineEdit(str(self.saved_values[9]), self)
                pol_max = QLineEdit(str(self.saved_values[10]), self)
            # pol_steps = QLineEdit('20.0', self)
            pol_min_label = QLabel("Azimuth Start", self)
            pol_max_label = QLabel("Azimuth End", self)
            # self.pol_steps_label = QLabel('Polar Stepsize', self)

            self.lay.addWidget(pol_min, 9, 1)
            self.lay.addWidget(pol_max, 10, 1)
            # self.lay.addWidget(self.pol_steps, 9, 1)

            self.lay.addWidget(pol_min_label, 9, 0)
            self.lay.addWidget(pol_max_label, 10, 0)
            # self.lay.addWidget(self.pol_steps_label, 9, 0)

        self.over_layout.addLayout(self.lay)
        self.sort_taborder()

    def sort_taborder(self):
        num_widgets = self.lay.count()
        for n, i in enumerate(range(num_widgets)):
            thiswidget = self.lay.itemAt(i).widget()
            if n > 0:
                self.setTabOrder(lastwidget, thiswidget) # also set tab order
            lastwidget = thiswidget

    def get_values(self):
        outvals = []
        num_widgets = self.lay.count()
        for n, i in enumerate(range(num_widgets)):
            thiswidget = self.lay.itemAt(i).widget()
            if "Line" in str(thiswidget):
                outvals.append(float(thiswidget.text())) # save the values in order
            lastwidget = thiswidget
        print('outvals {}'.format(outvals))
        return outvals
