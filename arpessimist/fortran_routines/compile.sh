rm *.o *.mod *.pyf *.so
gfortran -static -c -fPIC -o bspline_kinds_module.o bspline_kinds_module.f90
gfortran -static -c -fPIC -o bspline_sub_module.o bspline_sub_module.f90
gfortran -static -c -fPIC -o bspline_oo_module.o bspline_oo_module.f90
gfortran -static -c -fPIC -o bspline_module.o bspline_module.f90
#python3 -m numpy.f2py -c -m kmaps --fcompiler=gfortran kmaps.f90 *.o
python3 -m numpy.f2py -c -m kmaps --fcompiler=gfortran --f90flags='-fopenmp'\
    -lgomp kmaps.f90 *.o
mv *.so ..
