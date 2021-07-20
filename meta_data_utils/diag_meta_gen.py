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
It recursively looks in every directory for files ending in "meta_mod.f90".
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
DIRECTORIES_IN_ROOT = ["meta_data_utils", "rose_picker"]


def get_gpl_utilities_root_dir(directories_in_root):
    """Finds the root directory of the GPL-utilities source tree
    :return root_dir: The root directory as a string"""

    LOGGER.debug("GPL-utilities directory not supplied, attempting to find it")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    in_root_directory = False
    counter = 0
    max_count = 20

    while not in_root_directory:
        if all(x in os.listdir(root_dir) for x in directories_in_root):
            in_root_directory = True
        elif counter == max_count:
            raise IOError("Unable to ascertain GPL-utils root after {0} "
                          "attempts ({1})".format(str(max_count), root_dir))
        else:
            root_dir += "/.."
            counter += 1

    LOGGER.debug("The GPL-utils root directory was found to be %s", root_dir)

    return root_dir


def setup_logging(level: int, file_name: str):
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
    optional = arg_parser._action_groups.pop()
    required = arg_parser.add_argument_group('required arguments')
    optional.add_argument("-v", "--verbose", action="store_true",
                          help="increase output verbosity")
    required.add_argument("-p", "--path", type=str, required=True,
                          help='''
The root of your LFRic repository. This tool will recursively search through a
directory structure looking for files that end in '__meta_mod.f90'.
''')
    optional.add_argument("-o", "--output", type=str,
                          help='''
The location the generated meta data will be output to
This tool will output a JSON representation of the generated meta data and a
directory called 'meta'. This will contain a conf file made using the generated
meta data as well as a macro for adding output streams and their fields to the
configuration.''')
    optional.add_argument("-f", "--filename", type=str,
                          help='''
The name of the conf file output by the generator. Defaults to rose-meta.conf
''')
    optional.add_argument("-s", "--support_types", type=str,
                          help='''
This tool needs supporting type and enum declarations.
interpolation_enum_mod.90
levels_enum_mod.f90
positive_enum_mod.f90
time_step_enum_mod.f90
vertical_dimensions_mod.f90
Specify the directory containing these files, otherwise the tool will use the
default location''')
    arg_parser._action_groups.append(optional)
    return arg_parser.parse_args()


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


def add_rose_widget(root_dir: str, rose_suite_dir: str) -> None:
    """Copies vertical dimension widget files into rose suite
    :param root_dir: The path to the root directory of the GPL-utilities source
    :param rose_suite_dir: The path to the output Rose suite
    """
    LOGGER.info("Adding rose widget")
    # Ticket 2323 will remove this string concatenation
    source_directory = root_dir + "/meta_data_utils/widget/"
    dest_directory = rose_suite_dir + "/meta/lib/python/widget/"
    os.makedirs(os.path.abspath(dest_directory), exist_ok=True)

    files = ["vertical_dimension_choice.py", "vertical_dimension_util.py"]
    exported = True
    for file in files:
        shutil.copy(source_directory + file, dest_directory + file)
        if not os.path.isfile(dest_directory + file):
            exported = False
            LOGGER.error("Failed to copy file from %s",
                         source_directory + file)
    if not exported:
        raise OSError("File export failed")


def run():
    """Defines variables for file output and runs the parser"""

    args = parse_args()

    log_file_name = 'meta_data_parser.log'

    if args.verbose:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    setup_logging(logging_level, log_file_name)

    lfric_dir = args.path
    if not os.path.exists(lfric_dir):
        LOGGER.error("Path to LFRic directory does not exist: %s", lfric_dir)
        raise FileNotFoundError("Path to LFRic directory does not exist")

    if args.output:
        suite_dir = args.output
        suite_dir += '/example_rose_suite/'
    else:
        working_dir = os.path.dirname(os.path.abspath(__file__))
        suite_dir = working_dir + "/example_rose_suite/"

    if args.filename:
        metadata_file_name = args.filename
    else:
        metadata_file_name = "rose-meta"

    # Ticket 2323 will remove all this string concatenation for directory paths
    if args.support_types:
        meta_types_directory = args.support_types
    else:
        meta_types_directory = \
            lfric_dir + "/um_physics/source/diagnostics_meta/meta_types/"

    # Find meta data in fortran meta_mod.f90 files
    LOGGER.info("Starting parser")
    reader = FortranMetaDataReader(lfric_dir, meta_types_directory)

    meta_data, valid = reader.read_fortran_files()

    if not valid:
        LOGGER.info("Invalid Fortran files exist - please correct")

    else:
        LOGGER.info("Meta data valid, creating files")
        # If target directory doesn't exist make it
        os.makedirs(os.path.dirname(suite_dir + "meta/rose-meta.conf"),
                    exist_ok=True)

        create_rose_meta(meta_data, suite_dir, metadata_file_name)
        gpl_root_dir = get_gpl_utilities_root_dir(DIRECTORIES_IN_ROOT)
        add_rose_macro(gpl_root_dir, suite_dir)
        add_rose_widget(gpl_root_dir, suite_dir)
        write_json_meta(meta_data, suite_dir)


if __name__ == "__main__":
    run()
