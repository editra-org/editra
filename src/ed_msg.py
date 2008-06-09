###############################################################################
# Name: ed_msg.py                                                             #
# Purpose: Provide a messaging/notification system for actions performed in   #
#          the editor.                                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This module provides a light wrapping of a slightly modified pubsub module
to give it a lighter and simpler syntax for usage. It exports three main
methods. The first L{PostMessage} which is used to post a message for all
interested listeners. The second L{Subscribe} which allows an object to
subscribe its own listener function for a particular message type, all of
Editra's core message types are defined in this module using a naming
convention that starts each identifier with I{EDMSG_}. These identifier
constants can be used to identify the message type by comparing them with the
value of msg.GetType in a listener method. The third method is L{Unsubscribe}
which can be used to remove a listener from recieving messages.

@summary: Message system api and message type definitions

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['PostMessage', 'Subscribe', 'Unsubscribe']

#--------------------------------------------------------------------------#
# Dependancies
from wx import PyDeadObjectError
from extern.pubsub import Publisher

#--------------------------------------------------------------------------#
# Message Type Definitions

#---- General Messages ----#

# Listen to all messages
EDMSG_ALL = ('editra',)

#---- End General Messages ----#

#---- Log Messages ----#
# Used internally by the log system. Listed by priority lowest -> highest
# All message data from these functions are a LogMsg object which is a
# container object for the message string / timestamp / type
#
# Using these message types with the PostMessage method is not suggested for
# use in user code instead use the logging facilities (wx.GetApp().GetLog() or
# util.Getlog() ) as they will handle the formatting that is expected by the 
# log messaging listeners.

# Recieve all log messages (i.e anything put on the logging system)
EDMSG_LOG_ALL = EDMSG_ALL + ('log',)

# Recieve all messages that have been labled (info, events, warnings, errors)
EDMSG_LOG_INFO = EDMSG_LOG_ALL + ('info',)

# Messages generated by ui events
EDMSG_LOG_EVENT = EDMSG_LOG_INFO + ('evt',)

# Recieve only warning messages
EDMSG_LOG_WARN = EDMSG_LOG_INFO + ('warn',)

# Recieve only error messages
EDMSG_LOG_ERROR = EDMSG_LOG_INFO + ('err',)

#---- End Log Messages ----#

#---- File Action Messages ----#

# Recieve notification of all file actions
EDMSG_FILE_ALL = EDMSG_ALL + ('file',)

# File open was just requested / msgdata == file path
EDMSG_FILE_OPENING = EDMSG_FILE_ALL + ('opening',)

# File was just opened / msgdata == file path
EDMSG_FILE_OPENED = EDMSG_FILE_ALL + ('opened',)

# File save requested / msgdata == (filename, filetypeId)
# Note: All listeners of this message are processed *before* the save takes
#       place. Meaning the listeners block the save action until they are
#       finished.
EDMSG_FILE_SAVE = EDMSG_FILE_ALL + ('save',)

# File just written to disk / msgdata == (filename, filetypeId)
EDMSG_FILE_SAVED = EDMSG_FILE_ALL + ('saved',)

#---- End File Action Messages ----#

#---- UI Action Messages ----#

# Recieve notification of all ui typed messages
EDMSG_UI_ALL = EDMSG_ALL + ('ui',)

#- Recieve all Main Notebook Messages
EDMSG_UI_NB = EDMSG_UI_ALL + ('mnotebook',)

# Notebook page changing
# msgdata == (ref to notebook, 
#             index of previous selection,
#             index of current selection)
EDMSG_UI_NB_CHANGING = EDMSG_UI_NB + ('pgchanging',)

# Notebook page changed
# msgdata == (ref to notebook, index of currently selected page)
EDMSG_UI_NB_CHANGED = EDMSG_UI_NB + ('pgchanged',)

# Page is about to close
# msgdata == (ref to notebook, index of page that is closing)
EDMSG_UI_NB_CLOSING = EDMSG_UI_NB + ('pgclosing',)

# Page has just been closed
# msgdata == (ref to notebook, index of page that is now selected)
EDMSG_UI_NB_CLOSED = EDMSG_UI_NB + ('pgclosed',)

# Post message to show the progress indicator of the MainWindow
# msgdata == (frame id, True / False)
EDMSG_PROGRESS_SHOW = EDMSG_UI_ALL + ('progbar', 'show')

# Post this message to manipulate the state of the MainWindows status bar
# progress indicator. The message data should be a three tuple of the recipient
# frames id, current progress and the total range (current, total). If both 
# values are 0 then the bar will be hidden. If both are negative the bar will 
# be set into pulse mode. This message can safely be sent from background 
# threads.
EDMSG_PROGRESS_STATE = EDMSG_UI_ALL + ('progbar', 'state')

## Text Buffer
# msgdata == ((x, y), keycode)
EDMSG_UI_STC_KEYUP = EDMSG_UI_ALL + ('stc', 'keyup')

