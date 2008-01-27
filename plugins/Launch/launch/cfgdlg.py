# -*- coding: utf-8 -*-
###############################################################################
# Name: cfgdlg.py                                                             #
# Purpose: Configuration Dialog                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Configuration Dialog"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import handlers

#-----------------------------------------------------------------------------#

class ConfigDialog(wx.Frame):
    """Configuration dialog for configuring what executables are available
    for a filetype and what the preferred one is.

    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        # Attributes

        # Layout
        self.__DoLayout()

    def __DoLayout(self):
        """Layout the dialog"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

#-----------------------------------------------------------------------------#
ID_LANGUAGE = wx.NewId()

class ConfigPanel(wx.Panel):
    """Configuration panel that holds the controls for configuration"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes

        # Layout
        self.__DoLayout()

    def __DoLayout(self):
        """Layout the controls"""
        msizer = wx.BoxSizer(wx.VERTICAL)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_ch = wx.Choice(self, ID_LANGUAGE, choices=GetHandlerTypes())
        lsizer.AddMany([(wx.StaticText(self, label=_("File Type")), 0),
                        ((5, 5), 0), (lang_ch, 0)])

        # Main area
        sbox = wx.StaticBox(self, label=_("Executables"))
        boxsz = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        # Default exe
        dsizer = wx.BoxSizer(wx.HORIZONTAL)
        chandler = handlers.GetHandlerByName(lang_ch.GetStringSelection())
        def_ch = wx.Choice(self, wx.ID_DEFAULT, choices=chandler.GetCommands())
        dsizer.AddMany([(wx.StaticText(self, label=_("Default")), 0),
                        ((5, 5), 0), (chandler, 0)])

        # Edit List
        

        # Setup the main sizer
        msizer.AddMany([(lsizer, 0, wx.ALIGN_CENTER_HORIZONTAL),
                        (sbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)])

#-----------------------------------------------------------------------------#
def GetHandlerTypes():
    """Get the language type handlers for each language that
    has a handler defined.
    @return: list of handler names

    """
    keys = handlers.HANDLERS.keys()
    keys.remove(0)
    rlist = list()
    for key in keys:
        handle = handlers.HANDLERS[key]
        rlist.append(handle.GetName().title())
    return sorted(rlist)
