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
"""This module contains functionality for writing LFRic meta data to disk as a
rose-meta.conf file"""
import logging
import os
from textwrap import wrap
from typing import Dict

LOGGER = logging.getLogger("lfric_meta_data_parser")


def write_file(path: str, file_name, data: str):
    """
    Writes rose suite files to disk
    :param path: The path where the file is to be written
    :param file_name: The name of the file to be written
    :param data: file as a string
    """
    with open(path + file_name + ".conf", 'w') as file:
        file.write(data)


def create_rose_meta(meta_data: Dict, directory: str, file_name):
    """
    Creates a rose_meta.conf file using the supplied meta data
    :param meta_data: Dict containing all meta data
    :param directory: The directory the file will be saved in
    :param file_name: The name of the file that the meta data will be
    written to
    :return rose_meta: The rose-meta file as a string, ready to be written to
    disk
    """
    LOGGER.info("Creating %s.conf", file_name)
    rose_meta = ""

    rose_meta += """
[field_config]
title=LFRic Field Configuration
"""

    for section in meta_data["sections"].values():
        rose_meta += f"""
[field_config:{section.name}]
title={section.title}"""

        for group in section.groups.values():
            rose_meta += f"""
[field_config:{section.name}:{group.name}]
title={group.title}"""
            model_levels = set()
            for field in group.fields.values():
                if field.vertical_dimension:
                    if "top_arg" in field.vertical_dimension:
                        model_levels.add(field.vertical_dimension["top_arg"])
                    if "bottom_arg" in field.vertical_dimension:
                        model_levels.add(
                            field.vertical_dimension["bottom_arg"])
            rose_meta += f"""
[field_config:{section.name}:{group.name}=model_levels_for_group]
title=Model Levels used by this group
description=Vertical dimensions must define these levels to be valid
values=
"""
            for model_level in model_levels:
                rose_meta += "            " + model_level + os.linesep

            rose_meta += f"""
sort-key=01
compulsory=true
"""
            rose_meta += f"""
[field_config:{section.name}:{group.name}=vertical_dimension_for_group]
title=Vertical dimension used by this group
description=If you have edited the vertical dimensions please restart the GUI
            to pick up the changes to the rose-app.conf file
widget[rose-config-edit]=vertical_dimension_choice.VertDimWidget
sort-key=02
compulsory=true
"""

            for field in group.fields.values():
                rose_meta += f"""
[field_config:{section.name}:{group.name}={field.unique_id}]
type=boolean
title=Enable {field.item_title}
trigger=field_config:{section.name}:{group.name}={field.unique_id}{
                field.trigger}
help=Unit of Measure: {field.units}
    =Function Space: {field.function_space}
    =Data type: {field.data_type}
    =Time step: {field.time_step}
    =Interpolation: {field.recommended_interpolation}
"""
                if field.vertical_dimension:
                    attribute_string = f"    =vertical_dimension:{os.linesep}"
                    for key, value in field.vertical_dimension.items():
                        if key == "top_arg":
                            key = "top_level"
                        if key == "bottom_arg":
                            key = "bottom_level"
                        attribute_string += f"       ={key}: " \
                                            f"{str(value)}{os.linesep}"

                    rose_meta += attribute_string

                if field.synonyms:
                    attribute_string = f"    =Synonyms:{os.linesep}"
                    for key, values in field.synonyms.items():
                        for value in values:
                            attribute_string += f"    =    {key.value}: " \
                                                f"{str(value)}{os.linesep}"

                    rose_meta += attribute_string

                if field.non_spatial_dimension:
                    attribute_string = f"    =Required non-spatial " \
                                       f"dimensions:{os.linesep}"
                    for dimension in field.non_spatial_dimension.values():
                        attribute_string += f"""    =    {dimension["name"]}"""

                    rose_meta += attribute_string

                    # Formats the description, adding newlines every 100 chars
                line_sep = "\n           "
                rose_meta += f"""
description={line_sep.join(wrap(field.description,width=100))}
           =For more information on {field.item_title}, see the help text
"""

                rose_meta += f"""
[field_config:{section.name}:{group.name}={field.unique_id}__checksum]
type=boolean
title=Enable Checksum for {field.item_title}
"""

    rose_meta = add_file_meta(meta_data, rose_meta)
    rose_meta = add_vertical_meta(rose_meta,
                                  meta_data["standard_level_markers"])
    rose_meta = add_non_spatial_dims_meta(meta_data["non_spatial_dimensions"],
                                          rose_meta)

    write_file(directory + "meta/", file_name, rose_meta)


