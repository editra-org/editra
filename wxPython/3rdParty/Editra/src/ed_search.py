###############################################################################
# Name: ed_search.py                                                          #
# Purpose: Text searching services and utilities                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007,2008 Cody Precord <staff@editra.org>                    #
# License: wxWindows License                                                  #
###############################################################################

"""
Provides various search controls and searching services for finding text in a
document. The L{TextFinder} is a search service that can be used to search and
highlight text in a StyledTextCtrl.

@summary: Text searching and result ui

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import os
import re
import types
import threading
import wx

# Local imports
import ed_glob
import ed_txt
from util import FileTypeChecker
from profiler import Profile_Get
import eclib.ctrlbox as ctrlbox
import eclib.outbuff as outbuff
import eclib.platebtn as platebtn
import eclib.finddlg as finddlg

#--------------------------------------------------------------------------#
# Globals
RESULT_TEMPLATE = u"%(fname)s (%(lnum)d): %(match)s"

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class TextFinder(object):
    """Provides an object to manage finding text in documents
    through various different methods, plain text, regex, ect...
    the Finder must be initialized with the variable callable set
    to a method that fetches the stc control that the search is to take
    place in.
    @todo: possibly reimplement as a singleton so that it can be used
           without having to go through the notebook each time its needed.

    """
    def __init__(self, parent, getstc):
        """Initializes the Text Finding Service, the getstc argument
        needs to be a function that returns reference to stc to perform
        the search in.
        @param getstc: callable function that will return an stc

        """
        object.__init__(self)
        self._parent      = parent
        self._find_dlg    = None
        self._posinfo = dict(scroll=0, start=0, found=0)
        self.FetchPool    = getstc
        self._data        = wx.FindReplaceData()
        self._data.SetFlags(wx.FR_DOWN)

    def GetClientString(self, multiline=False):
        """Get the selected text in the current client buffer. By default
        it will only return the selected text if its on a single line.
        @keyword multiline: Return text if it is multiple lines
        @return: wx.stc.StyledTextCtrl

        """
        buffer =  self.FetchPool()
        start, end = buffer.GetSelection()
        rtext = buffer.GetSelectedText()
        if start != end:
            sline = buffer.LineFromPosition(start)
            eline = buffer.LineFromPosition(end)
            if not multiline and (sline != eline):
                rtext = u''
        return rtext

    def GetClientSelection(self):
        """Get the selected text from the client buffer if any
        @return: string

        """
        return self.FetchPool().GetSelectedText()

    def GetData(self):
        """Return the FindReplace data
        @return: search data
        @rtype: wx.FindReplaceData

        """
        return self._data

    def OnFind(self, evt):
        """Does the work of finding the text
        @param evt: Event that called this handler

        """
        # Map of search flags
        flag_map = {  wx.FR_MATCHCASE : wx.stc.STC_FIND_MATCHCASE,
                      wx.FR_WHOLEWORD : wx.stc.STC_FIND_WHOLEWORD,
                      wx.FR_MATCHCASE | wx.FR_WHOLEWORD : \
                                        wx.stc.STC_FIND_MATCHCASE | \
                                        wx.stc.STC_FIND_WHOLEWORD,
                      0               : 0
        }

        # Get Search Type
        search_id = evt.GetEventType()

        # Get the Search Flags
        s_flags = self._data.GetFlags()
        pool = self.FetchPool()
        query = self._data.GetFindString()

        if search_id in [wx.wxEVT_COMMAND_FIND, wx.wxEVT_COMMAND_FIND_NEXT]:
            if search_id == wx.wxEVT_COMMAND_FIND_NEXT:
                if wx.FR_DOWN & s_flags:
                    if self._posinfo['found'] < 0:
                        pool.SetCurrentPos(0) # Start at top again
                    else:
                        pool.SetCurrentPos(pool.GetCurrentPos() + len(query))
                else:
                    # Searching previous
                    if self._posinfo['found'] < 0:
                        pool.SetCurrentPos(pool.GetLength())
                    else:
                        pool.SetCurrentPos(pool.GetCurrentPos() - len(query))

            pool.SearchAnchor()
            if not s_flags & wx.FR_DOWN:
                found = pool.SearchPrev(flag_map[s_flags] | \
                                        wx.stc.STC_FIND_REGEXP, query)
            else:
                found = pool.SearchNext(flag_map[s_flags - wx.FR_DOWN] | \
                                        wx.stc.STC_FIND_REGEXP, query)

            if found > 0:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])
                pool.EnsureVisible(pool.LineFromPosition(found))
            else:
                # Try search from begining/end again
                self.SetStart(pool)
                self.SetScroll(pool)
                if not s_flags & wx.FR_DOWN:
                    pool.SetCurrentPos(pool.GetLength())
                    pool.SetSelection(pool.GetLength(), pool.GetLength())
                else:
                    pool.SetCurrentPos(0)
                    pool.SetSelection(0, 0)
                pool.SearchAnchor()

                if not s_flags & wx.FR_DOWN:
                    found = pool.SearchPrev(flag_map[s_flags] | \
                                            wx.stc.STC_FIND_REGEXP, query)
                else:
                    found = pool.SearchNext(flag_map[s_flags - wx.FR_DOWN] | \
                                            wx.stc.STC_FIND_REGEXP, query)

            if found < 0:
                # Couldnt find it anywhere so set screen back to start position
                pool.ScrollToLine(self._posinfo['scroll'])
                pool.SetCurrentPos(self._posinfo['start'])
                pool.SetSelection(self._posinfo['start'],
                                  self._posinfo['start'])
                wx.Bell() # alert user to unfound string
            else:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])

            self._posinfo['found'] = found
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE:
            replacestring = evt.GetReplaceString()
            pool.ReplaceSelection(replacestring)
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE_ALL:
            replacestring = evt.GetReplaceString()
            self.SetStart(pool) # Save Start point
            self.SetScroll(pool) # Save scroll pos
            pool.SetTargetStart(0)
            pool.SetTargetEnd(pool.GetLength())
            pool.SetSearchFlags(flag_map[max(0, s_flags - wx.FR_DOWN)] | \
                                wx.stc.STC_FIND_REGEXP)
            replaced = 0
            fail = 0
            pool.BeginUndoAction()
            while fail < 2: #pool.SearchInTarget(query) > 0:
                # HACK if the search pattern is at the begining of the buffer
                #      the search will fail the first time. So check twice
                #      before giving up. ?Scintilla Bug?
                if pool.SearchInTarget(query) < 0:
                    fail += 1
                    continue
                pool.ReplaceTarget(replacestring)
                replaced += 1
                pool.SetTargetEnd(pool.GetLength())
            pool.EndUndoAction()

            pool.ScrollToLine(self._posinfo['scroll'])
            pool.SetCurrentPos(self._posinfo['start']) # Move cursor to start
            pool.SetSelection(self._posinfo['start'], self._posinfo['start'])
            dlg = wx.MessageDialog(self._parent,
                                   _("Replace All Finished\n"
                                     "A Total of %d matches were replaced") % \
                                     replaced,
                                    _("All Done"),
                                    wx.OK | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            dlg.ShowModal()
            dlg.Destroy()
        else:
            evt.Skip()

    def GetLastFound(self):
        """Returns the position value of the last found search item
        if the last search resulted in nothing being found then the
        return value will -1.
        @return: position of last search opperation
        @rtype: int

        """
        return self._posinfo['found']

    def GetSearchFlags(self):
        """Get the find services search flags
        @return: bitmask of the set search flags

        """
        return self._data.GetFlags()

    def GetStart(self):
        """Get the value of the start position that was last set by a call
        to L{SetStart}.
        @return: integer position value
        @note: usually the returned value is the cursors position from the
               begining of the last search operation.

        """
        return self._poinfo['start']

    def OnFindClose(self, evt):
        """Destroy Find Dialog After Cancel is clicked in it
        @param evt: event that called this handler

        """
        if self._find_dlg is not None:
            self._find_dlg.Destroy()
        self._find_dlg = None
        evt.Skip()

    def OnShowFindDlg(self, evt):
        """Catches the Find events and shows the appropriate find dialog
        @param evt: event that called this handler
        @postcondition: find dialog is shown

        """
        if self._find_dlg is not None:
            self._find_dlg.Destroy()
            self._find_dlg = None

        # Check for a selection in the buffer and load that text if
        # there is any and it is at most one line.
        query = self.GetClientString()
        if len(query):
            self.SetQueryString(query)

        e_id = evt.GetId()
        if e_id == ed_glob.ID_FIND_REPLACE:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find/Replace"),
                                                  wx.FR_REPLACEDIALOG)
        elif e_id == ed_glob.ID_FIND:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find"))
        else:
            evt.Skip()
            return

        self._find_dlg.CenterOnParent()
        try:
            self._find_dlg.Show()
        except wx.PyAssertionError:
            # Yes this is a bit strange but on windows if there was a find
            # dialog prevously shown and destroyed then the second time through
            # here will raise this assertion but not for any times after.
            self._find_dlg.Show()

    def SetQueryString(self, query):
        """Sets the search query value
        @param query: string to search for

        """
        self._data.SetFindString(query)

    def SetSearchFlags(self, flags):
        """Set the find services search flags
        @param flags: bitmask of paramters to set

        """
        self._data.SetFlags(flags)

    def SetScroll(self, pool):
        """Sets the value of the scroll attribute to the value of the
        current position in the search pool.
        @param pool: the search pool (a.k.a the text control)

        """
        self._posinfo['scroll'] = pool.GetFirstVisibleLine()
        return True

    def SetStart(self, pool):
        """Sets the value of the start attribute to the value of the
        current position in the search pool.
        @param pool: the search pool (a.k.a the text control)

        """
        self._posinfo['start'] = pool.GetCurrentPos()
        return True

#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
class SearchController:
    """Controls the interface to the text search engine"""
    def __init__(self, owner, getbuff):
        """Create the controller
        @param owner: View that owns this controller
        @param getbuff: Callable to retrieve the buffer

        """
        # Attributes
        self._parent      = owner
        self._find_dlg    = None
        self._posinfo = dict(scroll=0, start=0, found=0)
        self.FetchPool    = getstc
        self._data        = wx.FindReplaceData()
        self._data.SetFlags(wx.FR_DOWN)

    def _CreateNewDialog(self, eid):
        """Create and set the controlers find dialog
        @param eid: Dialog Type Id

        """
        if e_id == ed_glob.ID_FIND_REPLACE:
            dlg = finddlg.AdvFindReplaceDlg(self._parent, self._data,
                                            _("Find/Replace"),
                                            finddlg.AFR_STYLE_REPLACEDIALOG)
        elif e_id == ed_glob.ID_FIND:
            dlg =  finddlg.AdvFindReplaceDlg(self._parent, self._data,
                                             _("Find"))
        else:
            dlg = None
        return dlg

    def _UpdateDialogState(self, eid):
        """Update the state of the existing dialog"""
        if self._finddlg is None:
            self._finddlg = self._CreateNewDialog(eid)
        else:
            self._finddlg

    def GetData(self):
        """Get the contollers FindReplaceData
        @return: wx.FindReplaceData

        """
        return self._data

    def OnShowFindDlg(self, evt):
        """Catches the Find events and shows the appropriate find dialog
        @param evt: event that called this handler
        @postcondition: find dialog is shown

        """
        # Check for a selection in the buffer and load that text if
        # there is any and it is at most one line.
        query = self.GetClientString()
        if len(query):
            self.SetQueryString(query)

        eid = evt.GetId()
        # Dialog is not currently open
        if self._finddlg is None:
            self._find_dlg = self._CreateNewDialog(eid)
            if self._finddlg is None:
                evt.Skip()
                return
            self._find_dlg.CenterOnParent()
            self._find_dlg.Show()
        else:
            # Dialog is open already so just update it
            self._UpdateDialogState(eid)
            self._find_dlg.Raise()

#-----------------------------------------------------------------------------#

class SearchEngine:
    """Text Search Engine
    @todo: Add file filter support

    """
    def __init__(self, query, regex=True, down=True,
                 matchcase=True, wholeword=False):
        """Initialize a search engine object
        @param query: search string
        @keyword regex: Is a regex search
        @keyword down: Search down or up
        @keyword matchcase: Match case
        @keyword wholeword: Match whole word

        """

        # Attributes
        self._isregex = regex
        self._next = down
        self._matchcase = matchcase
        self._wholeword = wholeword
        self._query = query
        self._regex = self._CompileRegex()

    def _CompileRegex(self):
        """Prepare and compile the regex object based on the current state
        and settings of the engine.
        @return: re pattern object

        """
        tmp = str(self._query)
        if not self._isregex:
            tmp = EscapeRegEx(tmp)
        if self._wholeword:
            tmp = "\\s%s\\s" % tmp
        return re.compile(tmp)

    def SearchInBuffer(self, sbuffer):
        """Search in the buffer
        @param sbuffer: buffer like object

        """
        

    def SearchInDirectory(self, directory, recursive=True):
        """Search in all the files found in the given directory
        @param directory: directory path
        @keyword recursive: search recursivly

        """
        paths = [os.path.join(directory, fname)
                for fname in os.listdir(directory) if not fname.startswith('.')]
        for path in paths:
            if recursive and os.path.isdir(path):
                for match in self.SearchInDirectory(path, recursive):
                    yield match
            else:
                for match in self.SearchInFile(path):
                    yield match
        return

    def SearchInFile(self, fname):
        """Search in a file for all lines with matches of the set query and
        yield the results as they are found.
        @param fname: filename

        """
        results = list()
        fchecker = FileTypeChecker()
        if fchecker.IsReadableText(fname):
            try:
                fobj = open(fname, 'rb')
            except (IOError, OSError):
                return

            flag = 0
            if not self._matchcase:
                flag = re.IGNORECASE

            for lnum, line in enumerate(fobj):
                if re.search(self._regex, line, flag) is not None:
                    yield FormatResult(fname, lnum, line)
            fobj.close()
        return

    def SearchInFiles(self, flist):
        """Search in a list of files and yeild results as they are found.
        @param flist: list of file names

        """
        for fname in flist:
            for match in self.SearchInFile(fname):
                yield match
        return

    def SearchInString(self, sstring):
        """Search in a string
        @param sstring: string to search in

        """

    def SetFlags(self, isregex=None, matchcase=None, wholeword=None, down=None):
        """Set the search engine flags. Leaving the parameter set to None
        will not change the flag. Setting it to non None will change the value.
        @keyword isregex: is regex search
        @keyword matchcase: matchcase search
        @keyword wholeword: wholeword search
        @keyword down: search down or up

        """
        for attr, val in (('_isregex', isregex), ('_matchcase', matchcase),
                          ('_wholeword', wholeword), ('_next', down)):
            if val is not None:
                setattr(self, attr, val)
        self._regex = self._CompileRegex()

    def SetQuery(self, query):
        """Set the search query"""
        self._query = query
        self._regex = self._CompileRegex()

#-----------------------------------------------------------------------------#

class SearchThread(threading.Thread):
    """Worker thread for doing searches on multiple files and buffers"""
    def __init__(self, target, query):
        """Create the search thread
        @param target: Search method to execute, should be a generator
        @param query: search queary string

        """
        threading.Thread.__init__(self)

        # Attributes
        self._query = query
        self.target = target
        self._exit = False
        
    def run(self):
        """Do the search and post the results"""
        for match in self.target():
            #TODO post results
            if self._exit:
                break

    def CancelSearch(self):
        """Cancel the current search
        @postcondition: Thread exits

        """
        self._exit = True

#-----------------------------------------------------------------------------#

def EscapeRegEx(regex):
    """Escape all special regex characters in the given string
    @param regex: string
    @return: string

    """
    for char in u"\\[](){}+*$^?":
        regex = regex.replace(char, "\\%s" % char)
    return regex

def FormatResult(fname, lnum, match):
    """Format the search result string
    @return: string
    @todo: better unicode handling

    """
    fname = ed_txt.DecodeString(fname, sys.getfilesystemencoding())
    if not isinstance(fname, types.UnicodeType):
        fname = _("DECODING ERROR")

    match = ed_txt.DecodeString(match)
    if not isinstance(match, types.UnicodeType):
        match = _("DECODING ERROR")
    else:
        match = u" " + match.lstrip()
    return RESULT_TEMPLATE % dict(fname=fname, lnum=lnum, match=match)

#-----------------------------------------------------------------------------#

class EdSearchCtrl(wx.SearchCtrl):
    """Creates a simple search control for use in the toolbar
    or a statusbar and the such. Supports incremental search,
    and uses L{TextFinder} to do the actual searching of the
    document.

    """
    def __init__(self, parent, id_, value="", menulen=0, \
                 pos=wx.DefaultPosition, size=wx.DefaultSize, \
                 style=wx.TE_RICH2|wx.TE_PROCESS_ENTER):
        """Initializes the Search Control
        @param menulen: max length of history menu

        """
        wx.SearchCtrl.__init__(self, parent, id_, value, pos, size, style)

        # Attributes
        self._parent     = parent
        # TEMP HACK
        self.FindService = self.GetTopLevelParent().nb.FindService
        self._flags      = wx.FR_DOWN
        self._recent     = list()        # The History List
        self._last       = None
        self.rmenu       = wx.Menu()
        self.max_menu    = menulen + 2   # Max menu length + descript/separator

        # Setup Recent Search Menu
        lbl = self.rmenu.Append(wx.ID_ANY, _("Recent Searches"))
        lbl.Enable(False)
        self.rmenu.AppendSeparator()
        self.SetMenu(self.rmenu)

        # Bind Events
        if wx.Platform in ['__WXMSW__', '__WXGTK__']:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
                    break
        else:
            self.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_MENU, self.OnHistMenu)

    #---- Functions ----#
    def AutoSetQuery(self, multiline=False):
        """Autoload a selected string from the controls client buffer"""
        query = self.FindService.GetClientString(multiline)
        if len(query):
            self.FindService.SetQueryString(query)
            self.SetValue(query)

    def ClearSearchFlag(self, flag):
        """Clears a previously set search flag
        @param flag: flag to clear from search data

        """
        self._flags ^= flag

    def DoSearch(self, next=True):
        """Do the search and move the selection
        @keyword next: search next or previous

        """
        s_cmd = wx.wxEVT_COMMAND_FIND
        if next:
            self.SetSearchFlag(wx.FR_DOWN)
        else:
            if wx.FR_DOWN & self._flags:
                self.ClearSearchFlag(wx.FR_DOWN)

        if self.GetValue() == self._last:
            s_cmd = wx.wxEVT_COMMAND_FIND_NEXT
        self.InsertHistoryItem(self.GetValue())

        self._last = self.GetValue()
        self.FindService.SetQueryString(self.GetValue())
        self.FindService.SetSearchFlags(self._flags)
        self.FindService.OnFind(wx.FindDialogEvent(s_cmd))

        # Give feedback on whether text was found or not
        if self.FindService.GetLastFound() < 0 and len(self.GetValue()) > 0:
            self.SetForegroundColour(wx.RED)
            wx.Bell()
        else:
            # ?wxBUG? cant set text back to black after changing color
            # But setting it to this almost black color works. Most likely its
            # due to bit masking but I havent looked at the source so I am not
            # sure
            self.SetForegroundColour(wx.ColorRGB(0 | 1 | 0))
        self.Refresh()

    def GetSearchData(self):
        """Gets the find data from the controls FindService
        @return: search data
        @rtype: wx.FindReplaceData

        """
        if hasattr(self.FindService, "GetData"):
            return self.FindService.GetData()
        else:
            return None

    def GetHistory(self):
        """Gets and returns the history list of the control
        @return: list of recent search items

        """
        return getattr(self, "_recent", list())

    def InsertHistoryItem(self, value):
        """Inserts a search query value into the top of the history stack
        @param value: search string
        @postcondition: the value is added to the history menu

        """
        if value == wx.EmptyString:
            return

        # Make sure menu only has unique items
        m_items = list(self.rmenu.GetMenuItems())
        for menu_i in m_items:
            if value == menu_i.GetLabel():
                self.rmenu.RemoveItem(menu_i)

        # Create and insert the new item
        n_item = wx.MenuItem(self.rmenu, wx.NewId(), value)
        self.rmenu.InsertItem(2, n_item)

        # Update History list
        self._recent.insert(0, value)
        if len(self._recent) > self.max_menu:
            self._recent.pop()

        # Check Menu Length
        m_len = self.rmenu.GetMenuItemCount()
        if m_len > self.max_menu:
            try:
                self.rmenu.RemoveItem(m_items[-1])
            except IndexError, msg:
                wx.GetApp().GetLog()("[ed_search][err] menu error: %s" % str(msg))

    def IsMatchCase(self):
        """Returns True if the search control is set to search
        in Match Case mode.
        @return: whether search is using match case or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_MATCHCASE & data.GetFlags():
                return True
        return False

    def IsSearchPrevious(self):
        """Returns True if the search control is set to search
        in Previous mode.
        @return: whether search is searchin up or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_DOWN & data.GetFlags():
                return False
        return True

    def IsWholeWord(self):
        """Returns True if the search control is set to search
        in Whole Word mode.
        @return: whether search is using match whole word or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_WHOLEWORD & data.GetFlags():
                return True
        return False

    def SetHistory(self, hist_list):
        """Populates the history list from a list of
        string values.
        @param hist_list: list of search items

        """
        hist_list.reverse()
        for item in hist_list:
            self.InsertHistoryItem(item)

    def SetSearchFlag(self, flags):
        """Sets the search data flags
        @param flags: search flag to add

        """
        self._flags |= flags

    #---- End Functions ----#

    #---- Event Handlers ----#
    def ProcessEvent(self, evt):
        """Processes Events for the Search Control
        @param evt: the event that called this handler

        """
        if evt.GetEventType() != wx.wxEVT_KEY_UP:
            evt.Skip()
            return

        e_key = evt.GetKeyCode()
        if e_key == wx.WXK_ESCAPE:
            # TODO change to more safely determine the context
            # Currently control is only used in command bar
            self.GetParent().Hide()
            return
        elif e_key == wx.WXK_SHIFT:
            self.SetSearchFlag(wx.FR_DOWN)
            return
        else:
            pass

        tmp = self.GetValue()
        self.ShowCancelButton(len(tmp) > 0)

        # Dont do search for navigation keys
        if tmp == wx.EmptyString or evt.CmdDown() or \
           e_key in [wx.WXK_COMMAND, wx.WXK_LEFT, wx.WXK_RIGHT,
                     wx.WXK_UP, wx.WXK_DOWN]:
            return

        s_cmd = wx.wxEVT_COMMAND_FIND
        if e_key == wx.WXK_RETURN or e_key == wx.WXK_F3:
            if evt.ShiftDown():
                self.DoSearch(next=False)
            else:
                self.DoSearch(next=True)
        else:
            self.DoSearch(next=True)

    def OnCancel(self, evt):
        """Cancels the Search Query
        @param evt: the event that called this handler

        """
        self.SetValue(u"")
        self.ShowCancelButton(False)
        evt.Skip()

    def OnHistMenu(self, evt):
        """Sets the search controls value to the selected menu item
        @param evt: the event that called this handler
        @type evt: wx.MenuEvent

        """
        item_id = evt.GetId()
        item = self.rmenu.FindItemById(item_id)
        if item != None:
            self.SetValue(item.GetLabel())
        else:
            evt.Skip()

    #---- End Event Handlers ----#

