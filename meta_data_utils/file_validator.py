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
import os
import re

LOGGER = logging.getLogger(__name__)

FILE_NAME_REGEX = re.compile(r"(?P<section_name>[a-zA-Z_0-9]+?)__"
                             r"(?P<group_name>[a-zA-Z_0-9]+)__meta_mod.f90")
MODULE_NAME_REGEX = re.compile(r"(?P<section_name>[a-zA-Z_0-9]+?)__"
                               r"(?P<group_name>[a-zA-Z_0-9]+)__meta_mod")
META_TYPE_NAME_REGEX = re.compile(r"(?P<section_name>[a-zA-Z_0-9]+?)__"
                                  r"(?P<group_name>[a-zA-Z_0-9]+)__meta_type")
GROUP_NAME_REGEX = re.compile(r"(?P<section_name>[a-zA-Z_0-9]+?)__"
                              r"(?P<group_name>[a-zA-Z_0-9]+)")


def validate_names(file_name, module_name, meta_type_name, group_name):
    """Validates the different names held within a *__meta_mod.f90
    param: file_name: name of the file being validated
    param: module_name: The module name declared within the file
    param: meta_type_name: The name of the meta type declared within the
    file
    param: group_name: The group name declared within the file
    return: valid: Boolean stating the validity of the naming"""

    valid = True

    if group_name is None:
        LOGGER.error('There is no group name in %s', file_name)
        valid = False
        return valid

    file_name_parts = FILE_NAME_REGEX.search(file_name)
    module_name_parts = MODULE_NAME_REGEX.search(module_name)
    meta_type_name_parts = META_TYPE_NAME_REGEX.search(meta_type_name)
    group_name_parts = GROUP_NAME_REGEX.search(group_name)

    if not file_name_parts:
        LOGGER.error('Filename in path is not correct: %s', file_name)
        valid = False

    if not module_name_parts:
        LOGGER.error('Module in file is not correct' + os.linesep + file_name +
                     os.linesep + module_name)
        valid = False

    if not meta_type_name_parts:
        LOGGER.error('meta_type_name in file is not correct' + os.linesep +
                     file_name + os.linesep + meta_type_name)
        valid = False

    if not group_name_parts:
        LOGGER.error('group_name in file is not correct' + os.linesep +
                     file_name + os.linesep + group_name)
        valid = False

    if file_name_parts and module_name_parts and \
            meta_type_name_parts and group_name_parts:
        file_section_name = file_name_parts.group("section_name")
        file_group_name = file_name_parts.group("group_name")
        file_name = file_name[file_name.rfind("/") + 1:]

        module_section_name = module_name_parts.group("section_name")
        module_group_name = module_name_parts.group("group_name")

        meta_type_section_name = meta_type_name_parts.group("section_name")
        meta_type_group_name = meta_type_name_parts.group("group_name")

        group_name_section_name_part = group_name_parts.group("section_name")
        group_name_group_name_part = group_name_parts.group("group_name")

        if module_section_name != file_section_name:
            LOGGER.error(
                "Section names do not match in %s", file_name + os.linesep +
                module_section_name + " != " + file_section_name)
            valid = False

        if module_group_name != file_group_name:
            LOGGER.error(
                "Group names do not match in %s", file_name + os.linesep +
                module_group_name + " != " + file_group_name)
            valid = False

        if module_group_name != meta_type_group_name:
            LOGGER.error(
                "Bad module name in %s", file_name + os.linesep +
                module_group_name + " != " + meta_type_group_name)
            valid = False

        if module_section_name != meta_type_section_name:
            LOGGER.error(
                "Bad meta_type name in %s", file_name + os.linesep +
                module_section_name + " != " + meta_type_section_name)
            valid = False

        if group_name_section_name_part != file_section_name:
            LOGGER.error(
                "Section names do not match in %s", file_name + os.linesep +
                group_name_section_name_part + " != " + file_section_name)
            valid = False

        if group_name_group_name_part != file_group_name:
            LOGGER.error(
                "Group names do not match in %s", file_name + os.linesep +
                group_name_group_name_part + " != " + file_group_name)
            valid = False

    return valid
