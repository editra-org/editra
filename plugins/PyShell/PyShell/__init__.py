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
__version__ = "0.5"

#-----------------------------------------------------------------------------#
# Imports
import wx
from wx.py import shell

# Local Imports
import ed_glob
import iface
from profiler import Profile_Get
import plugin

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class PyShell(plugin.Plugin):
    """Adds a PyShell to the Shelf"""
    plugin.Implements(iface.ShelfI)
    ID_PYSHELL = wx.NewId()
    __name__ = u'PyShell'

    def __SetupFonts(self):
        """Create the font settings for the shell by trying to get the
        users prefered font settings used in the EdStc

        """
        fonts = { 
                  'size'      : 11,
                  'lnsize'    : 10,
                  'backcol'   : '#FFFFFF',
                  'calltipbg' : '#FFFFB8',
                  'calltipfg' : '#404040',
        }

        font = Profile_Get('FONT1', 'font', wx.Font(11, wx.FONTFAMILY_MODERN, 
                                                        wx.FONTSTYLE_NORMAL, 
                                                        wx.FONTWEIGHT_NORMAL))
        if font.IsOk() and len(font.GetFaceName()):
            fonts['mono'] = font.GetFaceName()
            fonts['size'] = font.GetPointSize()
            fonts['lnsize'] = max(0, fonts['size'] - 1)

        font = Profile_Get('FONT2', 'font', wx.Font(11, wx.FONTFAMILY_SWISS, 
                                                        wx.FONTSTYLE_NORMAL, 
                                                        wx.FONTWEIGHT_NORMAL))
        if font.IsOk() and len(font.GetFaceName()):
            fonts['times'] = font.GetFaceName()
            fonts['helv'] = font.GetFaceName()
            fonts['other'] = font.GetFaceName()

        return fonts

    def AllowMultiple(self):
        """PyShell allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a PyShell Panel"""
        self._log = wx.GetApp().GetLog()
        self._log("[PyShell][info] Creating PyShell instance for Shelf")
        pyshell = shell.Shell(parent, locals=dict())
        pyshell.setStyles(self.__SetupFonts())
        return pyshell

    def GetBitmap(self):
        """Get the bitmap for representing this control in the ui
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PYSHELL), wx.ART_MENU)
        return bmp

    def GetId(self):
        return self.ID_PYSHELL

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, self.ID_PYSHELL, self.__name__, 
                                        _("Open A Python Shell"))

    def GetName(self):
        return self.__name__

    def IsStockable(self):
        return True
