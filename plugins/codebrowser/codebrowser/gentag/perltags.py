###############################################################################
# Name: perltags.py                                                           #
# Purpose: Generate Tags for Perl Scripts                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: perltags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of a Perl Script.
Currently supports parsing of subroutines and their declarations, as well as
package declarations.

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
    """Create a DocStruct object that represents a Perl Script
    @param buff: a file like buffer object (StringIO)

    """
    rtags = taglib.DocStruct()
    rtags.SetElementDescription('package', "Packages")
    rtags.SetElementPriority('package', 3)
    rtags.SetElementDescription('subdec', "Subroutine Declarations")
    rtags.SetElementPriority('subdec', 2)
    rtags.SetElementDescription('subroutine', "Subroutines")
    rtags.SetElementPriority('subroutine', 1)
    inpod = False

    for lnum, line in enumerate(buff):
        # Check for POD docs and skip as necessary
        if line.startswith(u"=") and len(line) > 2:
            if line.startswith(u"=cut"):
                inpod = False
            elif line[1].isalpha():
                inpod = True
            continue

        if inpod:
            continue

        # Not in POD so try to parse for elements
        line = line.strip()
        llen = len(line)

        # Skip comment and empty lines
        if line.startswith(u"#") or not line:
            continue

        # Check for subroutines
        if parselib.IsToken(line, 0, u'sub'):
            sub = ExtractSubroutine(line)
            if sub is not None:
                if sub[0]:
                    rtags.AddElement('subdec',
                                     taglib.Function(sub[1], lnum, "subdec"))
                else:
                    rtags.AddElement('subroutine',
                                     taglib.Function(sub[1], lnum, "subroutine"))
        elif parselib.IsToken(line, 0, u'package'):
            # Look for a package declaration
            parts = line.split()
            if line.endswith(u";") and len(parts) <= 3:
                name = parts[1].rstrip(u";")
                rtags.AddElement('package', taglib.Package(name, lnum))
        else:
            pass

    return rtags

#-----------------------------------------------------------------------------#
# Utilities

def ExtractSubroutine(line):
    """Extract a subroutine defintion from a line, if no valid
    subroutine is found in the line it will return None. It is
    assumed that passed in string starts with 'sub'.
    @param line: string
    @return: tuple (isdecl, name) or None

    """
    line = line[3:].strip()
    sub = ''
    foundname = False
    isdecl = False

    for char in line:
        if char.isalnum() or char == u"_":
            if not foundname:
                sub += char
            else:
                # If the name was already found this is invalid
                break
        elif char in [u";", u":", u"("] and line.endswith(u";"):
            # Declarations can be in a number of forms
            # sub foo;
            # sub foo :attr;
            # sub foo (bar);
            # sub foo (bar) :attr;
            foundname = True
            isdecl = True
            break
        elif char == u"{":
            foundname = True
            isdecl = False
            break
        elif char.isspace():
            # Assume first space found is end of name
            # keep checking to see if its a declaration or not
            foundname = True
        else:
            return None
    else:
        # Reached end of line assume { is on next line
        isdecl = False

    if len(sub) and foundname:
        return (isdecl, sub)
    else:
        return None

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
