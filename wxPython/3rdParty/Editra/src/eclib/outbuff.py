###############################################################################
# Name: outbuff.py                                                            #
# Purpose: Gui and helper classes for running processes and displaying output #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: OutputBuffer

This module contains classes that are usefull for displaying output from running
tasks and processes. The classes are divided into three main catagories, gui
classes, mixins, and thread classes. All the classes can be used together to
easily create multithreaded gui display classes without neededing to worry about
the details and thread saftey of the gui.

For example usage of these classes see ed_log and the Editra's Launch plugin

Class OutputBuffer:
  This is the main class exported by ths module. It provides a readonly output
display buffer that when used with the other classes in this module provides an
easy way to display continous output from other processes and threads. It 
provides two methods for subclasses to override if they wish to perform custom 
handling.

  * Override the ApplyStyles method to do any processing and coloring of the
    text as it is put in the buffer.
  * Override the DoUpdatesEmpty method to perform any idle processing when no
    new text is waiting to be processed.

Class ProcessBufferMixin:
  Mixin class for the L{OutputBuffer} class that provides handling for when an
OutputBuffer is used with a L{ProcessThread}. It provides three methods that can
be overridden in subclasses to perform extra processing.

  * DoProcessStart: Called as the process is being started in the ProcessThread,
                    it recieves the process command string as an argument.
  * DoFilterInput: Called as each chunk of output comes from the running process
                   use it to filter the results before displaying them in the
                   buffer.
  * DoProcessExit: Called when the running process has exited. It recieves the
                   processes exit code as a parameter.

Class ProcessThread:
  Thread class for running subprocesses and posting the output to an 
L{OutputBuffer} via events.
       
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import signal
import subprocess
import threading
import wx
import wx.stc

# Needed for killing processes on windows
if sys.platform.startswith('win'):
    import ctypes

#--------------------------------------------------------------------------#
# Globals
OUTPUTBUFF_NAME_STR = u'EditraOutputBuffer'
THREADEDBUFF_NAME_STR = u'EditraThreadedBuffer'

# Style Codes
OPB_STYLE_DEFAULT = 0
OPB_STYLE_INFO    = 1
OPB_STYLE_WARN    = 2
OPB_STYLE_ERROR   = 3

#--------------------------------------------------------------------------#

# Event for notifying that the proces has started running
# GetValue will return the command line string that started the process
edEVT_PROCESS_START = wx.NewEventType()
EVT_PROCESS_START = wx.PyEventBinder(edEVT_PROCESS_START, 1)

# Event for passing output data to buffer
# GetValue returns the output text retrieved from the process
edEVT_UPDATE_TEXT = wx.NewEventType()
EVT_UPDATE_TEXT = wx.PyEventBinder(edEVT_UPDATE_TEXT, 1)

# Event for notifying that the the process has finished and no more update
# events will be sent. GetValue will return the processes exit code
edEVT_PROCESS_EXIT = wx.NewEventType()
EVT_PROCESS_EXIT = wx.PyEventBinder(edEVT_PROCESS_EXIT, 1)

class OutputBufferEvent(wx.PyCommandEvent):
    """Event for data transfer and signaling actions in the L{OutputBuffer}"""
    def __init__(self, etype, eid, value=''):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value

#--------------------------------------------------------------------------#

