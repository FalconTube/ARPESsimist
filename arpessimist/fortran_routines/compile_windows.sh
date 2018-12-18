gfortran -fPIC -c bspline_kinds_module.f90
gfortran -fPIC -c bspline_sub_module.f90
gfortran -fPIC -c bspline_oo_module.f90
gfortran -fPIC -c bspline_module.f90
gfortran -c kmaps.f90
python -m numpy.f2py --compiler=mingw32 -m kmaps --f90flags='-fopenmp' -lgomp -I bspline_sub_module.o -I bspline_kinds_module.o -c kmaps.f90
mv *.dll ../src
#python3 -m numpy.f2py -c -m kmaps -I bspline_sub_module.o -I bspline_kinds_module.o kmaps.f90
# f2py3 -c bspline_module.f90 kmaps.f90 -m kmaps
