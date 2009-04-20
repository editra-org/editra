###############################################################################
# Name: fileutil.py                                                           #
# Purpose: File Management Utilities.                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: File Utilities

Utility functions for managing and working with files.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'GetFileModTime', 'GetFileSize', 'GetUniqueName', 'MakeNewFile',
            'MakeNewFolder' ]

#-----------------------------------------------------------------------------#
# Imports
import os
import stat

#-----------------------------------------------------------------------------#

def GetFileModTime(file_name):
    """Returns the time that the given file was last modified on
    @param file_name: path of file to get mtime of

    """
    try:
        mod_time = os.path.getmtime(file_name)
    except (OSError, EnvironmentError):
        mod_time = 0
    return mod_time

def GetFileSize(path):
    """Get the size of the file at a given path
    @param path: Path to file
    @return: long

    """
    try:
        return os.stat(path)[stat.ST_SIZE]
    except:
        return 0

#-----------------------------------------------------------------------------#

def GetUniqueName(path, name):
    """Make a file name that will be unique in case a file of the
    same name already exists at that path.
    @param path: Root path to folder of files destination
    @param name: desired file name base
    @return: string

    """
    tmpname = os.path.join(path, name)
    if os.path.exists(tmpname):
        if '.' not in name:
            ext = ''
            fbase = name
        else:
            ext = '.' + name.split('.')[-1]
            fbase = name[:-1 * len(ext)]

        inc = len([x for x in os.listdir(path) if x.startswith(fbase)])
        tmpname = os.path.join(path, "%s-%d%s" % (fbase, inc, ext))
        while os.path.exists(tmpname):
            inc = inc + 1
            tmpname = os.path.join(path, "%s-%d%s" % (fbase, inc, ext))

    return tmpname


#-----------------------------------------------------------------------------#

def MakeNewFile(path, name):
    """Make a new file at the given path with the given name.
    If the file already exists, the given name will be changed to
    a unique name in the form of name + -NUMBER + .extension
    @param path: path to directory to create file in
    @param name: desired name of file
    @return: Tuple of (success?, Path of new file OR Error message)

    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    fname = GetUniqueName(path, name)

    try:
        open(fname, 'w').close()
    except (IOError, OSError), msg:
        return (False, str(msg))

    return (True, fname)

def MakeNewFolder(path, name):
    """Make a new folder at the given path with the given name.
    If the folder already exists, the given name will be changed to
    a unique name in the form of name + -NUMBER.
    @param path: path to create folder on
    @param name: desired name for folder
    @return: Tuple of (success?, new dirname OR Error message)

    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    folder = GetUniqueName(path, name)
    try:
        os.mkdir(folder)
    except (OSError, IOError), msg:
        return (False, str(msg))

    return (True, folder)
