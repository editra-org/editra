###############################################################################
# Name: finddlg.py                                                            #
# Purpose: Custom advanced find dialog                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: Advanced Find Replace Dialog

Advanced find dialog class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import os
import wx

# Local Imports
import ctrlbox
import platebtn

#--------------------------------------------------------------------------#
# Globals

# Style Flags
AFR_DEFAULT       = 0
AFR_REPLACEDIALOG = 1

# Search Flags
AFR_UP          = 1
AFR_WHOLEWORD   = 2
AFR_MATCHCASE   = 4
AFR_REGEX       = 8

# Search Location Parameters (NOTE: must be kept in sync with Lookin List)
LOCATION_CURRENT_DOC = 0
LOCATION_OPEN_DOCS   = 1
LOCATION_IN_FILES    = 3

# Control Names
FindBoxName = "EdFindBox"
FindPanelName = "EdFindPanel"

# Find Panel Control Ids
ID_LOOKIN = wx.NewId()
ID_FIND_LBL = wx.NewId()
ID_REPLACE_LBL = wx.NewId()
ID_MATCH_CASE = wx.NewId()
ID_WHOLE_WORD = wx.NewId()
ID_REGEX = wx.NewId()
ID_FIND_ALL = wx.NewId()
ID_REPLACE_ALL = wx.NewId()
ID_CHOOSE_DIR = wx.NewId()

_ = wx.GetTranslation

from wx.lib.embeddedimage import PyEmbeddedImage

Dot = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAH1J"
    "REFUKJHt0K0NwlAAReHv0Z8nCxMAG3SEbkBHYQQkbMMo4JCVyOJIk1IERaBIKgnH3Nyboy5/"
    "fpH5l/65RVaRNtJmlJCzjQyR49vLaSJDTj2D4SUXKALV6NVjbiCjDCwhUCXQc0lY49yxxz2l"
    "wQKHntODa0rADbupX0znCbjbFaNn/o8tAAAAAElFTkSuQmCC")
GetDotBitmap = Dot.GetBitmap

#--------------------------------------------------------------------------#

# Events
edEVT_FIND = wx.NewEventType()
EVT_FIND = wx.PyEventBinder(edEVT_FIND, 1)

edEVT_FIND_NEXT = wx.NewEventType()
EVT_FIND_NEXT = wx.PyEventBinder(edEVT_FIND_NEXT, 1)

edEVT_FIND_ALL = wx.NewEventType()
EVT_FIND_ALL = wx.PyEventBinder(edEVT_FIND_ALL, 1)

edEVT_REPLACE = wx.NewEventType()
EVT_REPLACE = wx.PyEventBinder(edEVT_REPLACE, 1)

edEVT_REPLACE_ALL = wx.NewEventType()
EVT_REPLACE_ALL = wx.PyEventBinder(edEVT_REPLACE_ALL, 1)

EVENT_MAP = { wx.ID_FIND : edEVT_FIND,
              wx.ID_REPLACE : edEVT_REPLACE,
              ID_FIND_ALL : edEVT_FIND_ALL,
              ID_REPLACE_ALL : edEVT_REPLACE_ALL }

