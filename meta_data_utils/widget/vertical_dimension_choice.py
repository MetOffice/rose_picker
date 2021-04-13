# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2012-2021 British Crown (Met Office) & Contributors.
#
# This file is part of Rose, a framework for meteorological suites.
#
# Rose is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rose is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Rose. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import pygtk
import gtk
from vertical_dimension_util import ConfigFiles
pygtk.require('2.0')


class VertDimWidget(gtk.HBox):
    """Class that represents a combo box widget for the vertical dimension
    for a group of LFRic diagnostic fields.

    Contains methods to determine which standard levels are required to be
    defined in the dimension and use these to present only valid dimensions as
    options"""
    FRAC_X_ALIGN = 0.9

    def __init__(self, value, metadata, set_value, hook, arg_str=None):
        super(VertDimWidget, self).__init__(homogeneous=False, spacing=0)
        self.value = value
        self.metadata = metadata
        self.set_value = set_value
        self.hook = hook

        comboboxentry = gtk.ComboBox()
        liststore = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        cell.xalign = self.FRAC_X_ALIGN
        comboboxentry.pack_start(cell)
        comboboxentry.add_attribute(cell, 'text', 0)

        # Determine the user-defined dimensions from the config files then
        # then work out which ones are valid
        ConfigFiles.get_config_files()
        self.vertical_dimensions = ConfigFiles.user_defined_vertical_dimensions
        self.valid_dim_ids, self.valid_dim_names = self.find_valid_dimensions()

        var_values = self.valid_dim_ids
        var_titles = self.valid_dim_names

        for k, entry in enumerate(var_values):
            if var_titles is not None and var_titles[k]:
                liststore.append([var_titles[k] + " (" + entry + ")"])
            else:
                liststore.append([entry])
        comboboxentry.set_model(liststore)
        if self.value in var_values:
            # Changed from stock
            index = self.valid_dim_ids.index(self.value)
            comboboxentry.set_active(index)
        comboboxentry.connect('changed', self.setter)
        comboboxentry.connect('button-press-event',
                              lambda b: comboboxentry.grab_focus())
        comboboxentry.show()
        self.pack_start(comboboxentry, False, False, 0)
        self.grab_focus = lambda: self.hook.get_focus(comboboxentry)
        self.set_contains_error = (lambda e:
                                   comboboxentry.modify_bg(gtk.STATE_NORMAL,
                                                           self.bad_colour))

    def get_required_standard_levels(self):
        """Uses the meta data passed to the widget to determine which field
        group this widget is on. It then finds all of the standard levels that
        are required by fields in that group"""

        found = ConfigFiles.VERT_DIM_REGEX.search(self.metadata["id"])
        if found:
            section = found.group("section")
            group = found.group("group")

            # Get the immutable metadata for the fields in this group
            fields_meta = ConfigFiles.JSON_meta["meta_data"][
                "sections"][section]["groups"][group]["fields"]

            # Loop through the fields and make a set of their standard levels
            standard_levels = set()
            for field in fields_meta.keys():
                if "vertical_dimension" in fields_meta[field]:
                    vertical_info = fields_meta[field]["vertical_dimension"]
                    if "top_arg" in vertical_info:
                        standard_levels.add(vertical_info["top_arg"])
                    if "bottom_arg" in vertical_info:
                        standard_levels.add(vertical_info["bottom_arg"])

            return standard_levels

        raise Exception("'vertical_dimension_for_group' section not found in: "
                        + self.metadata["id"])

    def find_valid_dimensions(self):
        """Finds all the user-defined vertical dimensions that specify the
        standard levels required by the field group"""

        valid_vertical_dimension_ids = []
        valid_vertical_dimension_names = []
        required_levels = self.get_required_standard_levels()

        # Loop through vertical dimensions to find valid ones
        for id, definition in self.vertical_dimensions.items():
            for name, standard_levels in definition.items():

                # Loop through required levels to check if all are present
                dimension_valid = True
                for required_level in required_levels:
                    if required_level not in standard_levels:
                        dimension_valid = False

                # Add valid dimension ids and names to lists
                if dimension_valid:
                    valid_vertical_dimension_ids.append(id)
                    valid_vertical_dimension_names.append(name)

        # If there are none, tell the user via the title in the widget
        if not valid_vertical_dimension_ids:
            valid_vertical_dimension_ids = [""]
            valid_vertical_dimension_names = ["No valid vertical dimension "
                                              "found"]

        return valid_vertical_dimension_ids, valid_vertical_dimension_names

    def setter(self, widget):
        index = widget.get_active()
        self.value = self.valid_dim_ids[index]
        self.set_value(self.value)
        return False
