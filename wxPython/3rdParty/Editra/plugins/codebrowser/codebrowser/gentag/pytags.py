###############################################################################
# Name: pytags.py                                                             #
# Purpose: Generate Python Tags                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: pytags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of a python document.
It supports parsing for global and class variables, class, method, and function
definitions.

@fixme: Functions defined within functions/methods produce some parsing mistakes
@fixme: Classes defined within subscopes of the module scope are not parsed

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
    """Create a DocStruct object that represents a Python file
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('function', "Function Definitions")
    rtags.SetElementDescription('class', "Class Definitions")

    # Variables for managing the state of the parse
    parents = list()
    indent = 0
    fn_indent = 0
    parens = 0          # Paren nesting count
    indocstring = False
    ind_string = False  # Double quote string
    ins_string = False  # Single quote string
    infunction = False
    lastclass = None

    def IsEscaped(line, pos):
        """Check if the character at the given position is escaped or not
        @param line: string to check
        @param pos: position in string to check before

        """
        slashes = len(line[:pos]) - len(line[:pos].rstrip('\\'))
        return slashes % 2

    def InString():
        """Return whether the current state of the parse is in a string
        or not.

        """
        return indocstring or ind_string or ins_string

    # Do the parse of the text
    for lnum, line in enumerate(buff):
        indent = 0
        idx = 0
        llen = len(line)
        while idx < llen:
            # Check for docstrings
            if not (ind_string or ins_string) and \
               llen >= idx + 3 and line[idx:idx+3] in ['"""', "'''"]:
                indocstring = not indocstring
                idx += 3
                continue

            # If end of line or start of comment start next line
            if idx == llen or (line[idx] == u"#" and not InString()):
                break

            # Check indent sensitive tokens
            if not indocstring and not line[idx].isspace():

                if infunction and indent < fn_indent:
                    infunction = False

                if lastclass is not None:
                    if indent <= lastclass.get('indent', 0):
                        parents = PopScopes(parents, indent)
                        if len(parents):
                            lastclass = parents[-1]
                        else:
                            lastclass = None

                # Check for if in a string or not
                if line[idx] == u"'" and not ind_string and \
                   not IsEscaped(line, idx-1): # Single string
                    ins_string = not ins_string
                elif line[idx] == u'"' and not ins_string and \
                     not IsEscaped(line, idx-1): # Double String
                    ind_string = not ind_string
                else:
                    pass

            # Parse and look for elements to add to the DocStruct
            if InString():
                # Token is in a string so ignore and move on
                idx = idx + 1
            elif line[idx].isspace():
                # Get indent width for current scope
                if idx == 0:
                    indent = (len(line) - len(line.lstrip()))
                    idx += indent
                else:
                    # Non indent space
                    idx += 1
            elif parselib.IsToken(line, idx, u'class'):
                idx += 5
                cname = parselib.GetFirstIdentifier(line[idx:])
                if cname is not None:
                    if lastclass is None:
                        rtags.AddClass(taglib.Class(cname, lnum))
                    # TODO: check for classes defined within classes

                    lastclass = dict(name=cname, indent=indent)
                    parents.append(dict(lastclass))
                    break # Go to next line
            elif parselib.IsToken(line, idx, u'def'):
                # Function/Method Definition
                idx += 3
                fname = parselib.GetFirstIdentifier(line[idx:])
                if line[idx].isspace() and fname is not None:
                    infunction = True
                    fn_indent = indent + 1
                    if not line[0].isspace() or lastclass is None or \
                       not len(lastclass.get("name", "")):
                        rtags.AddFunction(taglib.Function(fname, lnum))
                    else:
                        lclass = rtags.GetLastClass()
                        if lclass is not None:
                            lclass.AddMethod(taglib.Method(fname, lnum, lclass.GetName()))
                        else:
                            # Something must have failed with the parse so
                            # ignore this element.
                            pass
                    break
            elif not infunction and line[idx] in u"()":
                # Track paren nesting to help with variable parsing
                if line[idx] == u"(":
                    parens += 1
                else:
                    parens -= 1
                idx += 1
            elif not infunction and line[idx] == u"=" and not parens:
                # Check for Global and Class variables
                idx += 1
                if line[idx] != u"=": # ignore == statements
                    var = line[:idx-1].strip().split()
                    if len(var) == 1 and parselib.IsGoodName(var[0]):
                        lclass = rtags.GetLastClass()
                        # Check if we are still inside a class def or not
                        if lastclass is not None and lclass is not None:
                            vobj = taglib.Variable(var[0], lnum, lclass.GetName())
                            lclass.AddVariable(vobj)
                        else:
                            # Global Scope variable
                            rtags.AddVariable(taglib.Variable(var[0], lnum))
            else:
                # Nothing so skip ahead
                idx += 1

    # Return the document structure object
    return rtags

#-----------------------------------------------------------------------------#
# Utilities

class PyFunction(taglib.Scope):
    """Python Functions/Methods need to derive from scope as they can
    contain definitions of other functions/methods

    """
    def __init__(self, name, line, obj="function", scope=None):
        Scope.__init__(self, name, line, obj, scope)

    def AddFunction(self, funct):
        """Convinience method for adding a function to this functions
        scope.

        """
        self.AddElement('function', method)

def PopScopes(lst, indent):
    """Pop all parent scopes until the list only contains scopes that are
    higher up in the hierarchy. The list should be a list of dictionary objects
    [dict(name='', indent=0),].
    @param lst: list of dictionaries
    @param indent: indent to check for

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
    print "\n\nVARIABLES:"
    for var in tags.GetVariables():
        print "%s [%d]" % (var.GetName(), var.GetLine())
    print "\n\nFUNCTIONS:"
    for fun in tags.GetFunctions():
        print "%s [%d]" % (fun.GetName(), fun.GetLine())
    print ""
    print "CLASSES:"
    for c in tags.GetClasses():
        print "* %s [%d]" % (c.GetName(), c.GetLine())
        for var in c.GetVariables():
            print "VAR: ", var.GetName()
        for meth in c.GetMethods():
            print "    %s [%d]" % (meth.GetName(), meth.GetLine())
    print "END"
