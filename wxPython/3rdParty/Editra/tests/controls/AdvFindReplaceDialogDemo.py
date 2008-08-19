###############################################################################
# Name: AdvFindReplaceDialogDemo.py                                           #
# Purpose: Advanced Find Replace Dialog Test and Demo File                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the Advanced Find Replace Dialog

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
import src.eclib.finddlg as finddlg

#-----------------------------------------------------------------------------#
ID_DEFAULT = wx.NewId()
ID_DIALOG  = wx.NewId()
ID_REPLACE = wx.NewId()
ID_NOOPTS  = wx.NewId()
ID_REGEX   = wx.NewId()
ID_NOLOOK  = wx.NewId()
ID_MINIMAL = wx.NewId()

#-----------------------------------------------------------------------------#
# There are a large number of possible flag/style combinations here are just a
# few examples for creating different versions of the dialog.
DIALOG_MAP = {ID_DEFAULT : (wx.FindReplaceData(), finddlg.AFR_STYLE_FINDDIALOG),
              ID_DIALOG  : (wx.FindReplaceData(), finddlg.AFR_STYLE_NON_FLOATING),
              ID_REPLACE : (wx.FindReplaceData(), finddlg.AFR_STYLE_REPLACEDIALOG),
              ID_NOOPTS  : (wx.FindReplaceData(finddlg.AFR_NOOPTIONS),
                           finddlg.AFR_STYLE_FINDDIALOG),
              ID_REGEX   : (wx.FindReplaceData(finddlg.AFR_REGEX),
                            finddlg.AFR_STYLE_FINDDIALOG),
              ID_NOLOOK  : (wx.FindReplaceData(finddlg.AFR_NOLOOKIN),
                            finddlg.AFR_STYLE_FINDDIALOG),
              ID_MINIMAL : (wx.FindReplaceData(finddlg.AFR_NOLOOKIN|finddlg.AFR_NOOPTIONS|finddlg.AFR_NOUPDOWN),
                            finddlg.AFR_STYLE_FINDDIALOG)}

BUTTONS = zip(DIALOG_MAP.keys(),
              ("Default", "Non-Floating", "Replace Dialog", "Options Hidden",
               "Regular Expression", "Lookin Hidden", "Minimal"))

#-----------------------------------------------------------------------------#

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent)

        # Attributes
        self.log = log

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(finddlg.EVT_FIND, self.OnFind)
        self.Bind(finddlg.EVT_FIND_ALL, self.OnFind)
        self.Bind(finddlg.EVT_FIND_NEXT, self.OnFind)
        self.Bind(finddlg.EVT_REPLACE, self.OnFind)
        self.Bind(finddlg.EVT_REPLACE_ALL, self.OnFind)

    def __DoLayout(self):
        """Layout the panel"""
        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add((10, 10), 0)
        for bid, lbl in BUTTONS:
            btn = wx.Button(self, bid, lbl)
            fsizer.Add(btn, 0)
            fsizer.Add((5, 5), 0)
        self.SetSizer(fsizer)
        self.SetAutoLayout(True)

    def OnButton(self, evt):
        """Show a dialog"""
        e_id = evt.GetId()
        if e_id in DIALOG_MAP:
            data, style = DIALOG_MAP.get(e_id)
            dlg = finddlg.AdvFindReplaceDlg(self, data, "Find/Replace Dialog", style)
            dlg.Show()
        else:
            evt.Skip()

    def OnFind(self, evt):
        self.log.write("Search String: %s" % evt.GetFindString())
        self.log.write("Replace String: %s" % evt.GetReplaceString())
        self.log.write("Location: %s" % evt.GetDirectory())
        self.log.write("Search Type: %d" % evt.GetSearchType())
        self.log.write("Whole Word: %d" % evt.IsWholeWord())
        self.log.write("Match Case: %d" % evt.IsMatchCase())
        self.log.write("Regular Expression: %d" % evt.IsRegEx())
        self.log.write("Search Up: %d" % evt.IsUp())
        self.log.write("EvtType: %d" % evt.GetEventType())

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
        frame = wx.Frame(None, title="Advanced Find Dialog Test")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.CreateStatusBar()
        frame.SetSizer(sizer)
        frame.SetInitialSize(wx.Size(300, 300))
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
