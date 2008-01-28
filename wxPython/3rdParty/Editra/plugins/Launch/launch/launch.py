# -*- coding: utf-8 -*-
###############################################################################
# Name: launch.py                                                             #
# Purpose: Launch Ui                                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Launch User Interface"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.stc

# Local Imports
import handlers
import cfgdlg

# Editra Libraries
import ed_glob
import ed_msg
import eclib.ctrlbox as ctrlbox
import eclib.outbuff as outbuff
import eclib.platebtn as platebtn

#-----------------------------------------------------------------------------#
# Globals
ID_SETTINGS = wx.NewId()
ID_EXECUTABLE = wx.NewId()
ID_ARGS = wx.NewId()
ID_RUN = wx.NewId()

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class LaunchWindow(ctrlbox.ControlBox):
    """Control window for showing and running scripts"""
    def __init__(self, parent):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self._mw = self.__FindMainWindow()
        self._buffer = OutputDisplay(self)
        self._worker = None
        self._busy = False
        self._config = dict(file='')

        # Setup
        self.__DoLayout()
        cbuffer = self._mw.GetNotebook().GetCurrentCtrl()
        self.SetupControlBar(cbuffer)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        ed_msg.Subscribe(self.OnPageChanged, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnPageChanged)
        ed_msg.Unsubscribe(self.OnThemeChanged)
        super(LaunchWindow).__del__()

    def __DoLayout(self):
        """Layout the window"""
        #-- Setup ControlBar --#
        ctrlbar = ctrlbox.ControlBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(ctrlbox.CTRLBAR_STYLE_DEFAULT)

        # Preferences
        prefbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        pref = platebtn.PlateButton(ctrlbar, ID_SETTINGS, '', prefbmp,
                                    style=platebtn.PB_STYLE_NOBG)
        pref.SetToolTipString(_("Settings"))
        ctrlbar.AddControl(pref, wx.ALIGN_LEFT)

        # Exe
        exe = wx.Choice(ctrlbar, ID_EXECUTABLE)
        exe.SetToolTipString(_("Program Executable Command"))
        ctrlbar.AddControl(exe, wx.ALIGN_LEFT)

        # Args
        args = wx.TextCtrl(ctrlbar, ID_ARGS)
        args.SetToolTipString(_("Program Arguments"))
        ctrlbar.AddControl(args, wx.ALIGN_LEFT)

        # Spacer
        ctrlbar.AddStretchSpacer()
        
        # Run Button
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        run = platebtn.PlateButton(ctrlbar, ID_RUN, _("Run"), rbmp,
                                   style=platebtn.PB_STYLE_NOBG)
        ctrlbar.AddControl(run, wx.ALIGN_RIGHT)

        # Clear Button
        cbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
        if cbmp.IsNull() or not cbmp.IsOk():
            cbmp = None
        clear = platebtn.PlateButton(ctrlbar, wx.ID_CLEAR, _("Clear"),
                                     cbmp, style=platebtn.PB_STYLE_NOBG)
        ctrlbar.AddControl(clear, wx.ALIGN_RIGHT)
        ctrlbar.SetVMargin(1, 1)
        self.SetControlBar(ctrlbar)

        self.SetWindow(self._buffer)

    def __FindMainWindow(self):
        """Find the mainwindow of this control
        @return: MainWindow or None

        """
        def IsMainWin(win):
            return getattr(tlw, '__name__', '') == 'MainWindow'

        tlw = self.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

    def GetFile(self):
        """Get the file that is currently set to be run
        @return: file path

        """
        return self._config['file']

    def GetMainWindow(self):
        """Get the mainwindow that created this instance
        @return: reference to MainWindow

        """
        return self._mw

    def OnButton(self, evt):
        """Handle events from the buttons on the control bar"""
        e_id = evt.GetId()
        if e_id == ID_SETTINGS:
            app = wx.GetApp()
            win = app.GetWindowInstance(cfgdlg.ConfigDialog)
            if win is None:
                config = cfgdlg.ConfigDialog(self._mw)
                config.CentreOnParent()
                config.Show()
            else:
                win.Raise()
        elif e_id == ID_RUN:
            self.SetProcessRunning(not self._busy)
        elif e_id == wx.ID_CLEAR:
            self._buffer.Clear()
        else:
            evt.Skip()

    def OnPageChanged(self, msg):
        """Update the status of the currently associated file
        when the page changes in the main notebook.
        @param msg: Message object

        """
        mval = msg.GetData()
        ctrl = mval[0].GetCurrentCtrl()
        if hasattr(ctrl, 'GetFileName'):
            self.SetupControlBar(ctrl)

    def OnThemeChanged(self, msg):
        """Update icons when the theme has been changed
        @param msg: Message Object

        """
        ctrls = ((ID_SETTINGS, ed_glob.ID_PREF),
                 (wx.ID_CLEAR, ed_glob.ID_DELETE))
        if self._busy:
            ctrls += ((ID_RUN, ed_glob.ID_STOP),)
        else:
            ctrls += ((ID_RUN, ed_glob.ID_BIN_FILE),)

        for ctrl, art in ctrls:
            btn = self.FindWindowById(ctrl)
            bmp = wx.ArtProvider.GetBitmap(str(art), wx.ART_MENU)
            btn.SetBitmap(bmp)
            btn.Refresh()

    def SetFile(self, fname):
        """Set the script file that will be run
        @param fname: file path

        """
        self._config['file'] = fname

    def SetProcessRunning(self, running=True):
        """Set the state of the window into either process running mode
        or process not running mode.
        @keyword running: Is a process running or not

        """
        rbtn = self.FindWindowById(ID_RUN)
        self._busy = running
        if running:
            abort = wx.ArtProvider.GetBitmap(str(ed_glob.ID_STOP), wx.ART_MENU)
            if abort.IsNull() or not abort.IsOk():
                abort = wx.ArtProvider.GetBitmap(wx.ART_ERROR,
                                                 wx.ART_MENU, (16, 16))
            rbtn.SetBitmap(abort)
            rbtn.SetLabel(_("Abort"))
        else:
            rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
            if rbmp.IsNull() or not rbmp.IsOk():
                rbmp = None
            rbtn.SetBitmap(rbmp)
            rbtn.SetLabel(_("Run"))

        self.GetControlBar().Layout()
        rbtn.Refresh()

    def SetupControlBar(self, ctrl):
        """Set the state of the controlbar based data found in the buffer
        passed in.
        @param ctrl: EdStc

        """
        fname = ctrl.GetFileName()
        self.SetFile(fname)

        # Setup filetype settings
        lang_id = ctrl.GetLangId()
        handler = handlers.GetHandlerById(lang_id)
        cmds = handler.GetCommands()

        # Get the controls
        exe_ch = self.FindWindowById(ID_EXECUTABLE)
        args_txt = self.FindWindowById(ID_ARGS)
        run_btn = self.FindWindowById(ID_RUN)

        # Set control states
        exe_ch.SetItems(cmds)
        if len(cmds):
            exe_ch.Enable()
            args_txt.Enable()
            run_btn.Enable()
            exe_ch.SetStringSelection(handler.GetDefault())
            self.GetControlBar().Layout()
        else:
            run_btn.Disable()
            args_txt.Disable()
            exe_ch.Disable()

