# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: PyShell Plugin                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
# Plugin Metadata
"""Adds a PyShell to the Shelf"""
__author__ = "Cody Precord"
__version__ = "0.6"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx
import wx.stc
from wx.py import shell

# Local Imports
import ed_glob
import util
import iface
import ed_style
import plugin
from profiler import Profile_Get, Profile_Set
import syntax.syntax as syntax
import eclib.ctrlbox as ctrlbox
import eclib.platebtn as platebtn

#-----------------------------------------------------------------------------#
# Globals

PYSHELL_STYLE = "PyShell.Style" # Profile Key

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class PyShell(plugin.Plugin):
    """Adds a PyShell to the Shelf"""
    plugin.Implements(iface.ShelfI)
    __name__ = u'PyShell'

    def AllowMultiple(self):
        """PyShell allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a PyShell Panel"""
        util.Log("[PyShell][info] Creating PyShell instance for Shelf")
        return EdPyShellBox(parent)

    def GetBitmap(self):
        """Get the bitmap for representing this control in the ui
        @return: wx.Bitmap

        """
        return wx.ArtProvider.GetBitmap(str(ed_glob.ID_PYSHELL), wx.ART_MENU)

    def GetId(self):
        return ed_glob.ID_PYSHELL

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, ed_glob.ID_PYSHELL, self.__name__, 
                                        _("Open A Python Shell"))

    def GetName(self):
        return self.__name__

    def IsStockable(self):
        return True

#-----------------------------------------------------------------------------#

class EdPyShellBox(ctrlbox.ControlBox):
    """Control box for PyShell"""
    def __init__(self, parent):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self._shell = EdPyShell(self)
        self._styles = util.GetResourceFiles('styles', True,
                                             True, title=False)
        self._choice = None
        self._clear = None

        # Setup
        self.__DoLayout()
        style = self._shell.GetShellTheme()
        for sty in self._styles:
            if sty.lower() == style.lower():
                self._choice.SetStringSelection(sty)
                break

        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self._clear)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self._choice)

    def __DoLayout(self):
        """Layout the control box"""
        ctrlbar = ctrlbox.ControlBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(ctrlbox.CTRLBAR_STYLE_DEFAULT)

        self._choice = wx.Choice(ctrlbar, wx.ID_ANY, choices=self._styles)

        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Color Scheme") + u":"),
                           wx.ALIGN_LEFT)
        ctrlbar.AddControl(self._choice, wx.ALIGN_LEFT)

        cbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
        self._clear = platebtn.PlateButton(ctrlbar, label=_("Clear"), bmp=cbmp)
        ctrlbar.AddStretchSpacer()
        ctrlbar.AddControl(self._clear, wx.ALIGN_RIGHT)

        self.SetControlBar(ctrlbar)
        self.SetWindow(self._shell)

    def OnButton(self, evt):
        """Button event handler
        @param evt: wx.EVT_BUTTON

        """
        if evt.GetEventObject() == self._clear:
            self._shell.clear()
            self._shell.prompt()
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Change the color style
        @param evt: wx.EVT_CHOICE

        """
        e_obj = evt.GetEventObject()
        val = e_obj.GetStringSelection()
        self._shell.SetShellTheme(val)

#-----------------------------------------------------------------------------#

class EdPyShell(shell.Shell, ed_style.StyleMgr):
    """Custom PyShell that uses Editras StyleManager"""
    def __init__(self, parent):
        """Initialize the Shell"""
        shell.Shell.__init__(self, parent, locals=dict())

        # Get the color scheme to use
        style = Profile_Get(PYSHELL_STYLE)
        if style is None:
            style = Profile_Get('SYNTHEME')

        ed_style.StyleMgr.__init__(self, self.GetStyleSheet(style))

        # Attributes
        self.SetStyleBits(5)
        self._shell_style = style
        mgr = syntax.SyntaxMgr(ed_glob.CONFIG['CACHE_DIR'])
        syn_data = mgr.SyntaxData('py')
        synspec = syn_data[syntax.SYNSPEC]
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.SetSyntax(synspec)

    def GetShellTheme(self):
        """Get the theme currently used by the shell
        @return: string

        """
        return self._shell_style

    def SetShellTheme(self, style):
        """Set the color scheme used by the shell
        @param style: style sheet name (string)

        """
        self._shell_style = style
        Profile_Set(PYSHELL_STYLE, style)
        self.UpdateAllStyles(style)
