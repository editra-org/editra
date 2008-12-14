###############################################################################
# Name: txtentry.py                                                           #
# Purpose: Text entry control base clases                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: TextEntry

Text entry base and helper classes.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx

#-----------------------------------------------------------------------------#

class CommandEntryBase(wx.SearchCtrl):
    """Base single line text control with key event handling callbacks."""
    def __init__(self, parent, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name="CommandEntryBase"):
        wx.SearchCtrl.__init__(self, parent, id, value, pos,
                               size, style, validator, name)

        # Attributes
        

        # Hide the search button and text by default
        self.ShowSearchButton(False)
        self.ShowCancelButton(False)
        self.SetDescriptiveText(wx.EmptyString)

        # MSW/GTK HACK need to bind directly to the text control component
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.SetValidator(validator)
                    child.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
                    child.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
                    break
        else:
            self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        # Event management
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

    def OnKeyDown(self, evt):
        """Handle KeyDown events"""
        evt.Skip()

    def OnKeyUp(self, evt):
        """Handle KeyUp events"""
        evt.Skip()

    def OnEnter(self, evt):
        """Handle the Enter key event"""
        evt.Skip()

