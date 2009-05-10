###############################################################################
# Name: common.py                                                             #
# Purpose: Common utilities for unittests.                                    #
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
import shutil
import wx

#-----------------------------------------------------------------------------#

class EdApp(wx.App):
    def GetLog(self):
        return lambda msg: None

#-----------------------------------------------------------------------------#

def CleanTempDir():
    """Clean all files from the temporary directory"""
    tdir = GetTempDir()
    for path in os.listdir(tdir):
        fpath = os.path.join(tdir, path)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)

def GetDataDir():
    """Get the path to the test data directory
    @return: string

    """
    path = os.path.join(u'.', u'data')
    return os.path.abspath(path)

def GetDataFilePath(fname):
    """Get the absolute path of the given data file
    @param fname: filename
    @return: string

    """
    path = os.path.join(u'.', u'data', fname)
    return os.path.abspath(path)

def GetTempDir():
    """Get the path to the test temp directory
    @return: string

    """
    path = os.path.join(u'.', u'temp')
    return os.path.abspath(path)

def MakeTempFile(fname):
    """Make a new file in the temp directory with a give name
    @param fname: file name
    @return: new file path

    """
    path = os.path.join(GetTempDir(), fname)
    if not os.path.exists(path):
        handle = open(path, "wb")
        handle.write(" ")
        handle.close()
    return path
