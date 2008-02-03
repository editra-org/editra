# -*- coding: utf-8 -*-
###############################################################################
# Name: handlers.py                                                           #
# Purpose: File Type Handlers                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""File Type Handlers
The file type handlers are used to handle the execution of and output of the
different file types that they represent. Each handler manages its own settings
and configuration.

It is easy to extend the filetypes supported by the Launch plugin through this
interface. To add support for a new filetype simply derive a new class from the
base L{FileTypeHandler} and override any of the following methods to provide
custom functionality.

Required Overrides:
__init__ : define default command list and default command
__name__ : set the name of the handler, this should be the file type

Other Overrides:
GetEnvironment : Return a dictionary of environmental variables to run the
                 process within
HandleHotSpot : Action to perform when a hotspot is clicked on in the output
                buffer.
StyleText : Perform custom styling on the text as its added, line by line

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['GetHandlerById', 'GetHandlerByName', 'GetState',
           'SetState', 'DEFAULT_HANDLER']

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re

# Editra Libraries
import eclib.outbuff as outbuff
import syntax.synglob as synglob

#-----------------------------------------------------------------------------#
# Globals
DEFAULT_HANDLER = 'handler'

# Ansi escape sequence color table
# For coloring shell script output
RE_ANSI_START = re.compile(r'\[[34][0-9];01m')
RE_ANSI_FORE = re.compile('\[3[0-9]m')
RE_ANSI_BLOCK = re.compile('\[[34][0-9]m*.*?\[m')
RE_ANSI_END = re.compile(r'\[[0]{0,1}m')
RE_ANSI_ESC = re.compile('\[[0-9]+m')
ANSI = {
        ## Forground colours ##
        '[30m' : (1, '#000000'),  # Black
        '[31m' : (2, '#FF0000'),  # Red
        '[32m' : (3, '#00FF00'),  # Green
        '[33m' : (4, '#FFFF00'),  # Yellow
        '[34m' : (5, '#0000FF'),  # Blue
        '[35m' : (6, '#FF00FF'),  # Magenta
        '[36m' : (7, '#00FFFF'),  # Cyan
        '[37m' : (8, '#FFFFFF'),  # White
        #'[39m' : default

        ## Background colour ##
        '[40m' : (011, '#000000'),  # Black
        '[41m' : (012, '#FF0000'),  # Red
        '[42m' : (013, '#00FF00'),  # Green
        '[43m' : (014, '#FFFF00'),  # Yellow
        '[44m' : (015, '#0000FF'),  # Blue
        '[45m' : (016, '#FF00FF'),  # Magenta
        '[46m' : (017, '#00FFFF'),  # Cyan
        '[47m' : (020, '#FFFFFF'),  # White
        #'[49m' : default
        }

# Process Start/Exit Regular Expression
RE_PROC_SE = re.compile('>{3,3}.*' + os.linesep)

#-----------------------------------------------------------------------------#
# Public Handler Api for use outside this module
def GetHandlerById(lang_id):
    """Get a handler for the specified language id"""
    if HANDLERS.has_key(lang_id):
        return HANDLERS[lang_id]
    else:
        return HANDLERS[0]

def GetHandlerByName(name):
    """Get an output handler by name"""
    for handler in HANDLERS.values():
        if name.lower() == handler.GetName().lower():
            return handler
    else:
        return HANDLERS[0]

def GetState():
    """Get a dictionary capturing the current state of all handlers
    @return: dict { handlername : (default, [commands]) }

    """
    rdict = dict()
    for handler in HANDLERS.values():
        rdict[handler.GetName()] = (handler.GetDefault(), handler.GetCommands())
    return rdict

def SetState(state):
    """Set the state of all handlers based on a dictionary of values
    @param state: dict { handlername : (default, [commands]) }

    """
    for ftype, vals in state.iteritems():
        handler = GetHandlerByName(ftype)
        handler.SetCommands(vals[1])
        handler.SetDefault(vals[0])

