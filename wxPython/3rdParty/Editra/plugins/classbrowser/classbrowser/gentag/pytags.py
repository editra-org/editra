###############################################################################
# Name: pytags.py                                                             #
# Purpose: Generate Python Tags                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE:
AUTHOR:
LANGUAGE: Python
SUMMARY:

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import taglib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Find all python tags in a given buffer object
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    parents = list()
    indent = 0
    indocstring = False
    lastclass = None
    infunction = False
    fn_indent = 0

    for lnum, line in enumerate(buff):
        indent = 0
        idx = 0
        while idx < len(line):
            # Check for docstrings
            if line[idx] in ['"', "'"] and line[idx:idx+3] in ['"""', "'''"]:
                indocstring = not indocstring
                idx += 3

            # If end of line break
            if idx == len(line) or line[idx] == u"#":
                break

            # Check indent sensitive tokens
            if not indocstring and not line[idx].isspace():

                if infunction and indent < fn_indent:
                    infunction = False

                if lastclass is not None:
                    if indent <= lastclass.get('indent', 0):
                        parents = CleanList(parents, indent)
                        if len(parents):
                            lastclass = parents[-1]
                        else:
                            lastclass = None
            
            if indocstring:
                idx = idx + 1
            elif line[idx].isspace():
                # Get indent width
                if idx == 0:
                    tstr = str(line)
                    indent = (len(tstr) - len(tstr.lstrip()))
                    idx += indent
                else:
                    # Non indent space
                    idx = idx + 1
            elif line[idx] == u"#":
                break
            elif line[idx:idx+5] == u"class":
                idx += 5
                if line[idx].isspace():
                    if u'(' in line:
                        cname = line[idx:].split('(')[0].strip()
                    else:
                        cname = line[idx:].split(':')[0].strip()

                    if lastclass is None:
                        rtags.AddClass(taglib.Class(cname, lnum))
                    # TODO: check for classes defined within classes

                    lastclass = dict(name=cname, indent=indent)
                    parents.append(dict(lastclass))
                    break
            elif line[idx:idx+3] == u"def":
                # Function/Method Definition
                idx += 3
                if line[idx].isspace():
                    fname = line[idx:].split('(')[0].strip()
                    infunction = True
                    fn_indent = indent + 1
                    if not line[0].isspace() or lastclass is None or not len(lastclass.get("name", "")):
                        rtags.AddFunction(taglib.Function(fname, lnum))
                    else:
                        lclass = rtags.GetLastClass()
                        if lclass is not None:
                            lclass.AddMethod(taglib.Method(fname, lnum, lclass.GetName()))
                        else:
                            print "ERR What shoudl I do?"
                    break
            elif not infunction and line[idx] == u"=":
                # TODO: Parse global and class variables
                break
            else:
                break

    return rtags

#-----------------------------------------------------------------------------#
# Utilities

def CleanList(lst, indent):
    """Clean the list of classes based on indent. The list should
    be a list of dictionary objects [dict(name='', indent=0),]

    """
    rlist = list()
    for item in lst:
        if item.get('indent', 0) >= indent:
            continue
        else:
            rlist.append(item)
    return rlist

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
    print ""
    print "CLASSES:"
    for c in tags.GetClasses():
        print "* %s [%d]" % (c.GetName(), c.GetLine())
        for meth in c.GetMethods():
            print "    %s [%d]" % (meth.GetName(), meth.GetLine())
    print "END"
