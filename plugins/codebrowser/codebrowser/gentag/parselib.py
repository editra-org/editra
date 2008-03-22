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

def IsGoodName(name):
    """Check if the name is a valid identifier name or not. A valid identifer
    is a string that only has alpha numeric and/or "_" characters in it. Also
    meaning it matches the following character class [a-zA-Z0-8_]+
    @param name: name to check
    @return: bool

    """
    # Try a quick check for common case first to try and save some time
    if name.isalnum():
        return True
    else:
        for char in name:
            if char.isalnum() or char == u'_':
                continue
            else:
                return False
    return True

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