class FindEvent(wx.PyCommandEvent):
    """Event to signal that text needs updating"""
    def __init__(self, etype, eid, flags=0):
        """Creates the event object
        @keyword flags: Find/Replace flags

        """
        wx.PyCommandEvent.__init__(self, etype, eid)

        # Attributes
        self._flags = flags
        self._loc = 0
        self._find = u''
        self._replace = u''
        self._dir = u''

    def GetDirectory(self):
        """Get the directory of files to search in
        @return: string

        """
        return self._dir

    def GetFindString(self):
        """Get the find string
        @return: string

        """
        return self._find

    def GetFlags(self):
        """Get the search flags
        @return: long

        """
        return self._flags

    def GetReplaceString(self):
        """Set the find String
        @return: string

        """
        return self._replace

    def GetSearchType(self):
        """Get the type of search (current buffer, open documents, ect...)
        @return: int (see LOCATION_* flags)

        """
        return self._loc

    def SetDirectory(self, directory):
        """Set the directory of files to search in
        @param directory: string

        """
        self._dir = directory

    def SetFindString(self, find):
        """Set the find String
        @param find: string

        """
        self._find = find

    def SetFlags(self, flags):
        """Returns the value from the event.
        @return: the value of this event

        """
        self._flags = flags

    def SetReplaceString(self, rstring):
        """Set the find String
        @param rstring: string

        """
        self._replace = rstring

    def SetSearchType(self, stype):
        """Set the type of search (current buffer, open documents, ect...)
        @param stype: int (see LOCATION_* flags)

        """
        self._loc = stype

    def IsMatchCase(self):
        """Is this a match case search
        @return: bool

        """
        return bool(self._flags & AFR_MATCHCASE)

    def IsRegEx(self):
        """Is RegEx enabled in the dialog
        @return: bool

        """
        return bool(self._flags & AFR_REGEX)

    def IsWholeWord(self):
        """Is this a whole word search
        @return: bool

        """
        return bool(self._flags & AFR_WHOLEWORD)

    def IsUp(self):
        """Is the search searching up
        @return: bool

        """
        return bool(self._flags & AFR_UP)

#--------------------------------------------------------------------------#

