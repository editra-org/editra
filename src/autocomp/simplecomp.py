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
# Imports
import string
import wx.stc as stc

# Local Imports
import completer

#--------------------------------------------------------------------------#

class Completer(completer.BaseCompleter):
    """Code completer provider"""
    autocompFillup = '.,;([]){}<>%^&+-=*/|'
    autocompStop = ' \'"\\`):'
    wordCharacters = "".join(['_', string.letters])
    autocompKeys = []
    caseSensitive = False

    def _GetCompletionInfo(self, command, calltip=False):
        """Get Completion list or Calltip
        @return: list or string

        """
        bf = self.GetBuffer()

        if command in [None, u''] or (len(command) and command[0].isdigit()):
            return bf.GetKeywords()

        currentPos = bf.GetCurrentPos()

        # Get the real word: segment using autocompFillup
        ls = list(command.strip(Completer.autocompFillup))
        ls.reverse()
        idx = 0
        for c in ls:
            if c in Completer.autocompFillup:
                break
            idx += 1
        ls2 = ls[:idx]
        ls2.reverse()
        command = u"".join(ls2)

        # Available completions so far
        wordsNear = []
        maxWordLength = 0
        nWords = 0
        minPos = 0
        maxPos = bf.GetLength()
        flags = stc.STC_FIND_WORDSTART
        if Completer.caseSensitive:
            flags |= stc.STC_FIND_MATCHCASE

        # TODO: calling this with an empty command string causes a program lockup...
        posFind = bf.FindText(minPos, maxPos, command, flags)
        while posFind >= 0 and posFind < maxPos:
            wordEnd = posFind + len(command)
            if posFind != currentPos:
                while -1 != Completer.wordCharacters.find(chr(bf.GetCharAt(wordEnd))):
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

        if len(wordsNear) > 0 and (maxWordLength > len(command)):
            return wordsNear

        return bf.GetKeywords()

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of autocomp activation keys

        """
        return Completer.autocompKeys

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
        return Completer.autocompStop

    def GetAutoCompFillups(self):
        """List of keys to fill up autocompletions on"""
        return Completer.autocompFillup

