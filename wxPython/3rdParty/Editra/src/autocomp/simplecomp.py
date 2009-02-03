###############################################################################
# Name: simplecomp.py                                                         #
# Purpose: Simple autocompletion based on buffer words (SciTE docet)          #
# Author: Giuseppe "Cowo" Corbelli                                            #
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli                                #
# License: wxWindows License                                                  #
###############################################################################

"""
Simple Generic autocompleter for completing words found in the current buffer.

"""

__author__ = "Giuseppe \"Cowo\" Corbelli"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import string
import wx
import wx.stc as stc

#--------------------------------------------------------------------------#

class Completer(object):
    """Code completer provider"""
    autocompFillup = '.,;([]){}<>%^&+-=*/|'
    autocompStop = ' \'"\\`):'
    wordCharacters = "".join(['_', string.letters])
    autocompKeys = []
    calltipKeys = []
    calltipCancel = []
    caseSensitive = False

    def __init__(self, stc_buffer):
        """Initiliazes the completer
        @param stc_buffer: buffer that contains code

        """
        object.__init__(self)

        # Attributes
        self._log = wx.GetApp().GetLog()
        self._buffer = stc_buffer

    def _GetCompletionInfo(self, command, calltip=False):
        """Get Completion list or Calltip
        @return: list or string

        """
        if command is None or (len(command) and command[0].isdigit()):
            return u''

        bf = self._buffer
        currentPos = bf.GetCurrentPos()

        #Get the real word: segment using autocompFillup
        ls = list(command.strip(self.autocompFillup))
        ls.reverse()
        idx = 0
        for c in ls:
            if c in self.autocompFillup:
                break
            idx += 1
        ls2 = ls[:idx]
        ls2.reverse()
        command = u"".join(ls2)

        #Available completions so far
        wordsNear = []
        maxWordLength = 0
        nWords = 0
        minPos = 0
        maxPos = bf.GetLength()
        flags = stc.STC_FIND_WORDSTART
        if self.caseSensitive:
            flags |= stc.STC_FIND_MATCHCASE

        posFind = bf.FindText(minPos, maxPos, command, flags)
        while posFind >= 0 and posFind < maxPos:
            wordEnd = posFind + len(command)
            if posFind != currentPos:
                while -1 != self.wordCharacters.find(chr(bf.GetCharAt(wordEnd))):
                    wordEnd += 1

                wordLength = wordEnd - posFind
                if wordLength > len(command):
                    word = bf.GetTextRange(posFind, wordEnd)
                    if not wordsNear.count(word):
                        wordsNear.append(word)
                        maxWordLength = max(maxWordLength, wordLength)
                        nWords += 1

            minPos = wordEnd
            posFind = bf.FindText(minPos, maxPos, command, flags)

        completionInfo = ""
        if len(wordsNear) > 0 and (maxWordLength > len(command)):
            return wordsNear
        return []

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of autocomp activation keys

        """
        return self.autocompKeys

    def IsAutoCompEvent(self, evt):
        """Is this a key event that we need to provide completions on"""
        if evt.ControlDown() and evt.GetKeyCode() == wx.WXK_SPACE:
            return True
        return False

    def GetAutoCompList(self, command):
        """Returns the list of possible completions for a
        command string. If namespace is not specified the lookup
        is based on the locals namespace
        @param command: commadn lookup is done on
        @keyword namespace: namespace to do lookup in

        """
        return self._GetCompletionInfo(command)

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of keys that will cancel autocomp/calltip actions

        """
        return self.autocompStop

    def GetAutoCompFillups(self):
        """List of keys to fill up autocompletions on"""
        return self.autocompFillup

    def GetCallTip(self, command):
        """Returns the formated calltip string for the command.
        If the namespace command is unset the locals namespace is used.
        @param command: command to get calltip for

        """
        return ""

    def GetCallTipKeys(self):
        """Returns the list of keys to activate a calltip on
        @return: list of keys that can activate a calltip

        """
        return self.calltipKeys

    def GetCallTipCancel(self):
        """Get the list of key codes that should stop a calltip"""
        return self.calltipCancel

    def IsCallTipEvent(self, evt):
        """@todo: How is this used?"""
        if evt.ControlDown() and evt.GetKeyCode() == ord('9'):
            return True
        return False

    def GetCaseSensitive(self):
        """Returns whether the autocomp commands are case sensitive
        or not.
        @return: whether lookup is case sensitive or not

        """
        return self.caseSensitive

    def SetCaseSensitive(self, value):
        """Sets whether the completer should be case sensitive
        or not, and returns True if the value was set.
        @param value: toggle case sensitivity

        """
        if isinstance(value, bool):
            self.caseSensitive = value
            return True
        else:
            return False