#-----------------------------------------------------------------------------#

class OutputDisplay(outbuff.OutputBuffer, outbuff.ProcessBufferMixin):
    """Main output buffer display"""
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)
        outbuff.ProcessBufferMixin.__init__(self)

        # Attributes
        self._mw = parent.GetMainWindow()
        self._cfile = ''

        # Event Handlers
        self.Bind(wx.stc.EVT_STC_HOTSPOT_CLICK, self.OnHotSpot)

    def ApplyStyles(self, start, txt):
        """Apply any desired output formatting to the text in
        the buffer.
        @param start: Start position of new text
        @param txt: the new text that was added to the buffer

        """
        lang_id = GetLangIdFromMW(self._mw)
        handler = handlers.GetHandlerById(lang_id)
        handler.StyleText(GetTextBuffer(self._mw), start, txt)

    def DoProcessExit(self):
        """Do all that is needed to be done after a process has exited"""
        parent = self.GetParent()
        parent.SetProcessRunning(False)

    def DoProcessStart(self):
        """Do all that is needed to be done after a process has exited"""
        parent = self.GetParent()
        parent.SetProcessRunning(True)

    def OnHotSpot(self, evt):
        """Handle clicks on hotspots"""
        lang_id = GetLangIdFromMW(self._mw)
        handler = GetOutputHandler(lang_id)
        line = self.LineFromPosition(evt.GetPosition())
        #TODO add filename parameter
        handler.HandleHotSpot(self._mw, self, line, self.GetParent().GetFile())

#-----------------------------------------------------------------------------#
def GetLangIdFromMW(mainw):
    """Get the language id of the file in the current buffer
    in Editra's MainWindow.
    @param mainw: mainwindow instance

    """
    ctrl = GetTextBuffer(mainw)
    if hasattr(ctrl, 'GetLangId'):
        return ctrl.GetLangId()

def GetTextBuffer(mainw):
    """Get the current text buffer of the current window"""
    nb = mainw.GetNotebook()
    return mainw.GetCurrentCtrl()
