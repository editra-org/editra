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
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import eclib
import util

#--------------------------------------------------------------------------#

def FindMainWindow(window):
        """Find the MainWindow of the given window
        @return: MainWindow or None

        """
        def IsMainWin(win):
            """Check if the given window is a main window"""
            return getattr(win, '__name__', '') == 'MainWindow'

        if IsMainWin(window):
            return window
        # else start looking up the parent hierarchy
        tlw = window.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

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
        """Handle frame closure event"""
        wx.GetApp().UnRegisterWindow(repr(self))
        event.Skip()

#--------------------------------------------------------------------------#

class EdBaseCtrlBox(eclib.ControlBox):
    """ControlBox base class to be used by all common components"""
    def __init__(self, parent):
        super(EdBaseCtrlBox, self).__init__(parent)

    def AddPlateButton(self, lbl=u"", bmp=-1,
                       align=wx.ALIGN_LEFT, cbarpos=wx.TOP):
        """Add an eclib.PlateButton to the ControlBar specified by
        cbarpos.
        @keyword lbl: Button Label
        @keyword bmp: Bitmap or EditraArtProvider ID
        @keyword align: button alignment
        @keyword cbarpos: ControlBar position
        @return: PlateButton instance

        """
        ctrlbar = self.GetControlBar(cbarpos)
        assert ctrlbar is not None, "No ControlBar at cbarpos"
        if not isinstance(bmp, wx.Bitmap):
            assert isinstance(bmp, int)
            bmp = wx.ArtProvider.GetBitmap(str(bmp), wx.ART_MENU)
        if bmp.IsNull() or not bmp.IsOk():
            bmp = None
        btn = eclib.PlateButton(ctrlbar, wx.ID_ANY, lbl, bmp,
                                style=eclib.PB_STYLE_NOBG)
        ctrlbar.AddControl(btn, align)
        return btn

    def CreateControlBar(self, pos=wx.TOP):
        """Override for CreateControlBar to automatically set the
        flat non-gradient version of the control under GTK.

        """
        cbar = super(EdBaseCtrlBox, self).CreateControlBar(pos)
        if wx.Platform == '__WXGTK__':
            cbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)
        return cbar
