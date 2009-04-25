###############################################################################
# Name: backupmgr.py                                                          #
# Purpose: File Backup Manager                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: FileBackupMgr

Helper class for managing and creating backups of files.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'FileBackupMgr', ]

#-----------------------------------------------------------------------------#
# Imports
import os
import shutil

# Local Imports
import fileutil

#-----------------------------------------------------------------------------#

class FileBackupMgr(object):
    """File backup creator and manager"""
    def __init__(self):
        object.__init__(self)

        # Attributes
        

    @staticmethod
    def GetBackupFilename(fname):
        """Get the unique name for the files backup copy
        @param fname: string (file path)
        @return: string

        """
        return u"%s~" % fname

    def HasBackup(self, fname):
        """Check if a given file has a backup file available or not
        @param fname: string (file path)

        """
        backup = self.GetBackupFilename(fname)
        return os.path.exists(backup)

    def IsBackupNewer(self, fname):
        """Is the backup of this file newer than the saved version
        of the file?
        @param fname: string (file path)
        @return: bool

        """
        backup = self.GetBackupFilename(fname)
        if os.path.exists(fname) and os.path.exists(backup):
            mod1 = fileutil.GetFileModTime(backup)
            mod2 = fileutil.GetFileModTime(fname)
            return mod1 > mod2
        else:
            return False

    def MakeBackupCopy(self, fname):
        """Create a backup copy of the given filename
        @param fname: string (file path)
        @return: bool (True == Success)

        """
        backup = self.GetBackupFilename(fname)
        try:
            if os.path.exists(backup):
                os.remove(backup)

            shutil.copy2(fname, backup)
        except:
            return False
        else:
            return True

    def MakeBackupCopyAsync(self, fname):
        """Do the backup asyncronously
        @param fname: string (file path)
        @todo: Not implemented yet

        """
        raise NotImplementedError, "TODO: once threadpool is finished"
