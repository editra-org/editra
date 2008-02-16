###############################################################################
# Name: shtags.py                                                             #
# Purpose: Generate Tags for Shell Scripts                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: shtags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of a shell script,
the returned structure contains all the function definitions in the document.
It currently should work well with Bourne, Bash, Korn, and C-Shell scripts.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import taglib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Create a DocStruct object that represents a Shell Script
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    for lnum, line in enumerate(buff):
        line = line.strip()

        # Skip comment and empty lines
        if line.startswith(u"#") or not line:
            continue

        # Check Regular Function Defs
        if line.startswith(u'function '):
            parts = line.split()
            plen = len(parts)
            if plen >= 2 and IsValidName(parts[1]):
                if plen == 2 or parts[2] == u"{" and parts[1] not in names:
                    rtags.AddFunction(taglib.Function(parts[1], lnum))
                    names.append(parts[1])
            continue

        # Check fname () function defs
        if u"(" in line:
            parts = line.split()
            plen = len(parts)
            if plen >= 2 and IsValidName(parts[0]):
                if u''.join(parts[1:]).startswith("()"):
                    rtags.AddFunction(taglib.Function(parts[0], lnum))
            else:
                continue

    return rtags

#-----------------------------------------------------------------------------#
# Utilities
def IsValidName(name):
    for char in name:
        if char.isalnum() or char == "_":
            continue
        else:
            return False
    return True

#-----------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    import sys
    import StringIO
    fhandle = open(sys.argv[1])
    txt = fhandle.read()
    fhandle.close()
    tags = GenerateTags(StringIO.StringIO(txt))
    print "\n\nFUNCTIONS:"
    for fun in tags.GetFunctions():
        print "%s [%d]" % (fun.GetName(), fun.GetLine())
    print "END"
