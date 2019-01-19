gfortran -static -fPIC -c bspline_kinds_module.f90
gfortran -static -fPIC -c bspline_sub_module.f90
gfortran -static -fPIC -c bspline_oo_module.f90
gfortran -static -fPIC -c bspline_module.f90
gfortran -static -c kmaps.f90
#python3 -m numpy.f2py -m kmaps --build-dir fortran_build --f90flags='-fopenmp' -lgomp -I bspline_sub_module.o -I bspline_kinds_module.o -c kmaps.f90
python3 -m numpy.f2py -m kmaps --f90flags='-fopenmp' -lgomp  bspline_sub_module.o  bspline_kinds_module.o -c kmaps.f90
#mv *.so ../src
#python3 -m numpy.f2py -c -m kmaps -I bspline_sub_module.o -I bspline_kinds_module.o kmaps.f90
# f2py3 -c bspline_module.f90 kmaps.f90 -m kmaps
