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
"""test the cmip standards library"""
import copy

import pytest

from entities import Field
from standards.cmip import CMIP
from standards.standard_synonyms import StandardSynonyms


def test_init():
    """check that initialising it populates some length in the dictionary"""
    test_cmip_obj = CMIP()

    assert len(test_cmip_obj.source) > 0


def test_json_loaded():
    """check the source file has loaded a field correctly"""
    test_cmip_obj = CMIP()
    sea_ice = test_cmip_obj.source['siconc']
    assert "%" == sea_ice.units
    assert "sea_ice_area_fraction" == sea_ice.cf_id
    assert "Sea-Ice Area Percentage (Ocean Grid)" == sea_ice.title
    assert "Percentage of grid cell covered by sea ice" == sea_ice.description
    assert "150ada98-357c-11e7-8257-5404a60d96b5" == sea_ice.unid


def get_field_data():
    """generate some valid and invalid sample data"""
    valid_field = Field("some_file")
    valid_field.unique_id = "test_cmip__conc_coarse_mode_aerosol"
    valid_field.units = "m-3"
    valid_field.function_space = "w3"
    valid_field.trigger = "..."
    valid_field.description = "includes all particles with diameter larger " \
                              "than 1 micron"
    valid_field.data_type = "test_data_type"
    valid_field.time_step = "1ts"
    valid_field.recommended_interpolation = "test_interpolation"
    valid_field.synonyms = {
        StandardSynonyms.CMIP6: ["conccmcn"],
        StandardSynonyms.CF:
            ["number_concentration_of_coarse_mode_"
             "ambient_aerosol_particles_in_air"]
        }
    invalid_field = copy.deepcopy(valid_field)
    invalid_field.units = "m-2"
    invalid_field.description = "includes all particles with diameter larger" \
                                " than 1 nanometer"
    invalid_field.synonyms = {
        StandardSynonyms.CMIP6: ["conccmcn"],
        StandardSynonyms.CF:
            ["number_concentration_of_coarse_mode_"
             "ambient_aerosol_particles_in_soil"]
        }

    unknown_field = copy.deepcopy(valid_field)
    unknown_field.synonyms = {StandardSynonyms.CMIP6: ["xxxinvalidxxx"]}
    missing_field = copy.deepcopy(valid_field)
    missing_field.synonyms = {StandardSynonyms.STASH: ["01234"]}

    test_data = [
        pytest.param(valid_field, True, [], id="valid_field_with_cmip_and_cf"),
        pytest.param(invalid_field, False,
                     ["a different CF code", "Unit does not match"],
                     id="invalid_cmip_and_cf_data"),
        pytest.param(unknown_field, False,
                     ["CMIP6 code is not recognised"], id="unknown_cmip_code"),
        pytest.param(missing_field, False,
                     ["no CMIP record"], id="missing_cmip_code")
        ]

    return test_data


@pytest.mark.parametrize("test_field, target_result, errors", get_field_data())
def test_validate_field(test_field, target_result, errors, caplog):
    """throw some fields at it to see what sticks"""
    test_cmip_obj = CMIP()

    result = test_cmip_obj.validate_field(test_field)

    assert result == target_result
    for error in errors:
        assert error in caplog.text
