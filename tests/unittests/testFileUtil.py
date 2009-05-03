###############################################################################
# Name: testFileUtil.py                                                       #
# Purpose: Unit tests for the fileutil functions of ebmlib                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the fileutil functions"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx
import unittest

# Local modules
import common

# Module to test
import ebmlib

#-----------------------------------------------------------------------------#
# Test Class

class FileUtilTest(unittest.TestCase):
    """Tests for the fileutil functions of ebmlib"""
    def setUp(self):
        self.ddir = common.GetDataDir()
        self.tdir = common.GetTempDir()
        self.fpath = common.GetDataFilePath(u'test_read_utf8.txt')

    def tearDown(self):
        common.CleanTempDir()

    #---- Tests ----#
    def testGetFileModTime(self):
        """Test getting a files modtime"""
        mtime = ebmlib.GetFileModTime(self.fpath)
        self.assertNotEqual(mtime, 0, "Mtime was: " + str(mtime))

    def testGetFileSize(self):
        """Test getting a files size"""
        self.assertTrue(ebmlib.GetFileSize(self.fpath) != 0)
        self.assertTrue(ebmlib.GetFileSize(u'SomeFakeFile.txt') == 0)

    def testGetUniqueName(self):
        """Test getting a unique file name at a given path"""
        path = ebmlib.GetUniqueName(self.ddir, u'test_read_utf8.txt')
        self.assertTrue(path != self.fpath)

        # File that does not yet exist
        path = common.GetDataFilePath(u'newfile.txt')
        uname = ebmlib.GetUniqueName(self.ddir, u'newfile.txt')
        self.assertTrue(path == uname)

    def testMakeNewFile(self):
        """Test the MakeNewFile utility"""
        result = ebmlib.MakeNewFile(self.tdir, u'test_new_file.txt')
        self.assertTrue(result[0])
        self.assertTrue(os.path.exists(result[1]))
        
        result2 = ebmlib.MakeNewFile(self.tdir, u'test_new_file.txt')
        self.assertTrue(result2[1])
        self.assertTrue(result[1] != result2[1])

    def testMakeNewFolder(self):
        """Test the MakeNewFoloder utility"""
        result = ebmlib.MakeNewFolder(self.tdir, u'test_new_folder')
        self.assertTrue(result[0])
        self.assertTrue(os.path.exists(result[1]))
        
        result2 = ebmlib.MakeNewFolder(self.tdir, u'test_new_folder')
        self.assertTrue(result2[1])
        self.assertTrue(result[1] != result2[1])