def add_file_meta(meta_data: Dict, rose_meta: str) -> str:
    """Adds meta data for file output in rose.
    :param meta_data: Dict containing parsed meta data
    :param rose_meta: String that the file output data will be appended to
    :return rose_meta: String with file output data appended to it"""

    values_list = []
    titles_list = []

    for section in meta_data["sections"].values():
        for group in section.groups.values():
            for field in group.fields.values():

                values_list.append(field.unique_id)
                titles_list.append(
                    section.title + ": " + group.title +
                    ": " + field.item_title)

    values = ', '.join(values_list)
    titles = '", "'.join(titles_list)

    rose_meta += f"""[output_stream]
duplicate=true
macro=add_section.AddField, add_section.AddStream
title=Output Streams

[output_stream=name]
type=character

[output_stream=timestep]
type=character

[output_stream:field]
duplicate=true
macro=add_section.AddField
title=Fields

[output_stream:field=id]
values={values}
value-titles="{titles}"

[output_stream:field=temporal]
values=instant,average,accumulate,minimum,maximum,once
"""
    return rose_meta


def add_vertical_meta(rose_meta: str, levels) -> str:
    """Adds data about vertical dimensions. Currently static, will be further
    developed in the future
    :param rose_meta: String that the vertical dimension data will be appended
    to
    :param levels: A List of model levels
    :return rose_meta: String with vertical dimension data appended to it"""
    rose_meta += """
[vertical_dimension]
duplicate=true
title=Vertical Dimension

[vertical_dimension=name]
title=Name
description=Name of the vertical dimension
help=The name used to identify this vertical dimension when associating a field
     with it in Rose
type=character
compulsory=true
fail-if=len(this) == 0 # Name must be specified
sort-key=01

[vertical_dimension=positive]
title=Positive
description=The positive direction
help=The positive direction of the vertical axis, either up or down
values=up, down
compulsory=true
sort-key=02

[vertical_dimension=units]
title=Units
description=Unit of measure
help=The unit of measure for this vertical axis is restricted to be in metres
values=m
compulsory=true
sort-key=03

[vertical_dimension=level_definition]
title=Level boundaries
description=Boundaries of levels in ascending order
help=Positive numbers defining the edges of each level in the vertical
     dimension. The boundaries should be entered in ascending order
length=:
type=real
macro=level_definition.Validator, level_definition.Transformer
range=0:
fail-if=len(this)<2 # There must be at least two level boundaries
compulsory=true
sort-key=04
"""
    num = 1001
    for level in levels:
        rose_meta += f"""[vertical_dimension={level}]
title={level.replace("_", " ".title())}
description=A Model Level
type=integer

range=0:
# Layer out of range
fail-if=this > len(vertical_dimension=level_definition)-1;
sort-key=model-levels-{num}"""
        rose_meta += os.linesep
        num += 1
    return rose_meta


def add_non_spatial_dims_meta(non_spatial_dims_meta: Dict,
                              rose_meta: str) -> str:
    """Adds the Rose metadata for the non-spatial dimensions.

    :param non_spatial_dims_meta: Dictionary containing metadata describing all
                                  of the non-spatial dimensions
    :param rose_meta: String that the non-spatial dimension data will be
                      appended to
    :return rose_meta: String with non-spatial dimension data appended to it"""

    dimension_type = {"label_definition": "character",
                      "axis_definition": "real"}
    rose_meta += """
[non_spatial_dimensions]
title=Non-Spatial Dimensions
"""

    for dimension in non_spatial_dims_meta.values():

        # Dimension only needs configuring if it doesn't have a definition
        if dimension.get("label_definition", None) is None and \
                dimension.get("axis_definition", None) is None:

            rose_meta += f"""
[non_spatial_dimensions={dimension["name"].lower().replace(" ", "_")}]
title={dimension["name"]}
description=Level definition for {dimension["name"]}
type={dimension_type[dimension["type"]]}
length=:
trigger="""
            # Trigger each field that uses this dimension
            for (section, group, field) in dimension["fields"]:
                rose_meta += f"""
       =field_config:{section}:{group}={field}: len(this) > 0 ;"""

            # Add the help text
            rose_meta += f"""
help={dimension["help"]}"""
            if "units" in dimension:
                rose_meta += f"""
    =Units: {dimension["units"]}"""

            # List each field that uses this dimension
            rose_meta += f"""
    =Necessary for:"""
            for _, _, field in dimension["fields"]:
                rose_meta += f"""
    =    {field}
"""

    return rose_meta
