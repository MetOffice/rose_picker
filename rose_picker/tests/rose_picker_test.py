#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017,  Met Office, on behalf of HMSO and Queen's Printer
# For further details please refer to the file GPL/LICENCE which you
# should have received as part of this distribution.
##############################################################################

import unittest
import os
from subprocess import check_output, CalledProcessError, STDOUT


picker_exe = './rose_picker'

###############################################################################
class RosePickerTest(unittest.TestCase):

    ##########################################################################
    def setUp(self):
        pass

    ##########################################################################
    def tearDown(self):
        os.remove(self.test_input_file)
        pass

    def test_no_namelist_for_member(self):

        self.test_input_file = './testNoNamelist.conf'
        with open(self.test_input_file, 'w+') as config_file:
            config_file.write('''
[namelist:kevin=orphan]
type=integer
''')
        picker_command = "{} {}".format(picker_exe, self.test_input_file)

        with self.assertRaises(CalledProcessError) as context:
            check_output(picker_command, shell=True, stderr=STDOUT)

        self.assertIn(
            'namelist:kevin has no section in metadata configuration file',
            context.exception.output)


