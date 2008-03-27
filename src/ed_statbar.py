###############################################################################
# Name: ed_statbar.py                                                         #
# Purpose: Custom statusbar with builtin progress indicator                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: ed_statbar.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
Custom StatusBar for Editra that contains a progress bar that responds to
messages from ed_msg to display progress of different actions.

@summary: Editra's StatusBar class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx

# Editra Libraries
import ed_glob
import ed_msg
import util
import eclib.pstatbar as pstatbar

#--------------------------------------------------------------------------#
# Globals

#--------------------------------------------------------------------------#

class EdStatBar(pstatbar.ProgressStatusBar):
    def __init__(self, parent):
        pstatbar.ProgressStatusBar.__init__(self, parent, style=wx.ST_SIZEGRIP)

        # Setup
        self._pid = parent.GetId() # Save parents id for filtering msgs
        self.SetFieldsCount(3) # Info, vi stuff, line/progress
        self.SetStatusWidths([-1, 90, 155])

        # Messages
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_PROGRESS_SHOW)
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_PROGRESS_STATE)
#        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENING)
#        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENED)

    def __del__(self):
        """Unsubscribe from messages"""
        ed_msg.Unsubscribe(self.OnProgress)
        pstatbar.ProgressStatusBar.__del__(self)

    def OnProgress(self, msg):
        """Set the progress bar's state
        @param msg: Message Object

        """
        mdata = msg.GetData()
        # Don't do anything if the message is not for this frame
        if self._pid != mdata[0]:
            return

        mtype = msg.GetType()
        if mtype == ed_msg.EDMSG_PROGRESS_STATE:
            # May be called from non gui thread so don't do anything with
            # the gui here.
            self.SetProgress(mdata[1])
            self.range = mdata[2]
            if sum(mdata[1:]) == 0:
                self.Stop()
        elif mtype == ed_msg.EDMSG_PROGRESS_SHOW:
            if mdata[1]:
                self.Start(75)
            else:
                self.Stop()
        elif mtype == ed_msg.EDMSG_FILE_OPENED:
            self.StopBusy()
        elif mtype == ed_msg.EDMSG_FILE_OPENING:
            # Clear any text from the progress field
            self.SetStatusText('', ed_glob.SB_ROWCOL)
            # Data is the file path
            self.SetRange(util.GetFileSize(mdata))
            self.Start(75)
