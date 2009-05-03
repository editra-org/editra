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
import wx

#-----------------------------------------------------------------------------#

class EdApp(wx.App):
    def GetLog(self):
        return lambda msg: None

#-----------------------------------------------------------------------------#

def GetDataFilePath(fname):
    """Get the absolute path of the given data file
    @param fname: filename
    @return: string

    """
    path = os.path.join(u'.', u'data', fname)
    return os.path.abspath(path)
