import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import time
from natsort import natsorted
import multiprocessing

from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication
from progbar import ProgressBar


class Sp2_loader():
    ''' Class able to load single or multiple SP2 files. '''

    def __init__(self, parent=None):
        self.multi_file_mode = False
        self.parent = parent

    def init_prog_bar(self):
        self.prog_widget = QWidget(self.parent)

    def read_sp2(self, filename, both_sets=False):
        ''' Reads a single SP2 file. '''
        with open(filename, 'r') as f:
            comments = []
            rawdata = []
            rawdata1 = []
            data_set_count = -1
            for line in f:
                stripline = line.strip()
                if str(stripline) == 'P2':
                    continue
                if line.startswith('#'):
                    comments.append(str(line))
                    continue
                if len(line.split()) > 1:
                    # A new data set starts
                    data_set_count += 1
                    # Return all dimensions as ints
                    xdim, ydim, total_counts = [int(i) for i in line.split()]
                    continue
                if data_set_count == 0:
                    rawdata.append(float(stripline))
                if data_set_count == 1:
                    if not both_sets:
                        break
                    rawdata1.append(float(stripline))

        data = self.reshape_data(rawdata, ydim)

        if both_sets:
            data1 = self.reshape_data(rawdata1, ydim)
            return np.array(data), np.array(data1)

        return np.array(data)

    def read_multiple_sp2(self, filenames, both_sets=False):
        ''' Only reads defined sp2 files '''
        starttime = time.time()
        self.multi_file_mode = True
        iterate_list = natsorted(filenames)
        p = multiprocessing.Pool()
        out = p.map(self.read_sp2, iterate_list)
        # Can be optimized by removing loop and putting it in self.read_sp2
        for n, data in enumerate(out):
            if n == 0:
                out_arr = data
            else:
                out_arr = np.dstack((out_arr, data))
        p.close()
        p.join()
        print('Time_elaped = {}'.format(time.time()-starttime))
        return out_arr

    def single_thread_sp2(self, filenames, both_sets=False):
        starttime = time.time()
        pb = ProgressBar()
        files_max_count = len(filenames)
        for n, filename in enumerate(natsorted(filenames)):
            data = self.read_sp2(filename, both_sets)
            if n == 0:
                out_arr = data
            else:
                out_arr = np.dstack((out_arr, data))
            progress = round(n/files_max_count * 100, 0)
            pb.setValue(progress)
            QApplication.processEvents()

        pb.close()
        print('Time_elaped = {}'.format(time.time()-starttime))
        return out_arr

    def read_all_sp2(self, folder='.', both_sets=False):
        ''' Stacks all sp2 files in specified folder into 3d array. '''
        self.multi_file_mode = True
        os.chdir(folder)
        for n, filename in enumerate(glob.glob('*.sp2')):
            data = self.read_sp2(filename, both_sets)
            if n == 0:
                out_arr = data
            else:
                out_arr = np.dstack((out_arr, data))
        return out_arr

    def reshape_data(self, indata: list, ydim: int):
        ''' Turns 1D array into proper 2D array '''
        indata = np.array(indata)
        indata = np.array(indata)
        indata = np.reshape(indata, (ydim, -1))
        data = np.swapaxes(indata, 0, 1)
        return data


if __name__ == '__main__':
    sp2 = Sp2_loader()
    out_data = sp2.read_sp2('mos2_2_015.sp2')
    plt.imshow(out_data)
    plt.show()
