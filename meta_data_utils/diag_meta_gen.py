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
"""This module contains code for parsing LFRic meta source files
It recursively looks in every folder for files ending in "meta_mod.f90".
It then parses these files and creates a rose-meta.conf file and JSON file.
It also creates a macro to add output streams and add diagnostic fields to
output streams in a rose-app.conf file"""
import argparse
import logging
import os
import shutil

from fortran_reader import FortranMetaDataReader
from json_meta_data import write_json_meta
from rose_config_creator import create_rose_meta

LOGGER = logging.getLogger(__name__)


def get_gpl_utilities_root_dir():
    """Finds the root directory of the GPL-utilities source tree
    :return root_dir: The root directory as a string"""

    LOGGER.debug("GPL-utilities directory not supplied, attempting to find it")
    folders_in_root = ["meta_data_utils", "rose_picker"]
    root_dir = os.path.dirname(os.path.abspath(__file__))
    in_root_folder = False
    counter = 0
    max_count = 20

    while not in_root_folder:
        if all(x in os.listdir(root_dir) for x in folders_in_root):
            in_root_folder = True
        elif counter == max_count:
            raise IOError("Unable to ascertain GPL-utils root after {0}" +
                          "attempts ({1})".format(max_count, root_dir))
        else:
            root_dir += "/.."
            counter += 1

    LOGGER.debug("The GPL-utils root directory was found to be %s", root_dir)

    return root_dir


def get_lfric_root_dir():
    """Finds the root directory of the LFRic source tree, expected to be the
    current working directory.
    :return root_dir: The root directory as a string"""

    LOGGER.debug("LFRic directory not supplied, attempting to find it")
    folders_in_root = ["infrastructure", "gungho"]
    root_dir = os.getcwd()
    in_root_folder = False
    counter = 0
    max_count = 20

    while not in_root_folder:
        if all(x in os.listdir(root_dir) for x in folders_in_root):
            in_root_folder = True
        elif counter == max_count:
            raise IOError("Unable to ascertain LFRic root after {0}" +
                          "attempts ({1})".format(max_count, root_dir))
        else:
            root_dir += "/.."

    LOGGER.debug("The LFRic root directory was found to be %s", root_dir)

    return root_dir


def setup_logging(level: str, file_name: str):
    """Creates logging handlers and configure the logging"""

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(file_name, mode='w')

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=level,
                        handlers=[stream_handler, file_handler])


def parse_args():
    """Parse arguments from the command line"""

    arg_parser = argparse.ArgumentParser(description='''
This tool generates meta data from fortran files. It will find all files that
end in __meta_mod.f90. These files should contain declarations for instances
of a specific fortran type, field_meta_data_type. The information in these
declarations are used to generate output files. These output files can be used
in a configuration utility, such as rose.''')
    arg_parser.add_argument("-v", "--verbose", action="store_true",
                            help="increase output verbosity")
    arg_parser.add_argument("-p", "--path", type=str,
                            help='''
This tool will recursively search through a folder structure looking for files
that end in __meta_mod.f90.  The folder structure should be
<root_folder>/<project directory>/source/diagnostics_meta/
There is default behaviour that will attempt to find the root folder of the
repository. If a specific folder is desired, specify it here.''')
    arg_parser.add_argument("-o", "--output", type=str,
                            help='''
The location the generated meta data will be output to
This tool will output a JSON representation of the generated meta data and a
folder called 'meta'. This will contain a conf file made using the generated
meta data as well as a macro for adding output streams and their fields to the
configuration''')
    arg_parser.add_argument("-f", "--filename", type=str,
                            help='''
The name of the conf file output by the generator. Defaults to rose-meta.conf
''')
    arg_parser.add_argument("-s", "--support_types", type=str,
                            help='''
This tool needs supporting type and enum declarations.
interpolation_enum_mod.90
levels_enum_mod.f90
positive_enum_mod.f90
time_step_enum_mod.f90
vertical_dimensions_mod.f90
Specify the folder containing these files, otherwise the tool will use the
default location''')

    args = arg_parser.parse_args()

    args_dict = {}
    if args.verbose:
        args_dict["logging_level"] = logging.DEBUG
    else:
        args_dict["logging_level"] = logging.INFO

    if args.path:
        args_dict["lfric_directory"] = args.path

    if args.output:
        args_dict["output_directory"] = args.output

    if args.filename:
        args_dict["metadata_file_name"] = args.filename

    if args.support_types:
        args_dict["support_types"] = args.support_types

    return args_dict


def add_rose_macro(root_dir: str, rose_suite_dir: str) -> None:
    """Copies add_section macro file into rose suite
    This contains macros to add an output stream section to the rose-app.conf,
    and to add a diagnostic field to an output stream
    :param root_dir: The path to the root directory of the GPL-utilities source
    :param rose_suite_dir: The path to the output Rose suite
    """
    LOGGER.info("Adding rose macro")
    macro_source = root_dir + "/meta_data_utils/macro/add_section.py"
    macro_dest = rose_suite_dir + "/meta/lib/python/macros/add_section.py"
    os.makedirs(os.path.dirname(macro_dest), exist_ok=True)
    shutil.copy(macro_source, macro_dest)


def run():
    """Defines variables for file output and runs the parser"""

    args = parse_args()

    log_file_name = 'meta_data_parser.log'

    setup_logging(args["logging_level"], log_file_name)

    if "lfric_directory" in args:
        lfric_dir = args["lfric_directory"]
    else:
        lfric_dir = get_lfric_root_dir()

    if "output_directory" in args:
        suite_dir = args["output_directory"]
        suite_dir += '/example_rose_suite/'
    else:
        working_dir = os.path.dirname(os.path.abspath(__file__))
        suite_dir = working_dir + "/example_rose_suite/"

    if "metadata_file_name" in args:
        metadata_file_name = args["metadata_file_name"]
    else:
        metadata_file_name = "rose-meta"

    if "support_types" in args:
        meta_types_folder = args["support_types"]
    else:
        meta_types_folder = "/um_physics/source/diagnostics_meta/meta_types/"

    # Find meta data in fortran meta_mod.f90 files
    LOGGER.info("Starting parser")
    reader = FortranMetaDataReader(lfric_dir, meta_types_folder)

    meta_data, valid = reader.read_fortran_files()

    if not valid:
        LOGGER.info("Invalid Fortran files exist - please correct")

    else:
        LOGGER.info("Meta data valid, creating files")
        # If target directory doesn't exist make it
        os.makedirs(os.path.dirname(suite_dir + "meta/rose-meta.conf"),
                    exist_ok=True)

        create_rose_meta(meta_data, suite_dir, metadata_file_name)
        add_rose_macro(get_gpl_utilities_root_dir(), suite_dir)
        write_json_meta(meta_data, suite_dir)


if __name__ == "__main__":
    run()
