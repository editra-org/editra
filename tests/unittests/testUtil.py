###############################################################################
# Name: testUtil.py                                                           #
# Purpose: Unit tests for util.py module in Editra/src                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import unittest

# Module to test
import util

#-----------------------------------------------------------------------------#
# Test Class

class UtilTest(unittest.TestCase):
    def setUp(self):
        self.app = wx.App(False)

    def tearDown(self):
        self.app.Destroy()

    #---- Tests ----#
    def testAdjustColour(self):
        """Test that a valid colour results are returned"""
        c = wx.Colour(125, 125, 125)

        # Check that the color was brightened
        c2 = util.AdjustColour(c, 50)
        self.assertTrue(sum(c.Get()) < sum(c2.Get()),
                        "Failed to lighten colour")

        # Check that the color was darkened
        c2 = util.AdjustColour(c, -50)
        self.assertTrue(sum(c.Get()) > sum(c2.Get()),
                        "Failed to darken colour")

    def testHexToRGB(self):
        """Test that the conversion of a hex string to rgb is acurate"""
        hexstr = ("#FF0000", "#00FF00", "#0000FF", "#000000", "#FFFFFF")
        rgb = ((255, 0, 0), (0, 255, 0), (0, 0, 255),
               (0, 0, 0), (255, 255, 255))

        for hval, rgbval in zip(hexstr, rgb):
            convert = tuple(util.HexToRGB(hval))
            self.assertEquals(convert, rgbval,
                              "(HexToRGB(%s) == %s) != %s" %
                              (hval, convert, str(rgbval)))

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
