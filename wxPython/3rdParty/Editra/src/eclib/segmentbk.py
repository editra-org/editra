###############################################################################
# Name: segmentbk.py                                                          #
# Purpose: SegmentBook Implementation                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library: SegmentBook

Custom notebook like class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = []

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import ctrlbox

#-----------------------------------------------------------------------------#
# Events
edEVT_SB_PAGE_CHANGING = wx.NewEventType()
EVT_SB_PAGE_CHANGING = wx.PyEventBinder(edEVT_SB_PAGE_CHANGING, 1)
edEVT_SB_PAGE_CHANGED = wx.NewEventType()
EVT_SB_PAGE_CHANGED = wx.PyEventBinder(edEVT_SB_PAGE_CHANGED, 1)
edEVT_SB_PAGE_CLOSED = wx.NewEventType()
EVT_SB_PAGE_CLOSED = wx.PyEventBinder(edEVT_SB_PAGE_CLOSED, 1)
class SegmentBookEvent(wx.NotebookEvent):
    """SegmentBook event"""
    pass

#-----------------------------------------------------------------------------#

class SegmentBook(ctrlbox.ControlBox):
    """Notebook Class"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL|wx.NO_BORDER,
                 name=u"SegmentBook"):
        """Initialie the SegmentBook"""
        ctrlbox.ControlBox.__init__(self, parent, id, pos, size, style, name)

        # Attributes
        self._pages = list()
        self._imglist = None

        # Setup
        bar = ctrlbox.SegmentBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT|\
                                             ctrlbox.CTRLBAR_STYLE_LABELS)
        self.SetControlBar(bar, wx.TOP)

        # Event Handlers
        self.Bind(ctrlbox.EVT_SEGMENT_SELECTED, self._OnSegmentSel)

    def _DoPageChange(self, psel, csel):
        """Change the page and post events
        @param psel: previous selection (int)
        @param csel: current selection (int)

        """
        # Post page changing event
        event = SegmentBookEvent(edEVT_SB_PAGE_CHANGING,
                                 self.GetId(), csel, psel)
        event.SetEventObject(self)
        handler = self.GetEventHandler()
        if not handler.ProcessEvent(event) or event.IsAllowed():
            # Do the actual page change
            self.Freeze()
            self.ChangePage(csel)
            self.Thaw()

            # Post page changed event
            event.SetEventType(edEVT_SB_PAGE_CHANGED)
            handler.ProcessEvent(event)
        else:
            # Reset the segment selection
            psel = max(psel, 0)
            evt.GetObject().SetSelection(psel)

    def _OnSegmentSel(self, evt):
        """Change the page in the book"""
        psel = evt.GetPreviousSelection()
        csel = evt.GetCurrentSelection()
        self._DoPageChange(psel, csel)

    def AddPage(self, page, text, select=False, img_id=-1):
        """Add a page to the notebook
        @param page: wxWindow object
        @param text: Page text
        @keyword select: should the page be selected
        @keyword img_id: Image to use

        """
        page.Hide()
        self._pages.append(dict(page=page, img=img_id))
        segbar = self.GetControlBar(wx.TOP)
        segbar.AddSegment(wx.ID_ANY, self._imglist.GetBitmap(img_id), text)
        idx = len(self._pages) - 1

        if select or idx == 0:
            segbar.SetSelection(idx)
            self._DoPageChange(segbar.GetSelection(), idx)

    def ChangePage(self, index):
        """Change the page to the given index"""
        cpage = self._pages[index]['page']
        page = self.ChangeWindow(cpage)
        if page is not None:
            page.Hide()
        cpage.Show()
        self.Layout()

    def DeleteAllPages(self):
        """Remove all pages from the control"""
        raise NotImplmentedError

    def DeletePage(self, index):
        """Delete the page at the given index
        @param index: int

        """
        segbar = self.GetControlBar(wx.TOP)
        cpage = segbar.GetSelection() 
        segbar.RemoveSegment(index)
        npage = segbar.GetSelection()
        self._DoPageChange(cpage, npage)

        self._pages[index]['page'].Destroy()
        del self._pages[index]
        
    def CurrentPage(self):
        """Get the currently selected page
        @return: wxWindow or None

        """
        idx = self.GetControlBar(wx.TOP).GetSelection()
        if idx != -1:
            return self._pages[idx]['page']
        else:
            return None

    def GetImageList(self):
        """Get the notebooks image list
        @return: wxImageList or None

        """
        return self._imglist

    def GetPage(self, index):
        """Get the page at the given index
        @param index: int

        """
        return self._pages[index]['page']

    def GetPageCount(self):
        """Get the number of pages in the book
        @return: int

        """
        return len(self._pages)

    def GetPageImage(self, index):
        """Get the image index of the current page
        @param index: page index
        @return: int

        """
        return self._pages[index]['img']

    def GetPageText(self, index):
        """Get the text of the current page
        @param index: page index
        @return: string

        """
        bar = self.GetControlBar(wx.TOP)
        return bar.GetSegmentLabel(index)

    def GetSelection(self):
        """Get the current selection
        @return: int

        """
        bar = self.GetControlBar(wx.TOP)
        return bar.GetSelection()

    def HasMultiplePages(self):
        """Does the book have multiple pages
        @return: bool

        """
        return bool(self.GetPageCount())

    def InsertPage(self, index, page, text, select=False, image_id=-1):
        """Insert a page a the given index
        @param index: index to insert page at
        @param page: page to add to book
        @param text: page text
        @keyword select: bool
        @keyword image_id: image list index

        """
        raise NotImplementedError

    def SetImageList(self, imglist):
        """Set the notebooks image list
        @param imglist: wxImageList

        """
        self._imglist = imglist

    def SetPageImage(self, index, img_id):
        """Set the image to use on the given page
        @param index: page index
        @param img_id: image list index

        """
        raise NotImplementedError

    def SetPageText(self, index, text):
        """Set the text to use on the given page
        @param index: page index
        @param text: string

        """
        raise NotImplementedError
