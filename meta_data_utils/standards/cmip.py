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
""" CMIP Metadata handling package """
import json
import logging
import os

from entities import Field
from standards.standard_synonyms import StandardSynonyms

JSON_DATA = os.path.dirname(os.path.abspath(__file__)) + "/data/cmip6.json"


class CMIPRecord:
    """ Basic entity to hold structured representation of CMIP record
    information  """

    def __init__(self, label: str, cf_id: str, title: str, units: str,
                 description: str, unid: str):
        """
        Populate a CMIP record
        @type label: str
        @type cf_id: str
        @type title: str
        @type units: str
        @type description: str
        @type unid: str
        """
        self.label = label
        self.cf_id = cf_id
        self.title = title
        self.units = units
        self.description = description
        self.unid = unid


class CMIP:
    """ CMIP Standard Metadata Class - handles validating CMIP metadata """
    LOGGER = logging.getLogger(__name__)

    def __init__(self):
        """ Primes the local library of metadata """
        with open(JSON_DATA, 'r') as file:
            source = json.load(file)
        # pre parse source
        self.source = {}
        for record in source:
            record = CMIPRecord(
                    label=record["0"].split(' ')[0],
                    cf_id=record["1"],
                    title=record["2"],
                    units=record["3"],
                    description=record["4"],
                    unid=record["5"]
                    )
            self.source.update({record.label: record})

    def validate_field(self, test_field: Field) -> bool:
        """
        Confirm if field conforms to CMIP reference data
        @type test_field: Field under test
        @return bool: outcome of test
        """
        valid = True
        cmip_synonyms = test_field.synonyms.get(StandardSynonyms.CMIP6, [])
        if not cmip_synonyms:
            valid = False
            self.LOGGER.exception("Field %s has no CMIP record",
                                  test_field.unique_id)
        for cmip_value in cmip_synonyms:
            if cmip_value in self.source.keys():
                dictionary_cmip = self.source[cmip_value]
                if test_field.units != dictionary_cmip.units:
                    self.LOGGER.warning(
                            "Unit does not match CMIP %s unit for field %s",
                            cmip_value,
                            test_field.unique_id
                            )
                    valid = False
                cf_synonyms = test_field.synonyms.get(StandardSynonyms.CF)
                if cf_synonyms and dictionary_cmip.cf_id not in cf_synonyms:
                    self.LOGGER.error(
                            "Field %s has a different CF code to the CMIP6 "
                            "standard for CMIP %s",
                            test_field.unique_id,
                            cmip_value
                            )
                    valid = False
                # could consider validating description too
            else:
                self.LOGGER.exception("Field %s CMIP6 code is not recognised",
                                      test_field.unique_id)
                valid = False
        return valid
