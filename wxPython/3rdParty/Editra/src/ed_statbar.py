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
        self.SetFieldsCount(3) # Info, vi stuff, line/progress
        self.SetStatusWidths([-1, 90, 155])

        # Messages
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_PROGRESS_STATE)
#        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENING)
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENED)

    def __del__(self):
        """Unsubscribe from messages"""
        ed_msg.Unsubscribe(self.OnProgress)
        pstatbar.ProgressStatusBar.__del__(self)

    def OnProgress(self, msg):
        """Set the progress bar's state
        @param msg: 

        """
        # Don't do anything if the parent window is not active
        if not self.GetParent().IsActive():
            return

        mtype = msg.GetType()
        mdata = msg.GetData()
        if mtype == ed_msg.EDMSG_PROGRESS_STATE:
            # May be called from non gui thread so don't do anything with
            # the gui here.
            self.progress = mdata[0]
        elif mtype == ed_msg.EDMSG_FILE_OPENED:
            self.StopBusy()
        elif mtype == ed_msg.EDMSG_FILE_OPENING:
            # Clear any text from the progress field
            self.SetStatusText('', ed_glob.SB_ROWCOL)
            # Data is the file path
            self.SetRange(util.GetFileSize(mdata))

