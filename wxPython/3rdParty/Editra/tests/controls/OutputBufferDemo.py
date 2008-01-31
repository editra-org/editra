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
#-----------------------------------------------------------------------------#

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent)

        # Attributes
        self._proc = list()
        self._buff = CustomOutputBuffer(self)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)

    def __DoLayout(self):
        """Layout the panel"""

        # Control Section Layout
        default = ["ping %s" % x for x in ['localhost', 'editra.org', 'google.com']]
        combo = wx.ComboBox(self, ID_COMMAND, value='ping localhost', choices=default)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5),), (wx.StaticText(self, label="Cmd: "), 0,
                                    wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT),
                        (combo, 1, wx.EXPAND), ((20, 20),),
                        (wx.Button(self, ID_STOP, "Stop"), 0,
                         wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL), ((5, 5),),
                        (wx.Button(self, ID_START, "Start"), 0,
                         wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL), ((5, 5),)])

        # Main Sizer Layout
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([(self._buff, 1, wx.EXPAND), (hsizer, 0, wx.EXPAND)])
        self.SetSizer(msizer)

    def OnButton(self, evt):
        """Start/Stop ProcessThread(s)"""
        e_id = evt.GetId()
        if e_id == ID_STOP:
            for proc in self._proc:
                proc.Abort()
            self._buff.Stop()
        elif e_id == ID_START:
            # Spawn a new ProcessThread
            combo = self.FindWindowById(ID_COMMAND)
            cmd = '%s' % combo.GetValue()
            self._proc.append(outbuff.ProcessThread(self._buff, cmd))
            self._proc[-1].start()
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#
STARTED_STR = 'ProcessThread Started'
FINISHED_STR = 'ProcessThread Finished'

class CustomOutputBuffer(outbuff.OutputBuffer, outbuff.ProcessBufferMixin):
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)
        outbuff.ProcessBufferMixin.__init__(self)

    def ApplyStyles(self, ind, txt):
        """Highlight some random words in the output to 
        Tests overriding of the ApplyStyles method from L{OutputBuffer}
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
        This method is called directly before a process thread is started.
        @keyword cmd: Command string used to start the process

        """
        self.AppendUpdate("%s: %s%s" % (STARTED_STR, cmd, os.linesep))

    def DoProcessExit(self, code=0):
        """Do all that is needed to be done after a process has exited
        This method is called when the process has exited
        @keyword code: Exit code of the process

        """
        self.AppendUpdate("%s: %d%s" % (FINISHED_STR, code, os.linesep))

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
        import sys
        import run
    except ImportError:
        app = wx.PySimpleApp(False)
        frame = wx.Frame(None, title="OutputBuffer Test")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.CreateStatusBar()
        frame.SetSizer(sizer)
        frame.SetInitialSize()
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
