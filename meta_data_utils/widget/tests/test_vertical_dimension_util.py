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
"""Test vertical_dimension_util """

import os
import unittest
from vertical_dimension_util import ConfigFiles

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data"


class TestVerticalDimensionUtil(unittest.TestCase):
    """Tests for vertical_dimension_util"""

    def test_add_user_defined_vertical_dimensions(self):
        """Test vertical dimensions are correctly parsed from rose-app.conf"""

        expected_dimensions = {
                "1": {"test_vertical_dimension_1": ["BOTTOM_SOIL_LEVEL",
                                                    "TOP_SOIL_LEVEL"]},
                "3": {"test_vertical_dimension_3": ["BOTTOM_ATMOSPHERIC_LEVEL",
                                                    "TOP_ATMOSPHERIC_LEVEL"]}
        }

        ConfigFiles.add_user_defined_vertical_dimensions(
                TEST_DATA_DIR + "/rose-app.conf")
        self.assertEqual(ConfigFiles.user_defined_vertical_dimensions,
                         expected_dimensions)

    def test_add_user_defined_vertical_dimensions_empty(self):
        """Test vertical dimensions are correctly parsed from an empty
        rose-app.conf"""

        expected_dimensions = {}

        ConfigFiles.add_user_defined_vertical_dimensions(
                TEST_DATA_DIR + "/empty-rose-app.conf")
        self.assertEqual(ConfigFiles.user_defined_vertical_dimensions,
                         expected_dimensions)

    def test_add_json_meta(self):
        """Test that immutable metadata json is correctly loaded"""

        expected_json = {
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
                                            "bottom_arg": "BOTTOM_ATMOSPHERIC_"
                                                          "LEVEL",
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
        ConfigFiles.add_json_meta(TEST_DATA_DIR + "/LFRic_meta_data.json")
        self.assertEqual(ConfigFiles.JSON_meta, expected_json)

    def test_add_json_meta_incorrect_checksum(self):
        """Test that incorrect json checksum is handled properly"""

        config_files = ConfigFiles()
        with self.assertRaises(RuntimeError) as e:
            config_files.add_json_meta(TEST_DATA_DIR +
                                       "/incorrect_checksum.json")

        self.assertEqual(str(e.exception),
                         "Immutable data has been modified by hand\n"
                         "Expected checksum: md5: "
                         "8fec930ffa6141918a19ed2aa6e6a75d")

    def test_add_json_meta_missing_checksum(self):
        """Test that missing json checksum is handled properly"""

        config_files = ConfigFiles()
        with self.assertRaises(KeyError) as e:
            config_files.add_json_meta(TEST_DATA_DIR +
                                       "/missing_checksum.json")

        self.assertEqual(
                str(e.exception),
                '"Can\'t find checksum to validate immutable metadata"')

    def test_create_md5_checksum(self):
        """Test that checksums can be generated correctly"""

        config_files = ConfigFiles()
        test_dict_1 = {}
        test_dict_2 = {"a key": "a value"}

        checksum_1 = config_files.create_md5_checksum(test_dict_1)
        checksum_2 = config_files.create_md5_checksum(test_dict_2)

        self.assertEqual(checksum_1, "md5: 99914b932bd37a50b983c5e7c90ae93b")
        self.assertEqual(checksum_2, "md5: 9eae1793e5a5fbd89e0b737c67173a46")
