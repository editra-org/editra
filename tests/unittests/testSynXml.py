###############################################################################
# Name: testSynXml.py                                                         #
# Purpose: Unit tests for the Syntax Xml Library                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for teh Syntax Xml Library"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx.stc
import unittest

# Local modules
import common

# Module to test
import syntax

#-----------------------------------------------------------------------------#
# Test Class

class SynXmlTest(unittest.TestCase):
    def setUp(self):
        self.path = common.GetDataFilePath(u'syntax.xml')
        self.xml = common.GetFileContents(self.path)
        self.fhandle = syntax.FileTypeHandler(self.path)
        self.fhandle.LoadFromDisk()

    def tearDown(self):
        pass

    #---- Base Tests ----#

    def testGetXml(self):
        """Test getting the xml representation"""
        tmp_h = syntax.FileTypeHandler()
        tmp_h.LoadFromString(self.xml)

        x1 = self.fhandle.GetXml()
        x2 = tmp_h.GetXml()
        self.assertEquals(x1, x2)

    #---- FileTypeHandler tests ----#

    def testGetCommentPattern(self):
        """Get retrieving the comment pattern from the xml"""
        self.assertEquals(self.fhandle.CommentPattern,
                          self.fhandle.GetCommentPattern())
        self.assertEquals(self.fhandle.CommentPattern, [u"#",],
                          "pattern is: %s" % self.fhandle.CommentPattern)

    def testGetFeature(self):
        """Test retrieving a feature"""
        feat = self.fhandle.GetFeature(u'AutoIndenter')
        self.assertEquals(feat, u'myextension.py')

    def testGetKeywords(self):
        """Test getting the keywords from the xml"""
        kwords = self.fhandle.GetKeywords()
        self.assertTrue(isinstance(kwords, list), "Not a List")
        self.assertTrue(isinstance(kwords[0], tuple), "Not a tuple")
        self.assertTrue(len(kwords) == 2)
        self.assertEquals(kwords[0][0], 0, "not sorted")
        self.assertTrue(u'else' in kwords[0][1])
        self.assertTrue(u'str' in kwords[1][1])

    def testGetProperties(self):
        """Test getting the property list from the xml"""
        props = self.fhandle.GetProperties()
        self.assertTrue(isinstance(props, list))
        self.assertTrue(isinstance(props[0], tuple))
        self.assertTrue(len(props) == 2)
        self.assertEquals(props[0][0], "fold")
        self.assertEquals(props[0][1], "1")

    def testGetSyntaxSpec(self):
        """Test geting the syntax specifications from the xml"""
        spec = self.fhandle.GetSyntaxSpec()
        self.assertTrue(isinstance(spec, list))
        self.assertTrue(isinstance(spec[0], tuple))
        self.assertTrue(len(spec) == 2)
        self.assertEquals(spec[0][0], wx.stc.STC_P_DEFAULT,
                          "val was: %s" % spec[0][0])
        self.assertEquals(spec[0][1], "default_style",
                          "val was: %s" % spec[0][1])

    def testVersion(self):
        """Test the xml version attribute"""
        self.assertEquals(self.fhandle.Version, 1,
                        "val was: " + str(self.fhandle.Version))
        
