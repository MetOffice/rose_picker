# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2012-2021 British Crown (Met Office) & Contributors.
#
# This file is part of Rose, a framework for meteorological suites.
#
# Rose is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rose is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Rose. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------
"""This is a utility script file for the vertical_dimension_choice widget.
This script loads and parses the needed files for the widget to function.
This script exists because static variables are not working as expected
(Possibly due to the way GTK works with threading). So all code that loads and
stores data is kept separately in this file """

import copy
import hashlib
import json
import os
import re

NAME_REGEX = re.compile(r"^name='(?P<name>[a-zA-Z0-9_]+)'")
DIMENSION_REGEX = re.compile(r"^\[vertical_dimension\((?P<id>[0-9]+)\)]$")
STD_LEVEL_REGEX = re.compile(r"^(?P<level>[A-Z_]+)=[0-9]+")


class ConfigFiles:
    """Class to retrieve and store necessary information for diagnostics
    VertDimWidget from LFRic_meta_data.json and rose-app.conf"""

    JSON_meta = None
    user_defined_vertical_dimensions = None

    VERT_DIM_REGEX = re.compile(
        r"^field_config:(?P<section>[a-zA-Z0-9_]+):(?P<group>[a-zA-Z0-9_]+)="
        r"vertical_dimension_for_group")

    @staticmethod
    def get_config_files():
        """Searches for the immutable metadata JSON file and the rose-app.conf
        file specifying the configuration. Then calls functions to extract
        the necessary information from them"""

        if ConfigFiles.JSON_meta is None or \
                ConfigFiles.user_defined_vertical_dimensions is None:

            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Number of parent directories to search for files
            max_attempts = 20

            attempt = 0
            while ConfigFiles.user_defined_vertical_dimensions is None or \
                    ConfigFiles.JSON_meta is None or attempt < max_attempts:

                if ConfigFiles.user_defined_vertical_dimensions is None:
                    if "rose-app.conf" in os.listdir(current_dir):
                        path = current_dir + "/rose-app.conf"
                        ConfigFiles.add_user_defined_vertical_dimensions(path)

                if ConfigFiles.JSON_meta is None:
                    if "LFRic_meta_data.json" in os.listdir(current_dir):
                        path = current_dir + "/LFRic_meta_data.json"
                        ConfigFiles.add_json_meta(path)

                # If the files cannot be found then raise an exception
                if attempt == max_attempts:
                    if ConfigFiles.user_defined_vertical_dimensions is None:
                        raise Exception("rose-app.conf file not found!")
                    if ConfigFiles.JSON_meta is None:
                        raise Exception("JSON meta data file not found!")
                attempt += 1
                current_dir += "/.."

    @staticmethod
    def add_user_defined_vertical_dimensions(rose_app_path):
        """Get the all the user defined vertical dimensions defined within the
        rose-app.conf
        :param rose_app_path: Path to the rose-app.conf file"""

        user_defined_vertical_dimensions = {}
        in_vertical_dimension_section = False

        with open(rose_app_path, "r") as rose_app:

            for line in rose_app:

                # Set id from dimension section heading and create data objects
                dimension_match = DIMENSION_REGEX.search(line)
                if dimension_match:
                    dimension_id = dimension_match.group("id")
                    user_defined_vertical_dimensions[dimension_id] = {}
                    standard_levels = []
                    in_vertical_dimension_section = True

                elif in_vertical_dimension_section:

                    # Store dimension name to pass to widget
                    name_match = NAME_REGEX.search(line)
                    if name_match:
                        dimension_name = name_match.group("name")

                    # Make a list of all standard levels present in definition
                    # These are the keys that are in all caps
                    level_match = STD_LEVEL_REGEX.search(line)
                    if level_match:
                        standard_level_marker = level_match.group("level")
                        standard_levels.append(standard_level_marker)

                    # At end of section add name and all standard levels to
                    # collection of vertical dimensions
                    if line == "\n":
                        in_vertical_dimension_section = False
                        user_defined_vertical_dimensions[dimension_id] = {
                                dimension_name: standard_levels}

            # Add last dimension in case there hasn't been a suitable blank
            # line since (if last section of file is a vertical dimension)
            if "standard_levels" in locals():
                user_defined_vertical_dimensions[dimension_id] = \
                        {dimension_name: standard_levels}
        ConfigFiles.user_defined_vertical_dimensions = \
            user_defined_vertical_dimensions

    @staticmethod
    def add_json_meta(file_path):
        """Adds immutable metadata from the JSON file given to the class.
        Validates the MD5 checksum to ensure the file has not been
        modified by hand after it was generated.
        :param file_path: Path to the immutable data JSON file"""

        with open(file_path, 'r') as file_handle:
            file_data = json.load(file_handle)

            if 'checksum' not in file_data:
                raise KeyError("Can't find checksum to validate immutable "
                               "metadata")
        # Generate a checksum from a copy of the data without the checksum
        # and check it against the original
        immutable_metadata = copy.deepcopy(file_data)
        del immutable_metadata['checksum']
        checksum = ConfigFiles.create_md5_checksum(immutable_metadata)

        if file_data['checksum'] != checksum:
            raise RuntimeError(
                "Immutable data has been modified by hand\n"
                "Expected checksum: {}".format(file_data['checksum']))

        ConfigFiles.JSON_meta = immutable_metadata

    @staticmethod
    def create_md5_checksum(obj):
        """:param obj: Object to hash
        :return: String containing checksum"""
        obj_str = json.dumps(obj, sort_keys=True)
        checksum_hex = hashlib.md5(obj_str.encode('utf-8')).hexdigest()
        return 'md5: {}'.format(checksum_hex)
