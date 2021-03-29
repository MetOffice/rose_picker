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
""" CF Metadata handling package """
import logging
import os
from xml.dom import minidom

from entities import Field
from standards.standard_synonyms import StandardSynonyms

XML_DATA = os.path.dirname(
        os.path.abspath(__file__)) + "/data/cf-standard-name-table.xml"


class CFRecord:
    """ Basic entity to hold structured representation of CF record
    information  """

    def __init__(self, cf_id: str, units: str = None, description: str = None,
                 amip_id: str = None, grib_id: str = None):
        """
        Populate a CF record
        @type cf_id: str
        @type units: str
        @type description: str
        @type amip_id: str
        @type grib_id: str
        """
        self.cf_id = cf_id
        self.units = units
        self.description = description
        self.amip_id = amip_id
        self.grib_id = grib_id


class CF:
    """ CF Standard Metadata Class - handles validating CF metadata """
    LOGGER = logging.getLogger(__name__)

    def __init__(self):
        """ Primes the local library of metadata """
        source = minidom.parse(XML_DATA)
        # pre parse source
        self.source = {}
        for record in source.getElementsByTagName("entry"):
            record = CFRecord(
                    cf_id=record.attributes['id'].value,
                    units=record.getElementsByTagName("canonical_units")[
                        0].childNodes[0].data if
                    record.getElementsByTagName("canonical_units")[
                        0].childNodes else None,
                    description=record.getElementsByTagName("description")[
                        0].childNodes[
                        0].data if
                    record.getElementsByTagName("description")[
                        0].childNodes else None,
                    amip_id=record.getElementsByTagName("amip")[0].childNodes[
                        0].data if
                    record.getElementsByTagName("amip")[
                        0].childNodes else None,
                    grib_id=record.getElementsByTagName("grib")[0].childNodes[
                        0].data if
                    record.getElementsByTagName("grib")[
                        0].childNodes else None,
                    )
            self.source.update({record.cf_id: record})

    def validate_field(self, test_field: Field) -> bool:
        """
        Confirm if field conforms to CF reference data
        @type test_field: Field under test
        @return bool: outcome of test
        """
        valid = True
        cf_synonyms = test_field.synonyms.get(StandardSynonyms.CF, [])
        if not cf_synonyms:
            self.LOGGER.exception("Field %s has no CF record",
                                  test_field.unique_id)
            valid = False
        for cf_value in cf_synonyms:
            if cf_value in self.source.keys():
                dictionary_cmip = self.source[cf_value]
                if test_field.units != dictionary_cmip.units and \
                        dictionary_cmip.units is not None:
                    self.LOGGER.warning(
                            "Unit does not match CF unit for field %s with CF "
                            "value %s",
                            test_field.unique_id,
                            cf_value
                            )
                    valid = False
                amip_synonyms = test_field.synonyms.get(StandardSynonyms.AMIP)
                if amip_synonyms and dictionary_cmip.amip_id not in \
                        amip_synonyms:
                    self.LOGGER.error(
                            "Field %s has a different AMIP code to the CF "
                            "standard",
                            test_field.unique_id
                            )
                    valid = False
                grib_synonyms = test_field.synonyms.get(StandardSynonyms.GRIB)
                if grib_synonyms and dictionary_cmip.grib_id not in \
                        grib_synonyms:
                    self.LOGGER.error(
                            "Field %s has a different GRIB code to the CF "
                            "standard",
                            test_field.unique_id
                            )
                    valid = False
                # could consider validating description too
            else:
                self.LOGGER.exception("Field %s CF code %s is not recognised",
                                      test_field.unique_id,
                                      cf_value)
                valid = False
        return valid
