###############################################################################
# Name: OutputBufferDemo.py                                                   #
# Purpose: OutputBuffer Test and Demo File                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Test file for testing the OutputBuffer (eclib.outbuff) module and controls


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import wx

sys.path.insert(0, os.path.abspath('../../'))
import src.eclib.outbuff as outbuff

#-----------------------------------------------------------------------------#
# Globals

ID_COMMAND = wx.NewId()
ID_START = wx.NewId()
ID_STOP = wx.NewId()
ID_PROC_LIST = wx.NewId()
ID_THREAD_STATUS = wx.NewId()
#-----------------------------------------------------------------------------#

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent)

        # Attributes
        self.ssizer = wx.BoxSizer(wx.HORIZONTAL)
        self._buff = ProcessOutputBuffer(self)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def __DoLayout(self):
        """Layout the panel"""

        # Status Display Layout (Top Section)
        self.ssizer.AddMany([((5, 5),),
                             (wx.StaticText(self, label="Running:"),
                              0, wx.ALIGN_CENTER_VERTICAL),
                             (wx.Choice(self, ID_PROC_LIST), 0),
                             ((-1, 5), 1, wx.EXPAND),
                             (wx.StaticText(self, ID_THREAD_STATUS, "Threads: 0"),
                              0, wx.ALIGN_CENTER_VERTICAL),
                             ((5, 5),)])

        default = ["ping localhost", "ping editra.org", "ping wxpython.org"]
        combo = wx.ComboBox(self, ID_COMMAND, value='ping localhost', choices=default)
        combo.SetToolTipString("Enter a command to run here")
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        stopb = wx.Button(self, ID_STOP, "Stop")
        stopb.SetToolTipString("Stop all running processes")
        startb = wx.Button(self, ID_START, "Start")
        startb.SetToolTipString("Run the command in the combo box")
        hsizer.AddMany([((5, 5),), (wx.StaticText(self, label="Cmd: "), 0,
                                    wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT),
                        (combo, 1, wx.EXPAND), ((20, 20),),
                        (stopb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5),),
                        (startb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5),)])

        # Main Sizer Layout
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([((3, 3),),
                        (self.ssizer, 0, wx.EXPAND),
                        (self._buff, 1, wx.EXPAND),
                        (hsizer, 0, wx.EXPAND)])
        self.SetSizer(msizer)

    def OnButton(self, evt):
        """Start/Stop ProcessThread(s)"""
        e_id = evt.GetId()
        if e_id == ID_STOP:
            self._buff.Abort()
            self.UpdateProcs()
        elif e_id == ID_START:
            # Spawn a new ProcessThread
            combo = self.FindWindowById(ID_COMMAND)
            cmd = '%s' % combo.GetValue()
            self._buff.StartProcess(cmd)
            self.UpdateProcs()
        else:
            evt.Skip()

    def UpdateProcs(self):
        """Update the controls to show the current processes/threads"""
        procs = self.FindWindowById(ID_PROC_LIST)
        status = self.FindWindowById(ID_THREAD_STATUS)

        running = self._buff.GetProcesses()
        procs.SetItems(running)
        if len(running):
            procs.SetStringSelection(running[-1])
        status.SetLabel("Threads: %d" % len(running))
        self.ssizer.Layout()

#-----------------------------------------------------------------------------#
STARTED_STR = 'ProcessThread Started'
FINISHED_STR = 'ProcessThread Finished'

class ProcessOutputBuffer(outbuff.OutputBuffer, outbuff.ProcessBufferMixin):
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)
        outbuff.ProcessBufferMixin.__init__(self)

        # Attributes
        self._threads = list()

    def Abort(self):
        """Kill off all running threads and procesess"""
        for proc in self._threads:
            proc[0].Abort()

    def ApplyStyles(self, ind, txt):
        """Highlight the begining and process exit text in the buffer
        Tests overriding of the ApplyStyles method from L{outbuff.OutputBuffer}
        This is called every time text is added to the output buffer.
        @param ind: Index of text insertion point in buffer
        @param txt: the text that was just inserted at ind

        """
        start = txt.find(STARTED_STR)
        end = txt.find(FINISHED_STR)
        if start >= 0:
            sty_s = ind + start
            slen = len(STARTED_STR)
            style = outbuff.OPB_STYLE_INFO
        elif end >= 0:
            sty_s = ind + end
            slen = len(FINISHED_STR)
            style = outbuff.OPB_STYLE_ERROR
        else:
            return

        # Do the styling if one of the patterns was found
        self.StartStyling(sty_s, 0xff)
        self.SetStyling(slen, style)

    def DoProcessStart(self, cmd=''):
        """Do any necessary preprocessing before a process is started.
        This method is called directly before the process in the
        L{outbuff.ProcessThread} is started. This method is an overridden 
        method of the L{outbuff.ProcessBufferMixin} super class.
        @keyword cmd: Command string used to start the process

        """
        self.AppendUpdate("%s: %s%s" % (STARTED_STR, cmd, os.linesep))

    def DoProcessExit(self, code=0):
        """Do all that is needed to be done after a process has exited
        This method is called when a L{outbuff.ProcessThread} has exited and
        is an overridden method from the L{outbuff.ProcessBufferMixin} super
        class.
        @keyword code: Exit code of the process

        """
        self.AppendUpdate("%s: %d%s" % (FINISHED_STR, code, os.linesep))
        dead = list()

        # Remove all Dead Threads
        for idx, proc in enumerate(self._threads):
            if not proc[0].isAlive():
                dead.append(idx)

        for zombie in reversed(dead):
            del self._threads[zombie]

        self.GetParent().UpdateProcs()

        # If there are no more running threads stop the buffers timer
        if not len(self._threads):
            self.Stop()

    def GetActiveCount(self):
        """Get the count of active threaded processes that are running
        @return: int

        """
        return len(self._threads)

    def GetProcesses(self):
        """Return the list of running process commands
        @return: list of strings

        """
        return [ proc[1] for proc in self._threads ]

    def StartProcess(self, cmd):
        """Start a new process thread, the process will be created by
        executing the given command.
        @param cmd: Command string (i.e 'ping localhost')

        """
        proc = outbuff.ProcessThread(self, cmd)
        self._threads.append((proc, cmd))
        self._threads[-1][0].start()
        
#-----------------------------------------------------------------------------#

def runTest(frame, nb, log):
    return TestPanel(nb, log)

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#----------------------------------------------------------------------

overview = outbuff.__doc__

#-----------------------------------------------------------------------------#
# Run the Test
if __name__ == '__main__':
    try:
        import run
    except ImportError:
        app = wx.PySimpleApp(False)
        frame = wx.Frame(None, title="OutputBuffer Test 'Ping-O-Matic'")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.CreateStatusBar()
        frame.SetSizer(sizer)
        frame.SetInitialSize()
        frame.SetStatusText("OutputBuffer test")
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
