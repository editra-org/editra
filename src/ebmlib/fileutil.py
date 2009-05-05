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
            'MakeNewFolder', 'GetFileExtension', 'GetFileName', 'GetPathName',
            'ResolveRealPath', 'IsLink' ]

#-----------------------------------------------------------------------------#
# Imports
import os
import platform
import stat

UNIX = WIN = False
if platform.system().lower() in ['windows', 'microsoft']:
    WIN = True
    try:
        # Check for if win32 extensions are available
        import win32com.client as win32client
    except ImportError:
        win32client = None
else:
    UNIX = True

#-----------------------------------------------------------------------------#

def GetFileExtension(file_str):
    """Gets last atom at end of string as extension if
    no extension whole string is returned
    @param file_str: path or file name to get extension from

    """
    return file_str.split('.')[-1]

def GetFileModTime(file_name):
    """Returns the time that the given file was last modified on
    @param file_name: path of file to get mtime of

    """
    try:
        mod_time = os.path.getmtime(file_name)
    except (OSError, EnvironmentError):
        mod_time = 0
    return mod_time

def GetFileName(path):
    """Gets last atom on end of string as filename
    @param path: full path to get filename from

    """
    return os.path.split(path)[-1]

def GetFileSize(path):
    """Get the size of the file at a given path
    @param path: Path to file
    @return: long

    """
    try:
        return os.stat(path)[stat.ST_SIZE]
    except:
        return 0

def GetPathName(path):
    """Gets the path minus filename
    @param path: full path to get base of

    """
    return os.path.split(path)[0]

def IsLink(path):
    """Is the file a link
    @return: bool

    """
    if WIN:
        return path.endswith(".lnk") or os.path.islink(path)
    else:
        return os.path.islink(path)

def ResolveRealPath(link):
    """Return the real path of the link file
    @param link: path of link file
    @return: string

    """
    assert IsLink(link), "ResolveRealPath expects a link file!"
    realpath = link
    if WIN and win32client is not None:
        shell = win32client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(link)
        realpath = shortcut.Targetpath
    else:
        realpath = os.path.realpath(link)
    return realpath

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
