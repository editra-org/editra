###############################################################################
# Name: tcltags.py                                                            #
# Purpose: Generate Tags for Tcl Scripts                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: tcltags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of a Tcl Scripts.
Currently supports searching for Procedure definitions.

TODO: Add support for namespace parsing?

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import taglib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Create a DocStruct object that represents a Tcl Script
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('procedure', "Procedure Definitions")

    for lnum, line in enumerate(buff):
        line = line.strip()

        # Skip comment and empty lines
        if line.startswith(u"#") or not line:
            continue

        # Check for Procedure defs
        if line.startswith(u'proc'):
            parts = line.split()
            if len(parts) > 1 and parts[1].isalnum():
                rtags.AddElement('procedure', taglib.Procedure(parts[1], lnum))

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
    print "\n\nFUNCTIONS:"
    for fun in tags.GetFunctions():
        print "%s [%d]" % (fun.GetName(), fun.GetLine())
    print "END"
