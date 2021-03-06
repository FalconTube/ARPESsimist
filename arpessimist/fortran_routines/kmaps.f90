module kmaps
!use bspline_sub_module
use bspline_module
  implicit none  

  contains


    subroutine kslice_spline(xgrid, ygrid, zgrid, nx, ny, nz, indata,&
                      xevalgrid, yevalgrid, zevalgrid, outx, outy, outz,&
                      tilt, azimuth, outarray)
      integer, intent(in) :: nx ! length of arrays
      integer, intent(in) :: ny
      integer, intent(in) :: nz
      integer, intent(in) :: outx ! length of out arrays
      integer, intent(in) :: outy
      integer, intent(in) :: outz
      

      
      double precision, dimension(nx), intent(in) :: xgrid
      double precision, dimension(ny), intent(in) :: ygrid
      double precision, dimension(nz), intent(in) :: zgrid
      double precision, dimension(nx, ny, nz), intent(in) :: indata

      double precision, dimension(outx), intent(in) :: xevalgrid
      double precision, dimension(outy), intent(in) :: yevalgrid
      double precision, dimension(outz), intent(in) :: zevalgrid

      double PRECISION, intent(in) :: tilt
      double PRECISION, intent(in) :: azimuth

      double precision, dimension(outx, outy, outz), intent(out) :: outarray 


      double precision :: outval

      double precision :: xeval
      double precision :: yeval
      double precision :: zeval
      double precision :: xpoint
      double precision :: ypoint
      double precision :: zpoint
      integer :: countx
      integer :: county
      integer :: countz

      integer :: knot_x = 2 ! order of knots
      integer :: knot_y = 2
      integer :: knot_z = 2

      integer :: idx = 0
      integer :: idy = 0
      integer :: idz = 0
      integer, dimension(2) :: iflag 
      integer :: iknot = 0

      integer :: inbvx = 0
      integer :: inbvy = 0
      integer :: inbvz = 0
      integer :: iloy  = 0
      integer :: iloz  = 0

