#!/usr/bin/env python
##############################################################################
# (C) British Crown Copyright 2021 Met Office.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Rose. If not, see <http://www.gnu.org/licenses/>.
##############################################################################
"""Test the field_validator module"""

from entities import Field
from field_validator import validate_field


def test_validate_field(caplog):
    """Test that validate_field works on a valid field"""
    test_field = Field("test__file_name__meta_mod.f90")
    test_field.unique_id = "test__unique_id"
    test_field.standard_name = "test_standard_name"
    test_field.units = "test_unit"
    test_field.function_space = "test_function_space"
    test_field.trigger = "test_triggering_syntax"
    test_field.description = "test_description"
    test_field.data_type = "test_data_type"
    test_field.time_step = "test_time_step"
    test_field.recommended_interpolation = "test_interpolation"

    result = validate_field(test_field)

    assert result is True
    assert caplog.text == ''


def test_validate_bad_field(caplog):
    """Test that validate_field outputs all the correct errors in logs on an
     invalid field"""

    test_field = Field("test_bad_file_name")
    result = validate_field(test_field)

    assert result is False
    assert ("A unique id is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A unit of measure is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A function space is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("Triggering syntax is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A description is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A data type is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A time step is missing from a field in test_bad_file_name"
            in caplog.text)
    assert ("A recommended_interpolation attribute is missing from a field "
            "in test_bad_file_name" in caplog.text)


def test_validate_bad_field_2(caplog):
    """Test that validate_field gives the feedback in error logs"""
    test_field = Field("test__file_name__meta_mod.f90")
    test_field.unique_id = "test__unique_name"

    result = validate_field(test_field)

    assert result is False
    assert ("test__unique_name in test__file_name__meta_mod.f90 has neither a"
            " standard name or long name" in caplog.text)
