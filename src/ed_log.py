###############################################################################
# Name: Cody Precord                                                          #
# Purpose: Log output viewer for the shelf                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra LogViewer

This module provides classes for managing the log display and filtering of its
messages. The module also exports an implementation of a shelf plugin for
displaying a LogViewer in the Shelf.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
import ed_msg
import eclib.outbuff as outbuff
import eclib.ctrlbox as ctrlbox
import eclib.platebtn as platebtn
import iface
import plugin
import ed_glob

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

# Interface Implementation
class EdLogViewer(plugin.Plugin):
    """Shelf interface implementation for the log viewer"""
    plugin.Implements(iface.ShelfI)
    ID_LOGGER = wx.NewId()
    __name__ = u'Editra Log'

    def AllowMultiple(self):
        """EdLogger allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a log viewr panel"""
        return LogViewer(parent)

    def GetId(self):
        """Plugin menu identifier ID"""
        return self.ID_LOGGER

    def GetMenuEntry(self, menu):
        """Get the menu entry for the log viewer
        @param menu: the menu items parent menu

        """
        return wx.MenuItem(menu, self.ID_LOGGER, _(self.__name__), 
                           _("View Editra's console log"))

    def GetName(self):
        """Return the name of this control"""
        return self.__name__

    def IsStockable(self):
        """EdLogViewer can be saved in the shelf preference stack"""
        return True

#-----------------------------------------------------------------------------#

# LogViewer Ui Implementation
class LogViewer(ctrlbox.ControlBox):
    """LogViewer is a control for displaying and working with output
    from Editra's log.
    """

    def __init__(self, parent):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self._buffer = LogBuffer(self)
        self.SetWindow(self._buffer)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def __DoLayout(self):
        """Layout the log viewer window"""
        # Setup ControlBar
        ctrlbar = ctrlbox.ControlBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(ctrlbox.CTRLBAR_STYLE_DEFAULT)

        ctrlbar.AddStretchSpacer()
        cbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
        if cbmp.IsNull() or not cbmp.IsOk():
            cbmp = None
        clear = platebtn.PlateButton(ctrlbar, wx.ID_CLEAR, _("Clear"),
                                     cbmp, style=platebtn.PB_STYLE_NOBG)
        ctrlbar.AddControl(clear, wx.ALIGN_RIGHT)
        ctrlbar.SetVMargin(1, 1)
        self.SetControlBar(ctrlbar)
        
    def OnButton(self, evt):
        """Handle button events from the controlbar"""
        e_id = evt.GetId()
        if e_id == wx.ID_CLEAR:
            self._buffer.Clear()
        else:
            evt.Skip()

class LogBuffer(outbuff.OutputBuffer):
    """Buffer for displaying log messages that are sent on Editra's
    log channel.

    """
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)

        # Attributes
        self._cache = dict()

        # Subscribe to Editra's Log
        ed_msg.Subscribe(self.UpdateLog, ed_msg.EDMSG_LOG_ALL) 

    def __del__(self):
        """Unregister from recieving any more log messages"""
        ed_msg.Unsubscribe(self.UpdateLog, ed_msg.EDMSG_LOG_ALL)
        super(LogBuffer, self).__del__()

    def UpdateLog(self, msg):
        """Add a new log message
        @param msg: Message Object containing a LogMsg

        """
        if not self.IsRunning():
            if wx.Thread_IsMain():
                self.Start(150)

        self.AppendUpdate(str(msg.GetData()) + os.linesep)

#-----------------------------------------------------------------------------#

class LogFilterCache(dict):
    """Data storage class for filtering and organizing log messages"""
    def __init__(self):
        """Create a new log cache"""
        dict.__init__(self)

    def Clear(self, subkey=None):
        """Clear the log cache, if subkey is specified only clear
        the subset of the cache pertaining to that
        @keyword subkey: Toplevel cache filter to clear

        """
        