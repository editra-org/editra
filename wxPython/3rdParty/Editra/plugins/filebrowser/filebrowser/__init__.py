# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: FileBrowser Plugin                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
# Plugin Meta
"""Adds a File Browser Sidepanel"""
__author__ = "Cody Precord"
__version__ = "0.7"

#-----------------------------------------------------------------------------#
# Imports
import wx.aui

# Libs from Editra
import iface
import plugin
from profiler import Profile_Get, Profile_Set

# Local imports
import browser

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface implementation
class FileBrowserPanel(plugin.Plugin):
    """Adds a filebrowser to the view menu"""
    plugin.Implements(iface.MainWindowI)

    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        self._mw = parent
        self._log = wx.GetApp().GetLog()
        if self._mw != None:
            self._log("[filebrowser][info] Installing filebrowser plugin")
            
            #---- Create File Browser ----#
            # TODO hook in saved filter from profile
            self._filebrowser = browser.BrowserPane(self._mw, 
                                                    browser.ID_BROWSERPANE)
            mgr = self._mw.GetFrameManager()
            mgr.AddPane(self._filebrowser, 
                        wx.aui.AuiPaneInfo().Name(browser.PANE_NAME).\
                            Caption("Editra | File Browser").Left().Layer(1).\
                            CloseButton(True).MaximizeButton(True).\
                            BestSize(wx.Size(215, 350)))

            # Get settings from profile
            if Profile_Get('SHOW_FB', 'bool', False):
                mgr.GetPane(browser.PANE_NAME).Show()
            else:
                mgr.GetPane(browser.PANE_NAME).Hide()

            mgr.Update()

            # Event Handlers
            self._mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def GetMenuHandlers(self):
        """Pass even handler for menu item to main window for management"""
        return [(browser.ID_FILEBROWSE, self._filebrowser.OnShowBrowser)]

    def GetUIHandlers(self):
        """Pass Ui handlers to main window for management"""
        return list()

    def OnPaneClose(self, evt):
        """ Handles when the pane is closed to update the profile """
        pane = evt.GetPane()
        if pane.name == browser.PANE_NAME:
            self._log('[filebrowser][info] Closed Filebrowser')
            Profile_Set('SHOW_FB', False)
        else:
            # Make sure to Skip if we are not the intended receiver
            # so other handlers waiting on this event can recieve it
            evt.Skip()
