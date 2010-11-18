###############################################################################
# Name: Cody Precord                                                          #
# Purpose:                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Bookmark manager

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import os
import re
import wx

# Editra Libraries
import ed_msg
import iface
import plugin
from profiler import Profile_Get, Profile_Set
import ed_glob
import util
import eclib
import ebmlib

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

# Interface Implementation
class EdBookmarks(plugin.Plugin):
    """Shelf interface implementation for the bookmark manager"""
    plugin.Implements(iface.ShelfI)

    __name__ = u'Bookmarks'

    @staticmethod
    def AllowMultiple():
        """EdBookmark only allows one instance"""
        return False

    @staticmethod
    def CreateItem(parent):
        """Returns a bookmark panel"""
        return BookmarkWindow(parent)

    def GetBitmap(self):
        """Get the log viewers tab icon
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_ADD_BM), wx.ART_MENU)
        return bmp

    @staticmethod
    def GetId():
        """Plugin menu identifier ID"""
        return ed_glob.ID_BOOKMARK_MGR

    @staticmethod
    def GetMenuEntry(menu):
        """Get the menu entry for the bookmark viewer
        @param menu: the menu items parent menu

        """
        item = wx.MenuItem(menu, ed_glob.ID_BOOKMARK_MGR,
                           _("Bookmarks"),
                           _("View all bookmarks"))
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_ADD_BM), wx.ART_MENU)
        item.SetBitmap(bmp)
        return item

    def GetName(self):
        """Return the name of this control"""
        return self.__name__

    @staticmethod
    def IsStockable():
        """EdBookmark can be saved in the shelf preference stack"""
        return True

    # Bookmark storage
    _handles = list()
    _marks = list()
    @classmethod
    def OnStoreBM(cls, msg):
        data = msg.GetData()
        buf = data.get('stc')
        line = data.get('line')
        value = (buf.GetFileName(), line)
        if data.get('added', False):
            if value not in cls._marks:
                cls._marks.append(value)
                cls._handles.append(data.get('handle'))
        else:
            if value in cls._marks:
                idx = cls._marks.index(value)
                cls._marks.pop(idx)
                cls._handles.pop(idx)

    @classmethod
    def GetHandles(cls):
        """Get the handles associated with the"""
        return cls._handles

    @classmethod
    def GetMarks(cls):
        return cls._marks

ed_msg.Subscribe(EdBookmarks.OnStoreBM, ed_msg.EDMSG_UI_STC_BOOKMARK)

#-----------------------------------------------------------------------------#

class BookmarkWindow(eclib.ControlBox):
    """Shelf window for managing bookmarks"""
    def __init__(self, parent):
        super(BookmarkWindow, self).__init__(parent)

        # Attributes
        self._list = BookmarkList(self)

        #Setup
        self.SetWindow(self._list)
        ctrlbar = eclib.ControlBar(self, style=eclib.CTRLBAR_STYLE_GRADIENT)
        ctrlbar.SetVMargin(2, 2)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)
        self.SetControlBar(ctrlbar)

        # Populate the listctrl with anything already in the cache
        marks = EdBookmarks.GetMarks()
        for fname, linenum in marks:
            self._list.AddBookmark(fname, unicode(linenum+1))

        # Message Handlers
        ed_msg.Subscribe(self.OnBookmark, ed_msg.EDMSG_UI_STC_BOOKMARK)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate, self._list)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnBookmark)

    def OnBookmark(self, msg):
        """Bookmark added or removed callback"""
        data = msg.GetData()
        line = data.get('line', -1)
        buf = data.get('stc', None)
        # Try to add a helpful alias for the bookmark automatically
        cline = buf.GetCurrentLine()
        name = u""
        if line == cline:
            name = buf.GetSelectedText()
        if not name:
            name = buf.GetLine(line)
        wx.CallAfter(self.DoUpdateListCtrl,
                     buf.GetFileName(),
                     unicode(line+1),
                     data.get('added', False),
                     markname=name.strip())

    def DoUpdateListCtrl(self, fname, lnum, added, markname=None):
        """Update the listctrl for changes in the cache
        @param value: tuple(fname, linenum)
        @param added: bool (add or remove)
        @keyword markname: custom bookmark name

        """
        if added:
            self._list.AddBookmark(fname, lnum, markname)
        else:
            self._list.DeleteBookmark(fname, lnum)

    def OnItemActivate(self, evt):
        """Handle double clicks on items to navigate to the
        selected bookmark.

        """
        index = evt.m_itemIndex
        handles = EdBookmarks.GetHandles()
        marks = EdBookmarks.GetMarks()
        if index < len(handles):
            mark = marks[index]
            handle = handles[index]
            self.GotoBookmark(mark[0], int(mark[1]), handle)

    def GotoBookmark(self, fname, lnum, handle):
        """Goto the bookmark in the editor
        @param fname: file name
        @param handle: stc bookmark handle

        """
        app = wx.GetApp()
        mw = app.GetActiveWindow()
        if mw:
            nb = mw.GetNotebook()
            buf = nb.FindBuffer(fname)
            use_handle = True
            if not buf:
                nb.OpenPage(ebmlib.GetPathName(fname),
                            ebmlib.GetFileName(fname))
                buf = nb.GetCurrentPage()
                use_handle = False # Handle is invalid so use line number

            if buf:
                # Ensure the tab is the current one
                nb.GotoPage(fname)
                # Jump to the bookmark line
                if use_handle:
                    lnum = buf.MarkerLineFromHandle(handle)
                buf.GotoLine(lnum)
        else:
            util.Log("[ed_bookmark][err] Failed to locate mainwindow")

#-----------------------------------------------------------------------------#

class BookmarkList(eclib.EBaseListCtrl):
    """ListCtrl for displaying the bookmarks in"""
    BOOKMARK = 0
    FILE_NAME = 1
    LINE_NUM = 2
    def __init__(self, parent):
        super(BookmarkList, self).__init__(parent,
                                           style=wx.LC_REPORT|\
                                                 wx.LC_EDIT_LABELS|\
                                                 wx.LC_SINGLE_SEL)

        # Attributes
        
        # Setup
        self.InsertColumn(BookmarkList.BOOKMARK, _("Bookmark"))
        self.InsertColumn(BookmarkList.FILE_NAME, _("File Location"))
        self.InsertColumn(BookmarkList.LINE_NUM, _("Line Number"))
        self.setResizeColumn(BookmarkList.FILE_NAME+1) #NOTE: +1 bug in mixin

    def AddBookmark(self, fname, lnum, markname=None):
        """Add a bookmark to the list
        @param fname: file name
        @param lnum: line number (unicode)
        @keyword markname: custom bookmark alias

        """
        if not markname:
            markname = _("Bookmark%d") % self.GetItemCount()
        self.Append((markname, fname, lnum))

    def DeleteBookmark(self, fname, lnum):
        """Delete an entry from the list
        @param fname: file name
        @param lnum: Line number

        """
        count = self.GetItemCount()
        for idx in range(count):
            item_name = self.GetItem(idx, BookmarkList.FILE_NAME)
            item_line = self.GetItem(idx, BookmarkList.LINE_NUM)
            item_key = (item_name.Text, item_line.Text)
            if item_key == (fname, lnum):
                self.DeleteItem(idx)
                break