!      real(wp) :: tx(nx+kx),ty(ny+ky),tz(nz+kz)
      double PRECISION, allocatable, dimension(:) :: tx
      double PRECISION, allocatable, dimension(:) :: ty
      double PRECISION, allocatable, dimension(:) :: tz
      ! double PRECISION, dimension(141) :: tx
      ! double PRECISION, dimension(1004) :: ty
      ! double PRECISION, dimension(1044) :: tz
      double PRECISION, dimension(nx, ny, nz) :: outcoeff
      

      double PRECISION :: inner_sqrt_term
      double PRECISION :: k
      double PRECISION :: pi
      double PRECISION :: tlt
      double PRECISION :: az
      double PRECISION :: kx
      double PRECISION :: ky
      double PRECISION :: kz
      double PRECISION :: atilt
      double PRECISION :: cospol
      double PRECISION :: pol_angle

      double PRECISION :: rad

      allocate (tx(nx+knot_x))
      allocate (ty(ny+knot_y))
      allocate (tz(nz+knot_z))
      ! convert to rad
      PI=4.D0*DATAN(1.D0)
      rad = 180.D0/PI
      tlt = tilt * PI/180.D0 
      az = azimuth*PI/180.D0

      call db3ink(xgrid,nx,ygrid,ny,zgrid,nz,indata,knot_x,knot_y,knot_z,&
                          iknot,tx,ty,tz,outcoeff,iflag(1))

      print *, 'STARTING NORMAL'
    !!$omp parallel num_threads(2) private(zeval, xeval, yeval, countz, countx, county) &
    !!$omp& private(kx, ky, kz, inner_sqrt_term, k, atilt, cospol) &
    !!$omp& private(pol_angle, xpoint, ypoint, zpoint, outval)
    !!$omp do
      do countz=1, outz
        zeval = zevalgrid(countz)
        do countx=1, outx
          xeval = xevalgrid(countx)
          do county=1, outy
            yeval = yevalgrid(county)

            call calc_k(zeval, xeval, yeval, inner_sqrt_term, k)
            !k = 0.512317 * SQRT(zeval)
            kx = xeval/k
            ky = yeval/k
            kz = sqrt(1.D0- kx*kx - ky*ky)
            
            call c_a_tilt(kx, ky, kz, az, tlt, atilt)
            call c_cos_pol(kz, tlt, atilt, cospol)
            call c_pol(atilt, az, tlt, kx, cospol, pol_angle)

            xpoint = -pol_angle * rad
            ypoint = atilt * rad
            zpoint = zeval
            if (isnan(xpoint)) then
              xpoint = 0d0
            end if
            if (isnan(ypoint)) then
              ypoint = 0d0
            end if
            if (isnan(zpoint)) then
              zpoint = 0d0
            end if
        
            call db3val(xpoint,ypoint,zpoint,idx,idy,idz,tx,ty,tz,nx,ny,nz,&
                        knot_x,knot_y,knot_z,outcoeff,outval,iflag(2),&
                        inbvx,inbvy,inbvz,iloy,iloz)
            
            outarray(countx, county, countz) = outval
            
          end do  
        end do
      end do
    !!$omp end do
    !!$omp end parallel


  end subroutine kslice_spline
  
  
  
  subroutine kslice_spline_horizontal(xgrid, ygrid, zgrid, nx, ny, nz, indata,&
                      xevalgrid, yevalgrid, zevalgrid, outx, outy, outz,&
                      tilt, azimuth, outarray)
      integer, intent(in) :: nx ! length of arrays
      integer, intent(in) :: ny
      integer, intent(in) :: nz
      integer, intent(in) :: outx ! length of out arrays
      integer, intent(in) :: outy
      integer, intent(in) :: outz

      
      double precision, dimension(nx), intent(in) :: xgrid
      double precision, dimension(ny), intent(in) :: ygrid
      double precision, dimension(nz), intent(in) :: zgrid
      double precision, dimension(nx, ny, nz), intent(in) :: indata

      double precision, dimension(outx), intent(in) :: xevalgrid
      double precision, dimension(outy), intent(in) :: yevalgrid
      double precision, dimension(outz), intent(in) :: zevalgrid

      double PRECISION, intent(in) :: tilt
      double PRECISION, intent(in) :: azimuth

      double precision, dimension(outx, outy, outz), intent(out) :: outarray 


      double precision :: outval

      double precision :: xeval
      double precision :: yeval
      double precision :: zeval
      double precision :: xpoint
      double precision :: ypoint
      double precision :: zpoint
      integer :: countx
      integer :: county
      integer :: countz

      integer :: knot_x = 2 ! order of knots
      integer :: knot_y = 2
      integer :: knot_z = 2

      integer :: idx = 0
      integer :: idy = 0
      integer :: idz = 0
      integer, dimension(2) :: iflag 
      integer :: iknot = 0

      integer :: inbvx = 0
      integer :: inbvy = 0
      integer :: inbvz = 0
      integer :: iloy  = 0
      integer :: iloz  = 0