#-----------------------------------------------------------------------------#
# Handler Base Class and Handler implementations
#
class FileTypeHandler(object):
    """Base default Output handler all output handlers should derive from
    this class. This base class is used when an output handler is request
    but no special one exists.

    """
    def __init__(self):
        object.__init__(self)
        self.commands = list()
        self.default = ''

    @property
    def __name__(self):
        return DEFAULT_HANDLER

    def AppendCommand(self, cmd):
        """Add a command to the list of commands known to this handler
        @param cmd: Command string / executable path

        """
        self.commands.append(cmd)
        self.commands = list(set(self.commands))
        self.commands.sort()

    def GetCommands(self):
        """Get the set of commands available for this file type"""
        return self.commands

    def GetDefault(self):
        """Get the prefered default command
        @return: string

        """
        return self.default

    def GetEnvironment(self):
        """Get the dictionary of environmental variables to run the
        command under.

        """
        return os.environ

    def GetName(self):
        """Get the name of this handler"""
        return self.__name__

    def HandleHotSpot(self, mainw, outbuff, line, fname):
        """Handle hotspot clicks. Called when a hotspot is clicked
        in an output buffer of this file type.
        @param mainw: MainWindow instance that created the launch instance
        @param outbuff: Buffer the click took place in
        @param line: line number of the hotspot region in the buffer
        @param fname: path of the script that was run to produce the output that
                      contains the hotspot.

        """
        pass

    def FilterInput(self, text):
        """Filter incoming text return the text to be displayed
        @param text: The incoming text to filter before putting in buffer

        """
        return text

    def SetCommands(self, cmds):
        """Set the list of commands known by the handler
        @param cmds: list of command strings

        """
        if not isinstance(cmds, list):
            raise TypeError, "SetCommands expects a list of strings"
        else:
            self.commands = cmds

    def SetDefault(self, cmd):
        """Set the prefered default command
        @param cmd: Command string to set as the preffered one
        @postcondition: if cmd is not in the saved command list it will be
                        added to that list as well as a side affect.

        """
        cmd = cmd.strip()
        if cmd not in self.GetCommands():
            self.AppendCommand(cmd)
        self.default = cmd

    def StyleText(self, stc, start, txt):
        """Style the text in the given buffer
        @param stc: stc based buffer to apply styling to
        @param start: start of text that was just added to buffer
        @param txt: text that was just added at start point

        """
        # Highlight Start End lines
        for info in RE_PROC_SE.finditer(txt):
            sty_s = start + info.start()
            sty_e = start + info.end()
            stc.StartStyling(sty_s, 0xff)
            stc.SetStyling(sty_e - sty_s, outbuff.OPB_STYLE_INFO)

#-----------------------------------------------------------------------------#
class BashHandler(FileTypeHandler):
    """FileTypeHandler for Bash scripts"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['bash',]
        self.default = 'bash'

    @property
    def __name__(self):
        return 'bash shell'

    def FilterInput(self, txt):
        """Filter out ansi escape sequences from input"""
        txt = RE_ANSI_START.sub('', txt)
        return RE_ANSI_END.sub('', txt)

#-----------------------------------------------------------------------------#

class BooHandler(FileTypeHandler):
    """FileTypeHandler for Boo"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['booi',]
        self.default = 'booi'

    @property
    def __name__(self):
        return 'boo'

#-----------------------------------------------------------------------------#

class CSHHandler(FileTypeHandler):
    """FileTypeHandler for C-Shell"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['csh',]
        self.default = 'csh'

    @property
    def __name__(self):
        return 'c shell'

#-----------------------------------------------------------------------------#

class FeriteHandler(FileTypeHandler):
    """FileTypeHandler for Ferite"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['ferite',]
        self.default = 'ferite'

    @property
    def __name__(self):
        return 'ferite'

#-----------------------------------------------------------------------------#

class KornHandler(FileTypeHandler):
    """FileTypeHandler for Korn Shell scripts"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['ksh',]
        self.default = 'ksh'

    @property
    def __name__(self):
        return 'korn shell'

#-----------------------------------------------------------------------------#

class LuaHandler(FileTypeHandler):
    """FileTypeHandler for Lua"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['lua',]
        self.default = 'lua'

    @property
    def __name__(self):
        return 'lua'

#-----------------------------------------------------------------------------#

