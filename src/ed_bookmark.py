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
import eclib
import iface
import plugin
from profiler import Profile_Get, Profile_Set
import ed_glob

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
        else:
            if value in cls._marks:
                cls._marks.remove(value)

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

        # Populate the list ctrl with anything in the cache
        self.marks = EdBookmarks.GetMarks()
        for fname, linenum in self.marks:
            self._list.Append((linenum, fname))

        # Message Handlers
        ed_msg.Subscribe(self.OnBookmark, ed_msg.EDMSG_UI_STC_BOOKMARK)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate, self._list)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnBookmark)

    def OnBookmark(self, msg):
        data = msg.GetData()
        line = data.get('line', -1)
        buf = data.get('stc', None)
        value = (buf.GetFileName(), line)
        if data.get('added', False):
            self.marks.append(value)
            self._list.Append((value[1], value[0]))
        else:
            if value in self.marks:
                idx = self.marks.index(value)
            self._list.DeleteItem(idx)

    def OnItemActivate(self, evt):
        """Handle double clicks on items to navigate to the
        selected bookmark.

        """
        index = event.m_itemIndex
        if index < self.marks:
            mark = self.marks[index]
            

#-----------------------------------------------------------------------------#

class BookmarkList(eclib.EBaseListCtrl):
    """ListCtrl for displaying the bookmarks in"""
    LINE_NUM = 0
    FILE_NAME = 1
    def __init__(self, parent):
        super(BookmarkList, self).__init__(parent)

        # Attributes
        
        # Setup
        self.InsertColumn(BookmarkList.LINE_NUM, _("Line Number"))
        self.InsertColumn(BookmarkList.FILE_NAME, _("File Location"))
