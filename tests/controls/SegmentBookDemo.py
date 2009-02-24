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

#-----------------------------------------------------------------------------#

class TestPanel(segmentbk.SegmentBook):
    def __init__(self, parent, log):
        segmentbk.SegmentBook.__init__(self, parent)

        # Attributes
        self.log = log
        self._imglst = wx.ImageList(16, 16)

        # Setup
        bmp = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MENU)
        self._imglst.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU)
        self._imglst.Add(bmp)
        self.SetImageList(self._imglst)

        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE), "Text Editor", img_id=0)
        self.AddPage(wx.GenericDirCtrl(self), "File Browser", img_id=1)
        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE), "Text Editor2", img_id=0)

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
