!! 
!! This module provides functionalities related to the obatin a vector with init
!! of each sparse matrix line.
!! 
!! This module is part of the IterativeSolvers project and contains various
!! subroutines and functions to implement and manage Crow iterative solvers.
!! 
!! @note Ensure that all dependencies are properly linked when using this module.
module modCrow
    use modVerify
    implicit none

    contains  

    !---------------------------------------------------------------------------
    !---------------------------------------------------------------------------
    ! Esta subrotina monta o vetor crow que indica o inicio de cada linha no 
    ! vetorde valores e no vetor que armazena as colunas dos coeficientes.
    !                         Kleucio Claudio 07/06/2002      
    !---------------------------------------------------------------------------     
    !! This subroutine generates the crow array based on the input vector.
    !!
    !! @param i_vect Input integer vector of size nz.
    !! @param n Number of unique elements in i_vect.
    !! @param nz Total number of elements in i_vect.
    !! @param crow Output integer vector of size n+1, which stores the indices 
    !!             where the unique elements in i_vect start.
    !!
    !! This subroutine initializes the crow array such that crow(1) is set to 1.
    !! It then iterates through the input vector i_vect and whenever a change in 
    !! value is detected, it records the index of the change in the crow array.
    !! Finally, it sets the last element of crow to nz + 1.
    subroutine crowf(i_vect, n, nz, crow)
    
        implicit none 
        integer, dimension (:), intent(in)    :: i_vect
        integer, dimension (:), intent(inout) :: crow 
        integer               , intent(in)    :: n, nz
    
        integer i, k
        call verify_size_integer(i_vect, nz)
        k = 2
        crow(1) = 1
        do 10 i = 2, nz 
            if (i_vect(i - 1).ne.i_vect(i)) then
                crow(k) = i
                k = k + 1
            end if
10      end do      
        crow(n + 1) = nz + 1
!      write (6, *) (crow(i),i = 1, nz)  

    end  subroutine crowf

    !---------------------------------------------------------------------------
    !---------------------------------------------------------------------------
    ! Esta subrotina encontra o numero maximo de colunas da matriz
    !
    !                         Kleucio Claudio 05/09/2024      
    !---------------------------------------------------------------------------     
    !----------------------------------------------------------------------
    !! Determines the maximum number of non-zero elements in any row of a 
    !! sparse matrix represented in compressed row storage (CRS) format.
    !!
    !! @param i_vect Integer array containing the row indices of the non-zero elements.
    !! @param n Integer representing the number of rows in the matrix.
    !! @param nz Integer representing the number of non-zero elements in the matrix.
    !! @param crow Integer array containing the starting index of each row in the i_vect array.
    !! @param n_line_max Integer output representing the maximum number of non-zero elements in any row.
    !----------------------------------------------------------------------
    subroutine max_row(i_vect, n, nz, crow, n_line_max)

        implicit none 

        integer, intent(in) :: nz
        integer, intent(in) :: n
        integer, dimension (:), intent(in) :: i_vect
        integer, dimension (:), intent(in) :: crow 
        integer, intent(out) :: n_line_max
        
        integer i
    
        call verify_size_integer(crow, n + 1)
        n_line_max = 0 
       do 10 i = 1, n 
            if ((crow(i + 1) - crow(i)).ge.n_line_max) then
                n_line_max = crow(i + 1) - crow(i)           
             end if
    10   end do      

     end  subroutine max_row


!   !---------------------------------------------------------------------------
    !---------------------------------------------------------------------------
!   ! Esta subrotina monta o vetor crow que indica o inicio de cada linha 
!   ! no vetorde valores e no vetor que armazena as colunas dos coeficientes 
!   ! das matrizes l e u.
!   !                       Kleucio Claudio 13/12/2002      
!   !---------------------------------------------------------------------------
!   !     
!       subroutine crowf_lu(i_vect_l,i_vect_u,n,nz_l,nz_u,crow_lu)
!   !
!       implicit none 
!       integer nz_l,nz_u,n,crow_lu(*), i_vect_l(*),i_vect_u(*)
    
!      integer i,k
!   !      
!       k=2
!       crow_lu(1)=1
!       do 10 i=2,nz_l 
!         if (i_vect_l(i-1).ne.i_vect_l(i)) then
! 	  crow_lu(k)=i
! 	  k=k+1
! 	end if
! 10    end do          
! 	crow_lu(n+1)=nz_l+1
!   !
! 	crow_lu(n+2)=1
!       k=n+3
! 	do 20 i=2,nz_u 
!         if (i_vect_u(i-1).ne.i_vect_u(i)) then
! 	  crow_lu(k)=i
! 	  k=k+1
! 	end if
! 20    end do      
!       crow_lu(2*n+2)=nz_u+1

!  !	 write (6, *) (crow_lu(i),i = 1, nz)  
!  ! 
! end  subroutine crowf_lu
!  !      !fim de crowf_lu.f

    ! !!  Verifies if the size of the integer vector matches the expected size.
    ! !! 
    ! !! This subroutine checks whether the size of the input integer vector `vect`
    ! !! is equal to the specified size `n_size`. It is useful for validating input
    ! !! data before performing operations that require vectors of a specific size.
    ! !!
    ! !! @param vect The integer vector whose size is to be verified.
    ! !! @param n_size The expected size of the integer vector.
    ! subroutine verify_size_integer(vect, n_size)

    ! implicit none
    ! integer, dimension(:), intent(in) :: vect
    ! integer, intent(in) :: n_size

    !     if (size(vect) /= n_size) then 
    !         print *, 'Error: Vector size does not match the expected size.'
    !         stop
    !     end if
        
    ! end subroutine verify_size_integer

    ! !!  Verifies the size of a complex vector.
    ! !! 
    ! !! This subroutine checks if the size of the given complex vector matches the expected size.
    ! !!
    ! !! @param vect The complex vector to be verified.
    ! !! @param n_size The expected size of the complex vector.
    ! subroutine verify_size_cplx(vect, n_size)
    ! use modPrecision

    !     implicit none
    !     complex (kind = dp), dimension(:), intent(in) :: vect
    !     integer, intent(in) :: n_size
    
    !         if (size(vect) /= n_size) then 
    !             print *, 'Error: Vector size does not match the expected size.'
    !             stop
    !         end if
            
    ! end subroutine verify_size_cplx
        
end module modCrow