class PikeHandler(FileTypeHandler):
    """FileTypeHandler for Pike"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['pike',]
        self.default = 'pike'

    @property
    def __name__(self):
        return 'pike'

#-----------------------------------------------------------------------------#

class PerlHandler(FileTypeHandler):
    """FileTypeHandler for Perl scripts"""
    RE_PERL_ERROR = re.compile(r'[a-zA-Z]+ error at (.+) line ([0-9]+),')
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['perl',]
        self.default = 'perl'

    @property
    def __name__(self):
        return 'perl'

    def HandleHotSpot(self, mainw, outbuff, line, fname):
        """Hotspots are error messages, find the file/line of the
        error in question and open the file to that point in the buffer.

        """
        txt = outbuff.GetLine(line)
        match = self.RE_PERL_ERROR.findall(txt)
        ifile = None
        if len(match):
            match = match[0]
            ifile = match[0]
            try:
                line = max(int(match[1]) - 1, 0)
            except:
                line = 0

            # If not an absolute path then the error is in the current script
            if not os.path.isabs(ifile):
                dname = os.path.split(fname)[0]
                ifile = os.path.join(dname, ifile)

            nb = mainw.GetNotebook()
            buffers = [ page.GetFileName() for page in nb.GetTextControls() ]
            if ifile in buffers:
                page = buffers.index(ifile)
                nb.SetSelection(page)
                nb.GetPage(page).GotoLine(line)
            else:
                nb.OnDrop([ifile])
                nb.GetPage(nb.GetSelection()).GotoLine(line)

    def StyleText(self, stc, start, txt):
        """Style python Information and Error messages from script
        output.

        """
        for group in self.RE_PERL_ERROR.finditer(txt):
            sty_s = start + group.start()
            sty_e = start + group.end()
            stc.StartStyling(sty_s, 0xff)
            stc.SetStyling(sty_e - sty_s, outbuff.OPB_STYLE_ERROR)
        else:
            # Highlight Start end lines this is what the
            # base classes method does.
            FileTypeHandler.StyleText(self, stc, start, txt)

#-----------------------------------------------------------------------------#

class PythonHandler(FileTypeHandler):
    """FileTypeHandler for Python"""
    RE_PY_ERROR = re.compile('File "(.+)", line ([0-9]+)')

    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['python', 'pylint']
        self.default = 'python'

    @property
    def __name__(self):
        return 'python'

    def GetEnvironment(self):
        """Get the environment to run the python script in"""
        if not hasattr(sys, 'frozen') or sys.platform.startswith('win'):
            proc_env = os.environ.copy()
        else:
            proc_env = dict()

        proc_env['PYTHONUNBUFFERED'] = '1'
        return proc_env

    def HandleHotSpot(self, mainw, outbuff, line, fname):
        """Hotspots are error messages, find the file/line of the
        error in question and open the file to that point in the buffer.

        """
        txt = outbuff.GetLine(line)
        match = self.RE_PY_ERROR.findall(txt)
        ifile = None
        if len(match):
            match = match[0]
            ifile = match[0]
            try:
                line = max(int(match[1]) - 1, 0)
            except:
                line = 0

            # If not an absolute path then the error is in the current script
            if not os.path.isabs(ifile):
                dname = os.path.split(fname)[0]
                ifile = os.path.join(dname, ifile)

            nb = mainw.GetNotebook()
            buffers = [ page.GetFileName() for page in nb.GetTextControls() ]
            if ifile in buffers:
                page = buffers.index(ifile)
                nb.SetSelection(page)
                nb.GetPage(page).GotoLine(line)
            else:
                nb.OnDrop([ifile])
                nb.GetPage(nb.GetSelection()).GotoLine(line)

    def StyleText(self, stc, start, txt):
        """Style python Information and Error messages from script
        output.

        """
        for group in self.RE_PY_ERROR.finditer(txt):
            sty_s = start + group.start()
            sty_e = start + group.end()
            stc.StartStyling(sty_s, 0xff)
            stc.SetStyling(sty_e - sty_s, outbuff.OPB_STYLE_ERROR)
        else:
            # Highlight Start end lines this is what the
            # base classes method does.
            FileTypeHandler.StyleText(self, stc, start, txt)

#-----------------------------------------------------------------------------#

class RubyHandler(FileTypeHandler):
    """FileTypeHandler for Ruby scripts"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['ruby',]
        self.default = 'ruby'

    @property
    def __name__(self):
        return 'ruby'

#-----------------------------------------------------------------------------#

class TCLHandler(FileTypeHandler):
    """FileTypeHandler for TCL/TK"""
    def __init__(self):
        FileTypeHandler.__init__(self)
        self.commands = ['wish',]
        self.default = 'wish'

    @property
    def __name__(self):
        return 'tcl/tk'

#-----------------------------------------------------------------------------#
# Handler Object Dictionary
# Used to keep one instance of each handler to use like a singleton
HANDLERS = { 0 : FileTypeHandler(),
            synglob.ID_LANG_BASH : BashHandler(),
            synglob.ID_LANG_BOO : BooHandler(),
            synglob.ID_LANG_CSH : CSHHandler(),
            synglob.ID_LANG_FERITE : FeriteHandler(),
            synglob.ID_LANG_KSH : KornHandler(),
            synglob.ID_LANG_LUA : LuaHandler(),
            synglob.ID_LANG_PERL : PerlHandler(),
            synglob.ID_LANG_PIKE : PikeHandler(),
            synglob.ID_LANG_PYTHON : PythonHandler(),
            synglob.ID_LANG_RUBY : RubyHandler(),
            synglob.ID_LANG_TCL : TCLHandler() }
