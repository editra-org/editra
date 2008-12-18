###############################################################################
# Name: auinavi.py                                                            #
# Purpose: AuiMgr Pane navigator                                              #
# Author: Cowo                                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library: AuiPaneNavigator

Popup navigation window for quickly navigating through AuiPanes in an AuiMgr.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Control Libray Imports
import ctrlbox

#-----------------------------------------------------------------------------#

class AuiPaneNavigator(wx.Dialog):
    """Navigate through Aui Panes"""
    closeKeys = [wx.WXK_ALT, wx.WXK_CONTROL, wx.WXK_RETURN]

    def __init__(self, parent, auiMgr, icon=None, title=''):
        """@param auiMgr: Main window Aui Manager"""
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", style=0)

        # Attributes
        self._auimgr = auiMgr
        self._selectedItem = -1
        self._indexMap = []
        self._sel = 0

        # Setup
        sz = wx.BoxSizer(wx.VERTICAL)
        self._listBox = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                   wx.Size(200, 150), list(),
                                   wx.LB_SINGLE | wx.NO_BORDER)

        self._panel = ctrlbox.ControlBar(self,
                                         style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        self._panel.SetVMargin(2, 2)

        if icon is not None:
            bmp = wx.StaticBitmap(self._panel, bitmap=icon)
            self._panel.AddControl(bmp, wx.ALIGN_LEFT)
        txt = wx.StaticText(self._panel, label=title)
        self._panel.AddControl(txt, wx.ALIGN_LEFT)

        sz.Add(self._panel, 0, wx.EXPAND)
        sz.Add(self._listBox, 1, wx.EXPAND)
        self.SetSizer(sz)

        # Event Handlers
        self._listBox.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self._listBox.Bind(wx.EVT_NAVIGATION_KEY, self.OnNavigationKey)
        self._listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnItemSelected)
        
        # Connect paint event to the panel
        self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        self._listBox.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        self.PopulateListControl()
        
        self.GetSizer().Fit(self)
        self.GetSizer().SetSizeHints(self)
        self.GetSizer().Layout()
        self.Centre()

        # Set focus on the list box to avoid having to click on it to change
        # the tab selection under GTK.
        self._listBox.SetFocus()
        self._listBox.SetSelection(0)

    def OnKeyUp(self, event):
        """Handles wx.EVT_KEY_UP"""
        if event.GetKeyCode() == wx.WXK_TAB:
           selected = self._listBox.GetSelection() + 1
           if selected >= self._listBox.GetCount():
               selected = 0

           self._listBox.SetSelection(selected)
           event.Skip()
           return
        elif event.GetKeyCode() in AuiPaneNavigator.closeKeys:
            self.CloseDialog()
        else:
            event.Skip()

    def OnNavigationKey(self, event):
        """Handles wx.EVT_NAVIGATION_KEY"""
        selected = self._listBox.GetSelection()
        maxItems = self._listBox.GetCount()
            
        if event.GetDirection():
            # Select next pane
            if selected == maxItems - 1:
                itemToSelect = 0
            else:
                itemToSelect = selected + 1
        else:
            # Previous pane
            if selected == 0:
                itemToSelect = maxItems - 1
            else:
                itemToSelect = selected - 1
        
        self._listBox.SetSelection(itemToSelect)

    def PopulateListControl(self):
        """Populates the L{AuiPaneNavigator} with the panes in the AuiMgr"""
        self._panes = self._auimgr.GetAllPanes()
        names = [pane.name for pane in self._panes]
        self._listBox.AppendItems(sorted(names))

    def OnItemSelected(self, event):
        """Handles the wx.EVT_LISTBOX_DCLICK event"""
        self.CloseDialog()

    def CloseDialog(self):
        """Closes the L{AuiPaneNavigator} dialog"""
        self._selectedItem = self._listBox.GetStringSelection()
        self.EndModal(wx.ID_OK)

    def GetSelection(self):
        """Get the index of the selected page"""
        return self._selectedItem
