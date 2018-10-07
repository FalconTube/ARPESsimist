module kmaps
use bspline_sub_module
  implicit none  

  contains

    subroutine kslice(xgrid, ygrid, zgrid, nx, ny, nz, indata,&
                      xeval, yeval, zeval, outval)
      ! subroutine kslice()

      integer, intent(in) :: nx ! length of arrays
      integer, intent(in) :: ny
      integer, intent(in) :: nz

      double precision, dimension(nx), intent(in) :: xgrid
      double precision, dimension(ny), intent(in) :: ygrid
      double precision, dimension(nz), intent(in) :: zgrid
      double precision, dimension(nz, ny, nz), intent(in) :: indata

      double precision, intent(in) :: xeval
      double precision, intent(in) :: yeval
      double precision, intent(in) :: zeval


      double precision, intent(out) :: outval

      integer :: kx = 4 ! order of knots
      integer :: ky = 4
      integer :: kz = 4

      integer :: idx = 0
      integer :: idy = 0
      integer :: idz = 0
      integer, dimension(2) :: iflag 
      integer :: iknot = 0

      integer :: inbvx = 1
      integer :: inbvy = 1
      integer :: inbvz = 1
      integer :: inbvq = 1
      integer :: inbvr = 1
      integer :: inbvs = 1
      integer :: iloy  = 1
      integer :: iloz  = 1
      integer :: iloq  = 1
      integer :: ilor  = 1
      integer :: ilos  = 1

!      real(wp) :: tx(nx+kx),ty(ny+ky),tz(nz+kz)
      double PRECISION, allocatable, dimension(:) :: tx
      double PRECISION, allocatable, dimension(:) :: ty
      double PRECISION, allocatable, dimension(:) :: tz
      double PRECISION, dimension(nx, ny, nz) :: outcoeff
      ! double PRECISION, intent(out) :: outdata

      ! type(bspline_3d) :: s
      allocate (tx(nx+kx))
      allocate (ty(ny+ky))
      allocate (tz(nz+kz))
      print *, xgrid
      print *, xeval
      

      call db3ink(xgrid,nx,ygrid,ny,zgrid,nz,indata,kx,ky,kz,&
        iknot,tx,ty,tz,outcoeff,iflag(1))
        print *, iflag(1)
        ! print *, outcoeff(1,1,1), outcoeff(2,2,2), outcoeff(3,3,3)
      call db3val(xeval,yeval,zeval,idx,idy,idz,tx,ty,tz,nx,ny,nz,kx,ky,kz,&
       outcoeff,outval, iflag(2),inbvx,inbvy,inbvz,iloy,iloz)
       print *, iflag(2)
       ! print *, outval
      !  print *, xgrid
      ! print*, outval
      !   print *, iflag(2)
      
      ! print *, kx
      ! kx = 6
      ! call s%initialize(xgrid,ygrid,zgrid,indata,kx,ky,kz,iflag)
      ! call s%evaluate(xeval, yeval, zeval,idx,idy,idz,outval,iflag)
      ! ! kx,ky,kz,iflag,extrap)
      ! !call s%evaluate(xval,yval,zval,idx,idy,idz,f,iflag)
      ! call s%destroy()
      ! print *, kx
      

  end subroutine kslice

end module kmaps