!      real(wp) :: tx(nx+kx),ty(ny+ky),tz(nz+kz)
      double PRECISION, allocatable, dimension(:) :: tx
      double PRECISION, allocatable, dimension(:) :: ty
      double PRECISION, allocatable, dimension(:) :: tz
      ! double PRECISION, dimension(141) :: tx
      ! double PRECISION, dimension(1004) :: ty
      ! double PRECISION, dimension(1044) :: tz
      double PRECISION, dimension(nx, ny, nz) :: outcoeff
      

      double PRECISION :: inner_sqrt_term
      double PRECISION :: k
      double PRECISION :: pi
      double PRECISION :: tlt
      double PRECISION :: az
      double PRECISION :: kx
      double PRECISION :: ky
      double PRECISION :: kz
      double PRECISION :: atilt
      double PRECISION :: pol_angle

      double PRECISION :: rad

      allocate (tx(nx+knot_x))
      allocate (ty(ny+knot_y))
      allocate (tz(nz+knot_z))
      ! convert to rad
      PI=4.D0*DATAN(1.D0)
      rad = 180.D0/PI
      tlt = tilt * PI/180.D0 
      az = azimuth*PI/180.D0

      call db3ink(xgrid,nx,ygrid,ny,zgrid,nz,indata,knot_x,knot_y,knot_z,&
                          iknot,tx,ty,tz,outcoeff,iflag(1))

    !!$omp parallel private(zeval, xeval, yeval, countz, countx, county) &
    !!$omp& private(kx, ky, kz, inner_sqrt_term, k, atilt) &
    !!$omp& private(pol_angle, xpoint, ypoint, zpoint)
    !!$omp do
      do countz=1, outz
        zeval = zevalgrid(countz)
        do countx=1, outx
          xeval = xevalgrid(countx)
          do county=1, outy
            yeval = yevalgrid(county)
            
            call calc_k(zeval, xeval, yeval, inner_sqrt_term, k)
            !k = 0.512317 * SQRT(zeval)
            kx = xeval/k
            ky = yeval/k
            kz = sqrt(1.D0- kx*kx - ky*ky)
            
            call az_horiz(kx, ky, kz, tlt, az)
            call pol_horiz(kx, ky, az, pol_angle)

            xpoint = -pol_angle * rad
            ypoint = zeval
            zpoint = -az * rad
            !zpoint = zeval
            !ypoint = -az * rad
            if (isnan(xpoint)) then
              xpoint = 0d0
            end if
            if (isnan(ypoint)) then
              ypoint = 0d0
            end if
            if (isnan(zpoint)) then
              zpoint = 0d0
            end if
        
            call db3val(xpoint,ypoint,zpoint,idx,idy,idz,tx,ty,tz,nx,ny,nz,&
                        knot_x,knot_y,knot_z,outcoeff,outval,iflag(2),&
                        inbvx,inbvy,inbvz,iloy,iloz)

            outarray(countx, county, countz) = outval
            
          end do  

        end do

      end do
    !!$omp end do
    !!$omp end parallel


  end subroutine kslice_spline_horizontal

  !subroutine kslice_trilin(xgrid, ygrid, zgrid, nx, ny, nz, indata,&
    !xevalgrid, yevalgrid, zevalgrid, outx, outy, outz,&
    !tilt, azimuth, outarray)
!integer, intent(in) :: nx ! length of arrays
!integer, intent(in) :: ny
!integer, intent(in) :: nz
!integer, intent(in) :: outx ! length of out arrays
!integer, intent(in) :: outy
!integer, intent(in) :: outz



!double precision, dimension(nx), intent(in) :: xgrid
!double precision, dimension(ny), intent(in) :: ygrid
!double precision, dimension(nz), intent(in) :: zgrid
!double precision, dimension(nx, ny, nz), intent(in) :: indata

!double precision, dimension(outx), intent(in) :: xevalgrid
!double precision, dimension(outy), intent(in) :: yevalgrid
!double precision, dimension(outz), intent(in) :: zevalgrid

!double PRECISION, intent(in) :: tilt
!double PRECISION, intent(in) :: azimuth

!double precision, dimension(outx, outy, outz), intent(out) :: outarray 
!double precision, dimension(outx, outy, nz) :: tmp_array 


!double precision :: outval

!double precision :: xeval
!double precision :: yeval
!double precision :: zeval
!double precision :: xpoint
!double precision :: ypoint
!double precision :: zpoint
!integer :: countx
!integer :: county
!integer :: countz




!double PRECISION :: inner_sqrt_term
!double PRECISION :: k
!double PRECISION :: pi
!double PRECISION :: tlt
!double PRECISION :: az
!double PRECISION :: kx
!double PRECISION :: ky
!double PRECISION :: kz
!double PRECISION :: atilt
!double PRECISION :: cospol
!double PRECISION :: pol_angle

!double PRECISION :: rad

!print *, 'init'

!! convert to rad
!PI=4.D0*DATAN(1.D0)
!rad = 180.D0/PI
!tlt = tilt * PI/180.D0 
!az = azimuth*PI/180.D0 
!print *, nx, ny, nz

!print *, 'starting loop'

