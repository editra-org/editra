###############################################################################
# Name: Cody Precord                                                          #
# Purpose: Log output viewer for the shelf                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""

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
import iface
import plugin

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
class LogViewer(outbuff.OutputBuffer):
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)

        # Attributes
        self._cache = dict()

        # Subscribe to Editra's Log
        ed_msg.Subscribe(self.UpdateLog, ed_msg.EDMSG_LOG_ALL) 

    def UpdateLog(self, msg):
        """Add a new log message
        @param msg: Message Object containing a LogMsg

        """
        if not self.IsRunning():
            if wx.Thread_IsMain():
                self.Start(150)

        self.AppendUpdate(str(msg.GetData()) + os.linesep)


#-----------------------------------------------------------------------------#
