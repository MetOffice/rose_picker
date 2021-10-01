!-------------------------------------------------------------------------------
! (C) Crown copyright 2020 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!-------------------------------------------------------------------------------
!
!               Test Module Diagnostic Meta File
!
! This is a test file that illustrates how you define meta data for a field
!
!-------------------------------------------------------------------------------
module system__test_with_vlevels__meta_mod

  use diagnostics_mod,                only: field_meta_data_type
  use constants_mod,                  only: real_type, r_def, i_def, str_short
  !> Only import the dimensions that you will actually be using
  use vertical_dimensions_mod,        only: model_height_dimension, &
                                            model_depth_dimension, &
                                            fixed_height_dimension
  use non_spatial_dimension_mod,      only: non_spatial_dimension_type, &
                                            NUMERICAL, &
                                            CATEGORICAL
  use misc_meta_data_mod,             only: misc_meta_data_type
  use field_synonym_mod,              only: field_synonym_type
  !> Only import the function spaces that you will actually be using
  use fs_continuity_mod,              only: W2, W3, Wtheta
  !> Only import the time steps that you will actually be using
  use time_step_enum_mod,             only: STANDARD_TIMESTEP
  !> Only import the interpolation methods that you will actually be using
  use interpolation_enum_mod,         only: BILINEAR
  !> Only import the levels that you will actually be using
  use levels_enum_mod,                only: TOP_WET_LEVEL, &
                                            BOTTOM_SOIL_LEVEL, &
                                            TOP_SOIL_LEVEL, &
                                            BOTTOM_ATMOSPHERIC_LEVEL, &
                                            TOP_ATMOSPHERIC_LEVEL
  use positive_enum_mod,              only: POSITIVE_UP, POSITIVE_DOWN
  use field_synonyms_enum_mod,        only: AMIP, GRIB, CF, CMIP6, STASH

  implicit none

  private

  type, public :: system__test_with_vlevels__meta_type

    !> Declare the name of your fields here
    type(field_meta_data_type), public :: &
      test_field
    character(str_def) :: name = "system__test_with_vlevels"

    end type system__test_with_vlevels__meta_type

  interface system__test_with_vlevels__meta_type
    module procedure system__test_with_vlevels__meta_constructor
  end interface

contains

  !>@brief Creates field_meta_data_type objects for a specific section of science
  function system__test_with_vlevels__meta_constructor() result(self)
    implicit none

    type(system__test_with_vlevels__meta_type) :: self

    !> Example field using a height vertical dimension using model levels
    !> If no arguments are present, it will default to top atmospheric level
    !> and bottom atmospheric level. This field also uses a standard name,
    !> which is optional
    self%test_field = field_meta_data_type(&
      unique_id = "example_fields__test_field", &
      units = "m s-1", &
      function_space = W2, &
      order = 0, &
      io_driver = "", &
      trigger = "__checksum: true;", &
      description = "u component of wind on u pts on native c grid.", &
      data_type = REAL_TYPE, &
      time_step = STANDARD_TIMESTEP, &
      recommended_interpolation = BILINEAR, &
      packing = 0, &
      standard_name = "test_field", &
      vertical_dimension = model_height_dimension( &
            bottom = BOTTOM_ATMOSPHERIC_LEVEL, &
            top = TOP_ATMOSPHERIC_LEVEL), &
      synonyms = [ &
            field_synonym_type(STASH, "2"),&
            field_synonym_type(AMIP, "ua"),&
            field_synonym_type(GRIB, "33 E131"),&
            field_synonym_type(CF, "eastward_wind"),&
            field_synonym_type(CMIP6, "ua")&
        ],&
      misc_meta_data = [misc_meta_data_type("positive","eastwards")])

  end function system__test_with_vlevels__meta_constructor
end module system__test_with_vlevels__meta_mod