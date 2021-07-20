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

"""Library function for carrying out all the validation of a field"""
import logging

from entities import Field
from standards.cf import CF
from standards.cmip import CMIP
from standards.standard_synonyms import StandardSynonyms

LOGGER = logging.getLogger(__name__)
CF = CF()
CMIP = CMIP()


def validate_field(field: Field) -> bool:
    """Checks for existence of mandatory values within the field.
    Logs any non-existent fields as errors
    :return: is_valid: A boolean value, True if meta data is valid,
    False otherwise"""
    is_valid = True

    if not field.unique_id:
        LOGGER.error("A unique id is missing from a field in %s",
                     field.file_name)
        is_valid = False
    # Field must have either a standard name or long name, it can have both
    if not field.standard_name and not field.long_name:
        LOGGER.error("%s in %s has neither a standard name or long name",
                     field.unique_id, field.file_name)
        is_valid = False
    if not field.units:
        LOGGER.error("A unit of measure is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.function_space:
        LOGGER.error("A function space is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.trigger:
        LOGGER.error("Triggering syntax is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.description:
        LOGGER.error("A description is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.data_type:
        LOGGER.error("A data type is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.time_step:
        LOGGER.error("A time step is missing from a field in %s",
                     field.file_name)
        is_valid = False
    if not field.recommended_interpolation:
        LOGGER.error(
            "A recommended_interpolation attribute is missing from a"
            " field in %s", field.file_name)
        is_valid = False
    if StandardSynonyms.CF in field.synonyms\
            and not CF.validate_field(field):
        is_valid = False
    if StandardSynonyms.CMIP6 in field.synonyms\
            and not CMIP.validate_field(field):
        is_valid = False

    return is_valid
