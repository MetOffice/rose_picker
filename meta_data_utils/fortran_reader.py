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
"""This module contains functionality for finding and parsing LFRic diagnostic
 meta data files"""
import glob
import logging
import re
from typing import Dict, Tuple

from fparser.common.readfortran import FortranFileReader
from fparser.two.Fortran2003 import Array_Constructor, Assignment_Stmt, \
    Char_Literal_Constant, Enumerator_Def_Stmt, \
    Level_3_Expr, Part_Ref, Structure_Constructor, \
    Component_Spec, Ac_Value_List, Derived_Type_Stmt, Derived_Type_Def, \
    Data_Component_Def_Stmt, Intrinsic_Type_Spec, Component_Decl
from fparser.two.parser import ParserFactory
from fparser.two.utils import FparserException, walk

from dimension_parser import translate_vertical_dimension, \
    parse_non_spatial_dimension
from entities import Field, Group, Section
from field_validator import validate_field
from file_validator import validate_names

F2003_PARSER = ParserFactory().create(std="f2003")


class FortranMetaDataReader:
    """This encapsulates all the parsing functionality. It is give a root
    directory (Head of the repository) upon creation"""

    LOGGER = logging.getLogger("lfric_meta_data_parser")
    vertical_dimension_definition = None
    valid_meta_data = True

    FILE_NAME_REGEX = re.compile(
        r"(?P<section_name>[a-zA-Z_0-9]+?)__"
        r"(?P<group_name>[a-zA-Z_0-9]+)__meta_mod.*90")

    def __init__(self, root_directory: str, meta_types_path: str):
        self.__root_dir = root_directory
        self.meta_types_path = meta_types_path
        self.meta_mod_files = None
        self.find_fortran_files()
        self.levels = read_enum(meta_types_path + "levels_enum_mod.f90")
        self.non_spatial_dims = {}

    def find_fortran_files(self):
        """Recursively looks for Fortran files ending with "__meta_mod.f90"
        Initialises the vertical_dimension_definition variable
        Returns a list of file names"""

        self.LOGGER.info("Scanning for Fortran meta data files...")
        self.meta_mod_files = glob.glob(
            self.__root_dir +
            '/**/source/diagnostics_meta/**/*__meta_mod.*90',
            recursive=True)

        self.meta_mod_files.sort()

        for file in self.meta_mod_files:
            self.LOGGER.debug("Found meta date file at: %s", file)

        self.LOGGER.info("Found %i meta data files", len(self.meta_mod_files))

    def validate_naming(self, file_path, parse_tree):
        """Finds all the different names declared within *__meta_mod.f90 files
        param: file_path: The file of the *__meta_mod.f90
        param: parse_tree: The Abstract Syntax Tree of the *__meta_mod.f90
        created by fparser"""

        # get module name
        module_name = parse_tree.children[0].children[0].children[
            1].string

        meta_type_name = None

        # Get meta_type name
        for meta_type in walk(parse_tree.content,
                              types=Derived_Type_Stmt):
            meta_type_name = meta_type.children[1].string

        # Get group name declared within
        group_name = None
        for type_def in walk(parse_tree.content, types=Derived_Type_Def):
            for variable in walk(type_def.children,
                                 types=Data_Component_Def_Stmt):
                if isinstance(variable.children[0], Intrinsic_Type_Spec):
                    if variable.children[0].children[0] == 'CHARACTER':
                        for group in walk(variable.children, Component_Decl):
                            if group.children[0].string == "name":
                                group_name = group.children[3].children[1].\
                                    string.replace('"', '')

        naming_valid = validate_names(file_path, module_name,
                                      meta_type_name, group_name)
        if not naming_valid:
            self.valid_meta_data = False

        return naming_valid

    def read_fortran_files(self) -> Tuple[Dict, bool]:
        """Takes a list of file names (meta_mod.f90 files)
        Checks for correctness and returns the relevant Fortran lines in a list
        :return Metadata: A dictionary, each key represents a Fortran file and
        it's value is a list of strings, each element representing a field"""

        sections_dict: Dict[str, Section] = {}
        valid_files = 0
        # Loop over each found Fortran file
        for file_path in self.meta_mod_files:

            try:
                # Load the Fortran file

                reader = FortranFileReader(file_path, ignore_comments=True)

                parse_tree = F2003_PARSER(reader)

                file_valid = self.validate_naming(file_path, parse_tree)

                file_name_parts = self.FILE_NAME_REGEX.search(file_path)

                if not file_name_parts:
                    self.LOGGER.error('Filename in path is not correct %s',
                                      file_path)
                    self.valid_meta_data = False
                    break

                section_name = file_name_parts.group("section_name")
                group_name = file_name_parts.group("group_name")
                file_name = file_path[file_path.rfind("/") + 1:]

                if file_section_name not in sections_dict:
                    sections_dict.update(
                        {file_section_name: Section(name=file_section_name)}
                        )

                group = Group(name=file_group_name, file_name=file_name)

                sections_dict[file_section_name].add_group(group)

                # For every instance of a meta type object being created
                for definition in walk(parse_tree.content,
                                       types=Assignment_Stmt):

                    field, valid = self.extract_field(definition, file_name)

                    if not valid:
                        self.valid_meta_data = False
                        file_valid = False

                    if validate_field(field):
                        group.add_field(field)
                    else:
                        self.LOGGER.error("%s is invalid. Please check",
                                          field.unique_id)
                        self.valid_meta_data = False
                        file_valid = False

                if file_valid:
                    valid_files += 1

            except FparserException as error:
                self.LOGGER.error(": Fparser Exception %s", error)
                self.valid_meta_data = False

        meta_data = {"sections": sections_dict,
                     "standard_level_markers": self.levels,
                     "non_spatial_dimensions": self.non_spatial_dims}

        if valid_files == len(self.meta_mod_files):
            self.LOGGER.info("All %i files are valid",
                             len(self.meta_mod_files))
        else:
            self.LOGGER.error("%i of %i files are invalid",
                              len(self.meta_mod_files) - valid_files,
                              len(self.meta_mod_files))

        return meta_data, self.valid_meta_data

    def extract_field(self, definition, file_name) -> Tuple[Field, bool]:
        """Takes an fparser object and extracts the field definition
        information
        :param definition: An fparser object that contains a field definition
        :param file_name: The name of the file that the field is declared in.
        This is needed for Field object creation
        :return Field"""

        valid_field = True
        field = Field(file_name)

        # For every instance argument in object creation
        for parameter in walk(definition, Component_Spec):

            key = parameter.children[0].string

            # This ignores arguments that are used to create attributes, such
            # as the arguments in vertical dimension and non_spatial_dimension
            # creation
            key_blacklist = ["top",
                             "bottom",
                             "label_definition",
                             "axis_definition",
                             "dimension_name",
                             "dimension_category",
                             "non_spatial_units",
                             "help_text"]
            if key in key_blacklist:
                continue

            # Adds the key / value to the Field object
            if not hasattr(field, key):
                self.LOGGER.error("Unexpected Field Property: %s", key)
                valid_field = False

            try:
                # For multi line statements - override the key value
                if isinstance(parameter.children[1], Level_3_Expr):
                    value = self.extract_multi_line_statement(
                        parameter.children[1])
                    field.add_value(key, value)

                # ENUM's
                elif isinstance(parameter.children[1], Char_Literal_Constant):
                    field.add_value(key, parameter.children[1].string[1:-1])

                # Dimension object creation without args
                # (Structure_Constructor) or with args (Part_Ref)
                elif isinstance(parameter.children[1],
                                (Part_Ref, Structure_Constructor)):
                    field.add_value(key, translate_vertical_dimension(
                        parameter.children[1].string))

                # For statements with arrays in them (misc_meta_data /
                # synonyms, non_spatial_dimensions)
                elif isinstance(parameter.children[1], Array_Constructor):
                    if parameter.children[0].string == "non_spatial_dimension":

                        self.find_nsd(parameter, field)

                    # Find synonyms
                    elif parameter.children[0].string == "synonyms":
                        for entry in \
                           parameter.children[1].children[1].children:
                            synonym_type = entry.children[1].children[0].string
                            value = entry.children[1].children[1].string[1:-1]
                            field.add_value(key, (synonym_type, value))

                    # Find Misc Meta Data
                    elif parameter.children[0].string == "misc_meta_data":
                        for entry in \
                           parameter.children[1].children[1].children:
                            inner_key = \
                                entry.children[1].children[0].string[1:-1]
                            value = entry.children[1].children[1].string[1:-1]
                            field.add_value(key, (inner_key, value))

                    else:
                        self.LOGGER.error("Attribute: %s is not a "
                                          "valid attribute",
                                          parameter.children[0].string)
                        valid_field = False

                else:

                    field.add_value(key, parameter.children[1].string)

            except Exception as error:
                if field.unique_id:
                    self.LOGGER.warning(
                        "Attribute: %s on field: %s in file: "
                        "%s is invalid: %s",
                        key, field.unique_id, file_name, error)
                else:
                    self.LOGGER.warning("Key: %s in file: %s is invalid: %s ",
                                        key, file_name, error)
                valid_field = False

        return field, valid_field

    @staticmethod
    def extract_multi_line_statement(statement: Level_3_Expr) -> str:
        """Accepts an fparser Level_3_Expr object as input. This object
        represents multi-line statements.
        The function reassembles an arbitrary amount of lines into one
        statement
        :param statement: An fparser Level_3_Expr object
        :return value: The reassembled value as string
        """
        for item in statement.children:
            value = None
            if isinstance(item, Char_Literal_Constant):
                value_1 = item.string[1:-1]
                value_2 = item.parent.children[2].string[1:-1]
                value = value_1 + value_2
            elif isinstance(item, Level_3_Expr):
                value = FortranMetaDataReader.extract_multi_line_statement(
                    item) + item.parent.children[2].string[1:-1]
                value = value.replace("\n", " ")
            return value

    def find_nsd(self, parameter: Component_Spec, field):
        """Takes an fparser object, which represents a list of
        non-spatial dimensions. Parses through that object for non-spatial
        dimension info and updates the FortranMetaDataReader.
        :param parameter: An fparser Ac_Value_List object
        :param field: A Field object to which the non-spatial dimension belongs
    """

        for array in walk(parameter.children,
                          types=Ac_Value_List):

            # Get non-spatial dimension information
            if "non_spatial_dimension" not in array.children[0].string:
                break

            nsd_list = parse_non_spatial_dimension(array, field)
            for nsd in nsd_list:
                field.add_value("non_spatial_dimension", (nsd["name"], nsd))

                section, group, _ = field.file_name.split("__")

                # Check if dimension is already stored in self
                if nsd["name"] in self.non_spatial_dims:
                    stored_dim = self.non_spatial_dims[nsd["name"]].copy()
                    stored_fields = stored_dim.pop("fields")

                    # If it matches stored dimension, add field to
                    # list of fields for that dimension
                    if nsd == stored_dim:
                        if (section, group, field.unique_id) not in \
                                self.non_spatial_dims[nsd["name"]]["fields"]:

                            self.non_spatial_dims[nsd["name"]]["fields"]\
                                .append((section, group, field.unique_id))

                    # If there are discrepancies, throw an error
                    else:
                        for stored_field in stored_fields:
                            self.LOGGER.error(
                                "Non-spatial dimension '%s' for field '%s' "
                                "does not match '%s' for field '%s'",
                                nsd["name"], field.unique_id,
                                stored_dim["name"],
                                stored_field[2])
                        raise Exception(
                            "Non-spatial dimension '{}' for field '{}' does "
                            "not match previous dimension '{}'".format(
                                nsd["name"],
                                field.unique_id,
                                stored_dim["name"]))

                # If dimension not stored, add it
                else:
                    self.non_spatial_dims[nsd["name"]] = nsd
                    self.non_spatial_dims[nsd["name"]]["fields"] = \
                        [(section, group, field.unique_id)]


def read_enum(path: str):
    """Reads enumerated values from a file. File should contain only one ENUM
    :param path: Path to the file containing the ENUM
    :return enumerated_values: A list of all enumerated values found
    """
    enumerated_values = []
    reader = FortranFileReader(path)
    parse_tree = F2003_PARSER(reader)
    for enum in walk(parse_tree, types=Enumerator_Def_Stmt):
        for item in enum.children[1].children:
            enumerated_values.append(item.string)
    return enumerated_values
