#gfortran -c bspline_kinds_module.f90 
#gfortran -c bspline_sub_module.f90 
#gfortran -c bspline_oo_module.f90 
#gfortran -fPIC -c bspline_module.f90  
gfortran -fPIC -c bspline_kinds_module.f90
gfortran -fPIC -c bspline_sub_module.f90
gfortran -c kmaps.f90
f2py -m kmaps --fcompiler=gfortran -I bspline_sub_module.o -I bspline_kinds_module.o -c kmaps.f90
# f2py3 -c bspline_module.f90 kmaps.f90 -m kmaps
