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

    def __init__(self, pol_map=False):
        super().__init__()
        self.pol_available = pol_map
        self.init_box()
        self.init_buttons()

    def init_buttons(self):
        self.buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.over_layout.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

    def init_box(self):
        self.over_layout = QVBoxLayout(self)

        self.lay = QGridLayout(self)

        # Define LineEdit Fields

        self.ksteps = QLineEdit("0.01", self)
        self.esteps = QLineEdit("0.005", self)
        self.pol_off = QLineEdit("0.0", self)
        self.tilt = QLineEdit("0.0", self)
        self.angle_off = QLineEdit("0.0", self)
        self.azi = QLineEdit("0.0", self)

        # Define Labels
        self.ksteps_label = QLabel("K Stepsize", self)
        self.esteps_label = QLabel("Energy Stepsize", self)
        self.pol_off_label = QLabel("Polar Offset", self)
        self.angle_off_label = QLabel("Angle Offset", self)
        self.tilt_label = QLabel("Tilt Angle", self)
        self.azi_label = QLabel("Azimuth Angle", self)

        # Add Edits
        self.lay.addWidget(self.ksteps, 0, 1)
        self.lay.addWidget(self.esteps, 1, 1)
        self.lay.addWidget(self.pol_off, 2, 1)
        self.lay.addWidget(self.angle_off, 3, 1)
        self.lay.addWidget(self.tilt, 4, 1)
        self.lay.addWidget(self.azi, 5, 1)

        # Add Labels
        self.lay.addWidget(self.ksteps_label, 0, 0)
        self.lay.addWidget(self.esteps_label, 1, 0)
        self.lay.addWidget(self.pol_off_label, 2, 0)
        self.lay.addWidget(self.angle_off_label, 3, 0)
        self.lay.addWidget(self.tilt_label, 4, 0)
        self.lay.addWidget(self.azi_label, 5, 0)

        if not self.pol_available:
            self.pol_min = QLineEdit("0.0", self)
            self.pol_max = QLineEdit("20.0", self)
            # self.pol_steps = QLineEdit('20.0', self)

            self.pol_min_label = QLabel("Polar Start", self)
            self.pol_max_label = QLabel("Polar End", self)
            # self.pol_steps_label = QLabel('Polar Stepsize', self)

            self.lay.addWidget(self.pol_min, 6, 1)
            self.lay.addWidget(self.pol_max, 7, 1)
            # self.lay.addWidget(self.pol_steps, 9, 1)

            self.lay.addWidget(self.pol_min_label, 6, 0)
            self.lay.addWidget(self.pol_max_label, 7, 0)
            # self.lay.addWidget(self.pol_steps_label, 9, 0)

        self.over_layout.addLayout(self.lay)

    def get_values(self):
        outvals = []
        num_widgets = self.lay.count()
        for i in range(num_widgets):
            thiswidget = self.lay.itemAt(i).widget()
            if "Line" in str(thiswidget):
                outvals.append(float(thiswidget.text()))
        return outvals
