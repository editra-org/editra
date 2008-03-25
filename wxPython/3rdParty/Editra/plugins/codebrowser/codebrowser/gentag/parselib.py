###############################################################################
# Name: parselib.py                                                           #
# Purpose: Common parseing utility functions                                  #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: parselib.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
    Contains misc common parsing helper functions used by the various parsers
in this library.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Function Definitions

def GetFirstIdentifier(line):
    """Extract the first identifier from the given line. Identifiers are
    classified as the first contiguous string of characters that only contains
    AlphaNumeric or "_" character. In other words [a-zA-Z0-9_]+.
    @return: identifer name or None

    """
    name = ''
    for char in line.strip():
        if char.isalnum() or char == "_":
            name += char
        else:
            break

    if len(name):
        return name
    else:
        return None

def GetTokenParenLeft(line, exchars='_'):
    """Get the first identifer token to the left of the first opening paren
    found in the given line.
    @param line: line to search
    @example: function myfunct(param1) => myfunct
    @keyword exchars: Extra non-alphnumeric characters that can be in the token
    @return: string or None

    """
    pidx = line.find(u'(')
    if pidx != -1:
        token = u''
        # Walk back from the paren ignoring whitespace
        for char in reversed(line[:pidx]):
            if char.isspace():
                if len(token):
                    break
            elif char.isalnum() or char in exchars:
                token += char
            else:
                break

        if len(token):
            return u"".join([char for char in reversed(token)])

    return None

def IsGoodName(name, exchars='_'):
    """Check if the name is a valid identifier name or not. A valid identifer
    is a string that only has alpha numeric and/or the specifed exchars in it.
    Also meaning it matches the following character class [a-zA-Z_][a-zA-Z0-8_]+
    @param name: name to check
    @keyword exchars: extra non alphanumeric characters that are valid
    @return: bool

    """
    if len(name) and (name[0].isalpha() or name[0] in exchars):
        for char in name:
            if char.isalnum() or char in exchars:
                continue
            else:
                return False
        return True
    else:
        return False

def IsToken(line, idx, name):
    """Check if the given item is a token or not. The function will return
    True if the item at the given index matches the name and is preceeded and
    followed by whitespace. It will return False otherwise.
    @param line: string to check
    @param idx: index in string to look from
    @param name: name of token to look for match
    @return: bool

    """
    nchar = idx + len(name)
    if line[idx:].startswith(name) and \
       (idx == 0 or line[idx-1].isspace()) and \
       (len(line) > nchar and line[nchar].isspace()):
        return True
    else:
        return False

def SkipWhitespace(line, idx):
    """Increment and return the index in the current line past any whitespace
    @param line: string
    @param idx: index to check from in line
    @return: int

    """
    return idx + (len(line[idx:]) - len(line[idx:].lstrip()))
