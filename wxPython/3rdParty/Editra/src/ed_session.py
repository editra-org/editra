###############################################################################
# Name: ed_session.py                                                         #
# Purpose: Object to help manage editor sessions                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra session file manager.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: $"
__revision__ = "$Revision: $"

#-----------------------------------------------------------------------------#
# Imports
import os
import cPickle

# Editra Imports
import util

#-----------------------------------------------------------------------------#

class EdSessionMgr(object):
    """Simple editing session manager helper class"""
    def __init__(self, savedir):
        """@param savedir: directory to load/save session files at"""
        super(EdSessionMgr, self).__init__()

        # Attributes
        self.__default = '__default' # default session file name
        self._sessiondir = savedir #ed_glob.CONFIG['SESSION_DIR']
        self._sessionext = '.session'

    #---- Properties ----#
    DefaultSession = property(lambda self: self.__default)

    SessionDir = property(lambda self: self._sessiondir,
                          lambda self, dpath: setattr(self, '_sessiondir', dpath))

    def _SetExtension(self, ext):
        assert ext.startswith('.')
        self._sessionext = ext
    SessionExtension = property(lambda self: self._sessionext,
                                lambda self, ext: self._SetExtension(ext))
    Sessions = property(lambda self: self.GetSavedSessions())

    #---- Implementation ----#

    def GetSavedSessions(self):
        """Get the list of available saved sessions by display name
        @return: list of strings

        """
        sessions = list()
        defaultSession = None
        for session in os.listdir(self.SessionDir):
            if session.endswith(self.SessionExtension):
                path = os.path.join(self.SessionDir, session)
                sName = self.SessionNameFromPath(path)
                if session.startswith(self.__default):
                    defaultSession = sName
                else:
                    sessions.append(sName)
        sessions.sort()
        if defaultSession:
            sessions.insert(0, defaultSession)
        return sessions

    def LoadSession(self, name):
        """Load a named session
        @param name: session name
        @return: list of paths

        """
        session = self.PathFromSessionName(name)
        assert os.path.exists(session)
        flist = list()
        with open(session, 'rb') as f_handle:
            # Load and validate file
            try:
                flist = cPickle.load(f_handle)
                # TODO: Extend in future to support loading sessions
                #       for multiple windows.
                flist = flist.get('win1', list())
                for item in flist:
                    if type(item) not in (unicode, str):
                        raise TypeError("Invalid item in unpickled sequence")
            except (cPickle.UnpicklingError, TypeError, EOFError), e:
                util.Log("[ed_session][err] %s" % e)
                raise e # Re throw
        return flist

    def SaveSession(self, name, paths):
        """Save the given list of files as a session with the given name
        @param name: session name
        @return: bool

        """
        session = self.PathFromSessionName(name)
        bOk = False
        with open(session, 'wb') as f_handle:
            try:
                # TODO multi window support
                sdata = dict(win1=paths)
                cPickle.dump(sdata, f_handle)
                bOk = True
            except Exception, msg:
                util.Log("[ed_session][err] Failed to SaveSessionFile: %s" % msg)

        return bOk

    def PathFromSessionName(self, session):
        """Get the full path to store a session file
        @param session: string base name (no extension)

        """
        name = session + ".session"
        path = os.path.join(self.SessionDir, name)
        return path

    def SessionNameFromPath(self, path):
        """Get the sessions display name from its path"""
        assert path.endswith(self.SessionExtension)
        name = os.path.basename(path)
        name = name.rsplit('.', 1)[0]
        return name
