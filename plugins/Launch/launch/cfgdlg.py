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
import sys
import wx
import wx.lib.mixins.listctrl as listmix
import cStringIO
import zlib

# Local Imports
import handlers

# Editra Libraries
import ed_msg
import util

#-----------------------------------------------------------------------------#
# Globals
ID_LANGUAGE = wx.NewId()
ID_EXECUTABLES = wx.NewId()

# Message Types
EDMSG_LAUNCH_CFG_EXIT = ed_msg.EDMSG_ALL + ('launch', 'cfg', 'exit')

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

def GetMinusData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2< \xcc\xc1\x06$\
\xc3Jc\x9e\x03)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2\x9d<]\x1cC4&&\xa7\
\xa4$\xa5)\xb0\x1aL\\RU\x90\x95\xe0\xf8,\xc6\xaa\xf0\xcf\xffr\x13\xd69\x87\
\xb8x\xaaVM\xea\x890\xf512N\x9e\xb1v\xf5\xe9\x05\xdc\xc2;jf:\x96\xdf\xd2\x14\
a\x96pO\xda\xc0\xc4\xa0\xf4\x8a\xab\xcau\xe2|\x1d\xa0i\x0c\x9e\xae~.\xeb\x9c\
\x12\x9a\x00Ij($" )

def GetMinusBitmap():
    stream = cStringIO.StringIO(GetMinusData())
    img = wx.ImageFromStream(stream)
    return wx.BitmapFromImage(img)

#----------------------------------------------------------------------
def GetPlusData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2< \xcc\xc1\x06$\
\xc3Jc\x9e\x03)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2{<]\x1cC4&&'Hp\x1c\
\xd8\xb9\xcf\xe6U\xfd\xefi\xbb\xffo\xf44J\x14L\xae\xde\x97+yx\xd3\xe9\xfc\
\x8d\xb3\xda|\x99\x99g\x1b07\x1b\xd8k\x87\xf1\xea\x18\x1c{\xaa\xec\xfe\xaf>%\
!\xf9A\xda\xef\x03\x06\xf67{\x1f\x1e\xf8\xf9\x98g\xf9\xb9\xf9\xbf\xfe\xbf~\
\xad\xcf\x96'h\xca\xe6\xcck\xe8&2\xb7\x8e\x87\xe7\xbfdAB\xfb\xbf\xe0\x88\xbf\
\xcc\xcc\x7f.\xcbH\xfc{\xfd(\xa0\xe5*\xff\xfd\xff\x06\x06\x1f\xfe\xffh\xbaj\
\xf2f^ZB\xc2\x83\xe4\xc3\xef2o13<r\xd5y\xc0\xb9\xc2\xfa\x0e\xd0]\x0c\x9e\xae\
~.\xeb\x9c\x12\x9a\x00\xcf9S\xc6" )

def GetPlusBitmap():
    stream = cStringIO.StringIO(GetPlusData())
    img = wx.ImageFromStream(stream)
    return wx.BitmapFromImage(img)

#----------------------------------------------------------------------

class ConfigDialog(wx.Frame):
    """Configuration dialog for configuring what executables are available
    for a filetype and what the preferred one is.

    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=_("Launch Configuration"))

        # Attributes

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Register with app
        wx.GetApp().RegisterWindow(repr(self), self)

    def __DoLayout(self):
        """Layout the dialog"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = ConfigPanel(self)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        self.SetMinSize((400, 300))

    def OnClose(self, evt):
        """Unregister the window when its closed"""
        wx.GetApp().UnRegisterWindow(repr(self))
        ed_msg.PostMessage(EDMSG_LAUNCH_CFG_EXIT)
        evt.Skip()

#-----------------------------------------------------------------------------#

class ConfigPanel(wx.Panel):
    """Configuration panel that holds the controls for configuration"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit)

    def __DoLayout(self):
        """Layout the controls"""
        msizer = wx.BoxSizer(wx.VERTICAL)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_ch = wx.Choice(self, ID_LANGUAGE, choices=GetHandlerTypes())
        lsizer.AddMany([(wx.StaticText(self, label=_("File Type") + ":"), 0,
                         wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (lang_ch, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)])

        # Main area
        sbox = wx.StaticBox(self, label=_("Executables"))
        boxsz = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        # Default exe
        dsizer = wx.BoxSizer(wx.HORIZONTAL)
        chandler = handlers.GetHandlerByName(lang_ch.GetStringSelection())
        def_ch = wx.Choice(self, wx.ID_DEFAULT, choices=chandler.GetCommands())
        dsizer.AddMany([(wx.StaticText(self, label=_("Default") + ":"), 0,
                         wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (def_ch, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)])

        # Executables List
        exelist = AutoWidthListCtrl(self, ID_EXECUTABLES,
                                    style=wx.LC_EDIT_LABELS|\
                                          wx.BORDER|\
                                          wx.LC_REPORT)
        exelist.InsertColumn(0, _("Executable Commands"))
        self.SetListItems(chandler.GetCommands())
        exelist.SetToolTipString(_("Click on an item to edit"))
        addbtn = wx.BitmapButton(self, wx.ID_ADD, GetPlusBitmap())
        addbtn.SetToolTipString(_("Add a new executable"))
        delbtn = wx.BitmapButton(self, wx.ID_REMOVE, GetMinusBitmap())
        delbtn.SetToolTipString(_("Remove selection from list"))
        btnsz = wx.BoxSizer(wx.HORIZONTAL)
        btnsz.AddMany([(addbtn, 0), ((2, 2), 0), (delbtn, 0)])

        # Box Sizer Layout
        boxsz.AddMany([((5, 5), 0), (dsizer, 0, wx.ALIGN_CENTER|wx.EXPAND),
                       ((5, 5), 0), (wx.StaticLine(self), 0, wx.EXPAND),
                       ((8, 8), 0), (exelist, 1, wx.EXPAND), ((5, 5), 0),
                       (btnsz, 0, wx.ALIGN_LEFT)])

        # Setup the main sizer
        msizer.AddMany([((10, 10), 0), (lsizer, 0, wx.EXPAND),
                        ((10, 10), 0), (wx.StaticLine(self), 0, wx.EXPAND),
                        ((10, 10), 0),
                        (boxsz, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL),
                        ((10, 10), 0)])

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((8, 8), 0), (msizer, 1, wx.EXPAND), ((8, 8), 0)])
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

    def GetCurrentHandler(self):
        """Get the currently selected file type handler
        @return: handlers.FileTypeHandler

        """
        ftype = self.FindWindowById(ID_LANGUAGE).GetStringSelection()
        return handlers.GetHandlerByName(ftype)

    def GetListItems(self):
        """Get all the values from the list control"""
        item_id = -1
        exes = list()
        elist = self.FindWindowById(ID_EXECUTABLES)
        for item in xrange(elist.GetItemCount()):
            item_id = elist.GetNextItem(item_id)
            if item_id == -1:
                break
            exes.append(elist.GetItemText(item_id))
        return exes

    def OnButton(self, evt):
        """Handle the add and remove button events
        @param evt: wxButtonEvent

        """
        e_id = evt.GetId()
        elist = self.FindWindowById(ID_EXECUTABLES)
        if e_id == wx.ID_ADD:
            elist.Append([_("**New Value**")])
        elif e_id == wx.ID_REMOVE:
            item = -1
            items = []
            while True:
                item = elist.GetNextItem(item, wx.LIST_NEXT_ALL,
                                         wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                items.append(item)

            for item in reversed(sorted(items)):
                elist.DeleteItem(item)

            handler = self.GetCurrentHandler()
            exes = self.GetListItems()
            def_ch = self.FindWindowById(wx.ID_DEFAULT)
            def_ch.SetItems(exes)
            handler.SetCommands(exes)
            def_ch.SetStringSelection(handler.GetDefault())

        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handle the choice selection events"""
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_val = e_obj.GetStringSelection()
        if e_id == ID_LANGUAGE:
            handler = handlers.GetHandlerByName(e_val)
            cmds = handler.GetCommands()
            elist = self.FindWindowById(ID_EXECUTABLES)
            elist.DeleteAllItems()
            def_ch = self.FindWindowById(wx.ID_DEFAULT)
            def_ch.SetItems(cmds)
            def_ch.SetStringSelection(handler.GetDefault())
            self.SetListItems(cmds)
        elif e_id == wx.ID_DEFAULT:
            handler = self.GetCurrentHandler()
            handler.SetDefault(e_val)
        else:
            evt.Skip()

    def OnEndEdit(self, evt):
        """Store the new list values after the editing of a
        label has finished.
        @param evt: wxEVT_LIST_END_LABEL_EDIT

        """
        handler = self.GetCurrentHandler()
        if handler.GetName() != handlers.DEFAULT_HANDLER:
            exes = self.GetListItems()
            idx = evt.GetIndex()
            nval = evt.GetLabel()
            if len(exes) >= idx:
                exes[idx] = nval
            else:
                exes.append(nval)

            # Store the new values
            handler.SetCommands(exes)
            def_ch = self.FindWindowById(wx.ID_DEFAULT)
            def_ch.SetItems(sorted(exes))
            def_ch.SetStringSelection(handler.GetDefault())

    def SetListItems(self, items):
        """Set the items that are in the list control
        @param items: list of strings

        """
        elist = self.FindWindowById(ID_EXECUTABLES)
        for exe in items:
            index = elist.InsertStringItem(sys.maxint, exe)
            elist.SetStringItem(index, 0, exe)

#-----------------------------------------------------------------------------#

class AutoWidthListCtrl(listmix.ListCtrlAutoWidthMixin,
                        wx.ListCtrl):
    """Auto-width adjusting list for showing editing the commands"""
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def Append(self, entry):
        """Append an entry to the list
        @param entry: entry to add

        """
        wx.ListCtrl.Append(self, entry)
        self.ColorRow(self.GetItemCount() - 1)
        
    def ColorRow(self, index):
        """Color the given index
        @param index: list index

        """
        if index % 2:
            color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            color = util.AdjustColour(color, 15)
            self.SetItemBackgroundColour(index, color)

    def SetStringItem(self, index, col, label, imageId=-1):
        """Set the item in the list at the given index and colorize
        the row if it is an odd one.

        """
        wx.ListCtrl.SetStringItem(self, index, col, label, imageId=imageId)
        self.ColorRow(index)

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
