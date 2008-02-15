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
  Generate a DocStruct object that captures the structure of a shell script

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
    @note: only generates function tags and will only generate a tag for
           the first time it finds a given function.

    """
    rtags = taglib.DocStruct()
    names = list()
    for lnum, line in enumerate(buff):
        line = line.strip()

        # Skip comment and empty lines
        if line.startswith(u"#") or not line:
            continue

        # Check Regular Function Defs
        if line.startswith(u'function '):
            parts = [ part.strip() for part in line.split() ]
            plen = len(parts)
            if plen >= 2 and IsValidName(parts[1]):
                if plen == 2 or parts[2] == u"{" and parts[1] not in names:
                    rtags.AddFunction(taglib.Function(parts[1], lnum))
                    names.append(parts[1])
            continue

        # Check fname () function defs
        parts = [ part.strip() for part in line.split() ]
        plen = len(parts)
        if plen >= 2 and parts[1].startswith("(") and IsValidName(parts[0]):
            if u''.join(parts[1:]).startswith("()") and parts[0] not in names:
                rtags.AddFunction(taglib.Function(parts[0], lnum))
                names.append(parts[0])
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