# Lexer Changed
# msgdata == None
EDMSG_UI_STC_LEXER = EDMSG_UI_ALL + ('stc', 'lexer')

#---- End UI Action Messages ----#

#---- Menu Messages ----#
EDMSG_MENU = EDMSG_ALL + ('menu',)

# Signal to all windows to update keybindings (msgdata == None)
EDMSG_MENU_REBIND = EDMSG_MENU + ('rebind',)

# Message to set key profile
# msgdata == keyprofile name
EDMSG_MENU_LOADPROFILE = EDMSG_MENU + ('load',)

#---- End Menu Messages ----#

#---- Misc Messages ----#
# Signal that the icon theme has changed. Respond to this to update icon
# resources from the ArtProvider.
EDMSG_THEME_CHANGED = EDMSG_ALL + ('theme',)

# Signal that the font preferences for the ui have changed (msgdata == font)
EDMSG_DSP_FONT = EDMSG_ALL + ('dfont',)

#--------------------------------------------------------------------------#
# Public Api

def PostMessage(msgtype, msgdata=None):
    """Post a message containing the msgdata to all listeners that are
    interested in the given msgtype.
    @param msgtype: Message Type EDMSG_*
    @keyword msgdata: Message data to pass to listener (can be anything)

    """
    Publisher().sendMessage(msgtype, msgdata)

def Subscribe(callback, msgtype=EDMSG_ALL):
    """Subscribe your listener function to listen for an action of type msgtype.
    The callback must be a function or a _bound_ method that accepts one
    parameter for the actions message. The message that is sent to the callback
    is a class object that has two attributes, one for the message type and the
    other for the message data. See below example for how these two values can
    be accessed.
      >>> def MyCallback(msg):
              print "Msg Type: ", msg.GetType(), "Msg Data: ", msg.GetData()

      >>> class Foo:
              def MyCallbackMeth(self, msg):
                  print "Msg Type: ", msg.GetType(), "Msg Data: ", msg.GetData()

      >>> Subscribe(MyCallback, EDMSG_SOMETHING)
      >>> myfoo = Foo()
      >>> Subscribe(myfoo.MyCallBackMeth, EDMSG_SOMETHING)

    @param callback: Callable function or bound method
    @keyword msgtype: Message to subscribe to (default to all)

    """
    Publisher().subscribe(callback, msgtype)

def Unsubscribe(callback, messages=None):
    """Remove a listener so that it doesn't get sent messages for msgtype. If
    msgtype is not specified the listener will be removed for all msgtypes that
    it is associated with.
    @param callback: Function or bound method to remove subscription for
    @keyword messages: EDMSG_* val or list of EDMSG_* vals

    """
    Publisher().unsubscribe(callback, messages)

#-----------------------------------------------------------------------------#

class NullValue:
    """Null value to signify that a callback method should be skipped or that
    no callback could answer the request.

    """
    def __int__(self):
        return 0

    def __nonzero__(self):
        return False

def RegisterCallback(callback, msgtype):
    """Register a callback method for the given message type
    @param callback: callable
    @param msgtype: message type

    """
    if isinstance(msgtype, tuple):
        mtype = '.'.join(msgtype)
    else:
        mtype = msgtype

    if not _CALLBACK_REGISTRY.has_key(mtype):
        _CALLBACK_REGISTRY[mtype] = list()

    if callback not in _CALLBACK_REGISTRY[mtype]:
        _CALLBACK_REGISTRY[mtype].append(callback)

def RequestResult(msgtype, args=list()):
    """Request a return value result from a registered function/method.
    If multiple callbacks have been registered for the given msgtype, the
    first callback to return a non-NullValue will be used for the return
    value. If L{NullValue} is returned then no callback could answer the
    call.
    @param msgtype: Request message
    @keyword args: Arguments to pass to the callback

    """
    if isinstance(msgtype, tuple):
        mtype = '.'.join(msgtype)
    else:
        mtype = msgtype

    to_remove = list()
    rval = NullValue()
    for idx, meth in enumerate(_CALLBACK_REGISTRY.get(mtype, list())):
        try:
            if len(args):
                rval = meth(args)
            else:
                rval = meth()
        except PyDeadObjectError:
            to_remove.append(meth)

        if not isinstance(rval, NullValue):
            break

    # Remove any dead objects that may have been found
    for val in reversed(to_remove):
        try:
            _CALLBACK_REGISTRY.get(mtype, list()).pop(val)
        except:
            pass

    return rval

def UnRegisterCallback(callback):
    """Un-Register a callback method
    @param callback: callable

    """
    for key, val in _CALLBACK_REGISTRY.iteritems():
        if callback in val:
            _CALLBACK_REGISTRY[key].remove(callback)

# Callback Registry for storing the methods sent in with RegisterCallback
_CALLBACK_REGISTRY = {}

#-----------------------------------------------------------------------------#
