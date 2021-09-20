!------------------------------------------------------------------------------
! (C) Crown copyright 2021 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!------------------------------------------------------------------------------
! File for testing parse_non_spatial_dimension() in dimension_parser.py
! This code is not intended to be compiled
module non_spatial_dimension__invalid_attribute__meta_mod

  use diagnostics_mod,                only: field_meta_data_type
  use constants_mod,                  only: real_type, r_def, str_def
  !> Only import the dimensions that you will actually be using
  use vertical_dimensions_mod,        only: model_height_dimension
  use misc_meta_data_mod,             only: misc_meta_data_type
  use field_synonym_mod,              only: field_synonym_type
  !> Only import the function spaces that you will actually be using
  use fs_continuity_mod,              only: W2
  !> Only import the time steps that you will actually be using
  use time_step_enum_mod,             only: STANDARD_TIMESTEP
  !> Only import the interpolation methods that you will actually be using
  use interpolation_enum_mod,         only: BILINEAR
  !> Only import the levels that you will actually be using
  use levels_enum_mod,                only: BOTTOM_ATMOSPHERIC_LEVEL, &
                                            TOP_ATMOSPHERIC_LEVEL
  use field_synonyms_enum_mod,        only: AMIP, GRIB, CF, CMIP6, STASH

  implicit none

  private

  type, public :: non_spatial_dimension__invalid_attribute__meta_type

    !> Declare the name of your fields here
    type(field_meta_data_type), public :: &
      test__field
      character(str_def) :: name = "non_spatial_dimension__invalid_attribute"
  end type non_spatial_dimension__invalid_attribute__meta_type

  interface non_spatial_dimension__invalid_attribute__meta_type
    module procedure non_spatial_dimension__invalid_attribute__meta_constructor
  end interface

contains

  function non_spatial_dimension__invalid_attribute__meta_constructor() result(self)

    implicit none

    type(example_science_section__example_fields__meta_type) :: self

    self%test__field = field_meta_data_type(&
      unrecognised_attribute = "something", &
      unique_id = "test_1", &
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
      vertical_dimension = model_height_dimension( &
              bottom = BOTTOM_ATMOSPHERIC_LEVEL, &
              top = TOP_ATMOSPHERIC_LEVEL), &
      standard_name = "eastward_wind", &
      synonyms = [ &
            field_synonym_type(STASH, "2"),& !> literally this stash code or approx - let the user know
            field_synonym_type(AMIP, "ua"),&
            field_synonym_type(GRIB, "33 E131"),&
            field_synonym_type(CF, "eastward_wind"),&
            field_synonym_type(CMIP6, "ua")&
        ],&
      non_spatial_dimension = [non_spatial_dimension_type( &
              dimension_name = "test_axis_non_spatial_dimension", &
              axis_definition = [real(r_def) :: 1,2,3,4,5,6,7,8,9])], &
      misc_meta_data = [misc_meta_data_type("positive","eastwards")])

  end function non_spatial_dimension__invalid_attribute__meta_constructor

end module non_spatial_dimension__invalid_attribute__meta_mod