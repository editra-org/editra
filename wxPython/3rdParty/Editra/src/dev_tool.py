###############################################################################
# Name: dev_tool.py                                                           #
# Purpose: Provides logging and error tracking utilities                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

""" Editra Development Tools 
@author: Cody Precord
@summary: Utility function for debugging the editor

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re
import platform
import traceback
import codecs
import time
import webbrowser
import wx
import ed_glob
import ed_msg

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation
RE_LOG_LBL = re.compile(r"\[(.+?)\]")

#-----------------------------------------------------------------------------#
# General Debuging Helper Functions

def DEBUGP(statement):
    """Prints debug messages and broadcasts them on the log message channel.
    Subscribing a listener with any of the EDMSG_LOG_* types will recieve its
    messages from this method.
    @param statement: Should be a formatted string that starts with two
                      identifier blocks. The first is used to indicate the
                      source of the message and is used as the primary means
                      of filtering. The second block is the type of message,
                      this is used to indicate the priority of the message and
                      is used as the secondary means of filtering.

        1. Formatting
            - [object/module name][msg_type] message string

        2. Message Type:
            - [err]  : Notes an exception or error condition (high priority)
            - [warn] : Notes a error that is not severe (medium priority)
            - [info] : General information message (normal priority)
            - [evt]  : Event related message (normal priority)

    @example: DEBUGP([ed_main][err] File failed to open)

    """
    # Create a LogMsg object from the statement string
    lbls = [lbl.strip() for lbl in RE_LOG_LBL.findall(statement)]
    info = RE_LOG_LBL.sub('', statement, 2).rstrip()
    if len(lbls) > 1:
        msg = LogMsg(info, lbls[0], lbls[1])
    elif len(lbls) == 1:
        msg = LogMsg(info, lbls[0])
    else:
        msg = LogMsg(info)

    # Only print to stdout when DEBUG is active
    if ed_glob.DEBUG:
        print str(msg)

    # Dispatch message to all interested parties
    if msg.Type in ['err', 'error']:
        mtype = ed_msg.EDMSG_LOG_ERROR
    elif msg.Type in ['warn', 'warning']:
        mtype = ed_msg.EDMSG_LOG_WARN
    elif msg.Type in ['evt', 'event']:
        mtype = ed_msg.EDMSG_LOG_EVENT
    elif msg.Type in ['info', 'information']:
        mtype = ed_msg.EDMSG_LOG_INFO
    else:
        mtype = ed_msg.EDMSG_LOG_ALL

    ed_msg.PostMessage(mtype, msg)

#-----------------------------------------------------------------------------#

class LogMsg:
    """LogMsg is a container class for representing log messages. Converting
    it to a string will yield a formatted log message with timestamp. Once a
    message has been displayed once (converted to a string) it is marked as
    being expired.

    """
    def __init__(self, msg, msrc='unknown', level="info"):
        """Create a LogMsg object
        @param msg: the log message string
        @keyword msrc: Source of message
        @keyword level: Priority of the message

        """
        # Attributes
        self._msg = dict(mstr=msg, msrc=msrc, lvl=level, tstamp=time.time())
        self._ok = True

    def __eq__(self, other):
        """Define the equal to operation"""
        return self.TimeStamp == other.TimeStamp

    def __ge__(self, other):
        """Define the greater than or equal to operation"""
        return self.TimeStamp >= other.TimeStamp

    def __gt__(self, other):
        """Define the greater than operation"""
        return self.TimeStamp > other.TimeStamp

    def __le__(self, other):
        """Define the less than or equal to operation"""
        return self.TimeStamp <= other.TimeStamp

    def __lt__(self, other):
        """Define the less than operation"""
        return self.TimeStamp < other.TimeStamp

    def __repr__(self):
        """String representation of the object"""
        return '<LogMsg %s:%d>' % (self._msg['lvl'], self._msg['tstamp'])

    def __str__(self):
        """Returns a nice formatted string version of the message"""
        statement = unicode(self._msg['mstr'])
        s_lst = [u"[%s][%s][%s]%s" % (self.ClockTime, self._msg['msrc'],
                                      self._msg['lvl'], msg) 
                 for msg in statement.split(u"\n")
                 if len(msg.strip())]
        out = os.linesep.join(s_lst)

        # Mark Message as have being fetched (expired)
        self._ok = False

        return out.encode('utf-8', 'replace')

    @property
    def ClockTime(self):
        ltime = time.localtime(self._msg['tstamp'])
        tstamp = u"%s:%s:%s" % (str(ltime[3]).zfill(2),
                                str(ltime[4]).zfill(2),
                                str(ltime[5]).zfill(2))
        return tstamp

    @property
    def Expired(self):
        """Has this message already been retrieved
        @return: bool

        """
        return not self._ok

    @property
    def Origin(self):
        """Where the message came from
        @return: string

        """
        return self._msg['msrc']

    @property
    def TimeStamp(self):
        """Property for accessing timestamp
        @return: long int

        """
        return self._msg['tstamp']

    @property
    def Type(self):
        """The messages level type
        @return string (err, warn, info, evt)

        """
        return self._msg['lvl']

    @property
    def Value(self):
        """Returns the message part of the log string
        @return: string

        """
        return self._msg['mstr']

#-----------------------------------------------------------------------------#

def EnvironmentInfo():
    """Returns a string of the systems information
    @return: System information string

    """
    info = list()
    info.append("#---- System Information ----#")
    info.append("%s Version: %s" % (ed_glob.PROG_NAME, ed_glob.VERSION))
    info.append("Operating System: %s" % wx.GetOsDescription())
    if sys.platform == 'darwin':
        info.append("Mac OSX: %s" % platform.mac_ver()[0])
    info.append("Python Version: %s" % sys.version)
    info.append("wxPython Version: %s" % wx.version())
    info.append("wxPython Info: (%s)" % ", ".join(wx.PlatformInfo))
    info.append("Python Encoding: Default=%s  File=%s" % \
                (sys.getdefaultencoding(), sys.getfilesystemencoding()))
    info.append("wxPython Encoding: %s" % wx.GetDefaultPyEncoding())
    info.append("System Architecture: %s %s" % (platform.architecture()[0], \
                                                platform.machine()))
    info.append("Byte order: %s" % sys.byteorder)
    info.append("Frozen: %s" % str(getattr(sys, 'frozen', 'False')))
    info.append("#---- End System Information ----#")
    info.append("#---- Runtime Variables ----#")
    from profiler import Profile
    ftypes = list()
    for key in sorted(Profile().keys()):
        # Exclude "private" information
        val = Profile().Get(key)
        if key.startswith('FILE') or 'proxy' in key.lower():
            continue
        elif key == 'LAST_SESSION' or key == 'FHIST':
            for fname in val:
                if '.' in fname:
                    ext = fname.split('.')[-1]
                    if ext not in ftypes:
                        ftypes.append(ext)
        else:
            info.append(u"%s=%s" % (key, str(val)))
    info.append(u"FTYPES=%s" % str(ftypes))
    info.append("#---- End Runtime Variables ----#")

    return os.linesep.join(info)

def ExceptionHook(exctype, value, trace):
    """Handler for all unhandled exceptions
    @param exctype: Exception Type
    @param value: Error Value
    @param trace: Trace back info

    """
    ftrace = FormatTrace(exctype, value, trace)

    # Ensure that error gets raised to console as well
    print ftrace

    # If abort has been set and we get here again do a more forcefull shutdown
    global ABORT
    if ABORT:
        os._exit(1)

    # Prevent multiple reporter dialogs from opening at once
    global REPORTER_ACTIVE
    if not REPORTER_ACTIVE and not ABORT:
        ErrorDialog(ftrace)

def FormatTrace(etype, value, trace):
    """Formats the given traceback
    @return: Formatted string of traceback with attached timestamp

    """
    exc = traceback.format_exception(etype, value, trace)
    exc.insert(0, "*** %s ***%s" % (TimeStamp(), os.linesep))
    return "".join(exc)

def TimeStamp():
    """Create a formatted time stamp of current time
    @return: Time stamp of the current time (Day Month Date HH:MM:SS Year)
    @rtype: string

    """
    now = time.localtime(time.time())
    now = time.asctime(now)
    return now

#-----------------------------------------------------------------------------#

class ErrorReporter(object):
    """Crash/Error Reporter Service
    @summary: Stores all errors caught during the current session and
              is implemented as a singleton so that all errors pushed
              onto it are kept in one central location no matter where
              the object is called from.

    """
    instance = None
    _first = True
    def __init__(self):
        """Initialize the reporter
        @note: The ErrorReporter is a singleton.

        """
        # Ensure init only happens once
        if self._first:
            object.__init__(self)
            self._first = False
            self._sessionerr = list()
        else:
            pass

    def __new__(cls, *args, **kargs):
        """Maintain only a single instance of this object
        @return: instance of this class

        """
        if not cls.instance:
            cls.instance = object.__new__(cls, *args, **kargs)
        return cls.instance

    def AddMessage(self, msg):
        """Adds a message to the reporters list of session errors
        @param msg: The Error Message to save

        """
        if msg not in self._sessionerr:
            self._sessionerr.append(msg)

    def GetErrorStack(self):
        """Returns all the errors caught during this session
        @return: formatted log message of errors

        """
        return "\n\n".join(self._sessionerr)

    def GetLastError(self):
        """Gets the last error from the current session
        @return: Error Message String

        """
        if len(self._sessionerr):
            return self._sessionerr[-1]
        
#-----------------------------------------------------------------------------#

ID_SEND = wx.NewId()
ABORT = False
REPORTER_ACTIVE = False
class ErrorDialog(wx.Dialog):
    """Dialog for showing errors and and notifying Editra.org should the
    user choose so.

    """
    def __init__(self, message):
        """Initialize the dialog
        @param message: Error message to display

        """
        global REPORTER_ACTIVE
        REPORTER_ACTIVE = True
        wx.Dialog.__init__(self, None, title="Error/Crash Reporter", 
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        # Give message to ErrorReporter
        ErrorReporter().AddMessage(message)

        # Attributes
        self.err_msg = "%s\n\n%s\n%s\n%s" % (EnvironmentInfo(), \
                                             "#---- Traceback Info ----#", \
                                             ErrorReporter().GetErrorStack(), \
                                             "#---- End Traceback Info ----#")
        # Layout
        self._DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Auto show at end of init
        self.CenterOnParent()
        self.ShowModal()

    def _DoLayout(self):
        """Layout the dialog and prepare it to be shown
        @note: Do not call this method in your code

        """
        # Objects
        icon = wx.StaticBitmap(self, 
                               bitmap=wx.ArtProvider.GetBitmap(wx.ART_ERROR))
        mainmsg = wx.StaticText(self, 
                                label=_("Error: Oh no something bad happend\n"
                                        "Help improve Editra by clicking on "
                                        "Report Error\nto send the Error "
                                        "Traceback shown below."))
        t_lbl = wx.StaticText(self, label=_("Error Traceback:"))
        tctrl = wx.TextCtrl(self, value=self.err_msg, style=wx.TE_MULTILINE | 
                                                            wx.TE_READONLY)
        abort_b = wx.Button(self, wx.ID_ABORT, _("Abort"))
        send_b = wx.Button(self, ID_SEND, _("Report Error"))
        send_b.SetDefault()
        close_b = wx.Button(self, wx.ID_CLOSE)

        # Layout
        sizer = wx.GridBagSizer()
        sizer.AddMany([(icon, (1, 1)), (mainmsg, (1, 2), (1, 2)), 
                       ((2, 2), (3, 0)), (t_lbl, (3, 1), (1, 2)),
                       (tctrl, (4, 1), (8, 5), wx.EXPAND), ((5, 5), (4, 6)),
                       ((2, 2), (12, 0)),
                       (abort_b, (13, 1), (1, 1), wx.ALIGN_LEFT),
                       (send_b, (13, 3), (1, 2), wx.ALIGN_RIGHT),
                       (close_b, (13, 5), (1, 1), wx.ALIGN_RIGHT),
                       ((2, 2), (14, 0))])
        self.SetSizer(sizer)
        self.SetInitialSize()

    def OnButton(self, evt):
        """Handles button events
        @param evt: event that called this handler
        @postcondition: Dialog is closed
        @postcondition: If Report Event then email program is opened

        """
        e_id = evt.GetId()
        if e_id == wx.ID_CLOSE:
            self.Close()
        elif e_id == ID_SEND:
            msg = u"mailto:%s?subject=Error Report&body=%s"
            addr = u"bugs@%s" % (ed_glob.HOME_PAGE.replace("http://", '', 1))
            msg = msg % (addr, self.err_msg)
            msg = msg.replace(u"'", u'')
            webbrowser.open(msg)
            self.Close()
        elif e_id == wx.ID_ABORT:
            global ABORT
            ABORT = True
            # Try a nice shutdown first time through
            wx.CallLater(500, wx.GetApp().OnExit, 
                         wx.MenuEvent(wx.wxEVT_MENU_OPEN, ed_glob.ID_EXIT),
                         True)
            self.Close()
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Cleans up the dialog when it is closed
        @param evt: Event that called this handler

        """
        REPORTER_ACTIVE = False
        self.Destroy()
        evt.Skip()
