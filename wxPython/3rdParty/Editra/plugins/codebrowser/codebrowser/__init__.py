###############################################################################
# Name: __ini__.py                                                            #
# Purpose: CodeBrowser Plugin                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

# Plugin Meta
"""Adds a CodeBrowser Sidepanel"""
__author__ = "Cody Precord"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx.aui

# Libs from Editra
import iface
import plugin
from profiler import Profile_Get, Profile_Set

# Local imports
import cbrowser

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface implementation
class CodeBrowser(plugin.Plugin):
    """Adds a CodeBrowser to the view menu"""
    plugin.Implements(iface.MainWindowI)

    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        self._mw = parent
        self._log = wx.GetApp().GetLog()
        if self._mw != None:
            self._log("[codebrowser][info] Installing classbrowser plugin")
            
            #---- Create File Browser ----#
            # TODO hook in saved filter from profile
            self._codebrowser = cbrowser.CodeBrowserTree(self._mw)
            mgr = self._mw.GetFrameManager()
            mgr.AddPane(self._codebrowser, 
                        wx.aui.AuiPaneInfo().Name(cbrowser.PANE_NAME).\
                            Caption("Editra | CodeBrowser").Left().Layer(1).\
                            CloseButton(True).MaximizeButton(True).\
                            BestSize(wx.Size(215, 350)))

            # Get settings from profile
#            if Profile_Get('SHOW_FB', 'bool', False):
#                mgr.GetPane(browser.PANE_NAME).Show()
#            else:
#                mgr.GetPane(browser.PANE_NAME).Hide()

            mgr.Update()

            # Event Handlers
            self._mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def GetMenuHandlers(self):
        """Pass even handler for menu item to main window for management"""
        return [(cbrowser.ID_CODEBROWSER, self._codebrowser.OnShowBrowser)]

    def GetUIHandlers(self):
        """Pass Ui handlers to main window for management"""
        return list()

    def OnPaneClose(self, evt):
        """ Handles when the pane is closed to update the profile """
        pane = evt.GetPane()
        if pane.name == cbrowser.PANE_NAME:
            self._log('[codebrowser][info] Closed CodeBrowser')
#            Profile_Set('SHOW_FB', False)
        else:
            # Make sure to Skip if we are not the intended receiver
            # so other handlers waiting on this event can recieve it
            evt.Skip()
