!!-----------------------------------------------------------------------------
! (c) Crown copyright 2020 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!------------------------------------------------------------------------------
!
!> @brief ENUM containing different time steps
!> @details This enumarator contains all the timesteps available for an LFRic
!> field. It is used by vertical_dimensions_mod.f90 and field meta data
!> definition files for specifying the timestep that the field is output on
module time_step_enum_mod

  implicit none

  enum, bind(c)
    enumerator :: STANDARD_TIMESTEP, &
                  RADIATION_TIMESTEP
  end enum
end module time_step_enum_mod