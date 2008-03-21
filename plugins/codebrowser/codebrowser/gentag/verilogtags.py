###############################################################################
# Name: verilogtags.py                                                        #
# Purpose: Generate Tags for Verilog and System Verilog Source Files          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: verilogtags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of Verilog and System
Verilog files.

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
    """Create a DocStruct object that represents a Verilog document
    @param buff: a file like buffer object (StringIO)
    @todo: add support for parsing module definitions / class variables

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('class', "Class Definitions")
    rtags.SetElementDescription('function', "Task Definitions")

    # Variables to track parse state
    inclass = False      # Inside a class defintion
    incomment = False    # Inside a comment
    intask = False       # Inside a task definition

    # Parse the text
    for lnum, line in enumerate(buff):
        line = line.strip()
        llen = len(line)
        idx = 0
        while idx < len(line):
            # Skip any leading Whitespace
            idx += (len(line[idx:]) - len(line[idx:].lstrip()))

            # Check for coments
            if line[idx:].startswith(u'/*'):
                idx += 2
                incomment = True
            elif line[idx:].startswith(u'//'):
                break # go to next line
            elif line[idx:].startswith(u'*/'):
                idx += 2
                incomment = False

            # At end of line
            if idx >= llen:
                break

            # Look for tags
            if incomment:
                idx += 1
            elif line[idx:].startswith(u"class") and len(line[idx:]) > 5 and \
                 line[idx+5].isspace() and \
                 ((idx > 0 and line[idx-1].isspace()) or idx == 0):
                idx += 5 # jump past class word
                idx += (len(line[idx:]) - len(line[idx:].lstrip()))
                cname = parselib.GetFirstIdentifier(line[idx:])
                if cname is not None:
                    inclass = True
                    rtags.AddClass(taglib.Class(cname, lnum))
                break # go to next line
            elif inclass and line[idx:].startswith(u"endclass") and \
                 ((len(line[idx:]) > 8 and line[idx+8].isspace()) or \
                   len(line[idx:]) == 8):
                inclass = False
                break # go to next line
            elif line[idx:].startswith(u"task") and len(line[idx:]) > 4 and \
                 line[idx+4].isspace() and \
                 ((idx > 0 and line[idx-1].isspace()) or idx == 0):
                idx += 4
                idx += (len(line[idx:]) - len(line[idx:].lstrip()))
                tname = parselib.GetFirstIdentifier(line[idx:])
                if tname is not None:
                    intask = True
                    if inclass:
                        lclass = rtags.GetLastClass()
                        lclass.AddMethod(taglib.Method(tname, lnum))
                    else:
                        rtags.AddFunction(taglib.Function(tname, lnum))
                break # goto next line
            elif intask and line[idx:].startswith(u"endtask") and \
                 len(line[idx:]) > 7 and line[idx+7].isspace():
                intask = False
                break # go to next line
            else:
                idx += 1

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
