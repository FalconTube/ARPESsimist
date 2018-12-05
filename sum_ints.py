import sys
import numpy as np
import os
from PyQt5.QtWidgets import QFileDialog, QApplication, QWidget, QMessageBox
from PyQt5 import QtCore

from load_sp2 import Sp2_loader

class SumImages(QWidget):
    def __init__(self, settings, appwin):
        super().__init__()
        self.settings = settings
        self.appwin = appwin
        self.appwin.statusBar().showMessage('Initialized Summation tool')
        self.sum_images()

    def get_multiple_batches(self):
        chooser = 1
        files = []
        LastDir = "."
        while chooser > 0:
            if chooser > 1:  # Dont ask for first time
                if not self.settings.value("SummationDir") == None:
                    LastDir = self.settings.value("SummationDir")

                if (
                    QMessageBox.Yes
                    == QMessageBox(
                        QMessageBox.Information,
                        "Summation",
                        "Do you want to add another batch of files?",
                        QMessageBox.Yes | QMessageBox.No,
                    ).exec()
                ):
                    many_files = QFileDialog.getOpenFileNames(
                        self, "Select one or more files to open", LastDir
                    )
                    many_files = many_files[0]
                    files.append(many_files)
                    LastDir = os.path.dirname(many_files[0])
                    self.settings.setValue("SummationDir", LastDir)
                else:
                    chooser = 0
            else:
                if not self.settings.value("SummationDir") == None:
                    LastDir = self.settings.value("SummationDir")

                many_files = QFileDialog.getOpenFileNames(
                    self, "Select one or more files to open", LastDir
                )
                many_files = many_files[0]
                files.append(many_files)
                LastDir = os.path.dirname(many_files[0])
                self.settings.setValue("SummationDir", LastDir)
                chooser += 1
        if len(files) > 0:
            return files
        return None

    def sum_images(self):
        folders = self.get_multiple_batches()
        savedir = QFileDialog.getExistingDirectory(
            self, "Choose directory for saving", "."
        )
        self.appwin.statusBar().showMessage("Summation...", 0)

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        data_storage = []
        if folders is not None:
            reader = Sp2_loader()
            for enum, files in enumerate(folders):
                print(files)
                data, extents = reader.read_multiple_sp2(files)
                if enum == 0:
                    out = data
                else:
                    for n in range(data.shape[-1]):
                        out[:, :, n] += data[:, :, n]
        self.save_to_sp2(out, folders, savedir)

    def save_to_sp2(self, data_stack, data_folders, savedir):
        def get_header(filename):
            with open(filename, "r") as f:
                comments = []
                for n, line in enumerate(f):
                    if n == 0:
                        continue
                    if not line.startswith("#"):
                        break
                    else:
                        comments.append(line)
            out = "".join(comments)
            return out

        self.appwin.statusBar().showMessage("Saving Data...", 0)
        os.chdir(savedir)
        savebase = "sum"
        for n, data in enumerate(data_stack.T):
            data = data.T
            shape = data.shape
            plain = np.ravel(data[::-1].T)
            intens = np.sum(plain)
            savename = savebase + "_{}.sp2".format(str(n).zfill(3))
            origin_files = []
            for i in data_folders:
                origin_files.append(i[n])
            comments = get_header(origin_files[0])
            header = "P2\n# Sum created from {}\n{}{} {} {}".format(
                origin_files, comments, shape[0], shape[1], int(intens)
            )
            np.savetxt(
                savename,
                plain.astype(int),
                fmt="%i",
                header=header,
                footer="P2",
                comments="",
            )
        self.appwin.statusBar().showMessage("Finished!", 2000)
        QApplication.restoreOverrideCursor()


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    # qApp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    SI = SumImages()
    SI.show()
    sys.exit(qApp.exec_())
