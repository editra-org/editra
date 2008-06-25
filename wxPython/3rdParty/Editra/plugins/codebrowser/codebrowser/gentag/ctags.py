###############################################################################
# Name: ctags.py                                                              #
# Purpose: Generate Tags for C Source code                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: ctags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of C source code.

@todo: add support for typdefs/structs/enum

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#

# Imports
import re

# Local Imports
import taglib
import parselib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Create a DocStruct object that represents the structure of a C source
    file.
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('macro', "Macros")
    rtags.SetElementPriority('macro', 3)
    rtags.SetElementDescription('function', "Function Definitions")
    rtags.SetElementPriority('function', 1)

    kwords = ("if else for while switch case")
    txt = buff.read()

    # Get function defintions
    pat = re.compile(r"([A-Za-z0-9_]+[ \t\r\n]+)+([A-Za-z0-9_]+)[ \t\r\n]*\([^)]+\)[ \t\r\n]*\{")
    for match in re.finditer(pat, txt):
        fname = match.group(2)
        if fname and fname not in kwords:
            line = txt.count('\n', 0, match.start(2))
            rtags.AddFunction(taglib.Function(fname, line))

    # Find all Macro defintions
    pat = re.compile(r"#define[ \t]+([A-Za-z0-9_]+)")
    for match in re.finditer(pat, txt):
        line = txt.count('\n', 0, match.start(1))
        rtags.AddElement('macro', taglib.Macro(match.group(1), line))

    return rtags

#-----------------------------------------------------------------------------#

# Test
if __name__ == '__main__':
    import sys
    import StringIO
    fhandle = open(sys.argv[1])
    txt = fhandle.read()
    fhandle.close()
    tags = GenerateTags(StringIO.StringIO(txt))
    print "\n\nElements:"
    for element in tags.GetElements():
        print "\n%s:" % element.keys()[0]
        for val in element.values()[0]:
            print "%s [%d]" % (val.GetName(), val.GetLine())
    print "END"