class OutputBuffer(wx.stc.StyledTextCtrl):
    """Output buffer to display results. The ouputbuffer is a readonly
    buffer meant for displaying results from running processes or batch
    jobs

    """
    def __init__(self, parent, id=wx.ID_ANY, 
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_SUNKEN,
                 name=OUTPUTBUFF_NAME_STR):
        wx.stc.StyledTextCtrl.__init__(self, parent, id, pos, size, style, name)

        # Attributes
        self._mutex = threading.Lock()
        self._updating = threading.Condition(self._mutex)
        self._updates = list()
        self._timer = wx.Timer(self)

        # Setup
        self.__ConfigureSTC()

        # Event Handlers
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    def __del__(self):
        """Ensure timer is cleaned up when we are deleted"""
        if self._timer.IsRunning():
            self._timer.Stop()

    def __ConfigureSTC(self):
        """Setup the stc to behave/appear as we want it to 
        and define all styles used for giving the output context.

        """
        self.SetMargins(3, 3)
        self.SetMarginWidth(0, 0)
        self.SetMarginWidth(1, 0)

        self.SetLayoutCache(wx.stc.STC_CACHE_DOCUMENT)
        self.SetReadOnly(True)
        
        #self.SetEndAtLastLine(False)
        self.SetVisiblePolicy(1, wx.stc.STC_VISIBLE_STRICT)

        # Define Styles
        font = wx.Font(11, wx.FONTFAMILY_MODERN, 
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        style = (font.GetFaceName(), font.GetPointSize(), "#FFFFFF")
        
        # Custom Styles
        self.StyleSetSpec(OPB_STYLE_DEFAULT, 
                          "face:%s,size:%d,fore:#000000,back:%s" % style)
        self.StyleSetSpec(OPB_STYLE_INFO,
                          "face:%s,size:%d,fore:#0000FF,back:%s" % style)
        self.StyleSetSpec(OPB_STYLE_WARN,
                          "face:%s,size:%d,fore:#0000FF,back:%s" % style)
        self.StyleSetSpec(OPB_STYLE_ERROR, 
                          "face:%s,size:%d,fore:#FF0000,back:%s" % style)
        self.StyleSetHotSpot(OPB_STYLE_ERROR, True)

        # Default Styles
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, \
                          "face:%s,size:%d,fore:#000000,back:%s" % style)
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, \
                          "face:%s,size:%d,fore:#000000,back:%s" % style)
        self.Colourise(0, -1)

    def __PutText(self, txt, ind):
        """
        @param txt: String to append
        @param ind: index in update buffer

        """
        self._updating.acquire()
        self.SetReadOnly(False)
        start = self.GetLength()
        self.AppendText(txt)
        self.GotoPos(self.GetLength())
        self._updates = self._updates[ind:]
        self.ApplyStyles(start, txt)
        self.SetReadOnly(True)
        self._updating.release()

    #---- Public Member Functions ----#
    def AppendUpdate(self, value):
        """Buffer output before adding to window
        @param value: update string to append to stack

        """
        self._updating.acquire()
        self._updates.append(value.decode(sys.getfilesystemencoding()))
        self._updating.release()

    def ApplyStyles(self, start, txt):
        """Apply coloring to text starting at start position.
        Override this function to do perform any styling that you want
        done on the text.
        @param start: Start position of text that needs styling in the buffer
        @param txt: The string of text that starts at the start position in the
                    buffer.

        """
        pass

    def Clear(self):
        """Clear the Buffer"""
        self.SetReadOnly(False)
        self.SetText('')
        self.SetReadOnly(False)

    def DoUpdatesEmpty(self):
        """Called when update stack is empty
        Override this function to perform actions when there are no updates
        to process. It can be used for things such as temporarly stopping
        the timer or performing idle processing.

        """
        pass

    def IsRunning(self):
        """Return whether the buffer is running and ready for output
        @return: bool

        """
        return self._timer.IsRunning()        

    def OnTimer(self, evt):
        """Process and display text from the update buffer
        @note: this gets called many times while running thus needs to
               return quickly to avoid blocking the ui.

        """
        ind = len(self._updates)
        if ind:
            wx.CallAfter(self.__PutText, u''.join(self._updates), ind)
        elif evt is not None:
            self.DoUpdatesEmpty()
        else:
            pass

    def SetText(self, text):
        """Set the text that is shown in the buffer
        @param text: text string to set as buffers current value

        """
        self.SetReadOnly(False)
        wx.stc.StyledTextCtrl.SetText(self, text)
        self.SetReadOnly(True)

    def Start(self, interval):
        """Start the window's timer to check for updates
        @param interval: interval in milliseconds to do updates

        """
        self._timer.Start(interval)

    def Stop(self):
        """Stop the update process of the buffer"""
        # Dump any output still left in tmp buffer before stopping
        self.OnTimer(None)
        self._timer.Stop()
        self.SetReadOnly(True)

#-----------------------------------------------------------------------------#

class ProcessBufferMixin:
    """Mixin class for L{OutputBuffer} to handle events
    generated by a L{ProcessThread}.

    """
    def __init__(self, update=100):
        """Initialize the mixin
        @keyword update: The update interval speed in msec

        """
        # Attributes
        self._rate = update

        # Event Handlers
        self.Bind(EVT_PROCESS_START, self._OnProcessStart)
        self.Bind(EVT_UPDATE_TEXT, self._OnProcessUpdate)
        self.Bind(EVT_PROCESS_EXIT, self._OnProcessExit)

    def _OnProcessExit(self, evt):
        """Handles EVT_PROCESS_EXIT"""
        self.DoProcessExit(evt.GetValue())

    def _OnProcessStart(self, evt):
        """Handles EVT_PROCESS_START"""
        self.DoProcessStart(evt.GetValue())
        self.Start(self._rate)

    def _OnProcessUpdate(self, evt):
        """Handles EVT_UPDATE_TEXT"""
        txt = self.DoFilterInput(evt.GetValue())
        self.AppendUpdate(txt)

    def DoFilterInput(self, txt):
        """Override this method to do an filtering on input that is sent to
        the buffer from the process text. The return text is what is put in
        the buffer.
        @param txt: incoming udpate text
        @return: string

        """
        return txt

    def DoProcessExit(self, code=0):
        """Override this method to do any post processing after the running
        task has exited. Typically this is a good place to call L{Stop} to
        stop the buffers timer.
        @keyword code: Exit code of program

        """
        self.Stop()

    def DoProcessStart(self, cmd=''):
        """Override this method to do any pre processing before starting
        a processes output.
        @keyword cmd: Command used to start program

        """
        pass

    def SetUpdateInterval(self, value):
        """Set the rate at which the buffer outputs update messages
        @param value: rate in milliseconds to do updates on

        """
        self._rate = value

