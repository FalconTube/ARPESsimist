# Clean up
rm *.a *.o *.mod *.pyf *.so

# Define Flags
FFLAGS='-fPIC'

# Compile all modules in right order
gfortran -c $FFLAGS -o bspline_kinds_module.o bspline_kinds_module.f90
gfortran -c $FFLAGS -o bspline_sub_module.o bspline_sub_module.f90
gfortran -c $FFLAGS -o bspline_oo_module.o bspline_oo_module.f90
gfortran -c $FFLAGS -o bspline_module.o bspline_module.f90
#gfortran -c $FFLAGS -o kmaps.o kmaps.f90

# Build library
#OBJS = $(SRCS_F:.f90=.o)
#ar crs libkmapslibrary.a  ../libgfortran.a ../libgcc.a

# Test dependencies with gfortran
#gfortran -c kmaps.f90 -L. -lkmapslibrary -static

# Try to link this static library to kmaps
#gfortran -o kmaps kmaps.f90 -L. -lkmapslibrary 
# Build kmaps module
#python3 -m numpy.f2py -m kmaps -h kmaps.pyf kmaps.f90 -l:libkmapslibrary
###python3 -m numpy.f2py -c -m kmaps kmaps.f90 -L. -lkmapslibrary
#python3 -m numpy.f2py  -L. -lgfortran -lgcc -lkmaps -c kmaps.pyf *.o
#python3 -m numpy.f2py -L. -lkmaps -c kmaps.pyf #*.o
#python3 -m numpy.f2py -c kmaps.pyf -L/home/yannic/Documents/PhD/arpessimist/arpessimist/fortran_routines/ -lkmapslibrary  
python3 -m numpy.f2py -c -m kmaps kmaps.f90 -I. *.o
