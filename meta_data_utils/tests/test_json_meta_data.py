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
"""Check the json output works"""
from json_meta_data import *

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data/"


def test_write_json_meta():
    """Check that it writes json with a checksum in the right shape"""
    test_data = {'section_name': 'test_section', 'unique_id': 'test_id'}

    write_json_meta(test_data, TEST_DATA_DIR, )
    with open(os.path.join(TEST_DATA_DIR, "rose.meta")) as json_test_data:
        test_data = json.load(json_test_data)
        assert test_data == {
            'meta_data': {
                'section_name': 'test_section',
                'unique_id': 'test_id'
            },
            'checksum': 'md5: 1461c4f998be95df7f0512b9ed772ce0'}


def test_set_checksum():
    """check the checksum actually seems plausible"""
    test_dict = {}
    test_dict_2 = {"a key": "a value"}

    set_checksum(test_dict)
    set_checksum(test_dict_2)

    assert test_dict['checksum'] == "md5: 99914b932bd37a50b983c5e7c90ae93b"
    assert test_dict_2['checksum'] == "md5: 9eae1793e5a5fbd89e0b737c67173a46"
