# -*- coding: utf-8 -*-

import numpy as np
import os
from scipy.interpolate import interp1d, interp2d
from scipy.ndimage import convolve1d
from scipy.constants import hbar, m_e

# Global constant
ev_to_j = 1.6e-19


class interp1d_picklable:
    """ class wrapper for piecewise linear function
    """

    def __init__(self, xi, yi, **kwargs):
        self.xi = xi
        self.yi = yi
        self.args = kwargs
        self.f = interp1d(xi, yi, **kwargs)

    def __call__(self, xnew):
        return self.f(xnew)

    def __getstate__(self):
        return self.xi, self.yi, self.args

    def __setstate__(self, state):
        self.f = interp1d(state[0], state[1], **state[2])


class Spectra1D(object):
    """
    Holds a 1d spectrum.
    """

    def __init__(self, xdata, ydata, name, directory, plotname=""):
        self.PLTNM = plotname
        self.PATH = directory
        self.NAME = name
        self.XDATA = xdata
        self.YDATA = ydata
        self.IDATA = interp1d_picklable(xdata, ydata, bounds_error=False)
        self.xlabel = ""
        self.ylabel = ""

    def reinterpolate_data(self):
        """reinterpolate data after adjustment"""
        self.IDATA = interp1d(self.XDATA, self.YDATA)

    def adjust_range(self, dim, value):
        """
        Adjusts the x or y range by the given value.
        :param dim: put "x" or "y" as string to define dimension
        :param value: float to add to the range
        """
        if dim == "x":
            self.XDATA += value
        elif dim == "y":
            self.YDATA += value
        else:
            print("wrong dimension")
        self.reinterpolate_data()


