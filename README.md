# ARPESsimist

A software suited for evaluation of Angle Resolved Photo Emission Spectroscopy (ARPES) data.

## About

This program is an attempt to create a free and open-source way of evaluating ARPES data, since there is a general lack of software in this regard. The main core is written in `Python3` and `PyQT5` to ensure ease of contribution from other scientists. Some computationally demanding routines are written in `FORTRAN90` to ensure high performance.

## Installation

### Windows
A pre-built, standalone `.exe` file can be found on this page. This can directly be run on any Windows 10 machine without further installation.
It is possible, that this file may be recognized as a virus, which is due to the compilation process using `PyInstaller`. More information on that topic can be found at this link:  

### Linux

*Pip install is in the works!*

Clone this repository using `git` or download it directly and extract it anywhere, e.g.

```git clone https://github.com/FalconTube/ARPESsimist.git```

Required python packages:
- matplotlib
- scipy
- numpy
- natsort
- PyWavelets
- h5py
- PyQt5
- pywt

All of these are installable via pip:

```pip3 install -r requirements.txt```

In addition, a fortran compiler (e. g. gfortran) is required to compile the
f90 routines for your respective system. This compiler can be installed in the
respective ways, listed below. Further information is available at https://gcc.gnu.org/wiki/GFortranBinaries. 


Debian based:

```sudo apt install gfortran```

Arch based:

```sudo pacman -S gcc-fortran```

### OSX

The recommended method is to use [Homebrew](https://brew.sh/) to install the fortran compiler. If Homebrew is installed, just use:

```brew install gcc```

### Windows

Install [MinGW](http://mingw-w64.org/doku.php) to make use of the fortran compiler.

## Compile fortran scripts

In order to test your fortran installation, open a terminal and enter `gfortran`. If it states something like "fatal error: no input files", then you are good to go!

Open a terminal at `<Your_install_location>/arpessimist/fortran_routines/` and execute `compile.sh` using `bash compile.sh` (should also work on Windows with MinGW installed. If not, extract the respective commands from the script manually).

## General Usage

Start the software by calling `python3 start_progs.py`. This will open an empty window with a file menu in its top left position. From here, you can load multiple `.sp2` data or a single `.nxs` (`hdf5` format) file.

![Empty window](https://github.com/FalconTube/ARPESsimist/blob/master/arpessimist/src/images/empty_win.png)

After loading a set of data, more widgets will populate the main window, like this:

![Main window](https://github.com/FalconTube/ARPESsimist/blob/master/arpessimist/src/images/main_win.png)

<!-- Here you have the options to change the displayed 2D image (bottom slider), the LUT (right slider) and to make lineprofiles (select and right click). Zooming in to the 2D image will automatically adjust the ranges of the respective lineprofiles. All of the obtained plots can be extracted as both data points and the plots themselves using the `Export` button at the top.

Another major point is the creation of a 3D Map in k-space. This can be performed for both polar and azimuthal maps, using the `Mapping` button. After entering the desired k-range and resolution (step sizes), the software will execute fortran routines to evaluate the map. At the time of writing, the main program still is unresponsive while performing the calculation.

After successful calculation, three new windows (with the same style as the main window) will open. These show the respective slices through all three dimensions, namely Energy, kx and ky. -->

## Bugs and Features

As this is still a very novel project, expect bugs to happen. The authors would be grateful, if these bugs were reported to <falke@ph2.uni-koeln.de>.

Additionally we are very grateful for any feature request or general comments on how to improve this project.

## Contributions

Due to the simple programming scheme of this work, adding more functionality in the form of python or fortran scripts can be done with ease. All contributions are always welcome! 

If you want to contribute to this project, feel free to contact Yannic Falke at <falke@ph2.uni-koeln.de>. 

## Authors

Yannic Falke, II. Institute of Physics, University of Cologne

## Contributors

Niels Ehlen, II. Institute of Physics, University of Cologne
