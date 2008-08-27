###############################################################################
# Name: ed_statbar.py                                                         #
# Purpose: Custom statusbar with builtin progress indicator                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Custom StatusBar for Editra that contains a progress bar that responds to
messages from ed_msg to display progress of different actions.

@summary: Editra's StatusBar class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import util
import ed_msg
import ed_cmdbar
from syntax.syntax import GetFtypeDisplayName
import eclib.pstatbar as pstatbar

#--------------------------------------------------------------------------#
# Globals

#--------------------------------------------------------------------------#

class EdStatBar(pstatbar.ProgressStatusBar):
    def __init__(self, parent):
        pstatbar.ProgressStatusBar.__init__(self, parent, style=wx.ST_SIZEGRIP)

        # Setup
        self._pid = parent.GetId() # Save parents id for filtering msgs
        self._widths = list()
        self.SetFieldsCount(6) # Info, vi stuff, line/progress
        self.SetStatusWidths([-1, 90, 40, 40, 40, 155])

        # Event Handlers
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)

        # Messages
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_PROGRESS_SHOW)
        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_PROGRESS_STATE)
        ed_msg.Subscribe(self.OnUpdateText, ed_msg.EDMSG_UI_SB_TXT)
        ed_msg.Subscribe(self.OnUpdateDoc, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnUpdateDoc, ed_msg.EDMSG_FILE_SAVED)
        ed_msg.Subscribe(self.OnUpdateDoc, ed_msg.EDMSG_UI_STC_LEXER)
#        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENING)
#        ed_msg.Subscribe(self.OnProgress, ed_msg.EDMSG_FILE_OPENED)

    def __del__(self):
        """Unsubscribe from messages"""
        ed_msg.Unsubscribe(self.OnProgress)
        ed_msg.Unsubscribe(self.OnUpdateText)
        ed_msg.Unsubscribe(self.OnUpdateDoc)
        pstatbar.ProgressStatusBar.__del__(self)

    def AdjustFieldWidths(self):
        """Adust each field width of status bar basing on the field text
        @return: None

        """
        widths = []
        # Calculate required widths
        # NOTE: Order of fields is important
        for field in [ed_glob.SB_BUFF,
                      ed_glob.SB_LEXER,
                      ed_glob.SB_READONLY,
                      ed_glob.SB_ENCODING,
                      ed_glob.SB_ROWCOL]:
            width = self.GetTextExtent(self.GetStatusText(field))[0]
            widths.append(width)

        # Adjust widths
        widths = [width + 20 for width in widths]
        widths.insert(0, -1)
        for idx, width in enumerate(list(widths)):
            if width == 20:
                widths[idx] = 0

        if widths[-1] < 155:
            widths[-1] = 155

        if widths != self._widths:
            self._widths = widths
            self.SetStatusWidths(self._widths)

    def OnLeftDClick(self, evt):
        """Handlers mouse left double click on status bar
        @param evt: Event fired that called this handler
        @type evt: 
        @note: Assumes parent is MainWindow instance

        """
        pt = evt.GetPosition()
        if self.GetFieldRect(ed_glob.SB_ROWCOL).Contains(pt):
            self.GetParent().ShowCommandCtrl(ed_cmdbar.ID_LINE_CTRL)
        else:
            evt.Skip()

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

    def OnUpdateDoc(self, msg):
        """Update document related fields
        @param msg: Message Object

        """
        self.UpdateFields()

    def OnUpdateText(self, msg):
        """Update the status bar text based on the recieved message
        @param msg: Message Object

        """
        # Only process if this status bar is in the active window and shown
        if self.GetTopLevelParent().IsActive() and self.IsShown():
            field, txt = msg.GetData()
            self.UpdateFields()
            self.SetStatusText(txt, field)

    def PushStatusText(self, txt, field):
        """Set the status text
        @param txt: Text to put in bar
        @param field: int

        """
        pstatbar.ProgressStatusBar.PushStatusText(self, txt, field)
        self.AdjustFieldWidths()

    def SetStatusText(self, txt, field):
        """Set the status text
        @param txt: Text to put in bar
        @param field: int

        """
        pstatbar.ProgressStatusBar.SetStatusText(self, txt, field)
        self.AdjustFieldWidths()


    def UpdateFields(self):
        """Update document fields based on the currently selected
        document in the editor.
        @postcondition: encoding and lexer fields are updated
        @todo: update when readonly hooks are implemented

        """
        nb = self.GetParent().GetNotebook()
        if nb is None:
            return

        cbuff = nb.GetCurrentCtrl()
        doc = cbuff.GetDocument()
        pstatbar.ProgressStatusBar.SetStatusText(self, doc.GetEncoding(),
                                                 ed_glob.SB_ENCODING)
        pstatbar.ProgressStatusBar.SetStatusText(self,
                                                 GetFtypeDisplayName(cbuff.GetLangId()),
                                                 ed_glob.SB_LEXER)
#        pstatbar.ProgressStatusBar.SetStatusText(self,
#                                                 ,
#                                                 ed_glob.SB_READONLY)

        self.AdjustFieldWidths()