class SpectraBase(object):
    """
    Holds all the data of an ARPES spectrum, intensities and xLimits/yLimits.
    Add features for data analysis here
    """

    def __init__(self, data: list, xlimits: list, ylimits: list):
        # self.PATH = os.path.dirname(filepath)
        # self.NAME = os.path.basename(filepath)
        # self.DATA = data
        self.xvals = np.linspace(xlimits[0], xlimits[1], data.shape[1])
        self.yvals = np.linspace(ylimits[1], ylimits[0], data.shape[0])
        # linear interpolation of data
        self.IDATA = interp2d(self.xvals, self.yvals, data, fill_value=0.0)
        self.xLimits = np.array(xlimits)
        self.yLimits = np.array(ylimits)

    def lineprofileX(self, yval, breadth=0.0):
        """
        returns the lineprofile along the x direction for a given y value with a broadening breadth
        :param yval: float
        :param breadth: float
        :return: xvalues, profile both as 1d arrays
        """
        profile = np.sum(
            self.IDATA(
                self.xvals,
                [yval - 0.5 * breadth + breadth * float(i) / 20.0 for i in range(21)],
            ),
            axis=0,
        )
        return self.xvals, profile

    def lineprofileY(self, xval, breadth=0.0):
        """
        returns the lineprofile along the y direction for a given x value with a broadening breadth
        :param xval: float
        :param breadth: float
        :return: yvalues, profile both as 1d arrays
        """
        profile = np.sum(
            self.IDATA(
                [xval - 0.5 * breadth + breadth * float(i) / 20.0 for i in range(21)],
                self.yvals,
            ),
            axis=1,
        )
        return self.yvals, profile

    def lineprofileXY(self, dim, val, breadth=0.0):
        """
        combines lineprofileX and lineprofileY, choose dimension via dim
        :param dim: "x" or "y" string
        :param val: value where to cut the profile
        :param breadth: width of the profile
        :return: values and profile
        """
        if dim == "x":
            vals, profile = self.lineprofileX(val, breadth)
        elif dim == "y":
            vals, profile = self.lineprofileY(val, breadth)
        else:
            print("lineprofile dim does not exist, ", dim)
            vals, profile = np.array([]), np.array([])
        return vals, profile

    def lineprofileFree(self, strtpnt: np.array, endpnt: np.array, N: int):
        """
        Returns the line profile along an arbitrary line with N steps
        :param strtpnt: 2-point array [x,y] for starting position
        :param endpnt: 2-point array [x,y] for end position
        :param N: integer on how many steps
        :return: lineprofile as a 1d array
        """
        N = int(N)
        dv = (np.array(endpnt) - np.array(strtpnt)) / N
        profile = [
            self.IDATA(strtpnt[0] + dv[0] * i, strtpnt[1] + dv[1] * i)[0]
            for i in range(N)
        ]
        return np.linspace(0, 1, N), profile

    def adjust_Fermilevel(self, xList, yList):
        """
        Method to correct the Fermi Level of the Spectrum. 
        Give the position of the Fermi level in x and y coordinates,
        the level will be adjusted to flatten the Fermilevel
        :param xList:
        :param yList:
        :return:
        """
        level = interp1d(xList, yList, fill_value=yList[0], bounds_error=False)
        level0 = yList[0]
        temp_data = np.zeros((len(self.yvals), len(self.xvals)))
        count = 0
        for xi in self.xvals:
            temp_data[:, count] = self.IDATA(xi, self.yvals + level(xi) - level0)[:, 0]
            count += 1
        # self.DATA = temp_data
        self.reinterpolate_data(temp_data)

    def adjust_range(self, dim, value):
        """
        Adjusts the x or y range by the given value.
        :param dim: put "x" or "y" as string to define dimension
        :param value: float to add to the range
        """
        if dim == "x":
            self.xLimits += value
        elif dim == "y":
            self.yLimits += value
        else:
            print("wrong dimension")
        data = self.IDATA(self.xvals, self.yvals)
        self.regenerate_vals_from_limits()
        self.reinterpolate_data(data)

    def regenerate_vals_from_limits(self):
        """
        generate new xvals and yvals after changing limits
        """
        self.xvals = np.linspace(self.xLimits[0], self.xLimits[1], len(self.xvals))
        self.yvals = np.linspace(self.yLimits[0], self.yLimits[1], len(self.yvals))

    def reinterpolate_data(self, data):
        """
        reinterpolate data after changing xvals or yvals
        """
        self.IDATA = interp2d(self.xvals, self.yvals, data, fill_value=0.0)

    def cutData(self, dim: str, limit_min: float, limit_max: float):
        """
        Cut the data between limit_min and limit_max along dimension dim
        :param dim: "x" or "y" string
        :param limit_min: float
        :param limit_max: float
        :return:
        """
        if dim == "x":
            self.xLimits = np.array([limit_min, limit_max], dtype=float)
            self.regenerate_vals_from_limits()
            data = self.IDATA(self.xvals, self.yvals)
            self.reinterpolate_data(data)
        elif dim == "y":
            self.yLimits = np.array([limit_min, limit_max], dtype=float)
            self.regenerate_vals_from_limits()
            data = self.IDATA(self.xvals, self.yvals)
            self.reinterpolate_data(data)

    def smoothData(self, dim, num, passes):
        """
        Uses convolution to smooth self.DATA along dim using a boxcar smooting. Num gives the size of the boxcar,
        passes the amount of smoothing passes.
        :param dim: "x" or "y" string
        :param num: int for the size of the boxcar
        :param passes: int for the amount of passes
        :return: ndarray smoothed version of self.DATA
        """
        if dim == "x":
            tempdat = self.IDATA(self.xvals, self.yvals)
            for p in range(passes):
                tempdat = convolve1d(
                    tempdat, np.array([1.0] * num), axis=1, mode="nearest"
                )
        elif dim == "y":
            tempdat = self.IDATA(self.xvals, self.yvals)
            for p in range(passes):
                tempdat = convolve1d(
                    tempdat, np.array([1.0] * num), axis=0, mode="nearest"
                )
        else:
            print(
                "smoothing not possible: (dim, num, passes) ",
                dim,
                ",",
                num,
                ",",
                passes,
            )
            tempdat = self.IDATA(self.xvals, self.yvals)
        return tempdat

    def secondDerivative(self, dim, num, passes):
        """
        Second derivative of self.DATA, num gives the size of the Boxcar for smoothing, passes the amount of smoothing
        passes before applying the 2nd derivative. This method uses convolutions to get the 2nd derivative of the data.
        :param dim: "x" or "y" string for the dimension along which the derivative should be applied.
        :param num: int for size of boxcar
        :param passes: int for number of smoothing passes
        :return: ndarray 2nd derivative of self.DATA
        """
        smth = self.smoothData(dim, num, passes)
        if dim == "x":
            d2 = convolve1d(smth, np.array([1.0, -2.0, 1.0]), axis=1, mode="nearest")
        elif dim == "y":
            d2 = convolve1d(smth, np.array([1.0, -2.0, 1.0]), axis=0, mode="nearest")
        else:
            print(
                "2nd derivative not possible: (dim, num, passes) ",
                dim,
                ",",
                num,
                ",",
                passes,
            )
            d2 = self.IDATA(self.xvals, self.yvals)
        return d2


