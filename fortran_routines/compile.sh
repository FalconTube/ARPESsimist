#gfortran -c bspline_kinds_module.f90 
#gfortran -c bspline_sub_module.f90 
#gfortran -c bspline_oo_module.f90 
#gfortran -fPIC -c bspline_module.f90  
gfortran -fPIC -c bspline_kinds_module.f90
gfortran -fPIC -c bspline_sub_module.f90
gfortran -c kmaps.f90
f2py -m kmaps --fcompiler=gfortran --f90flags='-fopenmp' -lgomp -I bspline_sub_module.o -I bspline_kinds_module.o -I pwl_interp_3d.o -I pwl_interp_2d.o -I pwl_interp_1d.o -I r8lib.o -c kmaps.f90
# f2py3 -c bspline_module.f90 kmaps.f90 -m kmaps
