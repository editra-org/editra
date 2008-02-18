###############################################################################
# Name: esstags.py                                                            #
# Purpose: Generate Tags for Editra Style Sheets                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: esstags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of Editra Style
Sheets. 

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import taglib
import parselib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Create a DocStruct object that represents an Editra Style Sheet
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('styletag', "Style Tags")

    incomment = False # Inside a comment
    indef = False     # Inside a style definition {}

    for lnum, line in enumerate(buff):
        line = line.strip()
        llen = len(line)
        idx = 0
        while idx < len(line):
            # Check for coments
            if line[idx] == u'/' and llen > idx and line[idx+1] == u'*':
                idx += 1
                incomment = True
            elif line[idx] == u'*' and llen > idx and line[idx+1] == u'/':
                idx += 1
                incomment = False

            # Look for tags
            if incomment:
                idx += 1
            elif line[idx] == u'{':
                idx += 1
                indef = True
            elif indef and line[idx] == u'}':
                idx += 1
                indef = False
            elif not indef and line[idx].isalpha():
                # Found start of tag
                name = parselib.GetFirstIdentifier(line[idx:])
                if name is not None:
                    rtags.AddElement('styletag', StyleTag(name, lnum))
                idx += len(name)
            else:
                idx += 1

    return rtags

#-----------------------------------------------------------------------------#
# Utilities
class StyleTag(taglib.Code):
    """Style Tag Code Object"""
    def __init__(self, name, line, scope=None):
        taglib.Code.__init__(self, name, line, "styletag", scope)

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
