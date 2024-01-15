#!/usr/bin/env python3
##############################################################################
# (C) British Crown Copyright 2018 Met Office.
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
"""
Rose Picker program script. Execution starts here.
"""
from argparse import ArgumentParser
import collections
import json
import os.path
from pathlib import Path
import re
from typing import Dict, List, Sequence

import rose_picker.rose  # type: ignore
from rose_picker.rose.config import ConfigSyntaxError  # type: ignore
from rose_picker.rose.config_tree import (  # type: ignore
    ConfigTree,
    ConfigTreeLoader
)

_NAMELISTS_REGEX = re.compile(r'^\s*namelist\s*:\s*(\w*)\s*(?:=\s*(\S+))?')


class RosePickerException(Exception):
    """
    Thrown by Rose Picker to indicate errors.
    """
    pass  # pylint: disable=unnecessary-pass


def _load_configuration(filename: Path,
                        include_dirs: Sequence[Path]) -> ConfigTree:
    """
    Load and expand the configuration file.
    """
    if not filename.exists():
        raise RosePickerException(f"File {filename} does not exist.")
    try:
        config_node = rose_picker.rose.config.load(str(filename))
        tree_loader = ConfigTreeLoader()

        tree_loader.load(filename.parent,
                         filename.name,
                         conf_dir_paths=include_dirs,
                         conf_node=config_node)
        return config_node
    except ConfigSyntaxError as config_syntax:
        raise RosePickerException(f"File {filename} is not a valid rose meta"
                                  " configuration file.") from config_syntax


def _list_configuration(config_node: ConfigTree) -> List[str]:
    """
    Get keys list of all the namelists/members in the configuration file.
    """
    node_keys = list(filter(_NAMELISTS_REGEX.match,
                            config_node.get_value().keys()))
    node_keys.sort()
    return node_keys


def _extract_namelists(
        config_node: ConfigTree,
        namelist_keys: Sequence[str],
        member_keys: Sequence[str],
        listnames: List[str],
        namelist_config: Dict[str, Dict[str, Dict[str, Dict[str, str]]]]
):

    # pylint: disable-msg=too-many-locals

    """
    Extracts namelist properties from meta-data.
    """
    node_keys = _list_configuration(config_node)

    for key in node_keys:

        match = _NAMELISTS_REGEX.match(key)
        if match is None:
            raise Exception(f"Failed to find key in string: {key}")
        node = match.group(0)
        namelist = match.group(1)
        member = match.group(2)

        if namelist:
            if not member:  # pylint: disable=no-else-continue
                listnames.append(namelist)
                namelist_config[namelist] = {}
                namelist_config[namelist]['members'] = {}

                list_node = config_node.get([node])
                list_node_keys = list_node.get_value().keys()

                for i in namelist_keys:
                    if i in list_node_keys:
                        list_prop = list_node.get([i])
                        list_prop = list_prop.get_value()

                        if i == 'duplicate':
                            KEY = 'multiple_instances_allowed'
                            namelist_config[namelist][KEY] \
                                = list_prop
                        else:
                            namelist_config[namelist][i] \
                                = list_prop

                continue

            elif namelist not in namelist_config.keys():
                message = (
                    'namelist:' + namelist
                    + ' has no section in metadata configuration file')
                raise RosePickerException(message)

            else:
                namelist_config[namelist]['members'][member] = {}

                member_node = config_node.get([node])
                member_node_keys = member_node.get_value().keys()
                for i in member_keys:
                    if i in member_node_keys:
                        member_prop = member_node.get([i])
                        member_prop = member_prop.get_value()
                        namelist_config[namelist]['members'][member][i] \
                            = member_prop


def main(meta_filename: Path, include_dirs: Sequence[Path], output_dir: Path):
    """
    Rose Picker entry point.

    Load in a config file. This is using Rose's "config.py" code which is
    different to pythons ConfigParser. We need to use config.py to ensure any
    changes to the way rose meta data is treated are picked up.

    Rose's "config_tree.py" code is used to expand any import statements in the
    specified configuration file.
    """
    config_node = _load_configuration(meta_filename, include_dirs)

    namelist_keys = ['duplicate',
                     'instance_key_member']

    member_keys = ['bounds',
                   'enumeration',
                   'expression',
                   'kind',
                   'length',
                   'string_length',
                   'type',
                   'values']

    listnames: List[str] = []
    namelist_config: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] \
        = collections.OrderedDict()
    _extract_namelists(config_node, namelist_keys, member_keys,
                       listnames, namelist_config)

    basename = os.path.basename(meta_filename).split('.')

    # Output as .json file
    nml_config_filename = f'{basename[0]}.json'
    with open(f'{output_dir}/{nml_config_filename}', 'wt',
              encoding='utf-8') as output:
        json.dump(namelist_config, output, indent=4, ensure_ascii=True)

    # Write out namelists in configuration
    with open(f'{output_dir}/config_namelists.txt', 'wt',
              encoding='utf-8') as output:
        for listname in listnames:
            output.write(f'{listname}\n')


def cli() -> None:
    parser = ArgumentParser(add_help=False, description=__doc__)
    parser.add_argument('-help', '-h', '--help', action='help',
                        help='Show this help message and exit')
    parser.add_argument('-directory', metavar='path',
                        type=Path, default=Path.cwd(),
                        help='Generated source files are put here.')
    parser.add_argument('-include_dirs', action='append',
                        type=Path,
                        help='Include directory to list of directories '
                             'to search for inherited metadata files')
    parser.add_argument('meta_filename', metavar='description-file',
                        type=Path,
                        help='The metadata file to load')
    arguments = parser.parse_args()
    main(arguments.meta_filename,
         arguments.include_dirs,
         arguments.directory)


if __name__ == '__main__':
    cli()
