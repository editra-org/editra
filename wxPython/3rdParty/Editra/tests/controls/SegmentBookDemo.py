###############################################################################
# Name: SegmentBookDemo.py                                                    #
# Purpose: SegmentBook control demo and test file                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the SegmentBook control.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import sys
import os
import wx

sys.path.insert(0, os.path.abspath('../../'))
import src.eclib.segmentbk as segmentbk

# Local imports
import IconFile

#-----------------------------------------------------------------------------#

class TestPanel(segmentbk.SegmentBook):
    def __init__(self, parent, log):
        segmentbk.SegmentBook.__init__(self, parent)

        # Attributes
        self.log = log
        self._imglst = wx.ImageList(32, 32)

        # Setup
        bmp = IconFile.Monkey.GetBitmap()
        self._imglst.Add(bmp)
        bmp = IconFile.Devil.GetBitmap()
        self._imglst.Add(bmp)
        self.SetImageList(self._imglst)

        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Hello"),
                     "Text Editor", img_id=0)
        self.AddPage(wx.GenericDirCtrl(self), "File Browser", img_id=1)
        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Test Control"),
                     "Text Editor2", img_id=0)
        todo = wx.ListBox(self, choices=['Wake up',
                                         'Finish Event handling',
                                         'Take a nap',
                                         'Procrastinate for a while',
                                         'Drink some coffee',
                                         'Check in code'])
        self.AddPage(todo, "TODO List", img_id=1)

#-----------------------------------------------------------------------------#

def MakeTestFrame(segment=False):
    frame = wx.Frame(None, title="SegmentBook Test")
    fsizer = wx.BoxSizer(wx.VERTICAL)
    panel = TestPanel(frame, TestLog())
    fsizer.Add(panel, 1, wx.EXPAND)
    return frame

#-----------------------------------------------------------------------------#

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    try:
        import sys
        import run
    except ImportError:
        app = wx.PySimpleApp(False)
        frame = MakeTestFrame()
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
