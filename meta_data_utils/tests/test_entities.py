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
"""Check the Entities"""
from entities import Field, Group
from field_validator import validate_field
from standards.standard_synonyms import StandardSynonyms


def test_bad_unique_id_setter(caplog):
    test_empty_field = Field("A File Path")
    test_empty_field.unique_id = "Bad Unique name"

    assert "Unique ID Bad Unique name does not conform to the standard" in \
           caplog.text


def test_good_unique_id_setter():
    test_empty_field = Field("A File Path")
    test_empty_field.unique_id = "good__unique_name"

    assert test_empty_field.item_title == "Unique Name"
    assert test_empty_field.item_name == "unique_name"


def test_is_valid_1(caplog):
    test_empty_field = Field("A File Path")

    assert validate_field(test_empty_field) is False

    assert "A unique id is missing from a field in A File Path" in caplog.text
    assert "A unit of measure is missing from a field in A File Path"\
           in \
           caplog.text
    assert "A function space is missing from a field in A File Path"\
           in \
           caplog.text
    assert "Triggering syntax is missing from a field in A File Path"\
           in \
           caplog.text
    assert "A description is missing from a field in A File Path" in \
           caplog.text
    assert "A data type is missing from a field in A File Path" in caplog.text
    assert "A time step is missing from a field in A File Path" in caplog.text
    assert "A recommended_interpolation attribute is missing from a field " \
           "in A File Path" in caplog.text


def test_is_valid_2(caplog):
    test_field = Field("A File Path")

    # Unique ID needs to conform to the naming standard
    setattr(test_field, "unique_id", "test_unique__id")
    setattr(test_field, "units", "test_units")
    setattr(test_field, "function_space", "test_function_space")
    setattr(test_field, "trigger", "test_trigger")
    setattr(test_field, "description", "test_description")
    setattr(test_field, "data_type", "test_data_type")
    setattr(test_field, "time_step", "test_time_step")
    setattr(test_field, "recommended_interpolation", "test_interpolation")

    assert validate_field(test_field) is True

    assert caplog.text == ''


def test_group_good_add_field(caplog):
    test_field = Field("A File Path")
    test_field.unique_id = "section_name__item_name"
    test_group = Group("Test Group", "Test filename")

    test_group.add_field(test_field)

    assert caplog.text == ''


def test_group_bad_add_field(caplog):
    test_field = Field("A File Path")
    test_field.unique_id = "section_name__item_name"
    test_group = Group("Test Group", "Test filename")

    test_group.add_field(test_field)
    test_group.add_field(test_field)

    assert 'Field with unique ID: section_name__item_name is already in ' \
           'Group: Test Group' in caplog.text


def test_add_synonyms():
    """check the adding works"""
    test_field = Field("somewhere")
    test_field.add_synonym(StandardSynonyms.AMIP.value, "foo")
    test_field.add_synonym(StandardSynonyms.AMIP.value, "bar")
    assert len(test_field.synonyms[StandardSynonyms.AMIP]) == 2
    test_field = Field("somewhere")
    test_field.add_value("synonyms", (StandardSynonyms.GRIB.value, "foo"))
    test_field.add_value("synonyms", (StandardSynonyms.GRIB.value, "bar"))
    assert len(test_field.synonyms[StandardSynonyms.GRIB]) == 2
    test_field = Field("somewhere")
    test_field.add_synonym(StandardSynonyms.CF, "shoop")
    test_field.add_synonym(StandardSynonyms.CF, "whoop")
    assert len(test_field.synonyms[StandardSynonyms.CF]) == 2
    test_field = Field("somewhere")
    test_field.add_synonym(StandardSynonyms.CMIP6, ["I'M", "CHARGIN"])
    test_field.add_synonym(StandardSynonyms.CMIP6, ["MAH", "LAZAAAAARRRR"])
    assert len(test_field.synonyms[StandardSynonyms.CMIP6]) == 4
