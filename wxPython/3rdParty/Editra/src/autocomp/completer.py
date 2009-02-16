###############################################################################
# Name: completer.py                                                          #
# Purpose: Autcompleter interface base class.                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Base class for autocompletion providers to implement the completion interface.

@summary: Autocompleter base class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import wx

#--------------------------------------------------------------------------#

class BaseCompleter(object):
    """Base Autocomp provider class"""
    def __init__(self, parent):
        """Initializes the autocompletion service
        @param parent: parent of this service object

        """
        object.__init__(self)

        # Attributes
        self._buffer = parent
        self._log = wx.GetApp().GetLog()
        self._case_sensitive = False

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the autocompletion.
        @return: list of characters used for activating autocompletion

        """
        return list()

    def IsCallTipEvent(self, evt):
        """Should a calltip be shown for the given key combo"""
        if evt.ControlDown() and evt.GetKeyCode() == ord('9'):
            return True
        return False

    def IsAutoCompEvent(self, evt):
        """Is it a key combination that should allow completions to be shown
        @param: wx.KeyEvent
        @return: bool
        @todo: this shoud probably be handled in edstc

        """
        if evt.ControlDown() and evt.GetKeyCode() == wx.WXK_SPACE:
            return True
        return False

    def GetAutoCompList(self, command):
        """Retrieves the sorted autocomplete list for a command
        @param command: command string to do lookup on
        @return: list of strings

        """
        return list()

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of characters that will hide the autocomp/calltip

        """
        return u''

    def GetAutoCompFillups(self):
        """Get the list of characters to do a fillup on
        @return: string

        """
        return u''

    def GetCallTip(self, command):
        """Returns the calltip string for a command
        @param command: command to get callip for (string)
        @return: string

        """
        return u''

    def GetCallTipKeys(self):
        """Returns the list of keys to activate a calltip on
        @return: list of calltip activation keys

        """
        return list()

    def GetCallTipCancel(self):
        """Get the list of key codes that should stop a calltip"""
        return list()

    def IsCallTipEvent(self, evt):
        """@todo: need docs"""
        return False

    def GetCaseSensitive(self):
        """Are commands case sensitive or not
        @return: bool

        """
        return self._case_sensitive

    def SetCaseSensitive(self, sensitive):
        """Set whether this completer is case sensitive or not
        @param sensitive: bool
        @return: bool

        """
        if isinstance(sensitive, bool):
            self._case_sensitive = sensitive
            return True
        else:
            return False
