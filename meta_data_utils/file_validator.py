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

"""Library function for carrying out all the validation of a file"""
import logging
import re

LOGGER = logging.getLogger(__name__)

FILE_NAME_REGEX = re.compile(r"(?P<section_name>[a-z_0-9]+?)__"
                             r"(?P<group_name>[a-z_0-9]+)__meta_mod\..90")


def validate_names(file_name, module_name, meta_type_name, group_name):
    """Validates the different names held within a *__meta_mod.f90
    param: file_name: name of the file being validated
    param: module_name: The module name declared within the file
    param: meta_type_name: The name of the meta type declared within the
    file
    param: group_name: The group name declared within the file
    return: valid: Boolean stating the validity of the naming"""

    valid = True

    file_name_parts = FILE_NAME_REGEX.search(file_name)

    if group_name is None:
        LOGGER.error('There is no group name in %s', file_name)
        return False

    if not file_name_parts:
        LOGGER.error('Filename in path is not correct: %s', file_name)
        return False

    name_from_file = file_name_parts.group("section_name") \
        + "__" + file_name_parts.group("group_name")

    test_module_name = name_from_file + "__meta_mod"
    test_meta_type_name = name_from_file + "__meta_type"

    if test_module_name != module_name:
        LOGGER.error('Naming Error! file name and module name do not match')
        LOGGER.error("module name: %s", module_name)
        LOGGER.error("file name: %s", test_module_name)
        valid = False

    if test_meta_type_name != meta_type_name:
        LOGGER.error('Naming Error! file name and meta type name do not match')
        LOGGER.error("meta type name: %s", meta_type_name)
        LOGGER.error("file name: %s", test_meta_type_name)
        valid = False

    if group_name != name_from_file:
        LOGGER.error('Naming Error! file name and group name do not match')
        LOGGER.error("group name: %s", group_name)
        LOGGER.error("file name: %s", name_from_file)
        valid = False

    return valid
