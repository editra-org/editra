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
        self.app = wx.App(False)
        self.path = common.GetDataFilePath(u'test_read_utf8.txt')

    def tearDown(self):
        self.app.Destroy()

    #---- Tests ----#

    def testGetFileName(self):
        """Test that getting the file name from a string returns the correct
        string.

        """
        roots = (("Home", "foo", "projects"), ("usr", "bin"),
                 ("Users", "bar", "Desktop"))
        fname = "test.py"
        paths = [os.path.join(os.sep.join(root), fname) for root in roots]
        for path in paths:
            self.assertEqual(fname, util.GetFileName(path),
                             "util.GetFileName(%s) != %s" % (path, fname))

    def testGetPathName(self):
        """Test that getting the path name from a string returns the correct
        string.

        """
        roots = (("Home", "foo", "projects"), ("usr", "bin"),
                 ("Users", "bar", "Desktop"))
        fname = "test.py"
        paths = [os.sep.join(root) for root in roots]
        for path in paths:
            tmp = os.path.join(path, fname)
            self.assertEqual(path, util.GetPathName(tmp),
                             "util.GetPathName(%s) != %s" % (tmp, path))
