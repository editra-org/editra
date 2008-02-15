###############################################################################
# Name: nsistags.py                                                           #
# Purpose: Generate Tags for Nullsoft Installer Scripts                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: nsistags.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  Generate a DocStruct object that captures the structure of a NSIS Script. It
currently supports generating tags for Sections, Functions, and Macro defs.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import taglib

#--------------------------------------------------------------------------#

def GenerateTags(buff):
    """Create a DocStruct object that represents a NSIS Script
    @param buff: a file like buffer object (StringIO)
    @todo: generate tags for lua tables?

    """
    rtags = taglib.DocStruct()

    # Set Descriptions of Document Element Types
    rtags.SetElementDescription('section', "Sections Definitions")
    rtags.SetElementDescription('macro', "Macros Definitions")

    # Parse the lines for code objects
    for lnum, line in enumerate(buff):
        line = line.strip()
        llen = len(line)

        # Skip comment and empty lines
        if line.startswith(u"#") or line.startswith(u";") or not line:
            continue

        # Look for functions and sections
        if line.startswith('Function') and llen > 8 and line[8].isspace():
            parts = [ part.strip() for part in line.split() ]
            if len(parts) > 1:
                rtags.AddFunction(taglib.Function(parts[1], lnum))
        elif line.startswith('Section') and llen > 7 and line[7].isspace():
            parts = [ part.strip() for part in line.split() ]
            if len(parts) > 1 and parts[1][0] not in ['"', "'", "`"]:
                rtags.AddElement('section', taglib.Section(parts[1], lnum))
            elif len(parts) > 2:
                rtags.AddElement('section', taglib.Section(parts[3], lnum))
        elif line.startswith('!macro') and llen > 6 and line[6].isspace():
            parts = [ part.strip() for part in line.split() ]
            if len(parts) > 1:
                rtags.AddElement('macro', taglib.Macro(parts[1], lnum))
        else:
            continue

    return rtags
