!!-----------------------------------------------------------------------------
! (c) Crown copyright 2020 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!------------------------------------------------------------------------------
!
!> @brief ENUM containing different model levels
!> @details This enumerator contains all the possible model levels
!> for an LFRic field. It is used by vertical_dimensions_mod.f90 and
!> field meta data definition files for specifying model levels

module levels_enum_mod

  implicit none

  enum, bind(c)
    enumerator :: BOTTOM_ATMOSPHERIC_LEVEL,                          &
                  TOP_ATMOSPHERIC_LEVEL,                             &
                  TOP_WET_LEVEL,                                     &
                  TOP_ATMOSPHERIC_LEVEL_MINUS_ONE,                   &
                  BOTTOM_LEVEL_IN_BOUNDARY_LAYER,                    &
                  TOP_LEVEL_IN_BOUNDARY_LAYER,                       &
                  BOTTOM_LEVEL_ABOVE_BOUNDARY_LAYER,                 &
                  BOTTOM_SOIL_LEVEL,                                 &
                  TOP_SOIL_LEVEL,                                    &
                  BOTTOM_TRACER_LEVEL,                               &
                  TOP_TRACER_LEVEL,                                  &
                  TOP_GRAVITY_WAVE_DRAG_LEVEL_PLUS_ONE,              &
                  BOTTOM_GRAVITY_WAVE_DRAG_LEVEL,                    &
                  TOP_GRAVITY_WAVE_DRAG_LEVEL,                       &
                  BOTTOM_LEVEL_IN_VERTICAL_DIFFUSION_ROUTINE,        &
                  TOP_LEVEL_IN_VERTICAL_DIFFUSION_ROUTINE_MINUS_ONE, &
                  TOP_LEVEL_IN_VERTICAL_DIFFUSION_ROUTINE,           &
                  TOP_LEVEL_IN_BOUNDARY_LAYER_MINUS_ONE,             &
                  TOP_LEVEL_OF_ATMOSPHERE_PLUS_ONE,                  &
                  BOTTOM_SOIL_LEVEL_PLUS_ONE,                        &
                  TOP_OZONE_LEVEL,                                   &
                  NUMBER_OF_CLOUDY_LEVELS

  end enum
end module levels_enum_mod