!!$omp parallel private(zeval, xeval, yeval, countx, county) &
!!$omp& private(kx, ky, kz, k, az, tlt, atilt, cospol, pol_angle) &
!!$omp& private(xpoint, ypoint, zpoint, outval)
!!$omp do
!do countz=1, nz
  !zeval = zgrid(countz)
  !do countx=1, outx
    !xeval = xevalgrid(countx)
    !do county=1, outy
      !yeval = yevalgrid(county)

      !call calc_k(zeval, xeval, yeval, inner_sqrt_term, k)
      !kx = xeval/k
      !ky = yeval/k
      !kz = sqrt(1.D0- kx*kx - ky*ky)
      !call c_a_tilt(kx, ky, kz, az, tlt, atilt)
      !call c_cos_pol(kz, tlt, atilt, cospol)
      !call c_pol(atilt, az, tlt, kx, cospol, pol_angle)

      !xpoint = -pol_angle * rad
      !ypoint = atilt * rad
      !! zpoint = zeval
      !call interpolate_2D(nx, xgrid, ny, ygrid, indata(:,:, countz),&
                          !xpoint, ypoint, outval)
      
      !tmp_array(countx, county, countz) = outval

    !end do
  !end do
!end do
!!$omp end do
!!$omp end parallel
!print *, 'finished first loop'


!print *, 'starting second loop'

!!!$omp parallel private(zeval, countx, county, outval)
!!!$omp do
!do countz=1, outz
  !zeval=zevalgrid(countz)
  !do countx=1, outx
    !do county=1, outy

      !call interpolate_1D(nz, zgrid, tmp_array(countx, county, :),&
                      !zeval, outval)
      
      !outarray(countx, county, countz) = outval

    !end do
  !end do
!end do
!! !$omp end do
!! !$omp end parallel

!print *, 'finished second loop'




!end subroutine kslice_trilin


  subroutine calc_k(E, k1, k2, inner_sqrt_term, k)
    double PRECISION, intent(in) :: E
    double PRECISION, intent(in) :: k1
    double PRECISION, intent(in) :: k2
    double PRECISION, intent(out) :: inner_sqrt_term
    double PRECISION, intent(out) :: k

    inner_sqrt_term = SQRT(k1*k1 + k2*k2)*0.512317**(-2)
    k = 0.512317 * SQRT(E + inner_sqrt_term)
  end subroutine

  subroutine c_a_tilt(kx, ky, kz, az, tlt, atilt)
  double PRECISION, intent(in)  :: kx, ky, kz, az, tlt
  double PRECISION, intent(out) ::  atilt
      atilt = ASIN(&
      (kx*sin(az)+ky*cos(az))*cos(tlt)-kz*sin(tlt)&
      )
      
  end subroutine c_a_tilt

  subroutine c_cos_pol(kz, tlt, atilt, cospol)
  double PRECISION, intent(in)  :: kz, tlt, atilt
  double PRECISION, intent(out) :: cospol
  cospol = (kz - sin(tlt)*sin(atilt)) / (cos(tlt)*cos(atilt))
      
  end subroutine c_cos_pol

  subroutine c_pol(atilt, az, tlt, kx, cospol, pol_angle)
  double precision, intent(in)  :: atilt, az, tlt, kx, cospol
  double precision, intent(out) :: pol_angle      

  pol_angle = asin((sin(atilt)*sin(az)*cos(tlt) - kx+cos(atilt)*cospol &
                   * sin(az)*sin(tlt))/(cos(atilt)*cos(az)))
      
  end subroutine c_pol

  subroutine az_horiz(kx, ky, kz, tlt, az)
  double precision, intent(in) :: kx, ky, kz, tlt
  double precision, intent(out) :: az
  double precision :: sin_term, cos_term
  
  sin_term = (&
    ((kx) * kz * tan(tlt) -(ky) * sqrt(1d0-kz**2/(cos(tlt)**2)))/&
    (1d0-kz**2))

  cos_term =(&
      (kz * tan(tlt) - kx * sin_term) / ky &
      )
  
  !az = mod(atan2(sin_term, cos_term) / 3.1415 * 180d0, 360d0) * 3.1415/180d0
  az = atan2(sin_term, cos_term)
  !az = asin(&
    !((kx) * kz * tan(tlt) -(ky) * sqrt(1d0-kz**2/(cos(tlt)**2)))/&
    !(1d0-kz**2))
  
  end subroutine

  subroutine pol_horiz(kx, ky, az, pol)
  double precision, intent(in) :: ky, kx, az
  double precision, intent(out) :: pol
  

  pol = asin((ky) * sin(az) -(kx) * cos(az))
  !pol = asin(abs(ky) * sin(az) - abs(kx) * cos(az))

  end subroutine

  function binarysearch(length, array, value, delta)
    ! Given an array and a value, returns the index of the element that
    ! is closest to, but less than, the given value.
    ! Uses a binary search algorithm.
    ! "delta" is the tolerance used to determine if two values are equal
    ! if ( abs(x1 - x2) <= delta) then
    !    assume x1 = x2
    ! endif

    implicit none
    integer, intent(in) :: length
    double PRECISION, dimension(length), intent(in) :: array
    !f2py depend(length) array
    double PRECISION, intent(in) :: value
    double PRECISION, intent(in), optional :: delta

    integer :: binarysearch

    integer :: left, middle, right
    double PRECISION :: d

    if (present(delta) .eqv. .true.) then
        d = delta
    else
        d = 1e-9
    endif
    
    left = 1
    right = length
    do
        if (left > right) then
            exit
        endif
        middle = nint((left+right) / 2.0)
        if ( abs(array(middle) - value) <= d) then
            binarySearch = middle
            return
        else if (array(middle) > value) then
            right = middle - 1
        else
            left = middle + 1
        end if
    end do
    binarysearch = right

