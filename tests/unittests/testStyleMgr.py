###############################################################################
# Name: testStyleMgr.py                                                       #
# Purpose: Unit test for Style Manager                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import wx
import unittest

# Module to Test
sys.path.insert(0, os.path.abspath("../../src"))
import ed_style

#-----------------------------------------------------------------------------#
class EdApp(wx.App):
    def GetLog(self):
        return lambda msg: None

#-----------------------------------------------------------------------------#
# Test Class

class StyleMgrTest(unittest.TestCase):
    def setUp(self):
        self.app = EdApp(False)
        self.mgr = ed_style.StyleMgr()
        self.dd = ed_style.DefaultStyleDictionary()
        self.bstr = ["fore:#000000", "back:#FFFFFF",
                     "face:%(primary)s", "size:%(size)d"]

    def tearDown(self):
        pass

    #---- Tests ----#
    def testBlankStyleDictionary(self):
        """Test that a dictionary of blank and null items are returned"""
        blank = self.mgr.BlankStyleDictionary()
        self.assertTrue(isinstance(blank, dict), "No dictionary returned")
        self.assertEquals(sorted(blank.keys()), sorted(self.dd.keys()),
                          "Blank dictionary is missing some keys")

        # Check that all the items are blank and the same
        for key, item in blank.iteritems():
            if not item.IsNull():
                self.assertEquals(sorted(item.GetAsList()), sorted(self.bstr),
                                  "%s != %s" % (str(item.GetAsList()), self.bstr)) 

    # TODO add more tests for checking after changing style sheets
    def testGetCurrentStyleSetName(self):
        """Test getting the name of the current style set"""
        name = self.mgr.GetCurrentStyleSetName()
        self.assertEquals(name, wx.EmptyString)

    def testGetDefaultBackColour(self):
        """Test getting the current default_style's background color"""
        pass

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    unittest.main()
