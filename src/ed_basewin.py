###############################################################################
# Name: ed_basewin.py                                                         #
# Purpose: Common window base class(es)                                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This module provides base classes for windows and dialogs to be used within
Editra.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import eclib
import util

#--------------------------------------------------------------------------#

class EdBaseDialog(eclib.ECBaseDlg):
    """Editra Dialog Base Class"""
    def __init__(self, parent, id=wx.ID_ANY, title=u"",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.DEFAULT_DIALOG_STYLE, name=u"EdBaseDialog"):
        super(EdBaseDialog, self).__init__(parent, id, title, pos,
                                           size, style, name)

#--------------------------------------------------------------------------#

class EdBaseFrame(wx.Frame):
    """Editra Frame Base Class"""
    def __init__(self, parent, id=wx.ID_ANY, title=u"",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE, name=u"EdBaseFrame"):
        super(EdBaseFrame, self).__init__(parent, id, title, pos,
                                          size, style, name)

        # Setup
        util.SetWindowIcon(self)

        # Register with App
        wx.GetApp().RegisterWindow(repr(self), self)

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        wx.GetApp().UnRegisterWindow(repr(self))
        event.Skip()

#--------------------------------------------------------------------------#

class EdBaseCtrlBox(eclib.ControlBox):
    def __init__(self, parent):
        super(EdBaseCtrlBox, self).__init__(parent)
    def CreateControlBar(self, pos=wx.TOP):
        """Override for CreateControlBar to automatically set the
        flat non-gradient version of the control under GTK.

        """
        cbar = super(EdBaseCtrlBox, self).CreateControlBar(pos)
        if wx.Platform == '__WXGTK__':
            cbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)
        return cbar
