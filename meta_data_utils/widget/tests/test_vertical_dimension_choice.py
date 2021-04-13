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
"""Test vertical_dimension_choice """

import os
import unittest
from vertical_dimension_choice import VertDimWidget
from vertical_dimension_util import ConfigFiles

JSON = {
    "meta_data": {
        "sections": {
            "section_name": {
                "groups": {
                    "field_group_1": {
                        "fields": {
                            "section_name__field_1": {
                                "_unique_id": "section_name__field_1",
                                "units": "units_1"},
                            "section_name__field_2": {
                                "_unique_id": "section_name__field_2",
                                "units": "units_2",
                                "vertical_dimension": {
                                    "top_arg": "TOP_ATMOSPHERIC_LEVEL",
                                    "bottom_arg": "BOTTOM_ATMOSPHERIC_LEVEL",
                                    "standard_name": "height",
                                    "positive": "POSITIVE_UP",
                                    "units": "m"
                                }
                            }
                        }
                    },
                    "field_group_2": {
                        "fields": {
                            "section_name__field_3": {
                                "_unique_id": "section_name__field_3",
                                "units": "units_3"
                            }
                        }
                    }
                }
            }
        }
    }
}


class TestVertDimWidget(unittest.TestCase):
    """Test the vertical dimension choice widget"""
    def test_VertDimWidget_valid(self):
        """Test that the widget correctly finds valid dimensions"""
        dimensions = {
                "1": {"test_vertical_dimension_1": ["BOTTOM_SOIL_LEVEL",
                                                    "TOP_SOIL_LEVEL"]},
                "3": {"test_vertical_dimension_3": ["BOTTOM_ATMOSPHERIC_LEVEL",
                                                    "TOP_ATMOSPHERIC_LEVEL"]}
        }
        value = ""
        metadata = {'id': 'field_config:section_name:field_group_1='
                          'vertical_dimension_for_group'}
        ConfigFiles.user_defined_vertical_dimensions = dimensions
        ConfigFiles.JSON_meta = JSON
        widget = VertDimWidget(value, metadata, None, None)
        self.assertEqual(widget.vertical_dimensions, dimensions)
        self.assertEqual(widget.valid_dim_ids, ['3'])
        self.assertEqual(widget.valid_dim_names,
                         ['test_vertical_dimension_3'])

    def test_VertDimWidget_no_valid(self):
        """Test that the widget correctly finds no valid dimensions"""
        dimensions = {
                "1": {"test_vertical_dimension_1": ["BOTTOM_SOIL_LEVEL",
                                                    "TOP_SOIL_LEVEL"]},
                "3": {"test_vertical_dimension_3": ["BOTTOM_ATMOSPHERIC_LEVEL",
                                                    "TOP_WET_LEVEL"]}
        }
        value = ""
        metadata = {'id': 'field_config:section_name:field_group_1='
                          'vertical_dimension_for_group'}
        ConfigFiles.user_defined_vertical_dimensions = dimensions
        ConfigFiles.JSON_meta = JSON
        widget = VertDimWidget(value, metadata, None, None)
        self.assertEqual(widget.vertical_dimensions, dimensions)
        self.assertEqual(widget.valid_dim_ids, [''])
        self.assertEqual(widget.valid_dim_names,
                         ['No valid vertical dimension found'])
