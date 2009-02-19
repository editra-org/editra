###############################################################################
# Name: testEdFile.py                                                         #
# Purpose: Unit tests for ed_txt.py                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittests for EdFile"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import types
import unittest

# Local imports
import common

# Module(s) to test
import ed_txt
import util

#-----------------------------------------------------------------------------#

class EdFileTest(unittest.TestCase):
    def setUp(self):
        self.app = common.EdApp(False)
        self.path = os.path.abspath('./data/test_read_utf8.txt')
        self.file = ed_txt.EdFile(self.path)
        self.mtime = util.GetFileModTime(self.path)

    def tearDown(self):
        self.file.Close()

    #---- Tests ----#
    def testRead(self):
        """Test reading from the file and getting the text"""
        txt = self.file.Read()
        self.assertTrue(len(txt))

    def testGetEncoding(self):
        """Test the encoding detection"""
        txt = self.file.Read()
        self.assertTrue(self.file.GetEncoding() == 'utf-8')

    def testGetExtension(self):
        """Test getting the file extension"""
        self.assertTrue(self.file.GetExtension() == 'txt')

    def testGetPath(self):
        """Test getting the files path"""
        self.assertTrue(self.file.GetPath() == self.path)

    def testGetModTime(self):
        """Test getting the files last modification time"""
        self.file.SetModTime(self.mtime)
        mtime = self.file.GetModtime()
        self.assertTrue(mtime == self.mtime, "Modtime was: " + str(mtime))

    def testHasBom(self):
        """Test checking if file has a bom marker or not"""
        self.assertFalse(self.file.HasBom(), "File has a BOM")

    def testIsReadOnly(self):
        """Test if the file is read only or not"""
        self.assertFalse(self.file.IsReadOnly(), "File is readonly")
        self.assertEqual(self.file.IsReadOnly(), self.file.ReadOnly)

    def testSetEncoding(self):
        """Test setting the file objects encoding"""
        self.file.SetEncoding('latin1')
        self.assertTrue(self.file.GetEncoding() == 'latin1')

    #---- Module utility function tests ----#

    def testDecodeString(self):
        """Test decoding a string to unicode."""
        test = "test string"
        self.assertTrue(isinstance(test, str), "Not a string")
        uni = ed_txt.DecodeString(test, 'utf-8')
        self.assertTrue(isinstance(uni, types.UnicodeType), "Failed decode")