end function binarysearch

subroutine interpolate_2D(x_len, x_array, y_len, y_array,&
   f, x, y,interpolate_result)
    ! This function uses bilinear interpolation to estimate the value
    ! of a function f at point (x,y)
    ! f is assumed to be sampled on a regular grid, with the grid x values specified
    ! by x_array and the grid y values specified by y_array
    ! Reference: http://en.wikipedia.org/wiki/Bilinear_interpolation
    implicit none
    integer, intent(in) :: x_len, y_len           
    double precision, dimension(x_len), intent(in) :: x_array
    double precision, dimension(y_len), intent(in) :: y_array
    double precision, dimension(x_len, y_len), intent(in) :: f
    double precision, intent(in) :: x,y
    ! double precision, intent(in), optional :: delta
    double PRECISION, intent(out) :: interpolate_result
    !f2py depend(x_len) x_array, f
    !f2py depend(y_len) y_array, f

    double PRECISION :: denom, x1, x2, y1, y2
    integer :: i,j

    i = binarysearch(x_len, x_array, x)
    j = binarysearch(y_len, y_array, y)

    x1 = x_array(i)
    x2 = x_array(i+1)

    y1 = y_array(j)
    y2 = y_array(j+1)
    
    denom = (x2 - x1)*(y2 - y1)

    interpolate_result = (f(i,j)*(x2-x)*(y2-y) + f(i+1,j)*(x-x1)*(y2-y) + &
        f(i,j+1)*(x2-x)*(y-y1) + f(i+1, j+1)*(x-x1)*(y-y1))/denom

end subroutine interpolate_2D

subroutine interpolate_1D(x_len, x_array, f, x, interpolate_result)
  ! This function uses bilinear interpolation to estimate the value
  ! of a function f at point (x,y)
  ! f is assumed to be sampled on a regular grid, with the grid x values specified
  ! by x_array and the grid y values specified by y_array
  ! Reference: http://en.wikipedia.org/wiki/Bilinear_interpolation
  implicit none
  integer, intent(in) :: x_len           
  double precision, dimension(x_len), intent(in) :: x_array
  
  double precision, dimension(x_len), intent(in) :: f
  double precision, intent(in) :: x
  ! double precision, intent(in), optional :: delta
  double PRECISION, intent(out) :: interpolate_result
  !f2py depend(x_len) x_array, f
  !f2py depend(y_len) y_array, f

  double PRECISION :: x1, x2
  integer :: i

  i = binarysearch(x_len, x_array, x)
  
  x1 = x_array(i)
  x2 = x_array(i+1)

  interpolate_result = (f(i)*(x2-x) + f(i+1) * (x-x1))/(x2-x1) 



end subroutine interpolate_1D


end module kmaps
