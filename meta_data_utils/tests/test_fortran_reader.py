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
"""Test the Fortran reader processes files"""
import os
import copy
import pytest
from pathlib import Path

from fparser.common.readfortran import FortranFileReader
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk
from fparser.two.Fortran2003 import Assignment_Stmt, Component_Spec, \
    Array_Constructor
from fortran_reader import FortranMetaDataReader, read_enum
from entities import Section, Field

WORKING_DIR = Path.cwd()
TEST_DIR = WORKING_DIR / "tests"
TEST_DATA_DIR = WORKING_DIR / "tests/test_data"
META_TYPES_FOLDER = "um_physics/source/diagnostics_meta/meta_types"
LFRIC_URL = "fcm:lfric.x_tr@head"
ENUM_TEST_FILE = "enum_test_file"


@pytest.fixture(scope="module")
def setup_lfric(tmpdir_factory):
    """Checks out the LFRic trunk which contains required Fortran modules"""
    temp_dir = tmpdir_factory.mktemp("data")
    returncode = os.system(
        "fcm export --force {0} {1}".format(LFRIC_URL, temp_dir))
    if returncode == 0 and os.path.isdir(temp_dir):
        return temp_dir
    raise OSError("Unable to check out {0}".format(LFRIC_URL))


def setup_non_spatial_dims(root_dir: Path):
    """Sets up the needed objects to test find_nsd().
    Monkey Patches in a compare function.
    :param root_dir: The root directory, as discovered by the
    setup_lfric() function"""
    # Monkey Patching in a compare function for comparing readers
    def monkey_patch_compare_func(self, other):
        return \
            self.non_spatial_dims == other.non_spatial_dims and \
            self.levels == other.levels and \
            self.meta_mod_files == other.meta_mod_files and \
            self.meta_types_path == other.meta_types_path and \
            self.valid_meta_data == other.valid_meta_data and \
            self.vertical_dimension_definition == \
            other.vertical_dimension_definition

    monkey_patch_func = monkey_patch_compare_func
    FortranMetaDataReader.__eq__ = monkey_patch_func

    parameters = []

    parser = ParserFactory().create(std="f2003")
    fparser_reader = FortranFileReader(
        (TEST_DATA_DIR / "find_nsd_test_data.f90").as_posix(),
        ignore_comments=True)
    parse_tree = parser(fparser_reader)

    reader = FortranMetaDataReader(root_dir, root_dir / META_TYPES_FOLDER)

    for definition in walk(parse_tree.content,
                           types=Assignment_Stmt):
        for parameter in walk(definition, Component_Spec):
            if isinstance(parameter.children[1], Array_Constructor):
                if parameter.children[0].string == "non_spatial_dimension":
                    parameters.append(parameter)

    return parameters, reader


def test_read_fortran_files_1(setup_lfric):
    """Does it find the files in the overall project?"""

    test_parser = FortranMetaDataReader(setup_lfric,
                                        setup_lfric / META_TYPES_FOLDER)
    result = test_parser.read_fortran_files()

    assert "example_science_section" in result[0]["sections"].keys()
    # assert result[1] is True # can't test this as it's outside of your
    # control
    assert isinstance(result[0]["sections"]["example_science_section"],
                      Section)


def test_read_fortran_files_2(setup_lfric):
    """Does our test file from test_data load?"""
    test_parser = FortranMetaDataReader(setup_lfric, setup_lfric /
                                        META_TYPES_FOLDER)
    test_parser.meta_mod_files = \
        [(TEST_DATA_DIR / "test_section__test_group__meta_mod.f90").as_posix()]
    result = test_parser.read_fortran_files()

    assert result[1] is True
    assert "test_section" in result[0]["sections"].keys()
    assert "test_group" in result[0]["sections"]["test_section"].groups
    assert "example_fields__eastward_wind" in \
           result[0]["sections"]["test_section"].groups["test_group"].fields


