###############################################################################
# Name: ed_editv.py                                                           #
# Purpose: Editor view notebook tab implementation                            #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Text editor buffer view control for the main notebook

@summary: Editor view

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import wx
import os

# Editra Libraries
import ed_glob
import ed_stc
import ed_tab
from doctools import DocPositionMgr
from profiler import Profile_Get
from util import GetFileModTime, Log

#--------------------------------------------------------------------------#

_ = wx.GetTranslation

#--------------------------------------------------------------------------#

class EdEditorView(ed_stc.EditraStc, ed_tab.EdTabBase):
    """Tab editor view for main notebook control."""
    DOCMGR = DocPositionMgr()

    def __init__(self, parent, id_, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, use_dt=True):
        """Initialize the editor view"""
        ed_stc.EditraStc.__init__(self, parent, id_, pos, size, style, use_dt)
        ed_tab.EdTabBase.__init__(self, parent)

        # Initialize the classes position manager for the first control
        # that is created only.
        if not EdEditorView.DOCMGR.IsInitialized():
            EdEditorView.DOCMGR.InitPositionCache(ed_glob.CONFIG['CACHE_DIR'] + \
                                                  os.sep + u'positions')

    def DoOnIdle(self):
        """Check if the file has been modified and prompt a warning"""
        if Profile_Get('CHECKMOD'):
            cfile = self.GetFileName()
            lmod = GetFileModTime(cfile)
            if self.GetModTime() and not lmod and not os.path.exists(cfile):
                wx.CallAfter(self.PromptToReSave, cfile)
            elif self.GetModTime() < lmod:
                wx.CallAfter(self.AskToReload, cfile)
            else:
                pass

    def DoTabClosing(self):
        """Save the current position in the buffer to reset on next load"""
        if len(self.GetFileName()) > 1:
            EdEditorView.DOCMGR.AddRecord([self.GetFileName(),
                                           self.GetCurrentPos()])

    def DoTabOpen(self, ):
        """Called to open a new tab"""
        pass

    def DoTabSelected(self):
        """Performs updates that need to happen when this tab is selected"""
        Log("[ed_editv][info] Tab has file: %s" % self.GetFileName())
        self.PostPositionEvent()

    def GetName(self):
        """Gets the unique name for this tab control.
        @return: (unicode) string

        """
        return u"EditraTextCtrl"

    def GetTitleString(self):
        """Get the title string to display in the MainWindows title bar
        @return: (unicode) string

        """
        fname = self.GetFileName()
        title = os.path.split(fname)[-1]

        # Its an unsaved buffer
        if not len(title):
            title = _("Untitled - %d") % self.GetParent().pg_num
            fname = title

        if self.GetModify():
            title = u"*" + title
        return u"%s - file://%s" % (title, fname)

    def CanCloseTab(self):
        """Called when checking if tab can be closed or not
        @return: bool

        """
        result = True
        if self.GetModify():
            # TODO: Move this method down from the frame to here
            result = self.GetTopLevelParent().ModifySave()
            result = result in (wx.ID_OK, wx.ID_NO)

        return result

    def PromptToReSave(self, cfile):
        """Show a dialog prompting to resave the current file
        @param cfile: the file in question

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been deleted since its "
                                  "last save point.\n\nWould you "
                                  "like to save it again?") % cfile,
                                _("Resave File?"),
                                wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            result = self.SaveFile(cfile)
        else:
            self.SetModTime(0)

    def AskToReload(self, cfile):
        """Show a dialog asking if the file should be reloaded
        @param win: Window to prompt dialog on top of
        @param cfile: the file to prompt for a reload of

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been modified by another "
                                  "application.\n\nWould you like "
                                  "to Reload it?") % cfile,
                                  _("Reload File?"),
                                  wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            ret, rmsg = self.ReloadFile()
            if not ret:
                errmap = dict(filename=cfile, errmsg=rmsg)
                mdlg = wx.MessageDialog(self,
                                        _("Failed to reload %(filename)s:\n"
                                          "Error: %(errmsg)s") % errmap,
                                        _("Error"),
                                        wx.OK | wx.ICON_ERROR)
                mdlg.ShowModal()
                mdlg.Destroy()
        else:
            self.SetModTime(GetFileModTime(cfile))
