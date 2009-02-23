###############################################################################
# Name: ControlBoxDemo.py                                                     #
# Purpose: ControlBox and ControlBar Test and Demo File                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the ControlBox and ControlBar

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
import src.eclib.ctrlbox as ctrlbox

#-----------------------------------------------------------------------------#

class TestPanel(ctrlbox.ControlBox):
    def __init__(self, parent, log):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.log = log

        # Setup
        tmpbar = ctrlbox.SegmentBar(self)
        self.CreateControlBar()

        cbar = self.GetControlBar()
        err_bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU, (16, 16))
        w_bmp = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MENU, (16, 16))
        cbar.AddTool(wx.ID_ANY, err_bmp, "hello world")
        cbar.AddTool(wx.ID_ANY, w_bmp, "warning")
        cbar.AddStretchSpacer()
        choice = wx.Choice(cbar, wx.ID_ANY, choices=[str(x) for x in range(10)])
        cbar.AddControl(choice, wx.ALIGN_RIGHT)
        cbar.AddControl(wx.Button(cbar, label="New Frame"), wx.ALIGN_RIGHT)

        self.CreateControlBar(wx.BOTTOM)
        bbar = self.GetControlBar(wx.BOTTOM)
        bbar.AddTool(wx.ID_ANY, err_bmp, "HELLO")

        self.SetWindow(wx.TextCtrl(self, style=wx.TE_MULTILINE))
        self.Bind(ctrlbox.EVT_CTRLBAR, self.OnControlBar)
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def OnControlBar(self, evt):
        self.log.write("ControlBarEvent: %d" % evt.GetId())

    def OnButton(self, evt):
        self.log.write("Button tool clicked")
        frame = MakeTestFrame(self.log)
        frame.Show()

#-----------------------------------------------------------------------------#

class SegmentPanel(ctrlbox.ControlBox):
    def __init__(self, parent, log):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.log = log

        # Setup
        segbar = ctrlbox.SegmentBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT|ctrlbox.CTRLBAR_STYLE_LABELS)
        err_bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU, (16, 16))

        for num in range(5):
            segbar.AddSegment(wx.NewId(), err_bmp, label=u'TestLabel')

        segbar2 = ctrlbox.SegmentBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)

        for num in range(5):
            segbar2.AddSegment(wx.NewId(), err_bmp, label=u'Test')

        self.SetControlBar(segbar, wx.TOP)
        self.SetControlBar(segbar2, wx.BOTTOM)

        self.SetWindow(wx.TextCtrl(self, style=wx.TE_MULTILINE))

        # Event Handlers
        self.Bind(ctrlbox.EVT_SEGMENT_SELECTED, self.OnSegmentClicked)

    def OnSegmentClicked(self, evt):
        cur = evt.GetCurrentSelection()
        pre = evt.GetPreviousSelection()
        self.log.write("Segment Clicked: Cur=%d, Pre=%d, Id=%d" % (cur, pre, evt.GetId()))

#-----------------------------------------------------------------------------#

def MakeTestFrame(segment=False):
    frame = wx.Frame(None, title="Test ControlBox")
    fsizer = wx.BoxSizer(wx.VERTICAL)
    if not segment:
        panel = TestPanel(frame, TestLog())
    else:
        panel = SegmentPanel(frame, TestLog())
        frame.CenterOnParent()
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
        frame = MakeTestFrame(segment=False)
        frame.Show()
        frame2 = MakeTestFrame(segment=True)
        frame2.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
