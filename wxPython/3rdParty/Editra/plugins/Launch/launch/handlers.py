# -*- coding: utf-8 -*-
###############################################################################
# Name: handlers.py                                                           #
# Purpose: Script Output Handlers                                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Script Output Handlers
To add a new handler derive from the OutputHandler base class and add an
instance of the class to the HANDLERS dictionary found at the end of this
module.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re

# Editra Libraries
import syntax.synglob as synglob
import eclib.outbuff as outbuff

#-----------------------------------------------------------------------------#
# Globals

#-----------------------------------------------------------------------------#

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

#-----------------------------------------------------------------------------#
# Handler Base Class
class OutputHandler(object):
    """Base default Output handler all output handlers should derive from
    this class. This base class is used when an output handler is request
    but no special one exists.

    """
    COMMANDS = list()
    __name__ == 'handler'

    def GetCommands(self):
        """Get the set of commands available for this file type"""
        return self.COMMANDS

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
        
    def StyleText(self, stc, start, txt):
        """Style the text in the given buffer
        @param stc: stc based buffer to apply styling to
        @param start: start of text that was just added to buffer
        @param txt: text that was just added at start point

        """
        pass

#-----------------------------------------------------------------------------#

class PythonHandler(OutputHandler):
    PY_ERROR_RE = re.compile('.*File "(.+)", line ([0-9]+)')
    PY_INFO_RE = re.compile('[>]{3,3}.*' + os.linesep)
    COMMANDS = ['python',]
    __name__ = 'python'

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
        match = self.PY_ERROR_RE.match(txt)
        ifile = None
        if match:
            ifile = match.group(1)
            try:
                line = max(int(match.group(2)) - 1, 0)
            except:
                line = 0

            # The error is in the script that ran if no other module name
            # is in the error message.
            if ifile is None:
                ifile = fname

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
        for group in self.PY_ERROR_RE.finditer(txt):
            sty_s = start + group.start()
            sty_e = start + group.end()
            stc.StartStyling(sty_s, 0xff)
            stc.SetStyling(sty_e - sty_s, outbuff.OPB_STYLE_ERROR)
        else:
            for info in self.PY_INFO_RE.finditer(txt):
                sty_s = start + info.start()
                sty_e = start + info.end()
                stc.StartStyling(sty_s, 0xff)
                stc.SetStyling(sty_e - sty_s, outbuff.OPB_STYLE_INFO)

#-----------------------------------------------------------------------------#
HANDLERS = { 0 : OutputHandler(),
            synglob.ID_LANG_PYTHON : PythonHandler() }