def test_read_fortran_files_3(setup_lfric):
    """Testing invalid attributes in field_meta_data_type"""

    test_parser = FortranMetaDataReader(setup_lfric, setup_lfric /
                                        META_TYPES_FOLDER)
    test_parser.meta_mod_files = \
        [(TEST_DATA_DIR /
         "non_spatial_dimension__invalid_attribute__meta_mod.f90").as_posix()]
    result = test_parser.read_fortran_files()

    assert result[1] is False
    with pytest.raises(Exception) as excinfo:
        assert "Attribute: unrecognised_attribute is not" \
               " a valid attribute!" in str(excinfo.value)


def test_read_enum():
    """Check that test enum file is correctly read"""
    assert read_enum(
        (TEST_DATA_DIR / ENUM_TEST_FILE).as_posix()) == ["ONE", "TWO"]


def test_find_nsd_1(setup_lfric):
    """Testing that if two similarly name non-spatial dimensions are not
     identical an error is thrown"""
    parameters, reader = setup_non_spatial_dims(setup_lfric)
    test_field = Field("test_section__test_field__meta_mod.f90")
    reader.non_spatial_dims = {"test_already_in_reader_error":
                               {"name": "test_already_in_reader_error",
                                "type": "label_definition",
                                "help": "test_help_text",
                                "label_definition": ["DIFFERENT",
                                                     "TEST",
                                                     "VALUES"],
                                "fields": [("test_section",
                                            "test_field",
                                            None)]}
                               }

    # Because the NSD being added had the same name as the one currently being
    # held, but is different in some way, and error should be raised.
    with pytest.raises(Exception):
        reader.find_nsd(parameters[1], test_field)


def test_find_nsd_2(setup_lfric):
    """Testing that if two similarly named non-spatial dimensions are
     identical nothing is altered"""

    parameters, reader_1 = setup_non_spatial_dims(setup_lfric)

    reader_1.non_spatial_dims = {"test_already_in_reader_error":
                                 {"name": "test_already_in_reader_error",
                                  "type": "label_definition",
                                  "help": "test_help_text",
                                  "label_definition": ["test_value_1",
                                                       "test_value_2",
                                                       "test_value_3"],
                                  "fields": [("test_section",
                                              "test_field",
                                              None)]}
                                 }
    # Creating a copy of the reader object, so it can be compared later
    reader_2 = copy.deepcopy(reader_1)

    test_field = Field("test_section__test_field__meta_mod.f90")
    reader_1.find_nsd(parameters[0], test_field)

    # Because the NSD being added is the same as the one currently held,
    # nothing should change.
    assert reader_1 == reader_2


def test_find_nsd_3(setup_lfric):
    """Testing that if a dimension is not known about, it is added"""

    parameters, reader_1 = setup_non_spatial_dims(setup_lfric)

    # Creating a copy of the reader object, so it can be compared later
    reader_2 = copy.deepcopy(reader_1)

    test_field = Field("test_section__test_field__meta_mod.f90")

    reader_1.find_nsd(parameters[0], test_field)

    # Because the NSD being added is not known about, it should be added to the
    # reader
    assert reader_1 != reader_2


def test_validate_naming_1(caplog, setup_lfric):
    """Testing that an error is thrown if a *__meta_mod.f90 file has more than
     one type definition"""

    test_parser = FortranMetaDataReader(setup_lfric, setup_lfric /
                                        META_TYPES_FOLDER)
    test_parser.meta_mod_files = [
        (TEST_DATA_DIR /
            "validate_naming__multiple_type_def__meta_mod.f90").as_posix()]
    result = test_parser.read_fortran_files()

    assert result[1] is False
    assert "More than one meta type has been declared in" in caplog.text


def test_validate_naming_2(caplog, setup_lfric):
    """Testing that an error is thrown if the filename doesn't match the
    group/module/type_def name"""

    test_parser = FortranMetaDataReader(setup_lfric, setup_lfric /
                                        META_TYPES_FOLDER)
    test_parser.meta_mod_files = [
        (TEST_DATA_DIR / "non_matching__file_name__meta_mod.f90").as_posix()]
    result = test_parser.read_fortran_files()

    assert result[1] is False
    assert "Naming Error! file name and module name do not match" \
           in caplog.text
    assert "Naming Error! file name and meta type name do not match" \
           in caplog.text
    assert "Naming Error! file name and group name do not match" \
           in caplog.text