class AdvFindReplaceDlg(wx.MiniFrame):
    """Advanced Find Replace Dialog"""
    def __init__(self, parent, fdata, title, style=AFR_DEFAULT):
        """Create the Dialog
        @param parent: Parent Window
        @param fdata: wx.FindReplaceData
        @param title: Dialog Title
        @keyword style: Dialog Style

        """
        wx.MiniFrame.__init__(self, parent, wx.ID_ANY, title,
                              style=wx.DEFAULT_DIALOG_STYLE)

        # Attributes
        self._panel = FindBox(self, fdata)

        # Layout
        self.__DoLayout()

    def __DoLayout(self):
        """Layout the dialog"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self._panel, 1, wx.EXPAND)
        self.SetSizer(vsizer)
        self.SetAutoLayout(True)
        self.Fit()

    def SetFindBitmap(self, bmp):
        """Set the find Bitmap
        @param bmp: wx.Bitmap

        """
        self._panel.SetFindBitmap(bmp)

    def SetReplaceBitmap(self, bmp):
        """Set the replace bitmap
        @param bmp: wx.Bitmap

        """
        self._panel.SetReplaceBitmap(bmp)

#--------------------------------------------------------------------------#

class FindBox(ctrlbox.ControlBox):
    """Container box that allows for switching the L{FindPanel}'s mode
    through the ui

    """
    def __init__(self, parent, fdata, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL|wx.NO_BORDER,
                 name=FindBoxName):
        """Create the container box
        @param fdata: wx.FindReplaceData

        """
        ctrlbox.ControlBox.__init__(self, parent, id, pos, size, style, name)

        # Attributes
        self._fpanel = FindPanel(self, fdata)
        ctrlbar = ctrlbox.ControlBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU)
        self.find = platebtn.PlateButton(ctrlbar, label=_("Find"), bmp=bmp,
                                         style=platebtn.PB_STYLE_NOBG)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        self.replace = platebtn.PlateButton(ctrlbar, label=_("Replace"),
                                            bmp=bmp,
                                            style=platebtn.PB_STYLE_NOBG)

        # Setup
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(ctrlbox.CTRLBAR_STYLE_DEFAULT)
        ctrlbar.SetVMargin(2, 2)
        ctrlbar.AddControl(self.find, wx.ALIGN_LEFT)
        ctrlbar.AddControl(self.replace, wx.ALIGN_LEFT)
        self.SetControlBar(ctrlbar)
        self.SetWindow(self._fpanel)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def OnButton(self, evt):
        """Change the mode
        @param evt: wx.EVT_BUTTON

        """
        eobj = evt.GetEventObject()
        if eobj == self.find:
            self._fpanel.SetFindMode(True)
            self.Layout()
            self.GetParent().Fit()
        elif eobj == self.replace:
            self._fpanel.SetFindMode(False)
            self.Layout()
            self.GetParent().Fit()
        else:
            evt.Skip()

    def SetFindBitmap(self, bmp):
        """Set the bitmap of the Find Button
        @param bmp: wx.Bitmap

        """
        self.find.SetBitmap(bmp)
        self.GetControlBar().Layout()

    def SetReplaceBitmap(self, bmp):
        """Set the bitmap of the Replace Button
        @param bmp: wx.Bitmap

        """
        self.replace.SetBitmap(bmp)
        self.GetControlBar().Layout()

#--------------------------------------------------------------------------#

class FindPanel(wx.Panel):
    """Find controls panel"""
    def __init__(self, parent, fdata, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=AFR_DEFAULT, name=FindPanelName):
        """Create the panel
        @param fdata: wx.FindReplaceData

        """
        wx.Panel.__init__(self, parent, id, pos, size,
                          wx.TAB_TRAVERSAL|wx.NO_BORDER, name)

        # Attributes
        # TODO: change to combo box when wxMac has native implementation
        self._mode = style
        self._ftxt = wx.TextCtrl(self)
        self._rtxt = wx.TextCtrl(self)
        locations = [_("Current Document"), _("Open Documents")]
        self._lookin = wx.Choice(self, ID_LOOKIN, choices=locations)
        self._sizers = dict()
        self._paths = dict()
        self._fdata = fdata

        # Layout
        self.__DoLayout()
        self.SetInitialSize()

        if style & AFR_REPLACEDIALOG:
            self.SetFindMode(False)
        else:
            self.SetFindMode(True)

        self._ConfigureControls()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnChooseDir, id=ID_CHOOSE_DIR)
        self.Bind(wx.EVT_BUTTON,
                  lambda evt: self.FireEvent(evt.GetId()) or evt.Skip())
        self.Bind(wx.EVT_CHECKBOX, self.OnOption)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnOption)
        for bid in (wx.ID_FIND, wx.ID_REPLACE, ID_FIND_ALL, ID_REPLACE_ALL):
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=bid)

    def __DoLayout(self):
        """Layout the panel"""
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)

        # Top Section
        topvsizer = wx.BoxSizer(wx.VERTICAL)

        # Platform dependant labels
        if wx.Platform == '__WXMSW__':
            findlbl = wx.StaticText(self, ID_FIND_LBL, _("Find what") + u":")
        else:
            findlbl = wx.StaticText(self, ID_FIND_LBL, _("Find") + u":")

        # Search Field
        fhsizer = wx.BoxSizer(wx.HORIZONTAL)
        fhsizer.Add(self._ftxt, 1, wx.EXPAND)
        topvsizer.AddMany([(findlbl, 0, wx.ALIGN_LEFT), ((3, 3), 0),
                          (fhsizer, 0, wx.EXPAND), ((5, 5), 0)])

        # Replace field
        rhsizer = wx.BoxSizer(wx.HORIZONTAL)
        rhsizer.Add(self._rtxt, 1, wx.EXPAND)
        rlbl = wx.StaticText(self, ID_REPLACE_LBL, _("Replace with") + u":")
        self._sizers[ID_REPLACE_LBL] = wx.BoxSizer(wx.VERTICAL)
        self._sizers[ID_REPLACE_LBL].AddMany([(rlbl, 0, wx.ALIGN_CENTER_VERTICAL),
                                             ((3, 3), 0), (rhsizer, 0, wx.EXPAND)])
        topvsizer.AddMany([(self._sizers[ID_REPLACE_LBL], 0, wx.EXPAND),
                           ((5, 5), 0)])

        # Look in field
        li_sz = wx.BoxSizer(wx.HORIZONTAL)
        dirbtn = wx.Button(self, ID_CHOOSE_DIR, u"...", style=wx.BU_EXACTFIT)
        li_sz.AddMany([(self._lookin, 1, wx.EXPAND), ((5, 5), 0),
                       (dirbtn, 0)])
        topvsizer.AddMany([(wx.StaticText(self, label=_("Look in") + u":"),
                            0, wx.ALIGN_LEFT),
                           ((3, 3), 0), (li_sz, 0, wx.EXPAND),
                           ((5, 5), 0)])

        # Search Direction Box
        dbox = wx.StaticBox(self, label=_("Direction"))
        dboxsz = wx.StaticBoxSizer(dbox, wx.HORIZONTAL)
        dboxsz.AddMany([(wx.RadioButton(self, wx.ID_UP, _("Up")), 0),
                        ((20, 5), 0),
                        (wx.RadioButton(self, wx.ID_DOWN, _("Down")), 0),
                        ((5, 5), 1)])

        # Search Options Box
        statbox = wx.StaticBox(self, label=_("Find Options"))
        sboxsz = wx.StaticBoxSizer(statbox, wx.VERTICAL)
        for cid, clbl in [(ID_MATCH_CASE, _("Match case")),
                          (ID_WHOLE_WORD, _("Whole word")),
                          (ID_REGEX, _("Regular expression"))]:
            sboxsz.AddMany([((3, 3), 0), (wx.CheckBox(self, cid, clbl), 0)])

        # Buttons
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add((100, 1), 1)
        for bid, blbl in [(wx.ID_FIND, _("Find")),
                          (wx.ID_REPLACE, _("Replace")),
                          (ID_FIND_ALL, _("Find All")),
                          (ID_REPLACE_ALL, _("Replace All"))]:
            self._sizers[bid] = wx.BoxSizer(wx.HORIZONTAL)
            self._sizers[bid].Add((5, 5), 0)
            self._sizers[bid].Add(wx.Button(self, bid, blbl), 0, wx.ALIGN_RIGHT)
            bsizer.Add(self._sizers[bid], 0)

        # Final Layout
        vsizer.AddMany([((5, 5), 0), (topvsizer, 0, wx.EXPAND), ((5, 5), 0),
                        (dboxsz, 0, wx.EXPAND), ((5, 5), 0),
                        (sboxsz, 0, wx.EXPAND), ((10, 10), 0),
                        (bsizer, 0), ((10, 10), 0)])
        hsizer.AddMany([((10, 10), 0), (vsizer, 0, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

    def _ConfigureControls(self):
        """Configure the state of the controls based on the FindReplaceData"""
        flags = self._fdata.GetFlags()
        self.FindWindowById(ID_MATCH_CASE).SetValue(flags & AFR_MATCHCASE)
        self.FindWindowById(ID_WHOLE_WORD).SetValue(flags & AFR_WHOLEWORD)
        self.FindWindowById(ID_REGEX).SetValue(flags & AFR_REGEX)
        self.FindWindowById(wx.ID_DOWN).SetValue(not (flags & AFR_UP))
        self.FindWindowById(wx.ID_UP).SetValue(flags & AFR_UP)

    def _ShowButtons(self, find=True):
        """Toggle the visiblity of a button set
        @param find: Show Find Buttons or Show Replace Buttons

        """
        if find:
            show = (wx.ID_FIND, ID_FIND_ALL)
            hide = (wx.ID_REPLACE, ID_REPLACE_ALL)
        else:
            show = (wx.ID_REPLACE, ID_REPLACE_ALL)
            hide = (ID_FIND_ALL,)

        for ctrl in show:
            self._sizers[ctrl].ShowItems(True)

        for ctrl in hide:
            self._sizers[ctrl].ShowItems(False)

    def ClearFlag(self, flag):
        """Clear a search flag
        @param flag: AFR_*

        """
        flags = self._fdata.GetFlags()
        flags &= ~flag 
        self._fdata.SetFlags(flags)

    def FireEvent(self, eid):
        """Fire an event
        @param eid: Event id

        """
        etype = EVENT_MAP.get(eid, None)
        if etype is not None:
            evt = FindEvent(etype, eid, self._fdata.GetFlags())
            evt.SetSearchType(min(3, self._lookin.GetSelection()))
            evt.SetFindString(self._ftxt.GetValue())
            if self._mode == AFR_REPLACEDIALOG:
                evt.SetReplaceString(self._rtxt.GetValue())
            else:
                evt.SetReplaceString(None)
            wx.PostEvent(self.GetParent(), evt)
            return True
        else:
            return False

    def OnChooseDir(self, evt):
        """Open the choose directory dialog for selecting what
        path to do a search in files in.
        @param evt: wx.EVT_BUTTON

        """
        if evt.GetId() == ID_CHOOSE_DIR:
            dlg = wx.DirDialog(self, _("Choose Search Folder"))
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                if path is not None and len(path):
                    items = self._lookin.GetItems()
                    the_dir = u''
                    for dname in reversed(path.split(os.sep)):
                        if len(dname):
                            the_dir = dname
                            break
                    else:
                        return

                    if the_dir not in items:
                        self._paths[len(items)] = path
                        self._lookin.Append(the_dir)

                    self._lookin.SetStringSelection(the_dir)
            dlg.Destroy()
        else:
            evt.Skip()

    def OnOption(self, evt):
        """Update search flags
        @param evt: wx.EVT_CHECKBOX

        """
        fmap = { ID_MATCH_CASE : AFR_MATCHCASE,
                 ID_WHOLE_WORD : AFR_WHOLEWORD,
                 ID_REGEX : AFR_REGEX,
                 wx.ID_UP : AFR_UP }
        eid = evt.GetId()
        eobj = evt.GetEventObject()
        if eid in fmap:
            if eobj.GetValue():
                self.SetFlag(fmap[eid])
            else:
                self.ClearFlag(fmap[eid])
        elif eid == wx.ID_DOWN:
            self.ClearFlag(fmap[wx.ID_UP])
        else:
            evt.Skip()

    def OnUpdateUI(self, evt):
        """Enable and disable buttons depending on state of find entry
        box.
        @param evt: wx.UpdateUIEvent

        """
        evt.Enable(len(self._ftxt.GetValue()))

    def SetFindMode(self, find=True):
        """Set the mode of the dialog Replace
        @param find: Set Find Mode or Replace Mode

        """
        if find:
            self._rtxt.Hide()
            self._sizers[ID_REPLACE_LBL].ShowItems(False)
            self._mode = AFR_DEFAULT
        else:
            self._rtxt.Show()
            self._sizers[ID_REPLACE_LBL].ShowItems(True)
            self._mode = AFR_REPLACEDIALOG

        self._ShowButtons(find)
        self.Layout()

    def SetFlag(self, flag):
        """Set a search flag
        @param flag: AFR_* flag value

        """
        flags = self._fdata.GetFlags()
        flags |= flag
        self._fdata.SetFlags(flags)

#--------------------------------------------------------------------------#

# Test
if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None)
    data = wx.FindReplaceData(AFR_MATCHCASE|AFR_REGEX)
    fdlg = AdvFindReplaceDlg(frame, data, "Find Replace Test")

    bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU)
    fdlg.SetFindBitmap(bmp)

    def OnFind(evt):
        print "Search String:", evt.GetFindString()
        print "Replace String:", evt.GetReplaceString()
        print "Location:", evt.GetDirectory()
        print "Search Type:", evt.GetSearchType()
        print "Whole Word:", evt.IsWholeWord()
        print "Match Case: ", evt.IsMatchCase()
        print "Regular Expression:", evt.IsRegEx()
        print "Search Up:", evt.IsUp()

    frame.Bind(EVT_FIND, OnFind)
    frame.Bind(EVT_FIND_ALL, OnFind)
    frame.Bind(EVT_FIND_NEXT, OnFind)
    frame.Bind(EVT_REPLACE, OnFind)
    frame.Bind(EVT_REPLACE_ALL, OnFind)
    frame.Show()
    fdlg.Show()
    app.MainLoop()
