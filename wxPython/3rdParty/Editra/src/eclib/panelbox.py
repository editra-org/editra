###############################################################################
# Name: panelbox.py                                                           #
# Purpose: Advanced listbox control                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: PanelBox

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.scrolledpanel as scrolled

#--------------------------------------------------------------------------#

edEVT_ITEM_SELECTED = wx.NewEventType()
EVT_ITEM_SELECTED = wx.PyEventBinder(edEVT_ITEM_SELECTED, 1)

class PanelBoxEventEvent(wx.PyCommandEvent):
    """Panel Box Event Object"""
    pass

#--------------------------------------------------------------------------#

class PanelBox(scrolled.ScrolledPanel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.HSCROLL|wx.VSCROLL,
                 name=u"PanelBox"):
        scrolled.ScrolledPanel.__init__(self, parent, id, pos, size, style, name)

        # Attributes
        self._items = list()
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        # Setup
        bkgrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        self.SetBackgroundColour(bkgrnd)

        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)

        self.SetupScrolling()

        # Event Handlers
#        self.Bind(wx.EVT_KEY_UP, self.OnNavigate)

    #---- Event Handlers ----#

    def OnItemClicked(self, evt):
        """Callback from when children are clicked on
        @param evt: wx.MouseEvent

        """
        item = evt.GetEventObject()
        selected = item.IsSelected()

        if evt.CmdDown():
            # Add/Remove from selection
            item.SetSelection(not selected)
        elif evt.ShiftDown():
            # Select all items between this item and the next selected one
            for pbitem in self._items:
                if pbitem is item:
                    index = None
        else:
            # Move selection to this item
            for pbitem in self._items:
                pbitem.SetSelection(False)

            if not selected:
                item.SetSelection(True)

    def OnNavigate(self, evt):
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_UP:
            print "KEY UP"
        elif key_code == wx.WXK_DOWN:
            print "KEY DOWN"
        else:
            evt.Skip()

    #---- Public Api ----#
    def AppendItem(self, item):
        """Append an item to the list
        @param item: PanelBoxItem

        """
        self._items.append(item)
        self._sizer.Add(item, 0, wx.EXPAND)
        item.Realize()

    def ClearSelections(self):
        """Unselect all items"""
        for item in self._items:
            item.SetSelection(False)

    def GetSelection(self):
        """Get the (first) selected item"""
        for item in self._items:
            if item.IsSelected():
                return item
        else:
            return None

    def GetSelections(self):
        """Get the list of selected items
        @return: list

        """
        return [item for item in self._items if item.IsSelected()]

    def InsertItem(self, index, item):
        """Insert an item into the list
        @param index: index to insert at
        @param item: PanelBoxItem

        """
        if index <= len(self._items):
            self._items.insert(index, item)
            self._sizer.Insert(index, item, 0, wx.EXPAND)
        else:
            raise IndexError, "Index %d: out of range" % index

    def Remove(self, index):
        """Remove an item from the list
        @param index: item index

        """
        if index < len(self._items):
            item = self._items.pop(index)
            self._sizer.Remove(item)
            self.Layout()
        else:
            raise IndexError, "Index %d: out of range" % index

    def RemoveAll(self):
        """Remove all items from the list"""
        for item in self._items:
            self._sizer.Remove(item)

        del self._items
        self._items = list()

        self.Layout()

#--------------------------------------------------------------------------#

class PanelBoxItemBase(wx.PyPanel):
    """Base L{PanelBox} Item"""
    def __init__(self, parent):
        """Create a PanelBoxItem"""
        wx.PyPanel.__init__(self, parent, style=wx.NO_BORDER|wx.TAB_TRAVERSAL)

        # Attributes
        self._selected = False

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)
#        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

    def OnKeyUp(self, evt):
        """Handle key navigation events"""
        self.GetParent().OnNavigate(evt)
        evt.Skip()

    def OnLeftUp(self, evt):
        """Handle when the item is clicked on"""
        e_obj = evt.GetEventObject()
        evt.SetEventObject(self)
        self.GetParent().OnItemClicked(evt)
        evt.SetEventObject(e_obj)
        evt.Skip()

    def OnPaint(self, evt):
        """Paint the items background"""
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()

