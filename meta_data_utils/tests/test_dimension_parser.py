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
from fparser.two.Fortran2003 import Component_Spec, \
    Array_Constructor, Ac_Value_List
from fparser.common.readfortran import FortranFileReader
from fparser.two.parser import ParserFactory
from dimension_parser import translate_vertical_dimension, \
    parse_non_spatial_dimension
from entities import Field

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data"


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


def test_parse_non_spatial_dimension():
    """
    Test that non-spatial-dimensions are correctly parsed when declared using
    axis- or label-definitions
    """

    expected_non_spatial_dims = [
        [{"name": "test_axis_non_spatial_dimension",
          "type": "axis_definition",
          "help": "test_axis_non_spatial_dimension help text",
          "axis_definition": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
          "unit": "1"}],
        [{"name": "test_tiles",
          "type": "label_definition",
          "help": "test_tiles help text",
          "label_definition": ['test_value_1',
                               'test_value_2',
                               'test_value_3']}]
    ]

    reader = FortranFileReader(TEST_DIR +
                               "/non_spatial_dimension__meta_mod.f90",
                               ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)
    dummy_field = Field("test_path")
    dummy_field.unique_id = "dummy__field"
    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Component_Spec):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":
                for array in walk(parameter.children,
                                  types=Ac_Value_List):
                    if "non_spatial_dimension" in array.children[0].string:
                        non_spatial_dim = parse_non_spatial_dimension(
                            array, dummy_field)
                        non_spatial_dimensions.append(non_spatial_dim)

    assert non_spatial_dimensions == expected_non_spatial_dims


def test_parse_non_spatial_dimension_no_name():
    """
    Test that an exception is raised when a non-spatial dimension is declared
    without a name
    """
    reader = FortranFileReader(TEST_DIR +
                               "/non_spatial_dimension__no_name__meta_mod.f90",
                               ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)
    dummy_field = Field("test_path")
    dummy_field.unique_id = "dummy__field"

    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Component_Spec):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":
                for array in walk(parameter.children,
                                  types=Ac_Value_List):
                    if "non_spatial_dimension" in array.children[0].string:
                        with pytest.raises(Exception) as excinfo:
                            definitions = parse_non_spatial_dimension(
                                array, dummy_field)
                            non_spatial_dimensions.append(definitions)
                        assert ("Non-spatial dimension in dummy__field "
                                "requires 'dimension_name' attribute"
                                in str(excinfo.value))


def test_parse_non_spatial_dimension_unrecognised_attribute():
    """
    Test that an exception is raised when an unrecognised non-spatial-dimension
    attribute is present
    """
    reader = FortranFileReader(
        TEST_DIR +
        "/non_spatial_dimension__unrecognised_attribute__meta_mod.f90",
        ignore_comments=True)
    f2003_parser = ParserFactory().create(std="f2003")
    parse_tree = f2003_parser(reader)
    dummy_field = Field("test_path")
    dummy_field.unique_id = "dummy__field"

    non_spatial_dimensions = []
    for parameter in walk(parse_tree, Component_Spec):
        if isinstance(parameter.children[1], Array_Constructor):
            if parameter.children[0].string == "non_spatial_dimension":

                for array in walk(parameter.children,
                                  types=Ac_Value_List):
                    if "non_spatial_dimension" in array.children[0].string:
                        with pytest.raises(Exception) as excinfo:
                            definitions = parse_non_spatial_dimension(
                                array, dummy_field)
                            non_spatial_dimensions.append(definitions)
                        assert ("Unrecognised non-spatial-dimension "
                                "attribute 'unrecognised_attribute'"
                                in str(excinfo.value))
