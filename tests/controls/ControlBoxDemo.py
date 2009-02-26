###############################################################################
# Name: ControlBoxDemo.py                                                     #
# Purpose: ControlBox and ControlBar Test and Demo File                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the ControlBox, ControlBar, and SegmentBar classes

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import time
import sys
import os
import wx

sys.path.insert(0, os.path.abspath('../../'))
import src.eclib.ctrlbox as ctrlbox

# Local imports
import IconFile

#-----------------------------------------------------------------------------#
# Globals
ID_SHOW_CONTROL = wx.NewId()
ID_SHOW_SEGMENT = wx.NewId()

#-----------------------------------------------------------------------------#

class TestPanel(ctrlbox.ControlBox):
    def __init__(self, parent, log):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.log = log

        # Setup
        self.CreateControlBar()
        cbar = self.GetControlBar()
        cbar.SetVMargin(2, 2)
        cbar.AddControl(wx.Button(cbar, ID_SHOW_CONTROL, label="Show ControlBar Sample"))
        cbar.AddControl(wx.Button(cbar, ID_SHOW_SEGMENT, label="Show SegmentBar Sample"))
        text = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_RICH2)
        text.SetValue("Welcome to the ControlBox Sample.\n\nThis window is a"
                      "ControlBox with a ControlBar in it.\n\n"
                      "Click a button to see the extended samples.")
        self.SetWindow(text)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def OnButton(self, evt):
        """Handle Button Events"""
        e_id = evt.GetId()
        if e_id == ID_SHOW_CONTROL:
            # Show a Frame with a ControlBox using ControlBars in it
            frame = MakeTestFrame(self, "ControlBar Sample", self.log, False)
            frame.Show()
        elif e_id == ID_SHOW_SEGMENT:
            # Show a frame with a ControlBox using SegmentBars in it
            frame = MakeTestFrame(self, "SegmentBar Sample", self.log, True)
            frame.Show()
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class ControlBarPanel(ctrlbox.ControlBox):
    def __init__(self, parent, log):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.log = log

        # Setup
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
        bbar.SetVMargin(1, 1)
        bbar.AddTool(wx.ID_ANY, err_bmp, "HELLO")

        self.SetWindow(wx.TextCtrl(self, style=wx.TE_MULTILINE))
        self.Bind(ctrlbox.EVT_CTRLBAR, self.OnControlBar)
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def OnControlBar(self, evt):
        self.log.write("ControlBarEvent: %d" % evt.GetId())

    def OnButton(self, evt):
        self.log.write("Button tool clicked: Id=%d" % evt.GetId())
        frame = MakeTestFrame(self, "Random Test Frame", self.log,
                              bool(long(time.time()) % 2))
        frame.Show()

#-----------------------------------------------------------------------------#

class SegmentPanel(ctrlbox.ControlBox):
    def __init__(self, parent, log):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.log = log

        # Make up the top segment bar
        segbar = ctrlbox.SegmentBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT|\
                                                ctrlbox.CTRLBAR_STYLE_LABELS|\
                                                ctrlbox.CTRLBAR_STYLE_NO_DIVIDERS)
        for num in range(5):
            if num % 2:
                segbar.AddSegment(wx.NewId(), IconFile.Home.GetBitmap(), label=u'Home')
            else:
                segbar.AddSegment(wx.NewId(), IconFile.Monkey.GetBitmap(), label=u'Monkey')

        # Make a bottom segment bar
        segbar2 = ctrlbox.SegmentBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        for num in range(5):
            if num % 2:
                segbar2.AddSegment(wx.NewId(), IconFile.Book.GetBitmap())
            else:
                segbar2.AddSegment(wx.NewId(), IconFile.Address.GetBitmap())

        # Put the components together
        self.SetControlBar(segbar, wx.TOP)
        self.SetControlBar(segbar2, wx.BOTTOM)
        self.SetWindow(wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Hello World"))

        # Event Handlers
        self.Bind(ctrlbox.EVT_SEGMENT_SELECTED, self.OnSegmentClicked)

    def OnSegmentClicked(self, evt):
        cur = evt.GetCurrentSelection()
        pre = evt.GetPreviousSelection()
        self.log.write("Segment Clicked: Cur=%d, Pre=%d, Id=%d" % (cur, pre, evt.GetId()))

#-----------------------------------------------------------------------------#

def MakeTestFrame(caller, title, log, segment=False):
    frame = wx.Frame(None, title=title)
    fsizer = wx.BoxSizer(wx.VERTICAL)
    if not segment:
        panel = ControlBarPanel(frame, log)
    else:
        panel = SegmentPanel(frame, log)
    fsizer.Add(panel, 1, wx.EXPAND)
    frame.SetSizer(fsizer)

    # Adjust Window Postion
    if caller is not None:
        pos = caller.GetScreenPosition()
        frame.SetPosition((pos[0]+22, pos[1]+22))

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
        frame = wx.Frame(None, title="ControlBox Test")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.SetSizer(sizer)
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
