#!/usr/bin/env python
##############################################################################
# (C) British Crown Copyright 2020 Met Office.
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
"""Test the dimension parsing..."""
import os
import pytest
from fparser.two.utils import walk
from fparser.two.Fortran2003 import Structure_Constructor_2, \
    Array_Constructor, Section_Subscript_List
from fparser.common.readfortran import FortranFileReader
from fparser.two.parser import ParserFactory
from dimension_parser import translate_vertical_dimension, \
    parse_non_spatial_dimension
from fortran_reader import read_enum

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data"
ENUM_TEST_FILE = "/enum_test_file"


def test_read_enum():
    """Check that test enum file is correctly read"""
    assert read_enum(TEST_DIR + ENUM_TEST_FILE) == ["ONE", "TWO"]


def test_translate_vertical_dimension():
    """
    Test that model and fixed dimensions are correctly translated for height
    and depth. Check input without height or depth correctly raises exception
    """
    model_height = translate_vertical_dimension("model_height_dimension("
                                                "bottom="
                                                "BOTTOM_ATMOSPHERIC_LEVEL, "
                                                "top=TOP_ATMOSPHERIC_LEVEL)")
    model_depth = translate_vertical_dimension("model_depth_dimension("
                                               "bottom=BOTTOM_SOIL_LEVEL, "
                                               "top=TOP_SOIL_LEVEL)")
    fixed_height = translate_vertical_dimension("fixed_height_dimension()")
    fixed_depth = translate_vertical_dimension("fixed_depth_dimension()")

    # Test that input without height or depth raises exception
    with pytest.raises(Exception) as excinfo:
        _ = translate_vertical_dimension("fixed_dimension()")
    assert "Attribute 'positive' has been declared incorrectly" in str(
            excinfo.value)

    assert model_height == {"standard_name": "height",
                            "units": "m",
                            "top_arg": "TOP_ATMOSPHERIC_LEVEL",
                            "bottom_arg": "BOTTOM_ATMOSPHERIC_LEVEL",
                            "positive": "POSITIVE_UP"}
    assert model_depth == {"standard_name": "depth",
                           "units": "m",
                           "top_arg": "TOP_SOIL_LEVEL",
                           "bottom_arg": "BOTTOM_SOIL_LEVEL",
                           "positive": "POSITIVE_DOWN"}
    assert fixed_height == {"standard_name": "height",
                            "units": "m",
                            "positive": "POSITIVE_UP"}
    assert fixed_depth == {"standard_name": "depth",
                           "units": "m",
                           "positive": "POSITIVE_DOWN"}


def test_parse_non_spatial_dimension(caplog):
    """
    Test that non-spatial-dimensions are correctly parsed when declared using
    axis- or label-definitions
    """
    reader = FortranFileReader(TEST_DIR +
                               "/non_spatial_dimension_test_data.f90",
                               ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)

    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Structure_Constructor_2):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":

                for array in walk(parameter.children,
                                  types=Section_Subscript_List):
                    key, value = parse_non_spatial_dimension(array)
                    non_spatial_dimensions.append((key, value))

    assert non_spatial_dimensions == \
        [('test_axis_non_spatial_dimension',
          ['1', '2', '3', '4', '5', '6', '7', '8', '9']),
         ("test_tiles", ['test_value_1', 'test_value_2', 'test_value_3'])]


def test_parse_non_spatial_dimension_no_name(caplog):
    """
    Test that an exception is raised when a non-spatial dimension is declared
    without a name
    """
    reader = FortranFileReader(TEST_DIR +
                               "/non_spatial_dimension_test_data_no_name.f90",
                               ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)

    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Structure_Constructor_2):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":

                for array in walk(parameter.children,
                                  types=Section_Subscript_List):
                    with pytest.raises(Exception) as excinfo:
                        key, value = parse_non_spatial_dimension(array)
                        non_spatial_dimensions.append((key, value))
                    assert "Non-spatial dimension requires 'dimension_name' " \
                           "attribute" in str(excinfo.value)


def test_parse_non_spatial_dimension_unrecognised_attribute(caplog):
    """
    Test that an exception is raised when an unrecognised non-spatial-dimension
    attribute is present
    """
    reader = FortranFileReader(
            TEST_DIR +
            "/non_spatial_dimension_test_data_unrecognised_attribute.f90",
            ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)

    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Structure_Constructor_2):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":

                for array in walk(parameter.children,
                                  types=Section_Subscript_List):
                    with pytest.raises(Exception) as excinfo:
                        key, value = parse_non_spatial_dimension(array)
                        non_spatial_dimensions.append((key, value))
                    assert "Unrecognised non-spatial-dimension attribute " \
                           "'unrecognised_attribute'" in str(excinfo.value)
