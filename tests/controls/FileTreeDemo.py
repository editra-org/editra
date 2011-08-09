###############################################################################
# Name: FileTreeDemo.py                                                       #
# Purpose: Test and demo file for eclib.FileTree                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the FileTree control

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import wx

import IconFile

# Put local package on the path
#sys.path.insert(0, os.path.abspath('../../src'))
import eclib

#-----------------------------------------------------------------------------#

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        super(TestPanel, self).__init__(parent)

        # Attributes
        self.ftree = eclib.FileTree(self)
        self.ftree.AddWatchDirectory(wx.GetUserHome())
        self.log = log

        # Layout
        self.__DoLayout()

    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ftree, 1, wx.EXPAND)
        self.SetSizer(sizer)

#-----------------------------------------------------------------------------#

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#----------------------------------------------------------------------

overview = eclib.FileTree.__doc__
title = "FileTree"

#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    try:
        import run
    except ImportError:
        app = wx.App(False)
        frame = wx.Frame(None, title="FileTree Demo")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.CreateStatusBar()
        frame.SetSizer(sizer)
        frame.SetInitialSize((300, 300))
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
