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
"""Test file for file_validator.py"""
from file_validator import validate_names

GOOD_FILE_NAME = 'trunk/miniapps/diagnostics/source/diagnostics_meta/' \
                 'test_section__test_group__meta_mod.f90'
BAD_FILE_NAMES = ['trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_groupmeta_mod.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__meta_mod']

GOOD_MODULE_NAMES = "test_section__test_group__meta_mod"

BAD_MODULE_NAMES = ["test_sectiontest_group__meta_mod",
                    "test_section__test_groupmeta_mod",
                    "test_section__test_group__metamod",
                    "test_section__test_group"]

GOOD_META_TYPE_NAME = "test_section__test_group__meta_type"

BAD_META_TYPE_NAMES = ["test_section__test_group__",
                       "test_section__test_groupmeta_type",
                       "test_sectiontest_group__meta_type",
                       "__test_group__meta_type",
                       "test_section__test_group__meta_pe",
                       "test_section__test_group__metatype",
                       "__meta_type"]

GOOD_GROUP_NAME = "test_section__test_group"

BAD_GROUP_NAME = ["test_sectiontest_group",
                  "test_section_test_group",
                  ""]


def test_validate_names():

    """Test function when given correct input"""
    result = validate_names(GOOD_FILE_NAME,
                            GOOD_MODULE_NAMES,
                            GOOD_META_TYPE_NAME,
                            GOOD_GROUP_NAME)

    assert result is True


def test_validate_names_bad_file_name(caplog):

    """Test function when given incorrect file name"""
    for bad_file_name in BAD_FILE_NAMES:
        result = validate_names(bad_file_name,
                                GOOD_MODULE_NAMES,
                                GOOD_META_TYPE_NAME,
                                GOOD_GROUP_NAME)

        assert result is False
        assert "Filename in path is not correct" in caplog.text
        assert bad_file_name in caplog.text


def test_validate_names_bad_module_name(caplog):

    """Test function when given incorrect module name"""
    for bad_module_name in BAD_MODULE_NAMES:
        result = validate_names(GOOD_FILE_NAME,
                                bad_module_name,
                                GOOD_META_TYPE_NAME,
                                GOOD_GROUP_NAME)

        assert result is False
        assert "Naming Error! file name and module name do not match" \
               in caplog.text
        assert bad_module_name in caplog.text


def test_validate_names_meta_type(caplog):

    """Test function when given incorrect meta type name"""
    for bad_meta_type_name in BAD_META_TYPE_NAMES:
        result = validate_names(GOOD_FILE_NAME,
                                GOOD_MODULE_NAMES,
                                bad_meta_type_name,
                                GOOD_GROUP_NAME)

        assert result is False
        assert "Naming Error! file name and meta type name do not match" \
               in caplog.text
        assert bad_meta_type_name in caplog.text


def test_validate_names_group_name(caplog):

    """Test function when given incorrect group name"""
    for bad_group_name in BAD_GROUP_NAME:
        result = validate_names(GOOD_FILE_NAME,
                                GOOD_MODULE_NAMES,
                                GOOD_META_TYPE_NAME,
                                bad_group_name)

        assert result is False
        assert "Naming Error! file name and group name do not match" \
               in caplog.text
        assert bad_group_name in caplog.text
