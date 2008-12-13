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

def MakeTestFrame(log):
    frame = wx.Frame(None, title="Test ControlBox")
    fsizer = wx.BoxSizer(wx.VERTICAL)
    cbox = TestPanel(frame, log)
    fsizer.Add(cbox, 1, wx.EXPAND)
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
        frame = MakeTestFrame(TestLog())
        frame.CenterOnParent()
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
