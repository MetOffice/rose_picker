!!-----------------------------------------------------------------------------
! (c) Crown copyright 2020 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!------------------------------------------------------------------------------
!
!> @brief ENUM containing different field synonyms methods
!> @details This enumerator contains all the possible field synonyms
!> methods for an LFRic field. It is used by meta_data_mod.f90 for
!> specifying the recommended field synonyms type

module field_synonyms_enum_mod

  implicit none

  enum, bind(c)

    enumerator :: AMIP, &
                  CF,   &
                  CMIP6,&
                  GRIB, &
                  STASH

  end enum

end module field_synonyms_enum_mod