#        if self.IsSelected():
#            color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
#            dc.SetBrush(wx.Brush(color))
#            dc.SetPen(wx.TRANSPARENT_PEN)
#            dc.DrawRectangle(*rect)
#        else:
#            col2 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX)
#            dc.SetBackground(wx.Brush(col2))
#            dc.SetBrush(wx.Brush(col2))
#            dc.SetPen(wx.TRANSPARENT_PEN)
#            dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height - 1)

        pcolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        dc.SetPen(wx.Pen(pcolor))
        dc.DrawLine(rect.x, rect.bottom, rect.right, rect.bottom)

    def IsSelected(self):
        """Is this item selected
        @return: bool

        """
        return self._selected

    def Realize(self):
        """Finalize initialization of the panel item"""
        for child in self.GetChildren():
            child.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

    def SetSelection(self, select=False):
        """Set the selection state on this item
        @keyword select: bool

        """
        self._selected = select
        if self._selected:
            color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        else:
            color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX)
        self.SetBackgroundColour(color)
        self.Refresh()

#--------------------------------------------------------------------------#

class PanelBoxItem(PanelBoxItemBase):
    """L{PanelBox} Item that has an icon, main label text and sub label
    +-------------------------+
    |                         |
    | ICON   label            |
    |        sub item         |
    +-------------------------+

    """
    def __init__(self, parent, bmp=None, label=u'', sub=None):
        """Create teh PanelBoxItem
        @param parent: L{PanelBox}
        @keyword bmp: wx.Bitmap
        @keyword label: string
        @keyword sub: Window object or None

        """
        PanelBoxItemBase.__init__(self, parent)

        # Attributes
        self._bmp = bmp
        self._label = label
        self._sub = sub

        # Layout
        self.__DoLayout()
        self.SetAutoLayout(True)

    def __DoLayout(self):
        """Layout the control"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        hsizer.Add((8, 8), 0)
        if self._bmp is not None:
            self._bmp = wx.StaticBitmap(self, bitmap=self._bmp)
            hsizer.Add(self._bmp, 0, wx.ALIGN_CENTER_VERTICAL)
            hsizer.Add((5, 5), 0)

        # Add Label Text
        isizer = wx.BoxSizer(wx.VERTICAL)
        self._label = wx.StaticText(self, label=self._label)
        isizer.Add(self._label, 0, wx.ALIGN_LEFT)
        if self._sub is not None:
            isizer.Add((3, 3), 0)

        # Add Subwindow if one is defined
        if self._sub is not None:
            self._sub.Reparent(self)
            s_sizer = wx.BoxSizer(wx.HORIZONTAL)
            s_sizer.Add(self._sub, 1, wx.EXPAND)
            isizer.Add(s_sizer, 1, wx.EXPAND)

        hsizer.Add(isizer, 1, wx.ALIGN_CENTER_VERTICAL)
        hsizer.Add((8, 8), 0)
        vsizer.AddMany([((8, 8), 0), (hsizer, 0, wx.EXPAND), ((8, 8), 0)])
        self.SetSizer(vsizer)

    def SetBitmap(self, bmp):
        """Set the items image
        param bmp: wx.Bitmap

        """
        self._bmp.SetBitmap(bmp)
        self._bmp.Refresh()
        self.Layout()

    def SetLabel(self, lbl):
        """Set the label text
        @param lbl: string

        """
        self._lbl.SetLabel(lbl)
        self._lbl.Refresh()
        self.Layout()

    def SetSecondaryCtrl(self, ctrl):
        """Set the secondary control
        @param ctrl: wxWindow

        """
        

#--------------------------------------------------------------------------#

if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, title="Test PanelBox")
    panel = PanelBox(frame)
    bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_TOOLBAR, (32, 32))
    for num in range(5):
        if num % 2:
            secondary = wx.StaticText(panel, label="PanelBoxItem test")
        else:
            secondary = wx.Gauge(panel, size=(-1, 16))
            secondary.Pulse()

        pi = PanelBoxItem(panel, bmp, "Hello", secondary)
        pi.SetMinSize((300, 50))
        panel.AppendItem(pi)
    frame.Show()
    app.MainLoop()