#-----------------------------------------------------------------------------#

class ProcessThread(threading.Thread):
    """Run a subprocess in a separate thread. Thread posts events back
    to parent object on main thread for processing in the ui.
    @see: EVT_PROCESS_START, EVT_PROCESS_END, EVT_UPDATE_TEXT

    """
    def __init__(self, parent, command, fname='',
                 args=list(), cwd=None, env=None):
        """Initialize the ProcessThread object
        @param parent: Parent Window/EventHandler to recieve the events
                       generated by the process.
        @param command: Command string to execute as a subprocess.
        @keyword fname: Filename or path to file to run command on.
        @keyword args: Argument list or string to pass to use with fname arg.
        @keyword cwd: Directory to execute process from or None to use current
        @keyword env: Environment to run the process in (dictionary) or None to
                      use default.
        @example:
            myproc = ProcessThread(myframe, '/usr/local/bin/python', 'hello.py',
                                   '--version', '/Users/me/home/')
            myproc.start()

        """
        threading.Thread.__init__(self)

        if isinstance(args, list):
            args = u' '.join([arg.strip() for arg in args])

        # Attributes
        self.abort = False          # Abort Process
        self._parent = parent       # Parent Window/Event Handler
        self._cwd = cwd             # Path at which to run from
        self._cmd = dict(cmd=command, file=fname, args=args)
        self._env = env

    def __DoOneRead(self, proc):
        """Read one line of output and post results.
        @param proc: process to read from
        @return: bool (True if more), (False if not)

        """
        try:
            result = proc.stdout.readline()
        except (IOError, OSError):
            return False

        if result == "" or result == None:
            return False

        # Ignore encoding errors and return an empty line instead
        try:
            result = result.decode(sys.getfilesystemencoding())
        except UnicodeDecodeError:
            result = os.linesep

        evt = OutputBufferEvent(edEVT_UPDATE_TEXT, self._parent.GetId(), result)
        wx.CallAfter(wx.PostEvent, self._parent, evt)
        return True

    def __KillPid(self, pid):
        """Kill a process by process id, causing the run loop to exit
        @param pid: Id of process to kill

        """
        # Dont kill if the process if it is the same one we
        # are running under (i.e we are running a shell command)
        if pid == os.getpid():
            return

        if wx.Platform != '__WXMSW__':
            # Try to be 'nice' the first time if that fails be more forcefull
            try:
                os.kill(pid, signal.SIGABRT)
            except OSError:
                os.kill(pid, signal.SIGKILL)

            os.waitpid(pid, os.WNOHANG)
        else:
            # 1 == Terminate
            handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)

    #---- Public Member Functions ----#
    def Abort(self):
        """Abort the running process and return control to the main thread"""
        self.abort = True

    def run(self):
        """Run the process until finished or aborted. Don't call this
        directly instead call self.start() to start the thread else this will
        run in the context of the current thread.
        @note: overridden from Thread

        """
        command = u' '.join([item.strip() for item in [self._cmd['cmd'],
                                                       self._cmd['file'],
                                                       self._cmd['args']]])
        
        proc = subprocess.Popen(command.strip(), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True,
                                cwd=self._cwd, env=self._env)

        evt = OutputBufferEvent(edEVT_PROCESS_START,
                                self._parent.GetId(),
                                command.strip())
        wx.CallAfter(wx.PostEvent, self._parent, evt)

        # Read from stdout while there is output from process
        while True:
            if self.abort:
                self.__KillPid(proc.pid)
                self.__DoOneRead(proc)
                break
            else:
                more = False
                try:
                    more = self.__DoOneRead(proc)
                except wx.PyDeadObjectError:
                    # Our parent window is dead so kill process and return
                    self.__KillPid(proc.pid)
                    return

                if not more:
                    break

        try:
            result = proc.wait()
        except OSError:
            result = -1

        # Notify that proccess has exited
        # Pack the exit code as the events value
        evt = OutputBufferEvent(edEVT_PROCESS_EXIT, self._parent.GetId(), result)
        wx.CallAfter(wx.PostEvent, self._parent, evt)

    def SetArgs(self, args):
        """Set the args to pass to the command
        @param args: list or string of program arguments

        """
        if isinstance(args, list):
            u' '.join(item.strip() for item in args)
        self._cmd['args'] = args.strip()

    def SetCommand(self, cmd):
        """Set the command to execute
        @param cmd: Command string

        """
        self._cmd['cmd'] = cmd

    def SetFilename(self, fname):
        """Set the command to execute
        @param cmd: Command string

        """
        self._cmd['file'] = fname
