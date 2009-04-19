###############################################################################
# Name: fchecker.py                                                           #
# Purpose: Filetype checker object.                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: FileTypeChecker

Helper class for checking what kind of a content a file contains.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'FileTypeChecker', ]

#-----------------------------------------------------------------------------#
# Imports
import os

#-----------------------------------------------------------------------------#

class FileTypeChecker(object):
    """File type checker and recognizer"""
    TXTCHARS = ''.join(map(chr, [7, 8, 9, 10, 12, 13, 27] + range(0x20, 0x100)))
    ALLBYTES = ''.join(map(chr, range(256)))

    def __init__(self, preread=4096):
        """Create the FileTypeChecker
        @keyword preread: number of bytes to read for checking file type

        """
        object.__init__(self)

        # Attributes
        self._preread = preread

    @staticmethod
    def _GetHandle(fname):
        """Get a file handle for reading
        @param fname: filename
        @return: file object or None

        """
        try:
            handle = open(fname, 'rb')
        except:
            handle = None
        return handle

    def IsBinary(self, fname):
        """Is the file made up of binary data
        @param fname: filename to check
        @return: bool

        """
        handle = self._GetHandle(fname)
        if handle is not None:
            bytes = handle.read(self._preread)
            handle.close()
            nontext = bytes.translate(FileTypeChecker.ALLBYTES,
                                      FileTypeChecker.TXTCHARS)
            return bool(nontext)
        else:
            return False

    def IsReadableText(self, fname):
        """Is the given path readable as text
        @param fname: filename

        """
        f_ok = False
        if os.access(fname, os.R_OK):
            f_ok = not self.IsBinary(fname)
        return f_ok
