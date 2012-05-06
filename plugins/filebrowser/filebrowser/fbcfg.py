# -*- coding: utf-8 -*-
###############################################################################
# Name: fbcfg.py                                                              #
# Purpose: FileBrowser configuration                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2012 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FileBrowser configuration

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import wx

from profiler import Profile_Get, Profile_Set

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

FB_PROF_KEY = "FileBrowser.Config"
FB_SYNC_OPT = "SyncNotebook"

#-----------------------------------------------------------------------------#

class FBConfigPanel(wx.Panel):
    def __init__(self, parent):
        super(FBConfigPanel, self).__init__(parent)

        # Attributes
        self._sb = wx.StaticBox(self, label=_("Actions"))
        self._sbs = wx.StaticBoxSizer(self._sb, wx.VERTICAL)
        self._sync_cb = wx.CheckBox(self,
                                    label=_("Synch tree with tab selection"),
                                    name=FB_SYNC_OPT)

        # Setup
        self.__DoLayout()
        self._sync_cb.Value = GetFBOption(FB_SYNC_OPT, True)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self._sync_cb)

    def __DoLayout(self):
        sizer = wx.BoxSizer()
        self._sbs.Add(self._sync_cb, 0, wx.ALL, 5)
        sizer.Add(self._sbs, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    def OnCheck(self, evt):
        """Update Profile"""
        e_obj = evt.GetEventObject()
        cfgobj = Profile_Get(FB_PROF_KEY, default=dict())
        if e_obj is self._sync_cb:
            cfgobj[FB_SYNC_OPT] = self._sync_cb.Value
            Profile_Set(FB_PROF_KEY, cfgobj)
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

def GetFBOption(opt, default=None):
    """Get FileBrowser option from the configuration"""
    cfgobj = Profile_Get(FB_PROF_KEY, default=dict())
    return cfgobj.get(opt, default)