class Spectra(SpectraBase):
    """
    Builds on SpectraBase to add conversion to k Space and simple plotting procedures. In most cases this class should
    be used to hold the ARPES data.
    """

    kSpace = False
    xlabel = "Angle [deg]"
    xlabelK = "Wavevector [$\mathrm{\AA^{-1}}]$"
    ylabel = "Energy [eV]"

    def convertKtoAngle(self, k, E):
        """
        convert K to Angle
        :param k: float Wavevector
        :param E: float Energy
        :return:
        """
        
        return (
            np.sign(k)
            * np.arcsin(hbar * (np.sign(k) * k * 1e10) / np.sqrt(2 * m_e * E * ev_to_j))
            * 180.0
            / np.pi
        )

    def convertAngleToK(self, a, E):
        """
        convert Angle to K space
        :param a: float angle
        :param E: float energy
        :return:
        """
        ev_to_j = 1.6e-19
        return np.sqrt(2 * m_e * E * ev_to_j) * np.sin(a * np.pi / 180.0) * 1e-10 / hbar

    def convertToKSpace(self):
        """
        convert the Spectrum from Angle into K space
        :return:
        """
        if not self.kSpace:
            self.kSpace = True
            # self.NAME = self.NAME[:-4] + '_k' + self.NAME[-4:]
            temp = np.zeros((len(self.yvals), len(self.xvals)))
            amax, amin = np.amax(self.xvals), np.amin(self.xvals)
            Emax, Emin = np.amax(self.yvals), np.amin(self.yvals)
            if amax < 0 and amin < 0:
                kvals = np.linspace(
                    self.convertAngleToK(amin, Emax),
                    self.convertAngleToK(amax, Emin),
                    len(self.xvals),
                )
            elif amax > 0 and amin > 0:
                kvals = np.linspace(
                    self.convertAngleToK(amin, Emin),
                    self.convertAngleToK(amax, Emax),
                    len(self.xvals),
                )
            else:
                kvals = np.linspace(
                    self.convertAngleToK(amin, Emax),
                    self.convertAngleToK(amax, Emax),
                    len(self.xvals),
                )
            kmax, kmin = np.amax(kvals), np.amin(kvals)
            for count, E in enumerate(self.yvals):
                # kvals[kvals > (np.sqrt(2*m_e * E * ev_to_j)/hbar)/1E10]
                cutoff = np.sqrt(2*m_e * E * ev_to_j)/hbar/1E10
                in_range = np.where(np.logical_and(-cutoff<kvals, kvals<cutoff))[0]
                lower_r = int(in_range[0])
                upper_r = int(in_range[-1])
                
                usevals = kvals[in_range]

                temp[count, lower_r:upper_r+1] = self.IDATA(self.convertKtoAngle(usevals, E), E)
                # temp[count, :] = self.IDATA(self.convertKtoAngle(kvals, E), E)
                
            # for countx, E in enumerate(self.yvals):
            #     for county, k in enumerate(kvals):
            #         temp[countx, county] = self.IDATA(self.convertKtoAngle(k, E), E)
            # self.DATA = temp
            self.xLimits = np.array([kmin, kmax])
            self.regenerate_vals_from_limits()
            self.reinterpolate_data(temp)
        else:
            print("Spectra object already in k space")

    def get_current_space(self):
        intens = self.IDATA(self.xvals, self.yvals)
        extent = [self.xLimits[0], self.xLimits[1], self.yLimits[0], self.yLimits[1]]
        return intens, extent
