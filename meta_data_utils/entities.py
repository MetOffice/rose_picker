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
"""This modules contains three classes that represent the three structures
that field meta data is kept in. Field encapsulates a field and all the meta
data for that field. Fields objects are held within Group objects. Group
objects are then in turn held within Section objects."""

import logging
import re
from typing import Dict, List, Union

from standards.standard_synonyms import StandardSynonyms

LOGGER = logging.getLogger(__name__)


# these just need loading once as they are static


class Field:
    """Encapsulates all information for a field. Provides methods to create
    derived fields and check for valid meta data"""

    UNIQUE_ID_REGEX = re.compile(
        r"(?P<section_name>[a-z_]+)__(?P<item_name>[a-z_]+)")

    def __init__(self, file_name):
        self.file_name = file_name
        self._unique_id = None
        self.units = None
        self.function_space = None
        self.order = None
        self.io_driver = None
        self.trigger = None
        self.description = None
        self.data_type = None
        self.time_step = None
        self.recommended_interpolation = None
        self.packing = None
        self.vertical_dimension = None
        self.non_spatial_dimension = {}
        self.standard_name = None
        self.level_definition = None
        self.misc_meta_data = {}
        self.synonyms: Dict[StandardSynonyms, List[str]] = {}
        self.item_name = None
        self.item_title = None
        self.long_name = None

    @property
    def unique_id(self) -> str:
        """getter method for unique_id"""
        return self._unique_id

    @unique_id.setter
    def unique_id(self, var: str):
        """setter method for unique_id"""
        if self._unique_id is None:

            found = Field.UNIQUE_ID_REGEX.search(var)
            if found:
                self.item_name = found.group("item_name")
                self.item_title = self.item_name.replace("_", " ").title()
            else:
                LOGGER.error("Unique ID %s does not conform to the standard",
                             var)

            self._unique_id = var
        else:
            LOGGER.error(
                "Unique ID %s has already been set. Tried to set to %s",
                self.unique_id, var)

    def add_value(self, property_name, value):
        """handle creation in stages"""
        if property_name == "synonyms":
            self.add_synonym(*value)
        elif isinstance(getattr(self, property_name), dict):
            dictionary = getattr(self, property_name, {})
            key, val = value
            dictionary.update({key: val})
            setattr(self, property_name, dictionary)
        elif isinstance(getattr(self, property_name), list):
            list_values = getattr(self, property_name, [])
            list_values.append(value)
            setattr(self, property_name, list_values)
        else:
            setattr(self, property_name, value)

    def add_synonym(self, synonym: Union[str, StandardSynonyms],
                    value: Union[List[str], str]):
        """
        Handle the addition of synonyms via either str or enum and value of
        list or individual
        @param synonym: Union[str, StandardSynonyms] str must be the name of
        a standard synonym
        @param value: Union[List[str], str])
        @return:
        """
        if isinstance(synonym, str):
            synonym = StandardSynonyms[synonym]
        if synonym not in self.synonyms:
            self.synonyms.update({synonym: []})
        if isinstance(value, List):
            self.synonyms[synonym] += value
        else:
            self.synonyms[synonym].append(value)


class Group:
    """Represents a group within a science section. Encapsulates all aspects of
    a groups and is composed of the fields within the group"""

    def __init__(self, name: str, file_name: str):
        self.file_name = file_name
        self.title = name.replace("_", " ").title()
        self.name = name
        self.fields: Dict[str, Field] = {}

    def add_field(self, field: Field):
        """Adds a field to the group
        :param field: The field to be added"""
        if field.unique_id not in self.fields:
            self.fields.update({field.unique_id: field})
        else:
            LOGGER.error("Field with unique ID: %s is already in Group: %s",
                         field.unique_id, self.title)


class Section:
    """Represents a science section. Encapsulates all aspects of a section and
    is composed of the groups within the section"""

    def __init__(self, name: str):
        self.title = name.replace("_", " ").title()
        self.name = name
        self.groups: Dict[str, Group] = {}

    def add_group(self, group: Group):
        """Adds a group to the section
        :param group: The group to be added"""
        if group.name not in self.groups:
            self.groups.update({group.name: group})
        else:
            LOGGER.error("Group: %s is already in Section: %s",
                         group.name, self.title)
