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
"""This module contains all functionality related to vertical dimension meta
data in LFRic. The two main features are the ability to parse the default and
hard coded values of vertical dimensions and to expand vertical dimension
declarations in LFRic meta data
e.g. model_height_dimension(top=TOP_WET_LEVEL)"""
# A no no-name-in-module error is caused by importing Ac_Value_List
# from fparser
# pylint: disable=no-name-in-module

import logging
import re
from typing import Dict, List
from fparser.two.Fortran2003 import Else_Stmt, \
    If_Then_Stmt, Component_Spec, Ac_Value_List
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk
from entities import Field


LOGGER = logging.getLogger(__name__)

DIMENSION_TYPE_REGEX = re.compile(r"(?P<type>[a-zA-Z_]+)[\s]*\([^)]*\)")
TOP_ARG_REGEX = re.compile(r"top[\s=]*(?P<top_arg>[A-Za-z_]+)")
BOTTOM_ARG_REGEX = re.compile(r"bottom[\s=]*(?P<bottom_arg>[A-Za-z_]+)")
LEVEL_DEF_REGEX = re.compile(r"(?P<level>[\d.]+)")
ENUM_REGEX = re.compile(r"(?P<levels>[a-zA-Z_]+)")

F2003_PARSER = ParserFactory().create(std="f2003")


def get_default_values(if_construct, path, levels):
    """Takes an fparser if_construct object as an argument. This if statement
    takes the form of
    if(present(DUMMY_ARG)) then
      a_level = DUMMY_ARG
    else
      a_level = DEFAULT_VALUE
    endif

    This function returns the DUMMY_ARG and DEFAULT_VALUE as a tuple. If values
    not found, the error is logged and a tuple containing none's is returned
    """
    dummy_arg = None
    default_value = None

    for i in range(len(if_construct.content)):

        # Get Dummy argument
        if isinstance(if_construct.content[i], If_Then_Stmt):
            line = if_construct.content[i + 1].items
            dummy_arg = line[2].tostr()

        # Get Default value
        if isinstance(if_construct.content[i], Else_Stmt):
            line = if_construct.content[i + 1].items
            default_value = line[2].tostr()

    if not dummy_arg or not default_value:
        LOGGER.error("File at %s is invalid. Problem with default "
                     "values", path)
    if default_value not in levels:
        LOGGER.error("File at %s is invalid. Default level does not"
                     " exist", path)

    return dummy_arg, default_value


def translate_vertical_dimension(dimension_declaration):
    """Takes dimension definition as a string and returns a dictionary
    containing that dimension's attributes
    :param dimension_declaration: A string that defines the type of vertical
    and any arguments that it is taking
    :return parsed_definition: """

    LOGGER.debug("Parsing a vertical dimension")
    LOGGER.debug("Dimension declaration: %s", dimension_declaration)

    parsed_definition = {}
    dimension_type_match = DIMENSION_TYPE_REGEX.search(dimension_declaration)
    top_arg = TOP_ARG_REGEX.search(dimension_declaration)
    bottom_arg = BOTTOM_ARG_REGEX.search(dimension_declaration)
    fixed_levels = LEVEL_DEF_REGEX.findall(dimension_declaration)

    dimension_type = dimension_type_match.group('type')

    if "model" in dimension_type:
        if top_arg:
            parsed_definition["top_arg"] = top_arg.group("top_arg")
        else:
            raise Exception("Top model level not declared")

        if bottom_arg:
            parsed_definition["bottom_arg"] = bottom_arg.group("bottom_arg")
        else:
            raise Exception("Bottom model level not declared")

    if fixed_levels:
        levels = []
        for level in fixed_levels:
            levels.append(float(level))
        parsed_definition["level_definition"] = levels

    parsed_definition["units"] = "m"
    if "height" in dimension_type:
        parsed_definition["positive"] = "POSITIVE_UP"
        parsed_definition["standard_name"] = "height"
    elif "depth" in dimension_type:
        parsed_definition["positive"] = "POSITIVE_DOWN"
        parsed_definition["standard_name"] = "depth"
    else:
        raise Exception("Attribute 'positive' has been declared incorrectly")

    LOGGER.debug("Parsed Definition: %s", parsed_definition)
    return parsed_definition


def parse_non_spatial_dimension(non_spatial_dimension: Ac_Value_List,
                                field: Field) -> List[Dict]:
    """Takes an fparser object, that contains non_spatial_dimension data for
    one field, and returns that data in a list of dictionaries.
    Each dictionary representing a non-spatial dimension.
    :param non_spatial_dimension:
    :param field: Used for logging purposes
    :return: A list of dictionaries that each contain definitions
     of non-spatial dimensions"""

    LOGGER.debug("Parsing non-spatial dimensions for %s", field.unique_id)
    LOGGER.debug("Dimension declaration: %s", non_spatial_dimension)

    definitions = []
    types = {"NUMERICAL": "axis_definition",
             "CATEGORICAL": "label_definition"}
    for nsd in non_spatial_dimension.children:
        definition = {}
        for attribute in walk(nsd, types=Component_Spec):

            if attribute.children[0].string == "dimension_name":
                definition.update(
                    {"name": attribute.children[1].string[1:-1].lower()})

            elif attribute.children[0].string == "dimension_category":
                definition.update(
                    {"type": types[attribute.children[1].string]})

            elif attribute.children[0].string == "label_definition":
                labels = []
                for item in attribute.children[1].children[1].children[1]\
                        .children:
                    labels.append(item.string[1:-1])
                definition.update({"label_definition": labels})

            elif attribute.children[0].string == "axis_definition":
                axis = []
                for item in attribute.children[1].children[1].children[1]\
                        .children:
                    axis.append(item.string)
                definition.update({"axis_definition": axis})

            elif attribute.children[0].string == "help_text":
                definition.update({"help": attribute.children[1].string[1:-1]})

            elif attribute.children[0].string == "non_spatial_units":
                definition.update(
                    {"unit": attribute.children[1].string[1:-1]})

            else:
                raise Exception(f"Unrecognised non-spatial-dimension attribute"
                                f" '{attribute.children[0].string}' in"
                                f" {field.unique_id}")

        definitions.append(definition)

        if not definition.get("name", None):
            raise Exception(f"Non-spatial dimension in {field.unique_id} "
                            f"requires 'dimension_name' attribute")

    LOGGER.debug("Parsed Definitions: %s", definitions)
    return definitions
