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
""" test the CF standards library """
import copy
import re

import pytest

from entities import Field
from standards.cf import CF
from standards.standard_synonyms import StandardSynonyms


def test_init():
    """confirm that the source file has loaded something"""
    test_cf_obj = CF()

    assert len(test_cf_obj.source) > 0


def test_json_loaded():
    """ Check that the source file has loaded a known object correctly"""
    test_cf_obj = CF()
    sea_ice = test_cf_obj.source['sea_ice_area_fraction']
    assert "1" == sea_ice.units
    expected_description = """"Area fraction" is the fraction of a grid
    cell's horizontal area that has some characteristic of interest. It is
    evaluated as the area of interest divided by the grid cell area. It may
    be expressed as a fraction, a percentage, or any other dimensionless
    representation of a fraction. Sea ice area fraction is area of the sea
    surface occupied by sea ice. It is also called "sea ice concentration".
    "Sea ice" means all ice floating in the sea which has formed from
    freezing sea water, rather than by other processes such as calving of
    land ice to form icebergs."""
    # only really care about basic string matching so remove weirdness
    assert re.sub("[\x00-\x20]+",
                  " ",
                  expected_description) == re.sub(
        "[\x00-\x20]+", " ", sea_ice.description)
    assert "sic" == sea_ice.amip_id
    assert "91" == sea_ice.grib_id


def get_field_data():
    """Generate some test cases"""
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
        StandardSynonyms.CMIP6: ["concnopenopenope"],
        StandardSynonyms.CF:
            ["number_concentration_of_coarse_mode_"
             "ambient_aerosol_particles_in_air"]
        }

    unknown_field = copy.deepcopy(valid_field)
    unknown_field.synonyms = {StandardSynonyms.CF: ["xxxinvalidxxx"]}
    missing_field = copy.deepcopy(valid_field)
    missing_field.synonyms = {StandardSynonyms.STASH: ["01234"]}
    valid_amip_grib = copy.deepcopy(valid_field)
    valid_amip_grib.synonyms = {
        StandardSynonyms.CF: ["geopotential_height"],
        StandardSynonyms.AMIP: ["zg"],
        StandardSynonyms.GRIB: ["7 E156"]
        }
    valid_amip_grib.units = "m"
    valid_amip_grib.description = """Geopotential is the sum of the specific
    gravitational potential energy relative to the geoid and the specific
    centripetal potential energy. Geopotential height is the geopotential
    divided by the standard acceleration due to gravity. It is numerically
    similar to the altitude (or geometric height) and not to the quantity
    with standard name height, which is relative to the surface."""
    invalid_amip_grib = copy.deepcopy(valid_amip_grib)
    invalid_amip_grib.synonyms = {
        StandardSynonyms.CF: ["geopotential_height"],
        StandardSynonyms.AMIP: ["zzzzzzz"],
        StandardSynonyms.GRIB: ["123"]
        }

    test_data = [
        pytest.param(valid_field, True, [], id="valid_field_with_cmip_and_cf"),
        pytest.param(invalid_field, False,
                     ["Unit does not match"],
                     id="invalid_cmip_data"),
        pytest.param(unknown_field, False,
                     ["CF code xxxinvalidxxx is not recognised"],
                     id="unknown_cf_code"),
        pytest.param(missing_field, False,
                     ["no CF record"], id="missing_cf_code"),
        pytest.param(valid_amip_grib, True, [], id="valid_with_amip_grib"),
        pytest.param(invalid_amip_grib, False,
                     ["a different AMIP code", "a different GRIB code"],
                     id="invalid_amip_grib")
        ]

    return test_data


@pytest.mark.parametrize("test_field, target_result, errors", get_field_data())
def test_validate_field(test_field, target_result, errors, caplog):
    """throw some fields at it to see what sticks"""
    test_cf_obj = CF()

    result = test_cf_obj.validate_field(test_field)

    assert result == target_result
    for error in errors:
        assert error in caplog.text
