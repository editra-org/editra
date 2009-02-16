###############################################################################
# Name: htmlcomp.py                                                           #
# Purpose: Simple input assistant for html                                    #
# Author: Cody Precord                                                        #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Simple autocompletion support for HTML.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports

# Local Imports
import completer

#--------------------------------------------------------------------------#

class Completer(completer.BaseCompleter):
    """Code completer provider"""
    _autocomp_keys = [ord('>'), ]
    _autocomp_stop = '<'
    _autocomp_fillup = ''

    def __init__(self, stc_buffer):
        completer.BaseCompleter.__init__(self, stc_buffer)

        # Setup
        self.SetAutoCompAfter(True) # Insert Text after cursor on completions

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of autocomp activation keys

        """
        return Completer._autocomp_keys

    def GetAutoCompList(self, command):
        """Returns the list of possible completions for a
        command string. If namespace is not specified the lookup
        is based on the locals namespace
        @param command: commadn lookup is done on
        @keyword namespace: namespace to do lookup in

        """
        if command in [None, u'']:
            print "EMPTY!!"
            return u''

        buff = self.GetBuffer()
        cpos = buff.GetCurrentPos()
        cline = buff.GetCurrentLine()
        print "CLINE", cline
        for line in range(cline, -1, -1):
            print "WTF", line
            txt = buff.GetLine(line)
            if line == cline:
                txt = txt[:buff.GetColumn(cpos)]

            print "HELLO", txt
            idx = txt.rfind('<')
            if idx != -1:
                parts = txt[idx:].lstrip('<').strip().split()
                if len(parts):
                    tag = parts[0]
                    if tag not in ('img', 'br') and not tag.startswith('!'):
                        return [u"</" + tag, ]
                break

        return list()

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of keys that will cancel autocomp/calltip actions

        """
        return Completer._autocomp_stop

    def GetAutoCompFillups(self):
        """List of keys to fill up autocompletions on"""
        return Completer._autocomp_fillup
