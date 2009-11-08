###############################################################################
# Name: txtutil.py                                                            #
# Purpose: Text Utilities.                                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Business Model Library: Text Utilities

Utility functions for managing and working with text.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'IsUnicode', ]

#-----------------------------------------------------------------------------#
# Imports
import types

#-----------------------------------------------------------------------------#

def IsUnicode(txt):
    """Is the given string a unicode string
    @param txt: object
    @return: bool

    """
    return isinstance(txt, types.UnicodeType)
