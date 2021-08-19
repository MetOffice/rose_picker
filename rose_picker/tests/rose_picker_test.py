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
Functional tests of rose-picker tool.
"""
import collections
import json
from pathlib import Path
from subprocess import run, PIPE
from typing import List


PICKER_EXE = Path(__file__).parent.parent / 'rose_picker'


###############################################################################
def test_no_namelist_for_member(tmp_path: Path):
    """
    Confirms that metadata which describes a variable but no associated
    namelist throws an error.
    """
    input_file = tmp_path / 'missing.nml'
    input_file.write_text('''
[namelist:kevin=orphan]
type=integer
''')

    command = [PICKER_EXE, input_file]
    process = run(command, cwd=input_file.parent, stderr=PIPE, check=False)
    assert process.returncode != 0

    expected = 'namelist:kevin has no section in metadata' \
               ' configuration file'
    assert expected in str(process.stderr)


###############################################################################
def test_good_picker(tmp_path: Path):
    """
    Confirms that valid metadata produces expected output.
    """
    input_file = tmp_path / 'good.nml'
    input_file.write_text('''
[namelist:aerial]

[namelist:aerial=fred]
type=real

[namelist:aerial=wilma]
type=real
length=:
!bounds=source:constants_mod=FUDGE

[namelist:aerial=betty]
type=logical
length=:
!bounds=fred

[namelist:aerial=dino]
type=integer
length=:
!bounds=namelist:sugar=TABLET

[namelist:aerial=bambam]
type=integer
length=:
''')

    command = [PICKER_EXE, input_file]
    process = run(command, cwd=input_file.parent, check=False)
    assert process.returncode == 0

    # json file
    output_file = input_file.with_suffix('.json')
    with output_file.open() as fhandle:
        result = json.load(fhandle)

    good_result = collections.OrderedDict(
        {'aerial': {'dino':   {'length': ':',
                               'type':   'integer',
                               'bounds': 'namelist:sugar=TABLET'},
                    'wilma':  {'length': ':',
                               'type':   'real',
                               'bounds': 'source:constants_mod=FUDGE'},
                    'betty':  {'length': ':',
                               'type':   'logical',
                               'bounds': 'fred'},
                    'bambam': {'length': ':',
                               'type':   'integer'},
                    'fred':   {'type':   'real'}}})

    assert result == good_result


###############################################################################
def test_full_commandline(tmp_path: Path):
    input_file = tmp_path / 'input/config-meta.conf'
    input_file.parent.mkdir()
    input_file.write_text('''
''')

    include_dir = tmp_path / 'include'
    include_dir.mkdir()

    output_file = tmp_path / 'output/config-meta.json'
    output_file.parent.mkdir()

    command: List[str] = [str(PICKER_EXE), str(input_file),
                          '-directory', str(output_file.parent),
                          '-include_dirs', str(include_dir)]
    process = run(command, check=False)
    assert process.returncode == 0

    assert output_file.exists()
