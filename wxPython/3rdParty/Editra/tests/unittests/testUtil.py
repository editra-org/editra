###############################################################################
# Name: testUtil.py                                                           #
# Purpose: Unit tests for util.py module in Editra/src                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the various Utility functions in
the util module.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import unittest

# Local modules
import common

# Module to test
import util

#-----------------------------------------------------------------------------#
# Test Class

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.path = common.GetDataFilePath(u'test_read_utf8.txt')

    def tearDown(self):
        pass

    #---- Tests ----#
