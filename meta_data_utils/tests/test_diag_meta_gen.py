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
"""Test the diag_meta_gen module"""

import pytest
from os import getcwd, chdir
from diag_meta_gen import get_gpl_utilities_root_dir


def test_get_gpl_utilities_root_dir_1():
    """Testing that an error is thrown if the root dir cannot be found"""

    with pytest.raises(IOError):
        get_gpl_utilities_root_dir(["A directory that does not exist"])


def test_get_gpl_utilities_root_dir_2():
    """Testing that an error is not thrown when the root dir is found should
    not error"""
    get_gpl_utilities_root_dir(["meta_data_utils", "rose_picker"])


def test_get_gpl_utilities_root_dir_3(tmp_path):
    """Testing that an error is not thrown when the current working directory
    is different from the directory `diag_meta_gen.py located"""
    cwd = getcwd()
    chdir(tmp_path)
    get_gpl_utilities_root_dir(["meta_data_utils", "rose_picker"])
    chdir(cwd)
