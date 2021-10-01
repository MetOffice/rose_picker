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

from rose_config_creator import *
from entities import Section, Group, Field


def test_create_rose_meta_no_vert_dim():
    """
    Tests that the rose meta data is correctly output when a group has no
    vertical dimension
    """
    test_section = Section("test_section")
    test_group = Group("test_group", "test_filename")
    test_field = Field("test_file_name")
    test_field.description = "test_description"
    test_field.item_title = "test_item_title"
    test_field.unique_id = "test__unique_id"

    test_group.fields = {"test_group__test_name": test_field}
    test_section.groups = {"test_group": test_group}

    test_meta_data = {'sections': {'test_section': test_section},
                      'standard_level_markers': [],
                      'non_spatial_dimensions': {}}

    result = create_rose_meta(test_meta_data, "test_filename")
    assert "=vertical_dimension:" not in result
    assert "title=Model Levels used by this group" not in result
    assert "description=Vertical dimensions must define these levels " \
           "to be valid" not in result
    assert "widget[rose-config-edit]=vertical_dimension_choice.VertDimWidget"\
           not in result


def test_create_rose_meta_vert_dim():
    """
    Tests that the rose meta data is correctly output when a group has
    vertical dimension
    """
    test_section = Section("test_section")
    test_group = Group("test_group", "test_filename")
    test_field = Field("test_file_name")
    test_field.vertical_dimension = {
        'top_arg': 'test_top_level',
        'bottom_arg': 'test_bottom_level',
        'units': 'test_unit',
        'positive': 'test_positive',
        'standard_name': 'test_standard_name'
    }
    test_field.description = "test_description"
    test_field.item_title = "test_item_title"
    test_field.unique_id = "test__unique_id"

    test_group.fields = {"test_group__test_name": test_field}
    test_section.groups = {"test_group": test_group}

    test_meta_data = {'sections': {'test_section': test_section},
                      'standard_level_markers': [],
                      'non_spatial_dimensions': {}}

    result = create_rose_meta(test_meta_data, "test_filename")

    assert "=vertical_dimension:" in result
    assert "title=Model Levels used by this group" in result
    assert "description=Vertical dimensions must define these levels " \
           "to be valid" in result
    assert "widget[rose-config-edit]=vertical_dimension_choice.VertDimWidget"\
           in result
