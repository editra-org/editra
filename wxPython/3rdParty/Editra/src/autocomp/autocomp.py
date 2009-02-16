###############################################################################
# Name: autocomp.py                                                           #
# Purpose: Provides the front end interface for autocompletion services for   #
#          the editor.                                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Provides an interface/service for getting autocompletion/calltip data
into an stc control. This is a data provider only it does not do provide
any UI functionality or calls. The user called object from this library
is intended to be the AutoCompService. This service provides the generic
interface into the various language specific autocomplete services, and
makes the calls to the other support objects/functions in this library.

@summary: Autocompletion support interface implementation

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx.stc as stc
import htmlcomp
import pycomp
import simplecomp

#--------------------------------------------------------------------------#

class AutoCompService(object):
    """Interface to retrieve and provide autcompletion and
    calltip information to an stc control. The plain text
    (empty) completion provider is built in. All other provders
    are loaded from external modules on request.

    """
    def __init__(self, parent):
        """Initializes the autocompletion service
        @param parent: parent of this service object

        """
        object.__init__(self)

        # Attributes
        self._buffer = parent
        self._completer = None
        self._simpleCompleter = simplecomp.Completer(self._buffer)

    def GetAutoCompAfter(self):
        """Should the text insterted by the completer be inserted after the
        cursor.
        @return: bool

        """
        comp = self._completer or self._simpleCompleter
        return comp.GetAutoCompAfter()

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of characters used for activating autocomp

        """
        comp = self._completer or self._simpleCompleter
        return comp.GetAutoCompKeys()

    def IsAutoCompEvent(self, evt):
        comp = self._completer or self._simpleCompleter
        return comp.IsAutoCompEvent(evt)

    def GetAutoCompList(self, command):
        """Retrieves the sorted autocomplete list for a command
        @param command: command string to do lookup on

        """
        if self._completer:
            rlist = self._completer.GetAutoCompList(command)
        else:
            rlist = self._simpleCompleter.GetAutoCompList(command)
            rlist = sorted(list(set(rlist)))

        return rlist

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of characters that will hide the autocomp/calltip

        """
        comp = self._completer or self._simpleCompleter
        return comp.GetAutoCompStops()

    def GetAutoCompFillups(self):
        comp = self._completer or self._simpleCompleter
        return comp.GetAutoCompFillups()

    def GetCallTip(self, command):
        """Returns the calltip string for a command
        @param command: command to get callip for

        """
        comp = self._completer or self._simpleCompleter
        return comp.GetCallTip(command)

    def GetCallTipKeys(self):
        """Returns the list of keys to activate a calltip on
        @return: list of calltip activation keys

        """
        comp = self._completer or self._simpleCompleter
        return comp.GetCallTipKeys()

    def GetCallTipCancel(self):
        """Get the list of key codes that should stop a calltip"""
        comp = self._completer or self._simpleCompleter
        return comp.GetCallTipCancel()

    def IsCallTipEvent(self, evt):
        comp = self._completer or self._simpleCompleter
        return comp.IsCallTipEvent(evt)

    def GetIgnoreCase(self):
        """Are commands case sensitive or not
        @return: whether case is ignored or not by lookup

        """
        comp = self._completer or self._simpleCompleter
        return not comp.GetCaseSensitive()

    def LoadCompProvider(self, lex_value):
        """Loads a specified completion provider by stc_lex value
        @param lex_value: lexer id to get autocomp service for

        """
        if lex_value == stc.STC_LEX_PYTHON:
            self._completer = pycomp.Completer(self._buffer)
        elif lex_value in (stc.STC_LEX_HTML, stc.STC_LEX_XML):
            self._completer = htmlcomp.Completer(self._buffer)
        else:
            self._completer = None
