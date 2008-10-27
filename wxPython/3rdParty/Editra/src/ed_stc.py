###############################################################################
# Name: ed_stc.py                                                             #
# Purpose: Editra's styled editing buffer                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This is the main component of the editor that manages all the information
of the on disk file that it represents in memory. It works with the StyleManager
and SyntaxManager to provide an editing pane that auto detects and configures
itself for type of file that is in buffer to do highlighting and other language
specific options such as commenting code.

@summary: Editra's main text buffer class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------#
# Imports

import os
import re
import wx, wx.stc

# Local Imports
import ed_event
import ed_glob
from profiler import Profile_Get as _PGET
from syntax import syntax
from autocomp import autocomp
import util
import ed_style
import ed_msg
import ed_txt
import ed_menu
from ed_keyh import KeyHandler, ViKeyHandler

#-------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

# Margin Positions
MARK_MARGIN = 0
NUM_MARGIN  = 1
FOLD_MARGIN = 2

SPACECHARS = " \t\r\n"
NONSPACE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
OPERATORS = "./\?[]{}<>!@#$%^&*():=-+\"';,"

#-------------------------------------------------------------------------#

class EditraStc(wx.stc.StyledTextCtrl, ed_style.StyleMgr):
    """Defines a styled text control for editing text
    @summary: Subclass of wx.stc.StyledTextCtrl and L{ed_style.StyleMgr}.
              Manages the documents display and input.

    """
    ED_STC_MASK_MARKERS = ~wx.stc.STC_MASK_FOLDERS

    def __init__(self, parent, id_,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, use_dt=True):
        """Initializes a control and sets the default objects for
        Tracking events that occur in the control.
        @keyword use_dt: wheter to use a drop target or not

        """
        wx.stc.StyledTextCtrl.__init__(self, parent, id_, pos, size, style)
        ed_style.StyleMgr.__init__(self, self.GetStyleSheet())

        self.SetModEventMask(wx.stc.STC_PERFORMED_UNDO | \
                             wx.stc.STC_PERFORMED_REDO | \
                             wx.stc.STC_MOD_DELETETEXT | \
                             wx.stc.STC_MOD_INSERTTEXT)

        self.CmdKeyAssign(ord('-'), wx.stc.STC_SCMOD_CTRL, \
                          wx.stc.STC_CMD_ZOOMOUT)
        self.CmdKeyAssign(ord('+'), wx.stc.STC_SCMOD_CTRL | \
                          wx.stc.STC_SCMOD_SHIFT, wx.stc.STC_CMD_ZOOMIN)

        #---- Drop Target ----#
        if use_dt and hasattr(parent, 'OnDrop'):
            self.SetDropTarget(util.DropTargetFT(self, None, parent.OnDrop))

        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self.key_handler = KeyHandler(self)

        # File Attributes
        self.file = ed_txt.EdFile()

        # Macro Attributes
        self._macro = list()
        self.recording = False

        # Command/Settings Attributes
        self._config = dict(autocomp=_PGET('AUTO_COMP'),
                            autoindent=_PGET('AUTO_INDENT'),
                            brackethl=_PGET('BRACKETHL'),
                            folding=_PGET('CODE_FOLD'),
                            highlight=_PGET('SYNTAX'))

        # Code Related Objects
        self._code = dict(compsvc=autocomp.AutoCompService(self),
                          synmgr=syntax.SyntaxMgr(ed_glob.CONFIG['CACHE_DIR']),
                          keywords=[ ' ' ],
                          syntax_set=list(),
                          comment=list(),
                          clexer=None,      # Container lexer method
                          indenter=None,    # Auto indenter
                          lang_id=0)        # Language ID from syntax module

        # Set Up Margins
        ## Outer Left Margin Bookmarks
        self.SetMarginType(MARK_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(MARK_MARGIN, self.ED_STC_MASK_MARKERS)
        self.SetMarginSensitive(MARK_MARGIN, True)
        self.SetMarginWidth(MARK_MARGIN, 12)

        ## Middle Left Margin Line Number Indication
        self.SetMarginType(NUM_MARGIN, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(NUM_MARGIN, 0)

        ## Inner Left Margin Setup Folders
        self.SetMarginType(FOLD_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(FOLD_MARGIN, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(FOLD_MARGIN, True)

        # Set Default Styles used by all documents
        self.Configure()
        self.UpdateBaseStyles()

        # Other Settings
        self._menu = MakeMenu()
        self.UsePopUp(False)

        #self.Bind(wx.stc.EVT_STC_MACRORECORD, self.OnRecordMacro)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnModified)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        # Context Menu Events
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: self.PopupMenu(self._menu))

       #---- End Init ----#

    @property
    def __name__(self):
        return u"EditraTextCtrl"

    #---- Protected Member Functions ----#
    def _BuildMacro(self):
        """Constructs a macro script from items in the macro
        record list.
        @status: in limbo

        """
        if not len(self._macro):
            return

        # Get command mappings
        cmds = list()
        for x in dir(wx.stc):
            if x.startswith('STC_CMD_'):
                cmds.append(x)
        cmdvals = [getattr(wx.stc, x) for x in cmds]
        cmds = [x.replace('STC_CMD_', u'') for x in cmds]

        # Get the commands names used in the macro
        named = list()
        for x in self._macro:
            if x[0] in cmdvals:
                named.append(cmds[cmdvals.index(x[0])])
        code = list()

        stc_dict = wx.stc.StyledTextCtrl.__dict__
        for cmd in named:
            for attr in stc_dict:
                if attr.upper() == cmd:
                    code.append(attr)
                    break

        code_txt = u''
        for fun in code:
            code_txt += "    ctrl.%s()\n" % fun
        code_txt += "    print \"Executed\""    #TEST
        code_txt = "def macro(ctrl):\n" + code_txt
        self.GetParent().NewPage()
        self.GetParent().GetCurrentPage().SetText(code_txt)
        self.GetParent().GetCurrentPage().FindLexer('py')
#         code = compile(code_txt, self.__module__, 'exec')
#         exec code in self.__dict__ # Inject new code into this namespace

    #---- Public Member Functions ----#
    def PlayMacro(self):
        """Send the list of built up macro messages to the editor
        to be played back.
        @postcondition: the macro of this control has been played back

        """
        self.BeginUndoAction()
        for msg in self._macro:
            if msg[0] == 2170:
                self.AddText(msg[2])
            elif msg[0] == 2001:
                self.AddText(self.GetEOLChar() + u' ' * (msg[1] - 1))
            else:
                self.SendMsg(msg[0], msg[1], msg[2])
        self.EndUndoAction()

    #---- Begin Function Definitions ----#
    def AddLine(self, before=False):
        """Add a new line to the document
        @param before: whether to add the line before current pos or not
        @postcondition: a new line is added to the document

        """
        line = self.LineFromPosition(self.GetCurrentPos())
        if before:
            line = max(line - 1, 0)

        if line or not before:
            pos = self.GetLineEndPosition(line)
            curr = len(self.GetEOLChar())
        else:
            pos = 0
            curr = 0
        self.InsertText(pos, self.GetEOLChar())
        self.GotoPos(pos + curr)

    def AutoIndent(self):
        """Indent from the current postion to match the indentation
        of the previous line.
        @postcondition: proper type of white space is added from current pos
                        to match that of indentation in above line
        """
        cpos = self.GetCurrentPos()

        # Check if a special purpose indenter has been registered
        if self._code['indenter'] is not None:
            txt = self._code['indenter'](self, cpos, self.GetIndentChar())
            txt = txt.replace('\n', self.GetEOLChar())
        else:
            # Default Indenter
            line = self.GetCurrentLine()
            text = self.GetTextRange(self.PositionFromLine(line), cpos)
            if text.strip() == u'':
                self.AddText(self.GetEOLChar() + text)
                self.EnsureCaretVisible()
                return
            indent = self.GetLineIndentation(line)
            i_space = indent / self.GetTabWidth()
            ndent = self.GetEOLChar() + self.GetIndentChar() * i_space
            txt = ndent + ((indent - (self.GetTabWidth() * i_space)) * u' ')

        self.AddText(txt)
        self.EnsureCaretVisible()

    def Bookmark(self, action):
        """Handles bookmark actions
        @param action: An event ID that describes what is to be done
        @return: None

        """
        lnum = self.GetCurrentLine()
        mark = -1
        if action == ed_glob.ID_ADD_BM:
            if self.MarkerGet(lnum):
                self.MarkerDelete(lnum, MARK_MARGIN)
            else:
                self.MarkerAdd(lnum, MARK_MARGIN)
        elif action == ed_glob.ID_DEL_ALL_BM:
            self.MarkerDeleteAll(MARK_MARGIN)
        elif action == ed_glob.ID_NEXT_MARK:
            if self.MarkerGet(lnum):
                lnum += 1
            mark = self.MarkerNext(lnum, 1)
            if mark == -1:
                mark = self.MarkerNext(0, 1)
        elif action == ed_glob.ID_PRE_MARK:
            if self.MarkerGet(lnum):
                lnum -= 1
            mark = self.MarkerPrevious(lnum, 1)
            if mark == -1:
                mark = self.MarkerPrevious(self.GetLineCount(), 1)

        if mark != -1:
            self.GotoLine(mark)

    def BraceBadLight(self, pos):
        """Highlight the character at the given position
        @param pos: position of character to highlight with STC_STYLE_BRACEBAD

        """
        # Check if we are still alive or not, as this may be called
        # after we have been deleted.
        if isinstance(self, wx.stc.StyledTextCtrl):
            wx.stc.StyledTextCtrl.BraceBadLight(self, pos)

    def BraceHighlight(self, pos1, pos2):
        """Highlight characters at pos1 and pos2
        @param pos1: position of char 1
        @param pos2: position of char 2

        """
        # Check if we are still alive or not, as this may be called
        # after we have been deleted.
        if isinstance(self, wx.stc.StyledTextCtrl):
            wx.stc.StyledTextCtrl.BraceHighlight(self, pos1, pos2)

    def GetBookmarks(self):
        """Gets a list of all lines containing bookmarks
        @return: list of line numbers

        """
        return [mark for mark in xrange(self.GetLineCount()) if self.MarkerGet(mark)]

    def GetBracePair(self):
        """Get a tuple of the positions in the buffer where the brace at the
        current caret position and its match are. if a brace doesn't have a 
        match it will return -1 for the missing brace.
        @return: tuple (brace_at_caret, brace_opposite)

        """
        brace_at_caret = -1
        brace_opposite = -1
        char_before = None
        caret_pos = self.GetCurrentPos()

        if caret_pos > 0:
            char_before = self.GetCharAt(caret_pos - 1)

        # check before
        if char_before and unichr(char_before) in "[]{}()<>":
            brace_at_caret = caret_pos - 1

        # check after
        if brace_at_caret < 0:
            char_after = self.GetCharAt(caret_pos)
            if char_after and chr(char_after) in "[]{}()<>":
                brace_at_caret = caret_pos

        if brace_at_caret >= 0:
            brace_opposite = self.BraceMatch(brace_at_caret)

        return (brace_at_caret, brace_opposite)

    def Configure(self):
        """Configures the editors settings by using profile values
        @postcondition: all profile dependant attributes are configured

        """
#        self.SetControlCharSymbol(172)
        self.SetWrapMode(_PGET('WRAP', 'bool'))
        self.SetViewWhiteSpace(_PGET('SHOW_WS', 'bool'))
        self.SetUseAntiAliasing(_PGET('AALIASING'))
        self.SetUseTabs(_PGET('USETABS'))
        self.SetBackSpaceUnIndents(_PGET('BSUNINDENT'))
        self.SetCaretLineVisible(_PGET('HLCARETLINE'))
        self.SetIndent(_PGET('INDENTWIDTH', 'int'))
        self.SetTabWidth(_PGET('TABWIDTH', 'int'))
#        self.SetTabIndents(True) # Add option for this too?
        self.SetIndentationGuides(_PGET('GUIDES'))
        self.SetEOLFromString(_PGET('EOL'))
        self.SetViewEOL(_PGET('SHOW_EOL'))
        self.SetAutoComplete(_PGET('AUTO_COMP'))
        self.FoldingOnOff(_PGET('CODE_FOLD'))
        self.ToggleAutoIndent(_PGET('AUTO_INDENT'))
        self.ToggleBracketHL(_PGET('BRACKETHL'))
        self.ToggleLineNumbers(_PGET('SHOW_LN'))
        self.SetViEmulationMode(_PGET('VI_EMU'))
        self.SetViewEdgeGuide(_PGET('SHOW_EDGE'))

    def Comment(self, uncomment=False):
        """(Un)Comments a line or a selected block of text
        in a document.
        @param uncomment: uncomment selection

        """
        if len(self._code['comment']):
            sel = self.GetSelection()
            start = self.LineFromPosition(sel[0])
            end = self.LineFromPosition(sel[1])
            c_start = self._code['comment'][0]
            c_end = u''
            if len(self._code['comment']) > 1:
                c_end = self._code['comment'][1]
            if end > start and self.GetColumn(sel[1]) == 0:
                end = end - 1

            self.BeginUndoAction()
            try:
                nchars = 0
                lines = range(start, end+1)
                lines.reverse()
                for line_num in lines:
                    lstart = self.PositionFromLine(line_num)
                    lend = self.GetLineEndPosition(line_num)
                    text = self.GetTextRange(lstart, lend)
                    tmp = text.strip()
                    if len(tmp):
                        if uncomment:
                            if tmp.startswith(c_start):
                                text = text.replace(c_start, u'', 1)
                            if c_end and tmp.endswith(c_end):
                                text = text.replace(c_end, u'', 1)
                            nchars = nchars - len(c_start + c_end)
                        else:
                            text = c_start + text + c_end
                            nchars = nchars + len(c_start + c_end)

                        self.SetTargetStart(lstart)
                        self.SetTargetEnd(lend)
                        self.ReplaceTarget(text)
            finally:
                self.EndUndoAction()
                if sel[0] != sel[1]:
                    self.SetSelection(sel[0], sel[1] + nchars)
                else:
                    if len(self._code['comment']) > 1:
                        nchars = nchars - len(self._code['comment'][1])
                    self.GotoPos(sel[0] + nchars)

    def CanCopy(self):
        """Check if copy/cut is possible"""
        return self.GetSelectionStart() != self.GetSelectionEnd()

    def ConvertCase(self, upper=False):
        """Converts the case of the selected text to either all lower
        case(default) or all upper case.
        @keyword upper: Flag whether conversion is to upper case or not.

        """
        if upper:
            self.UpperCase()
        else:
            self.LowerCase()

    def InvertCase(self):
        """Invert the case of the selected text
        @postcondition: all text in selection has case inverted

        """
        text = self.GetSelectedText()
        if len(text):
            self.BeginUndoAction()
            self.ReplaceSelection(text.swapcase())
            self.EndUndoAction()

    def GetAutoIndent(self):
        """Returns whether auto-indent is being used
        @return: whether autoindent is active or not
        @rtype: bool

        """
        return self._config['autoindent']

    def GetCommentChars(self):
        """Return the list of characters used to comment a string in the
        current language.
        @return: list of strings

        """
        return self._code['comment']

    def GetLangId(self):
        """Returns the language identifer of this control
        @return: language identifier of document
        @rtype: int

        """
        return self._code['lang_id']

    def GetLineStartPosition(self, line):
        """Get the starting position of the given line
        @param line: int
        @return: int

        """
        if line > 0:
            spos = self.GetLineEndPosition(line-1)
            if self.GetLine(line).endswith("\r\n"):
                spos += 2
            else:
                spos += 1
        else:
            spos = 0
        return spos

    def GetLastVisibleLine(self):
        """Return what the last visible line is
        @return: int

        """
        return self.GetFirstVisibleLine() + self.LinesOnScreen() - 1

    def GetMiddleVisibleLine(self):
        """Return the number of the line that is in the middle of the display
        @return: int

        """
        fline = self.GetFirstVisibleLine()
        if self.LinesOnScreen() < self.GetLineCount():
            mid = (fline + (self.LinesOnScreen() / 2))
        else:
            mid = (fline + (self.GetLineCount() / 2))
        return mid

    def GetModTime(self):
        """Get the value of the buffers file last modtime"""
        return self.file.GetModtime()

    def GetPos(self):
        """Update Line/Column information
        @return: tuple (line, column)

        """
        return (self.GetCurrentLine() + 1, self.GetColumn(self.GetCurrentPos()))

    def GotoBraceMatch(self):
        """Jump the caret to the brace opposite of the one the caret is
        currently at. If there is no match or the caret currently is not next
        to a brace no action is taken.
        @return: bool

        """
        cbrace, brace_opposite = self.GetBracePair()
        if -1 in (cbrace, brace_opposite):
            return False
        else:
            self.GotoPos(brace_opposite)
            return True

    def GotoColumn(self, column):
        """Move caret to column of current line
        @param column: Column to move to

        """
        cline = self.GetCurrentLineNum()
        lstart = self.PositionFromLine(cline)
        lend = self.GetLineEndPosition(cline)
        linelen = lend - lstart
        if column > linelen:
            column = linelen
        self.GotoPos(lstart + column)

    def GotoLine(self, line):
        """Move caret to begining given line number
        @param line: line to go to

        """
        if line > self.GetLineCount():
            line = self.GetLineCount()
        elif line < 0:
            line = 0
        else:
            pass

        self.SetYCaretPolicy(wx.stc.STC_CARET_STRICT, 0)
        wx.stc.StyledTextCtrl.GotoLine(self, line)
        self.SetYCaretPolicy(wx.stc.STC_CARET_EVEN, 0)

    def SetCurrentCol(self, column):
        """Set the current column position on the currently line
        extending the selection.
        @param column: Column to move to

        """
        cline = self.GetCurrentLineNum()
        lstart = self.PositionFromLine(cline)
        lend = self.GetLineEndPosition(cline)
        linelen = lend - lstart
        if column > linelen:
            column = linelen
        self.SetCurrentPos(lstart + column)

    def GotoIndentPos(self, line):
        """Move the caret to the end of the indentation
        on the given line.
        @param line: line to go to

        """
        self.GotoPos(self.GetLineIndentPosition(line))

    def DefineMarkers(self):
        """Defines the folder and bookmark icons for this control
        @postcondition: all margin markers are defined

        """
        style = self.GetItemByName('foldmargin_style')
        # The foreground/background settings for the marker column seem to
        # backwards from what the parameters take so use our Fore color for
        # the stcs back and visa versa for our Back color.
        back = style.GetFore()
        rgb = util.HexToRGB(back[1:])
        back = wx.Colour(red=rgb[0], green=rgb[1], blue=rgb[2])

        fore = style.GetBack()
        rgb = util.HexToRGB(fore[1:])
        fore = wx.Colour(red=rgb[0], green=rgb[1], blue=rgb[2])

        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,
                          wx.stc.STC_MARK_BOXMINUS, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,
                          wx.stc.STC_MARK_BOXPLUS,  fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,
                          wx.stc.STC_MARK_VLINE, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,
                          wx.stc.STC_MARK_LCORNER, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,
                          wx.stc.STC_MARK_BOXPLUSCONNECTED, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID,
                          wx.stc.STC_MARK_BOXMINUSCONNECTED, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL,
                          wx.stc.STC_MARK_TCORNER, fore, back)
        self.MarkerDefine(0, wx.stc.STC_MARK_SHORTARROW, fore, back)
        self.SetFoldMarginHiColour(True, fore)
        self.SetFoldMarginColour(True, fore)

    def FindTagById(self, style_id):
        """Find the style tag that is associated with the given
        Id. If not found it returns an empty string.
        @param style_id: id of tag to look for
        @return: style tag string
        @todo: change syntax modules to all use ids

        """
        for data in self._code['syntax_set']:
            # If its a standard lexer the style id will be stored as
            # a string. If its a container lexer it is the id.
            if isinstance(data[0], basestring):
                s_id = getattr(wx.stc, data[0])
            else:
                s_id = data[0]

            if style_id == s_id:
                return data[1]

        return 'default_style'

    def GetAutoComplete(self):
        """Is Autocomplete being used by this instance
        @return: whether autocomp is active or not

        """
        return self._config['autocomp']

    def GetFileName(self):
        """Returns the full path name of the current file
        @return: full path name of document

        """
        return self.file.GetPath()

    def GetDocument(self):
        """Return a reference to the document object represented in this buffer.
        @return: EdFile
        @see: L{ed_txt.EdFile}

        """
        return self.file

    def GetStyleSheet(self, sheet_name=None):
        """Finds the current style sheet and returns its path. The
        Lookup is done by first looking in the users config directory
        and if it is not found there it looks for one on the system
        level and if that fails it returns None.
        @param sheet_name: style sheet to look for
        @return: full path to style sheet

        """
        if sheet_name:
            style = sheet_name
            if sheet_name.split(u'.')[-1] != u"ess":
                style += u".ess"
        elif _PGET('SYNTHEME', 'str').split(u'.')[-1] != u"ess":
            style = (_PGET('SYNTHEME', 'str') + u".ess").lower()
        else:
            style = _PGET('SYNTHEME', 'str').lower()

        # Get Correct Filename if it exists
        for sheet in util.GetResourceFiles('styles', False, True, title=False):
            if sheet.lower() == style.lower():
                style = sheet
                break

        user = os.path.join(ed_glob.CONFIG['STYLES_DIR'], style)
        sysp = os.path.join(ed_glob.CONFIG['SYS_STYLES_DIR'], style)
        if os.path.exists(user):
            return user
        elif os.path.exists(sysp):
            return sysp
        else:
            return None

    def OnKeyDown(self, evt):
        """Handles keydown events, currently only deals with
        auto indentation.
        @param evt: event that called this handler
        @type evt: wx.KeyEvent

        """
        k_code = evt.GetKeyCode()
        if self.key_handler.PreProcessKey(k_code, evt.ControlDown(),
                                          evt.CmdDown(), evt.ShiftDown(),
                                          evt.AltDown()):
            return                

        if k_code == wx.WXK_RETURN:

            if self._config['autoindent'] and not self.AutoCompActive():
                if self.GetSelectedText():
                    self.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
                else:
                    self.AutoIndent()
            else:
                evt.Skip()

            if self.CallTipActive():
                self.CallTipCancel()

        else:
            evt.Skip()

    def OnChar(self, evt):
        """Handles Char events that arent caught by the
        KEY_DOWN event.
        @param evt: event that called this handler
        @type evt: wx.EVT_CHAR
        @todo: autocomp/calltip lookup can be very cpu intesive it may
               be better to try and process it on a separate thread to
               prevent a slow down in the input of text into the buffer

        """
        key_code = evt.GetKeyCode()
        cpos = self.GetCurrentPos()
        if self.key_handler.ProcessKey(key_code, evt.ControlDown(),
                                       evt.CmdDown(), evt.ShiftDown(),
                                       evt.AltDown()):
            # The key handler handled this keypress, we don't need to insert
            # the character into the buffer.
            pass
        elif not self._config['autocomp'] or \
             self.IsString(cpos) or \
             self.IsComment(cpos):
            evt.Skip()
            return
        elif key_code in self._code['compsvc'].GetAutoCompKeys():
            if self.AutoCompActive():
                self.AutoCompCancel()
            command = self.GetCommandStr() + unichr(key_code)
            self.AddText(unichr(key_code))
            if self._config['autocomp']:
                self.ShowAutoCompOpt(command)
        elif key_code in self._code['compsvc'].GetCallTipKeys():
            if self.AutoCompActive():
                self.AutoCompCancel()
            command = self.GetCommandStr()
            self.AddText(unichr(key_code))
            if self._config['autocomp']:
                self.ShowCallTip(command)
        else:
            evt.Skip()
        return

    def OnKeyUp(self, evt):
        """Update status bar of window
        @param evt: wxEVT_KEY_UP

        """
        evt.Skip()
        self.PostPositionEvent()
        ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_KEYUP,
                           (evt.GetPositionTuple(), evt.GetKeyCode()))

    def PostPositionEvent(self):
        """Post an event to update the status of the line/column"""
        msg = _("Line: %d  Column: %d") % self.GetPos()
        nevt = ed_event.StatusEvent(ed_event.edEVT_STATUS, self.GetId(),
                                    msg, ed_glob.SB_ROWCOL)
        wx.PostEvent(self.GetTopLevelParent(), nevt)

    def OnRecordMacro(self, evt):
        """Records macro events
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        if self.IsRecording():
            msg = evt.GetMessage()
            if msg == 2170:
                lparm = self.GetTextRange(self.GetCurrentPos()-1, \
                                          self.GetCurrentPos())
            else:
                lparm = evt.GetLParam()
            mac = (msg, evt.GetWParam(), lparm)
            self._macro.append(mac)
#             if mac[0] != 2170:
#                 self._macro.append(mac)
        else:
            evt.Skip()

    def OnStyleNeeded(self, evt):
        """Perform custom styling when registered for a container lexer"""
        if self._code['clexer'] is not None:
            self._code['clexer'](self, self.GetEndStyled(), evt.GetPosition())
        else:
            evt.Skip()

    def ParaDown(self):
        """Move the caret one paragraph down
        @note: overrides the default function to set caret at end
               of paragraph instead of jumping to start of next

        """
        self.WordPartRight()
        wx.stc.StyledTextCtrl.ParaDown(self)
        if self.GetCurrentPos() != self.GetLength():
            self.WordPartLeft()
            self.GotoPos(self.GetCurrentPos() + len(self.GetEOLChar()))

    def ParaDownExtend(self):
        """Extend the selection a paragraph down
        @note: overrides the default function to set selection at end
               of paragraph instead of jumping to start of next so that
               extra blank lines don't get swallowed.

        """
        self.WordRightExtend()
        wx.stc.StyledTextCtrl.ParaDownExtend(self)
        if self.GetCurrentPos() != self.GetLength():
            self.WordLeftExtend()
            self.SetCurrentPos(self.GetCurrentPos() + len(self.GetEOLChar()))

    def GetCommandStr(self):
        """Gets the command string to the left of the autocomp
        activation character.
        @return: the command string to the left of the autocomp char

        """
        curr_pos = self.GetCurrentPos()
        start = curr_pos - 1
        col = self.GetColumn(curr_pos)
        cmd_lmt = list(self._code['compsvc'].GetAutoCompStops())
        for key in self._code['compsvc'].GetAutoCompKeys():
            kval = chr(key)
            if kval in cmd_lmt:
                cmd_lmt.remove(kval)

        while self.GetTextRange(start, curr_pos)[0] not in cmd_lmt \
              and col - (curr_pos - start) > 0:
            start -= 1

        if self.GetColumn(start) != 0:
            start += 1
        cmd = self.GetTextRange(start, curr_pos)
        return cmd.strip()

    def ShowAutoCompOpt(self, command):
        """Shows the autocompletion options list for the command
        @param command: command to look for autocomp options for

        """
        lst = self._code['compsvc'].GetAutoCompList(command)
        if len(lst):
            self.AutoCompShow(0, u' '.join(lst))
            self.SetFocus()

    def ShowCallTip(self, command):
        """Shows call tip for given command
        @param command: command to  look for calltips for

        """
        if self.CallTipActive():
            self.CallTipCancel()

        tip = self._code['compsvc'].GetCallTip(command)
        if len(tip):
            curr_pos = self.GetCurrentPos()
            tip_pos = curr_pos - (len(command.split('.')[-1]) + 1)
            fail_safe = curr_pos - self.GetColumn(curr_pos)
            self.CallTipShow(max(tip_pos, fail_safe), tip)

    def ShowKeywordHelp(self):
        """Displays the keyword helper
        @postcondition: keyword helper list is shown if it currently is not
                        otherwise it is hidden.

        """
        if self.AutoCompActive():
            self.AutoCompCancel()
        elif len(self._code['keywords']) > 1:
            pos = self.GetCurrentPos()
            pos2 = self.WordStartPosition(pos, True)
            self.AutoCompShow(pos - pos2, self._code['keywords'])
        return

    def OnLeftUp(self, evt):
        """Set primary selection and inform mainwindow that cursor position 
        has changed.
        @param evt: wx.MouseEvent()

        """
        evt.Skip()
        # FIXME: there is problems with using the primary selection. Setting
        #        the primary selection causes anything else on the clipboard
        #        to get killed.
#        stxt = self.GetSelectedText()
#        if len(stxt):
#            util.SetClipboardText(stxt, primary=True)
        self.PostPositionEvent()

    def OnModified(self, evt):
        """Handles updates that need to take place after
        the control has been modified.
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        # Adjust line number margin width to expand as needed when line
        # number width over fills the area.
        lines = self.GetLineCount()
        mwidth = self.GetTextExtent(str(lines))[0]

        if wx.Platform == '__WXMAC__':
            adj = 2
        else:
            adj = 8

        self.SetMarginWidth(NUM_MARGIN, max(15, mwidth + adj))

        wx.PostEvent(self.GetParent(), evt)

    def OnUpdateUI(self, evt):
        """Check for matching braces
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        brace_at_caret, brace_opposite = self.GetBracePair()
        # CallAfter necessary to reduce CG warnings on Mac
        if brace_at_caret != -1  and brace_opposite == -1:
            wx.CallAfter(self.BraceBadLight, brace_at_caret)
        else:
            wx.CallAfter(self.BraceHighlight, brace_at_caret, brace_opposite)

    def OnMarginClick(self, evt):
        """Open and Close Folders as Needed
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        if evt.GetMargin() == FOLD_MARGIN:
            if evt.GetShift() and \
               (evt.GetControl() or (wx.Platform == '__WXMAC__' and evt.GetAlt())):
                self.FoldAll()
            else:
                line_clicked = self.LineFromPosition(evt.GetPosition())
                level = self.GetFoldLevel(line_clicked)
                if level & wx.stc.STC_FOLDLEVELHEADERFLAG:

                    # Expand node and all Subnodes
                    if evt.GetShift():
                        self.SetFoldExpanded(line_clicked, True)
                        self.Expand(line_clicked, True, True, 100, level)
                    elif evt.GetControl() or \
                        (wx.Platform == '__WXMAC__' and evt.GetAlt()):
                        # Contract all subnodes of clicked one
                        # Note: using Alt as Ctrl can not be recieved for
                        # clicks on mac (Scintilla Bug).
                        if self.GetFoldExpanded(line_clicked):
                            self.SetFoldExpanded(line_clicked, False)
                            self.Expand(line_clicked, False, True, 0, level)
                        else:
                            # Expand all subnodes
                            self.SetFoldExpanded(line_clicked, True)
                            self.Expand(line_clicked, True, True, 100, level)
                    else:
                        self.ToggleFold(line_clicked)
        elif evt.GetMargin() == MARK_MARGIN:
            # Bookmarks ect...
            line_clicked = self.LineFromPosition(evt.GetPosition())
            if self.MarkerGet(line_clicked):
                self.MarkerDelete(line_clicked, MARK_MARGIN)
            else:
                self.MarkerAdd(line_clicked, MARK_MARGIN)

    def FoldAll(self):
        """Fold Tree In or Out
        @postcondition: code tree is folded open or closed

        """
        line_count = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for line_num in xrange(line_count):
            if self.GetFoldLevel(line_num) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(line_num)
                break
        line_num = 0

        while line_num < line_count:
            level = self.GetFoldLevel(line_num)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
               (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == \
               wx.stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(line_num, True)
                    line_num = self.Expand(line_num, True) - 1
            else:
                last_child = self.GetLastChild(line_num, -1)
                self.SetFoldExpanded(line_num, False)

                if last_child > line_num:
                    self.HideLines(line_num + 1, last_child)
            line_num = line_num + 1

    def Expand(self, line, do_expand, force=False, vis_levels=0, level=-1):
        """Open the Margin Folder
        @postcondition: the selected folder is expanded

        """
        last_child = self.GetLastChild(line, level)
        line = line + 1

        while line <= last_child:
            if force:
                if vis_levels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if do_expand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    self.SetFoldExpanded(line, vis_levels > 1)
                    line = self.Expand(line, do_expand, force, vis_levels - 1)
                else:
                    if do_expand:
                        if self.GetFoldExpanded(line):
                            self.SetFoldExpanded(line, True)
                    line = self.Expand(line, do_expand, force, vis_levels - 1)
            else:
                line = line + 1
        return line

    def FindLexer(self, set_ext=u''):
        """Sets Text Controls Lexer Based on File Extension
        @param set_ext: explicit extension to use in search
        @postcondition: lexer is configured for file

        """
        if not self._config['highlight']:
            return 2

        if set_ext != u'':
            ext = set_ext.lower()
        else:
            ext = self.file.GetExtension()
        self.ClearDocumentStyle()

        # Configure Lexer from File Extension
        self.ConfigureLexer(ext)

        # If syntax auto detection fails from file extension try to
        # see if there is an interpreter line that can be parsed.
        if self.GetLexer() == wx.stc.STC_LEX_NULL:
            interp = self.GetLine(0)
            if interp != wx.EmptyString:
                interp = interp.split(u"/")[-1]
                interp = interp.strip().split()
                if len(interp) and interp[-1][0] != "-":
                    interp = interp[-1]
                elif len(interp):
                    interp = interp[0]
                else:
                    interp = u''
                ex_map = { "python" : "py", "wish" : "tcl", "ruby" : "rb",
                           "bash" : "sh", "csh" : "csh", "perl" : "pl",
                           "ksh" : "ksh", "php" : "php", "booi" : "boo",
                           "pike" : "pike"}
                self.ConfigureLexer(ex_map.get(interp, interp))
        self.Colourise(0, -1)

        # Configure Autocompletion
        # NOTE: must be done after syntax configuration
        if self._config['autocomp']:
            self.ConfigureAutoComp()
        return 0

    def ControlDispatch(self, evt):
        """Dispatches events caught from the mainwindow to the
        proper functions in this module.
        @param evt: event that was posted to this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_map = { ed_glob.ID_COPY  : self.Copy, ed_glob.ID_CUT  : self.Cut,
                  ed_glob.ID_PASTE : self.Paste, ed_glob.ID_UNDO : self.Undo,
                  ed_glob.ID_REDO  : self.Redo, ed_glob.ID_INDENT : self.Tab,
                  ed_glob.ID_REVERT_FILE : self.RevertToSaved,
                  ed_glob.ID_KWHELPER: self.ShowKeywordHelp,
                  ed_glob.ID_CUT_LINE : self.LineCut,
                  ed_glob.ID_COPY_LINE : self.LineCopy,
                  ed_glob.ID_DUP_LINE : self.LineDuplicate,
                  ed_glob.ID_BRACKETHL : self.ToggleBracketHL,
                  ed_glob.ID_SYNTAX : self.SyntaxOnOff,
                  ed_glob.ID_UNINDENT : self.BackTab,
                  ed_glob.ID_TRANSPOSE : self.LineTranspose,
                  ed_glob.ID_SELECTALL: self.SelectAll,
                  ed_glob.ID_FOLDING : self.FoldingOnOff,
                  ed_glob.ID_SHOW_LN : self.ToggleLineNumbers,
                  ed_glob.ID_COMMENT : self.Comment,
                  ed_glob.ID_AUTOINDENT : self.ToggleAutoIndent,
                  ed_glob.ID_LINE_AFTER : self.AddLine,
                  ed_glob.ID_TRIM_WS : self.TrimWhitespace,
                  ed_glob.ID_MACRO_START : self.StartRecord,
                  ed_glob.ID_MACRO_STOP : self.StopRecord,
                  ed_glob.ID_MACRO_PLAY : self.PlayMacro,
                  ed_glob.ID_GOTO_MBRACE : self.GotoBraceMatch
        }

        e_idmap = { ed_glob.ID_ZOOM_OUT : self.DoZoom,
                    ed_glob.ID_ZOOM_IN  : self.DoZoom,
                    ed_glob.ID_ZOOM_NORMAL : self.DoZoom,
                    ed_glob.ID_EOL_MAC  : self.ConvertLineMode,
                    ed_glob.ID_EOL_UNIX : self.ConvertLineMode,
                    ed_glob.ID_EOL_WIN  : self.ConvertLineMode,
                    ed_glob.ID_SPACE_TO_TAB : self.ConvertWhitespace,
                    ed_glob.ID_TAB_TO_SPACE : self.ConvertWhitespace,
                    ed_glob.ID_NEXT_MARK : self.Bookmark,
                    ed_glob.ID_PRE_MARK  : self.Bookmark,
                    ed_glob.ID_ADD_BM    : self.Bookmark,
                    ed_glob.ID_DEL_ALL_BM : self.Bookmark}

        if self.CallTipActive():
            self.CallTipCancel()

        if self.AutoCompActive():
            self.AutoCompCancel()

        if e_obj.GetClassName() == "wxToolBar" or e_map.has_key(e_id):
            if e_map.has_key(e_id):
                e_map[e_id]()
            return

        if e_id in e_idmap:
            e_idmap[e_id](e_id)
        elif e_id == ed_glob.ID_SHOW_EDGE:
            self.SetViewEdgeGuide(not self.GetEdgeMode())
        elif e_id == ed_glob.ID_SHOW_EOL:
            self.SetViewEOL(not self.GetViewEOL())
        elif e_id == ed_glob.ID_SHOW_WS:
            self.SetViewWhiteSpace(not self.GetViewWhiteSpace())
        elif e_id == ed_glob.ID_WORD_WRAP:
            self.SetWrapMode(not self.GetWrapMode())
        elif e_id == ed_glob.ID_JOIN_LINES:
            self.SetTargetStart(self.GetSelectionStart())
            self.SetTargetEnd(self.GetSelectionEnd())
            self.LinesJoin()
        elif e_id == ed_glob.ID_INDENT_GUIDES:
            self.SetIndentationGuides(not bool(self.GetIndentationGuides()))
        elif e_id == ed_glob.ID_HLCARET_LINE:
            self.SetCaretLineVisible(not self.GetCaretLineVisible())
        elif e_id in syntax.SyntaxIds():
            f_ext = syntax.GetExtFromId(e_id)
            self.LOG("[ed_stc][evt] Manually Setting Lexer to %s" % str(f_ext))
            self.FindLexer(f_ext)
        elif e_id == ed_glob.ID_AUTOCOMP:
            self.SetAutoComplete(not self.GetAutoComplete())
        elif e_id == ed_glob.ID_UNCOMMENT:
            self.Comment(True)
        elif e_id == ed_glob.ID_LINE_BEFORE:
            self.AddLine(before=True)
        elif e_id in [ed_glob.ID_TO_UPPER, ed_glob.ID_TO_LOWER]:
            self.ConvertCase(e_id == ed_glob.ID_TO_UPPER)
        elif e_id == ed_glob.ID_USE_SOFTTABS:
            self.SetUseTabs(not self.GetUseTabs())
        else:
            evt.Skip()

    def CheckEOL(self):
        """Checks the EOL mode of the opened document. If the mode
        that the document was saved in is different than the editors
        current mode the editor will switch modes to preserve the eol
        type of the file, if the eol chars are mixed then the editor
        will toggle on eol visibility.
        @postcondition: eol mode is configured to best match file
        @todo: Is showing line endings the best way to show mixed?

        """
        mixed = diff = False
        eol_map = {"\n" : wx.stc.STC_EOL_LF,
                   "\r\n" : wx.stc.STC_EOL_CRLF,
                   "\r" : wx.stc.STC_EOL_CR}
        eol = chr(self.GetCharAt(self.GetLineEndPosition(0)))
        if eol == "\r":
            tmp = chr(self.GetCharAt(self.GetLineEndPosition(0) + 1))
            if tmp == "\n":
                eol += tmp
        if eol != self.GetEOLChar():
            diff = True
        for line in range(self.GetLineCount() - 1):
            end = self.GetLineEndPosition(line)
            tmp = chr(self.GetCharAt(end))
            if tmp == "\r":
                tmp2 = chr(self.GetCharAt(self.GetLineEndPosition(0) + 1))
                if tmp2 == "\n":
                    tmp += tmp2
            if tmp != eol:
                mixed = True
                break

        if mixed or diff:
            if mixed:
                self.SetViewEOL(True)
            else:
                self.SetEOLMode(eol_map.get(eol, wx.stc.STC_EOL_LF))
        else:
            pass

    def ConvertLineMode(self, mode_id):
        """Converts all line endings in a document to a specified
        format.
        @param mode_id: id of eol mode to set

        """
        eol_map = { ed_glob.ID_EOL_MAC  : wx.stc.STC_EOL_CR,
                    ed_glob.ID_EOL_UNIX : wx.stc.STC_EOL_LF,
                    ed_glob.ID_EOL_WIN  : wx.stc.STC_EOL_CRLF
                  }
        self.ConvertEOLs(eol_map[mode_id])
        self.SetEOLMode(eol_map[mode_id])

    def ConvertWhitespace(self, mode_id):
        """Convert whitespace from using tabs to spaces or visa versa
        @param mode_id: id of conversion mode

        """
        if mode_id not in (ed_glob.ID_TAB_TO_SPACE, ed_glob.ID_SPACE_TO_TAB):
            return
        tabw = self.GetIndent()
        pos = self.GetCurrentPos()
        sel = self.GetSelectedText()
        if mode_id == ed_glob.ID_TAB_TO_SPACE:
            cmd = (u"\t", u" " * tabw)
            tabs = False
        else:
            cmd = (" " * tabw, u"\t")
            tabs = True

        if sel != wx.EmptyString:
            self.ReplaceSelection(sel.replace(cmd[0], cmd[1]))
        else:
            self.BeginUndoAction()
            part1 = self.GetTextRange(0, pos).replace(cmd[0], cmd[1])
            tmptxt = self.GetTextRange(pos, self.GetLength()).replace(cmd[0], \
                                                                      cmd[1])
            self.SetText(part1 + tmptxt)
            self.GotoPos(len(part1))
            self.SetUseTabs(tabs)
            self.EndUndoAction()

    def GetCurrentLineNum(self):
        """Return the number of the line that the caret is currently at
        @return: Line number (int)

        """
        return self.LineFromPosition(self.GetCurrentPos())

    def GetEOLChar(self):
        """Gets the eol character used in document
        @return: the character used for eol in this document

        """
        m_id = self.GetEOLModeId()
        if m_id == ed_glob.ID_EOL_MAC:
            return u'\r'
        elif m_id == ed_glob.ID_EOL_WIN:
            return u'\r\n'
        else:
            return u'\n'

    def GetIndentChar(self):
        """Gets the indentation char used in document
        @return: indentation char used either space or tab

        """
        if self.GetUseTabs():
            return u'\t'
        else:
            return u' ' * self.GetIndent()

    def GetEOLModeId(self):
        """Gets the id of the eol format
        @return: id of the eol mode of this document

        """
        eol_map = { wx.stc.STC_EOL_CR : ed_glob.ID_EOL_MAC,
                    wx.stc.STC_EOL_LF : ed_glob.ID_EOL_UNIX,
                    wx.stc.STC_EOL_CRLF : ed_glob.ID_EOL_WIN
                  }
        return eol_map.get(self.GetEOLMode(), ed_glob.ID_EOL_UNIX)

    def IsBracketHlOn(self):
        """Returns whether bracket highlighting is being used by this
        control or not.
        @return: status of bracket highlight activation

        """
        return self._config['brackethl']

    def IsComment(self, pos):
        """Is the given position in a comment region of the current buffer
        @param pos: int position in buffer
        @return: bool

        """
        return 'comment' in self.FindTagById(self.GetStyleAt(pos))

    def IsFoldingOn(self):
        """Returns whether code folding is being used by this
        control or not.
        @return: whether folding is on or not

        """
        return self._config['folding']

    def IsHighlightingOn(self):
        """Returns whether syntax highlighting is being used by this
        control or not.
        @return: whether syntax highlighting is on or not

        """
        return self._config['highlight']

    def IsRecording(self):
        """Returns whether the control is in the middle of recording
        a macro or not.
        @return: whether recording macro or not

        """
        return self.recording

    def IsString(self, pos):
        """Is the given position in a string region of the current buffer
        @param pos: int position in buffer
        @return: bool

        """
        style = self.GetStyleAt(pos)
        return self.FindTagById(style) in ('string_style', 'char_style')

    def LinesJoin(self):
        """Join lines in target and compress whitespace
        @note: overrides default function to allow for leading
               whitespace in joined lines to be compressed to 1 space

        """
        sline = self.LineFromPosition(self.GetTargetStart())
        eline = self.LineFromPosition(self.GetTargetEnd())
        if not eline:
            eline = 1
        lines = list()
        for line in xrange(sline, eline + 1):
            if line != sline:
                tmp = self.GetLine(line).strip()
            else:
                tmp = self.GetLine(line)
                if not tmp.isspace():
                    tmp = tmp.rstrip()
                else:
                    tmp = tmp.replace("\n", u'').replace("\r", u'')
            if len(tmp):
                lines.append(tmp)
        self.SetTargetStart(self.PositionFromLine(sline))
        self.SetTargetEnd(self.GetLineEndPosition(eline))
        self.ReplaceTarget(u' '.join(lines))

    def LineTranspose(self):
        """Switch the current line with the previous one
        @note: overrides base stc method to do transpose in single undo action

        """
        self.BeginUndoAction()
        wx.stc.StyledTextCtrl.LineTranspose(self)
        self.EndUndoAction()

    def SetAutoComplete(self, value):
        """Turns Autocompletion on and off
        @param value: use autocomp or not
        @type value: bool

        """
        if isinstance(value, bool):
            self._config['autocomp'] = value
            if value:
                self._code['compsvc'].LoadCompProvider(self.GetLexer())

    def SetDocument(self, doc):
        """Change the document object used.
        @param doc: an L{ed_txt.EdFile} instance

        """
        del self.file
        self.file = doc

    def SetEncoding(self, enc):
        """Sets the encoding of the current document
        @param enc: encoding to set for document

        """
        self.file.SetEncoding(enc)

    def SetEOLFromString(self, mode_str):
        """Sets the EOL mode from a string descript
        @param mode_str: eol mode to set
        @todo: get rid of this somehow

        """
        mode_map = { 'Macintosh (\\r)' : wx.stc.STC_EOL_CR,
                     'Unix (\\n)' : wx.stc.STC_EOL_LF,
                     'Windows (\\r\\n)' : wx.stc.STC_EOL_CRLF
                   }
        mode = mode_map.get(mode_str, wx.stc.STC_EOL_LF)
        self.SetEOLMode(mode)

    def SetFileName(self, path):
        """Set the buffers filename attributes from the given path"""
        self.file.SetPath(path)

    def SetFocus(self):
        """Set the focus to this control
        @note: overriden as a hack for msw

        """
        wx.stc.StyledTextCtrl.SetFocus(self)
        if wx.Platform == '__WXMSW__':
            wx.PostEvent(self, wx.FocusEvent(wx.wxEVT_SET_FOCUS, self.GetId()))

    def SetLexer(self, lexer):
        """Set the buffers lexer
        @param lexer: lexer to use
        @note: Overrides StyledTextCtrl.SetLexer

        """
        if lexer == wx.stc.STC_LEX_CONTAINER:
            # If setting a container lexer only bind the event if it hasn't
            # been done yet.
            if self._code['clexer'] is None:
                self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.OnStyleNeeded)
        else:
            # If changing from a container lexer to a non container
            # lexer we need to unbind the event.
            if self._code['clexer'] is not None:
                self.Unbind(wx.stc.EVT_STC_STYLENEEDED)
                self._code['clexer'] = None

        wx.stc.StyledTextCtrl.SetLexer(self, lexer)

    def SetModTime(self, modtime):
        """Set the value of the files last modtime"""
        self.file.SetModTime(modtime)

    def SetViEmulationMode(self, use_vi):
        """Activate/Deactivate Vi eumulation mode
        @param use_vi: Turn vi emulation on/off
        @type use_vi: boolean

        """
        self.key_handler.ClearMode()
        if use_vi:
            self.key_handler = ViKeyHandler(self)
        else:
            self.key_handler = KeyHandler(self)

    def SetViewEdgeGuide(self, switch=None):
        """Toggles the visibility of the edge guide
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.GetEdgeMode()) or switch:
            self.SetEdgeColumn(_PGET("EDGE", 'int', 80))
            self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        else:
            self.SetEdgeMode(wx.stc.STC_EDGE_NONE)

    def StartRecord(self):
        """Starts recording all events
        @return: None

        """
        self.recording = True
        evt = ed_event.StatusEvent(ed_event.edEVT_STATUS, self.GetId(),
                                   _("Recording Macro") + u"...",
                                   ed_glob.SB_INFO)
        wx.PostEvent(self.GetTopLevelParent(), evt)
        wx.stc.StyledTextCtrl.StartRecord(self)

    def StopRecord(self):
        """Stops the recording and builds the macro script
        @postcondition: macro recording is stopped

        """
        self.recording = False
        wx.stc.StyledTextCtrl.StopRecord(self)
        evt = ed_event.StatusEvent(ed_event.edEVT_STATUS, self.GetId(),
                                   _("Recording Finished"),
                                   ed_glob.SB_INFO)
        wx.PostEvent(self.GetTopLevelParent(), evt)
        self._BuildMacro()

    def TrimWhitespace(self):
        """Trims trailing whitespace from all lines in the document.
        @postcondition: all trailing whitespace is removed from document

        """
        cpos = self.GetCurrentPos()
        cline = self.GetCurrentLine()
        cline_len = len(self.GetLine(cline))
        s_len = self.GetLength()
        epos = cline_len - (self.GetLineEndPosition(cline) - cpos)

        # Begin stripping trailing whitespace
        self.BeginUndoAction()
        for line in xrange(self.GetLineCount() + 1):
            eol = u''
            tmp = self.GetLine(line)
            tlen = len(tmp)
            if tlen:
                if "\r\n" in tmp:
                    eol = "\r\n"
                elif "\n" in tmp:
                    eol = "\n"
                else:
                    eol = tmp[-1]

                if not eol.isspace():
                    continue
                elif eol in u' \t':
                    eol = u''
            else:
                continue

            # Strip the extra whitespace from the line
            end = self.GetLineEndPosition(line) + len(eol)
            start = max(end - tlen, 0)
            self.SetTargetStart(start)
            self.SetTargetEnd(end)
            self.ReplaceTarget(tmp.rstrip() + eol)
        self.EndUndoAction()

        # Restore carat position
        cline_len = len(self.GetLine(cline))
        end = self.GetLineEndPosition(cline)
        if epos >= cline_len:
            epos = end
        else:
            start = max(end - cline_len, 0)
            epos += start

        self.GotoPos(epos)

    def FoldingOnOff(self, switch=None):
        """Turn code folding on and off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self._config['folding']) or switch:
            self.LOG("[ed_stc][evt] Code Folding Turned On")
            self._config['folding'] = True
            self.SetMarginWidth(FOLD_MARGIN, 12)
        else:
            self.LOG("[ed_stc][evt] Code Folding Turned Off")
            self._config['folding'] = False
            self.SetMarginWidth(FOLD_MARGIN, 0)

    def SyntaxOnOff(self, switch=None):
        """Turn Syntax Highlighting on and off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self._config['highlight']) or switch:
            self.LOG("[ed_stc][evt] Syntax Highlighting Turned On")
            self._config['highlight'] = True
            self.FindLexer()
        else:
            self.LOG("[ed_stc][evt] Syntax Highlighting Turned Off")
            self._config['highlight'] = False
            self.SetLexer(wx.stc.STC_LEX_NULL)
            self.ClearDocumentStyle()
            self.UpdateBaseStyles()
        return 0

    def ToggleAutoIndent(self, switch=None):
        """Toggles Auto-indent On and Off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self._config['autoindent']) or switch:
            self._config['autoindent'] = True
        else:
            self._config['autoindent'] = False

    def ToggleBracketHL(self, switch=None):
        """Toggle Bracket Highlighting On and Off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self._config['brackethl']) or switch:
            self.LOG("[ed_stc][evt] Bracket Highlighting Turned On")
            self._config['brackethl'] = True
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        else:
            self.LOG("[ed_stc][evt] Bracket Highlighting Turned Off")
            self._config['brackethl'] = False
            self.Unbind(wx.stc.EVT_STC_UPDATEUI)

    def ToggleLineNumbers(self, switch=None):
        """Toggles the visibility of the line number margin
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.GetMarginWidth(NUM_MARGIN)) or switch:
            self.LOG("[ed_stc][evt] Showing Line Numbers")
            self.SetMarginWidth(NUM_MARGIN, 30)
        else:
            self.LOG("[ed_stc][evt] Hiding Line Numbers")
            self.SetMarginWidth(NUM_MARGIN, 0)

    def WordLeft(self):
        """Move caret to begining of previous word
        @note: override builtin to include extra characters in word

        """
        self.SetWordChars(NONSPACE)
        wx.stc.StyledTextCtrl.WordLeft(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordLeft(self)
        self.SetWordChars('')

    def WordLeftExtend(self):
        """Extend selection to begining of previous word
        @note: override builtin to include extra characters in word

        """
        self.SetWordChars(NONSPACE)
        wx.stc.StyledTextCtrl.WordLeftExtend(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordLeftExtend(self)
        self.SetWordChars('')

    def WordPartLeft(self):
        """Move the caret left to the next change in capitalization/puncuation
        @note: overrides default function to not count whitespace as words

        """
        wx.stc.StyledTextCtrl.WordPartLeft(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordPartLeft(self)

    def WordPartLeftExtend(self):
        """Extend selection left to the next change in capitalization/puncuation
        @note: overrides default function to not count whitespace as words

        """
        wx.stc.StyledTextCtrl.WordPartLeftExtend(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordPartLeftExtend(self)

    def WordPartRight(self):
        """Move the caret to the start of the next word part to the right
        @note: overrides default function to exclude white space

        """
        wx.stc.StyledTextCtrl.WordPartRight(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordPartRight(self)

    def WordPartRightEnd(self):
        """Move caret to end of next change in capitalization/puncuation
        @postcondition: caret is moved

        """
        wx.stc.StyledTextCtrl.WordPartRight(self)
        wx.stc.StyledTextCtrl.WordPartRight(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos - 1) in SPACECHARS:
            self.CharLeft()

    def WordPartRightEndExtend(self):
        """Extend selection to end of next change in capitalization/puncuation
        @postcondition: selection is extended

        """
        wx.stc.StyledTextCtrl.WordPartRightExtend(self)
        wx.stc.StyledTextCtrl.WordPartRightExtend(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos - 1) in SPACECHARS:
            self.CharLeftExtend()

    def WordPartRightExtend(self):
        """Extend selection to start of next change in capitalization/puncuation
        @postcondition: selection is extended

        """
        wx.stc.StyledTextCtrl.WordPartRightExtend(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordPartRightExtend(self)

    def WordRight(self):
        """Move caret to begining of next word
        @note: override builtin to include extra characters in word

        """
        self.SetWordChars(NONSPACE)
        wx.stc.StyledTextCtrl.WordRight(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordRight(self)
        self.SetWordChars('')

    def WordRightEnd(self):
        """Move caret to end of next change in word
        @note: override builtin to include extra characters in word

        """
        self.SetWordChars(NONSPACE)
        wx.stc.StyledTextCtrl.WordRightEnd(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos - 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordRightEnd(self)
        self.SetWordChars('')

    def WordRightExtend(self):
        """Extend selection to begining of next word
        @note: override builtin to include extra characters in word

        """
        self.SetWordChars(NONSPACE)
        wx.stc.StyledTextCtrl.WordRightExtend(self)
        cpos = self.GetCurrentPos()
        if self.GetTextRange(cpos, cpos + 1) in SPACECHARS:
            wx.stc.StyledTextCtrl.WordRightExtend(self)
        self.SetWordChars('')

    def LoadFile(self, path):
        """Load the file at the given path into the buffer. Returns
        True if no errors and False otherwise. To retrieve the errors
        check the last error that was set in the file object returned by
        L{GetDocument}.
        @param path: path to file

        """
        # Post notification that a file load is starting
        ed_msg.PostMessage(ed_msg.EDMSG_FILE_OPENING, path)
        self.file.SetPath(path)
        txt = self.file.Read()
        if txt is not None:
            self.SetText(txt)
        else:
            self.file.SetPath('')
            return False

        if self.file.GetLastError() != 'None':
            # Return false if there was an encoding error and a fallback
            # was used. So the caller knows to check the error status
            return False
        else:
            return True

    def ReloadFile(self):
        """Reloads the current file, returns True on success and
        False if there is a failure.
        @return: whether file was reloaded or not
        @rtype: bool

        """
        cfile = self.GetFileName()
        if os.path.exists(cfile):
            try:
                self.BeginUndoAction()
                marks = self.GetBookmarks()
                cpos = self.GetCurrentPos()
                self.SetText(self.file.Read())
                self.SetModTime(util.GetFileModTime(cfile))
                for mark in marks:
                    self.MarkerAdd(mark, MARK_MARGIN)
                self.EndUndoAction()
                self.SetSavePoint()
            except (AttributeError, OSError, IOError), msg:
                self.LOG("[ed_stc][err] Failed to Reload %s" % cfile)
                return False, msg
            else:
                self.GotoPos(cpos)
                ed_msg.PostMessage(ed_msg.EDMSG_FILE_OPENED, self.GetFileName())
                return True, ''
        else:
            self.LOG("[ed_stc][err] %s does not exists, cant reload." % cfile)
            return False, _("%s does not exist") % cfile

    def RevertFile(self):
        """Revert all the changes made to the file since it was opened
        @postcondition: undo history is re-wound to initial state and file
                        is re-saved if it has an on disk file.

        """
        self.Freeze()
        while self.CanUndo():
            self.Undo()
        self.Thaw()

        fname = self.GetFileName()
        if len(fname):
            self.SaveFile(fname)

    def RevertToSaved(self):
        """Revert the current buffer back to the last save point"""
        self.Freeze()
        while self.CanUndo():
            if self.GetModify():
                self.Undo()
            else:
                break
        self.Thaw()

    def SaveFile(self, path):
        """Save buffers contents to disk
        @param path: path of file to save
        @return: whether file was written or not
        @rtype: bool

        """
        result = True
        try:
            ed_msg.PostMessage(ed_msg.EDMSG_FILE_SAVE,
                               (path, self._code['lang_id']))
            self.file.SetPath(path)
            self.LOG("[ed_stc][info] Writing file %s, with encoding %s" % \
                     (path, self.file.GetEncoding()))

            if _PGET('AUTO_TRIM_WS', 'bool', False):
                self.TrimWhitespace()

            self.file.Write(self.GetText())
        except Exception, msg:
            result = False
            self.LOG("[ed_stc][err] There was an error saving %s" % path)
            self.LOG("[ed_stc][err] ERROR: %s" % str(msg))

        if result:
            self.SetSavePoint()
            self.SetModTime(util.GetFileModTime(path))
            self.OnModified(wx.stc.StyledTextEvent(wx.stc.wxEVT_STC_MODIFIED,
                                                   self.GetId()))
            self.SetFileName(path)

        wx.CallAfter(ed_msg.PostMessage,
                    ed_msg.EDMSG_FILE_SAVED,
                    (path, self._code['lang_id']))

        return result

    def DoZoom(self, mode):
        """Zoom control in or out
        @param mode: either zoom in or out
        @type mode: int id value

        """
        id_type = mode
        zoomlevel = self.GetZoom()
        if id_type == ed_glob.ID_ZOOM_OUT:
            if zoomlevel > -9:
                self.ZoomOut()
        elif id_type == ed_glob.ID_ZOOM_IN:
            if zoomlevel < 19:
                self.ZoomIn()
        else:
            self.SetZoom(0)
        return self.GetZoom()

    def ConfigureAutoComp(self):
        """Sets up the Autocompleter, the autocompleter
        configuration depends on the currently set lexer
        @postcondition: autocomp is configured

        """
        self.AutoCompSetAutoHide(False)
        self._code['compsvc'].LoadCompProvider(self.GetLexer())
        self.AutoCompSetIgnoreCase(self._code['compsvc'].GetIgnoreCase())
        self.AutoCompStops(self._code['compsvc'].GetAutoCompStops())

    def ConfigureLexer(self, file_ext):
        """Sets Lexer and Lexer Keywords for the specifed file extension
        @param file_ext: a file extension to configure the lexer from

        """
        syn_data = self._code['synmgr'].SyntaxData(file_ext)

        # Set the ID of the selected lexer
        try:
            self._code['lang_id'] = syn_data[syntax.LANGUAGE]
        except KeyError:
            self.LOG("[ed_stc][err] Failed to get Lang Id from Syntax package")
            self._code['lang_id'] = 0

        lexer = syn_data[syntax.LEXER]
        # Check for special cases
        # TODO: add fetch method to check if container lexer requires extra
        #       style bytes beyond the default 5.
        if lexer in [ wx.stc.STC_LEX_HTML, wx.stc.STC_LEX_XML]:
            self.SetStyleBits(7)
        elif lexer == wx.stc.STC_LEX_NULL:
            self.SetStyleBits(5)
            self.SetIndentationGuides(False)
            self.SetLexer(lexer)
            self.ClearDocumentStyle()
            self.UpdateBaseStyles()
            return True
        else:
            self.SetStyleBits(5)

        try:
            keywords = syn_data[syntax.KEYWORDS]
        except KeyError:
            self.LOG("[ed_stc][err] No Keywords Data Found")
            keywords = []

        try:
            synspec = syn_data[syntax.SYNSPEC]
        except KeyError:
            self.LOG("[ed_stc][err] Failed to get Syntax Specifications")
            synspec = []

        try:
            props = syn_data[syntax.PROPERTIES]
        except KeyError:
            self.LOG("[ed_stc][err] No Extra Properties to Set")
            props = []

        try:
            comment = syn_data[syntax.COMMENT]
        except KeyError:
            self.LOG("[ed_stc][err] No Comment Pattern to set")
            comment = []

        try:
            clexer = syn_data[syntax.CLEXER]
        except KeyError:
            self.LOG("[ed_stc][err] No Container Lexer to set")
            clexer = None

        try:
            indenter = syn_data[syntax.INDENTER]
        except KeyError:
            self.LOG("[ed_stc][err] No Auto-Indenter")
            indenter = None

        # Set Lexer
        self.SetLexer(lexer)
        # Set Keywords
        self.SetKeyWords(keywords)
        # Set Lexer/Syntax Specifications
        self.SetSyntax(synspec)
        # Set Extra Properties
        self.SetProperties(props)
        # Set Comment Pattern
        self._code['comment'] = comment
        # Set the Container Lexer Method
        self._code['clexer'] = clexer
        # Auto-indenter function
        self._code['indenter'] = indenter

        # Notify that lexer has changed
        ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_LEXER,
                           (self.GetFileName(), self.GetLangId()))
        return True

    def SetKeyWords(self, kw_lst):
        """Sets the keywords from a list of keyword sets
        @param kw_lst: [ (KWLVL, "KEWORDS"), (KWLVL2, "KEYWORDS2"), ect...]
        @todo: look into if the uniquifying of the list has a more optimal
               solution.

        """
        # Parse Keyword Settings List simply ignoring bad values and badly
        # formed lists
        self._code['keywords'] = ""
        for keyw in kw_lst:
            if len(keyw) != 2:
                continue
            else:
                if not isinstance(keyw[0], int) or \
                   not isinstance(keyw[1], basestring):
                    continue
                else:
                    self._code['keywords'] += keyw[1]
                    wx.stc.StyledTextCtrl.SetKeyWords(self, keyw[0], keyw[1])

        kwlist = self._code['keywords'].split()    # Split into a list of words
        kwlist = list(set(kwlist))                 # Uniqueify the list
        kwlist.sort()                              # Sort into alphbetical order
        # Can't have ? in scintilla autocomp list unless specifying an image
        if '?' in kwlist:
            kwlist.remove('?')
        self._code['keywords'] = " ".join(kwlist)  # Put back into a string
        return True

    def SetSyntax(self, syn_lst):
        """Sets the Syntax Style Specs from a list of specifications
        @param syn_lst: [(STYLE_ID, "STYLE_TYPE"), (STYLE_ID2, "STYLE_TYPE2)]

        """
        # Parses Syntax Specifications list, ignoring all bad values
        self.UpdateBaseStyles()
        valid_settings = list()
        for syn in syn_lst:
            if len(syn) != 2:
                self.LOG("[ed_stc][warn] Error setting syntax spec")
                continue
            else:
                if self.GetLexer() == wx.stc.STC_LEX_CONTAINER:
                    self.StyleSetSpec(syn[0], self.GetStyleByName(syn[1]))
                else:
                    if not isinstance(syn[0], basestring) or \
                       not hasattr(wx.stc, syn[0]):
                        self.LOG("[ed_stc][warn] Unknown syntax region: %s" % \
                                 str(syn[0]))
                        continue
                    elif not isinstance(syn[1], basestring):
                        self.LOG("[ed_stc][warn] Poorly formated styletag: %s" % \
                                 str(syn[1]))
                        continue
                    else:
                        self.StyleSetSpec(getattr(wx.stc, syn[0]), \
                                          self.GetStyleByName(syn[1]))
                valid_settings.append(syn)
        self._code['syntax_set'] = valid_settings
        return True

    def SetProperties(self, prop_lst):
        """Sets the Lexer Properties from a list of specifications
        @param prop_lst: [ ("PROPERTY", "VAL"), ("PROPERTY2", "VAL2) ]

        """
        # Parses Property list, ignoring all bad values
        for prop in prop_lst:
            if len(prop) != 2:
                continue
            else:
                if not isinstance(prop[0], basestring) or not \
                   isinstance(prop[1], basestring):
                    continue
                else:
                    self.SetProperty(prop[0], prop[1])
        return True

    #---- End Function Definitions ----#

    #---- Style Function Definitions ----#
    def RefreshStyles(self):
        """Refreshes the colorization of the window by reloading any
        style tags that may have been modified.
        @postcondition: all style settings are refreshed in the control

        """
        self.Freeze()
        self.StyleClearAll()
        self.SetSyntax(self._code['syntax_set'])
        self.DefineMarkers()
        self.Thaw()
        self.Refresh()

    def StyleDefault(self):
        """Clears the editor styles to default
        @postcondition: style is reset to default

        """
        self.StyleClearAll()
        self.SetCaretForeground(wx.NamedColor("black"))
        self.Colourise(0, -1)

    def UpdateBaseStyles(self):
        """Updates the base styles of editor to the current settings
        @postcondition: base style info is updated

        """
        self.StyleDefault()
        self.SetMargins(4, 0)
        # Global default styles for all languages
        self.StyleSetSpec(0, self.GetStyleByName('default_style'))
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, \
                          self.GetStyleByName('default_style'))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, \
                          self.GetStyleByName('line_num'))
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, \
                          self.GetStyleByName('ctrl_char'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, \
                          self.GetStyleByName('brace_good'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, \
                          self.GetStyleByName('brace_bad'))
        self.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, \
                          self.GetStyleByName('guide_style'))

        # wx.stc.STC_STYLE_CALLTIP doesnt seem to do anything
        calltip = self.GetItemByName('calltip')
        self.CallTipSetBackground(calltip.GetBack())
        self.CallTipSetForeground(calltip.GetFore())

        sback = self.GetItemByName('select_style')
        if not sback.IsNull():
            sback = sback.GetBack()
        else:
            sback = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self.SetSelBackground(True, sback)

        wspace = self.GetItemByName('whitespace_style')
        if not wspace.IsNull():
            self.SetWhitespaceBackground(True, wspace.GetBack())
            self.SetWhitespaceForeground(True, wspace.GetFore())

        self.SetCaretForeground(self.GetDefaultForeColour())
        self.SetCaretLineBack(self.GetItemByName('caret_line').GetBack())
        self.DefineMarkers()
        self.Colourise(0, -1)

    def UpdateAllStyles(self, spec_style=None):
        """Refreshes all the styles and attributes of the control
        @param spec_style: style scheme name
        @postcondition: style scheme is set to specified style

        """
        if spec_style != self.style_set:
            self.LoadStyleSheet(self.GetStyleSheet(spec_style), force=True)
        self.UpdateBaseStyles()
        self.SetSyntax(self._code['syntax_set'])
        self.Refresh()

    #---- End Style Definitions ----#

#-----------------------------------------------------------------------------#

def MakeMenu():
    """Make the buffers context menu"""
    menu = ed_menu.EdMenu()
    menu.Append(ed_glob.ID_UNDO, _("Undo"))
    menu.Append(ed_glob.ID_REDO, _("Redo"))
    menu.AppendSeparator()
    menu.Append(ed_glob.ID_CUT, _("Cut"))
    menu.Append(ed_glob.ID_COPY, _("Copy"))
    menu.Append(ed_glob.ID_PASTE, _("Paste"))
    menu.AppendSeparator()
    menu.Append(ed_glob.ID_TO_UPPER, _("To Uppercase"))
    menu.Append(ed_glob.ID_TO_LOWER, _("To Lowercase"))
    menu.AppendSeparator()
    menu.Append(ed_glob.ID_SELECTALL, _("Select All"))
    return menu
