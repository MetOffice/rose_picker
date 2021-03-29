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
"""test the fortran reader processes files"""
import os

from fortran_reader import *


TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data"
meta_types_folder = "/um_physics/source/diagnostics_meta/meta_types/"
LFRIC_URL = "fcm:lfric.x_tr@head"

def setup_lfric():
    """checks out the LFRic trunk which contains required Fortran modules"""
    dir = "trunk"
    returncode = os.system("fcm export --force {0} {1}".format(LFRIC_URL, dir))
    if returncode == 0 and os.path.isdir(dir):
        return dir
    else:
        raise OSError("Unable to check out {0}".format(LFRIC_URL))


def test_read_fortran_files_1():
    """does it find the files in the overall project?"""
    root_dir = setup_lfric()
    test_parser = FortranMetaDataReader(root_dir, meta_types_folder)
    result = test_parser.read_fortran_files()
    assert "example_science_section" in result[0]["sections"].keys()
    # assert result[1] is True # can't test this as it's outside of your
    # control
    assert isinstance(result[0]["sections"]["example_science_section"],
                      Section)


def test_read_fortran_files_2():
    """does our test file from test_data load?"""
    root_dir = setup_lfric()
    test_parser = FortranMetaDataReader(root_dir, meta_types_folder)
    test_parser.meta_mod_files = [TEST_DATA_DIR +
                                  "/test_section__test_group__.f90"]
    result = test_parser.read_fortran_files()

    assert result[1] is True
    assert "test_section" in result[0]["sections"].keys()
    assert "test_group" in result[0]["sections"]["test_section"].groups
    assert "example_fields__eastward_wind" in \
           result[0]["sections"]["test_section"].groups["test_group"].fields