#-----------------------------------------------------------------------------#

class SearchResultScreen(ctrlbox.ControlBox):
    """Screen for displaying search results and navigating to them"""
    def __init__(self, parent):
        """Create the result screen
        @param parent: parent window

        """
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self._list = SearchResultsList(self)

        # Setup
        ctrlbar = ctrlbox.ControlBar(self)
        ctrlbar.AddStretchSpacer()
        cbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
        if cbmp.IsNull() or not cbmp.IsOk():
            cbmp = None
        clear = platebtn.PlateButton(ctrlbar, wx.ID_CLEAR, _("Clear"),
                                     cbmp, style=platebtn.PB_STYLE_NOBG)
        ctrlbar.AddControl(clear, wx.ALIGN_LEFT)

        # Layout
        self.SetWindow(self._list)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, lambda evt: self._list.Clear(), wx.ID_CLEAR)

#-----------------------------------------------------------------------------#

class SearchResultList(outbuff.OutputBuffer):
    STY_SEARCH_MATCH = outbuff.OPB_STYLE_MAX + 1
    RE_FIND_MATCH = re.compile('(.+?) ([0-9]+)\: .+?')
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)

        # Attributes
        

        # Setup
        font = Profile_Get('FONT1', 'font', wx.Font(11, wx.FONTFAMILY_MODERN, 
                                                    wx.FONTSTYLE_NORMAL, 
                                                    wx.FONTWEIGHT_NORMAL))
        self.SetFont(font)
        style = (font.GetFaceName(), font.GetPointSize(), "#FFFFFF")
        self.StyleSetSpec(SearchResultList.STY_SEARCH_MATCH,
                          "face:%s,size:%d,fore:#000000,back:%s" % style)
        self.StyleSetHotSpot(SearchResultList.STY_SEARCH_MATCH, True)

    def ApplyStyles(self, start, txt):
        """Set a hotspot for each search result
        Search matches strings should be formatted as follows
        /file/name (line) match string
        @param start: long
        @param txt: string

        """
        self.StartStyling(start, 0x1f)
        if SearchResultList.RE_FIND_MATCH(txt):
            self.SetStyling(len(txt), SearchResultList.STY_SEARCH_MATCH)
        else:
            self.SetStyling(len(txt), outbuff.OPB_STYLE_DEFAULT)

    def DoHotspotClicked(self, pos, line):
        """Handle a click on a hotspot
        @param pos: long
        @param line: int

        """
        txt = self.GetLine(line)
        match = SearchResultList.RE_FIND_MATCH.match(txt)
        if match is not None:
            groups = match.groups()
            if len(groups) == 2:
                fname, lnum = groups
                print fname, lnum

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    import sys
    engine = SearchEngine('def [a-zA-Z]+\(')
    for x in engine.SearchInDirectory(sys.argv[1]):
        print x.rstrip()
