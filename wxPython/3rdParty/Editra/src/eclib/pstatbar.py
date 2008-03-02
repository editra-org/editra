###############################################################################
# Name: pstatbar.py                                                           #
# Purpose: Custom statusbar with builtin progress indicator                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: Progress StatusBar

Custom StatusBar that has a builtin progress gauge to indicate busy status and
progress of long running tasks in a window. The progress bar is only shown when
it is active and shown in the far rightmost field of the StatusBar. The size of
the progress Guage is also determined by the size of the right most field. When
created the StatusBar will create two fields by default, to change this behavior
simply call SetFields after creating the bar to change it.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx

#--------------------------------------------------------------------------#
# Globals

#--------------------------------------------------------------------------#
class ProgressStatusBar(wx.StatusBar):
    """Custom StatusBar with a builtin progress bar"""
    def __init__(self, parent, id_=wx.ID_ANY,
                 style=wx.DEFAULT_STATUSBAR_STYLE,
                 name="ProgressStatusBar"):
        """Creates a status bar that can hide and show a progressbar
        in the far right section. The size of the progressbar is also
        determined by the size of the right most section.
        @param parent: Frame this status bar belongs to

        """
        wx.StatusBar.__init__(self, parent, id_, style, name)
  
        # Attributes
        self._changed = False   # position has changed ?
        self.busy = False       # Bar in busy mode ?
        self.progress = 0       # Current progress value of the bar
        self.timer = wx.Timer(self)
        self.prog = wx.Gauge(self, style=wx.GA_HORIZONTAL)
        self.prog.Hide()

        # Layout
        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 155])

        # Event Handlers
        self.Bind(wx.EVT_IDLE, lambda evt: self.__Reposition())
        self.Bind(wx.EVT_TIMER, lambda evt: self.prog.Pulse())
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def __del__(self):
        """Make sure the timer is stopped
        @postcondition: timer is cleaned up

        """
        if self.timer.IsRunning():
            self.timer.Stop()

    def __Reposition(self):
        """Does the actual repositioning of progress bar
        @postcondition: Progress bar is repostioned to right side

        """
        if self._changed:
            rect = self.GetFieldRect(self.GetFieldsCount() - 1)
            self.prog.SetPosition((rect.x + 2, rect.y + 2))
            self.prog.SetSize((rect.width - 8, rect.height - 4))
        self._changed = False

    #---- Public Methods ----#

    def Destroy(self):
        """Cleanup timer
        @postcondition: timer is cleaned up and status bar is destroyed

        """
        if self.timer.IsRunning():
            self.timer.Stop()
        del self.timer
        wx.StatusBar.Destroy(self)

    def GetProgress(self):
        """Get the progress of the progress bar
        @return: int

        """
        return self.prog.GetValue()

    def GetRange(self):
        """Get the what the range of the progress bar is
        @return: int

        """
        return self.prog.GetRange()

    def OnSize(self, evt):
        """Reposition progress bar on resize
        @param evt: wx.EVT_SIZE

        """
        self.__Reposition()
        self._changed = True
        evt.Skip()

    def OnTimer(self, evt):
        """Update the progress bar while the timer is running
        @param evt: wx.EVT_TIMER

        """
        if self.busy or self.progress < 0:
            self.prog.Pulse()
        else:
            self.SetProgress(self.progress)

    def Run(self, rate=100):
        """Start the bar's timer to check for updates to progress
        @keyword rate: rate at which to check for updates

        """
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def SetProgress(self, val):
        """Set the controls internal progress value that is reflected in the
        progress bar when the timer next updates. Be sure to call Start before
        calling this method if you want the changes to be visible. This method
        can be called from non gui threads.
        @param val: int

        """
        self.progress = val

    def SetRange(self, val):
        """Set the what the range of the progress bar is
        @param val: int

        """
        self.prog.SetRange(val)

    def ShowProgress(self, show=True):
        """Manually show or hide the progress bar
        @keyword show: bool

        """
        # If showing make sure bar is positioned properly
        if show:
            self.__Reposition()
        self.prog.Show(show)

    def StartBusy(self, rate=100):
        """Show and start the progress indicator in pulse mode
        @keyword rate: interval to pulse indicator at in msec

        """
        self.busy = True
        self.ShowProgress(True)
        self.Run(rate)

    def Stop(self):
        """Stop and hide the progress bar"""
        self.timer.Stop()
        self.ShowProgress(False)
        self.prog.SetValue(0)   # Rest progress value
        self.progress = 0

    def StopBusy(self):
        """Stop and hide the progress indicator
        @postcondition: Progress bar is hidden from view

        """
        self.busy = False
        self.Stop()
