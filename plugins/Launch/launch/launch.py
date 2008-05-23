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
import os
import wx
import wx.stc

# Local Imports
import handlers
import cfgdlg

# Editra Libraries
import ed_glob
import util
from profiler import Profile_Get, Profile_Set
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

# Profile Settings Key
LAUNCH_KEY = 'Launch.Config'
#LAUNCH_PREFS = 'Launch.Prefs' # defined in cfgdlg

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class LaunchWindow(ctrlbox.ControlBox):
    """Control window for showing and running scripts"""
    def __init__(self, parent):
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self._mw = self.__FindMainWindow()
        self._buffer = OutputDisplay(self)
        self._slbl = None # Created in __DoLayout
        self._worker = None
        self._busy = False
        self._config = dict(file='', lang=0,
                            cfile='', clang=0,
                            last='', lastlang=0,
                            prelang=0)
        self._prefs = Profile_Get('Launch.Prefs', default=None)

        # Setup
        self.__DoLayout()
        hstate = Profile_Get(LAUNCH_KEY)
        if hstate is not None:
            handlers.SetState(hstate)
        if self._prefs is None:
            Profile_Set('Launch.Prefs',
                        dict(autoclear=False,
                             defaultf=self._buffer.GetDefaultForeground().Get(),
                             defaultb=self._buffer.GetDefaultBackground().Get(),
                             errorf=self._buffer.GetErrorForeground().Get(),
                             errorb=self._buffer.GetErrorBackground().Get(),
                             infof=self._buffer.GetInfoForeground().Get(),
                             infob=self._buffer.GetInfoBackground().Get(),
                             warnf=self._buffer.GetWarningForeground().Get(),
                             warnb=self._buffer.GetWarningBackground().Get()))
            self._prefs = Profile_Get('Launch.Prefs')

        self.UpdateBufferColors()
        cbuffer = self._mw.GetNotebook().GetCurrentCtrl()
        self.SetupControlBar(cbuffer)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        ed_msg.Subscribe(self.OnPageChanged, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnFileOpened, ed_msg.EDMSG_FILE_OPENED)
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnConfigExit, cfgdlg.EDMSG_LAUNCH_CFG_EXIT)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnPageChanged)
        ed_msg.Unsubscribe(self.OnThemeChanged)
        ed_msg.Unsubscribe(self.OnConfigExit)
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
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("exec") + ":"),
                           wx.ALIGN_LEFT)
        exe = wx.Choice(ctrlbar, ID_EXECUTABLE)
        exe.SetToolTipString(_("Program Executable Command"))
        ctrlbar.AddControl(exe, wx.ALIGN_LEFT)

        # Script Label
        ctrlbar.AddControl((5, 5), wx.ALIGN_LEFT)
        self._slbl = wx.StaticText(ctrlbar, label="")
        ctrlbar.AddControl(self._slbl, wx.ALIGN_LEFT)

        # Args
        ctrlbar.AddControl((5, 5), wx.ALIGN_LEFT)
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("args") + ":"),
                           wx.ALIGN_LEFT)
        args = wx.TextCtrl(ctrlbar, ID_ARGS)
        args.SetToolTipString(_("Script Arguments"))
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

    def GetLastRun(self):
        """Get the last file that was run
        @return: (fname, lang_id)

        """
        return (self._config['last'], self._config['lastlang'])

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
                config = cfgdlg.ConfigDialog(self._mw,
                                             ftype=self._config['lang'])
                config.CentreOnParent()
                config.Show()
            else:
                win.Raise()
        elif e_id == ID_RUN:
            if self._prefs.get('autoclear'):
                self._buffer.Clear()

            self.SetProcessRunning(not self._busy)
            if self._busy:
                util.Log("[Launch][info] Starting process")
                handler = handlers.GetHandlerById(self._config['lang'])
                cmd = self.FindWindowById(ID_EXECUTABLE).GetStringSelection()
                cmd = handler.GetCommand(cmd)
                path, fname = os.path.split(self._config['file'])
                args = self.FindWindowById(ID_ARGS).GetValue().split()
                self._worker = outbuff.ProcessThread(self._buffer, cmd, fname,
                                                     args, path,
                                                     handler.GetEnvironment())
                self._worker.start()
            else:
                self._worker.Abort()
                self._worker = None
        elif e_id == wx.ID_CLEAR:
            self._buffer.Clear()
        else:
            evt.Skip()

    def OnConfigExit(self, msg):
        """Update current state when the config dialog has been closed
        @param msg: Message Object

        """
        util.Log("[Launch][info] Saving config to profile")
        self.RefreshControlBar()
        Profile_Set(LAUNCH_KEY, handlers.GetState())
        self.UpdateBufferColors()

    def OnFileOpened(self, msg):
        """Reset state when a file open message is recieved
        @param msg: Message Object

        """
        # Only update when in the active window
        if not self._mw.IsActive():
            return

        fname = msg.GetData()
        self.SetFile(fname)

        # Setup filetype settings
        self._config['lang'] = GetLangIdFromMW(self._mw)
        self.RefreshControlBar()

    def OnPageChanged(self, msg):
        """Update the status of the currently associated file
        when the page changes in the main notebook.
        @param msg: Message object

        """
        # Only update when in the active window
        if not self._mw.IsActive():
            return

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

    def RefreshControlBar(self):
        """Refresh the state of the control bar based on the current config"""
        handler = handlers.GetHandlerById(self._config['lang'])
        cmds = handler.GetAliases()

        # Get the controls
        exe_ch = self.FindWindowById(ID_EXECUTABLE)
        args_txt = self.FindWindowById(ID_ARGS)
        run_btn = self.FindWindowById(ID_RUN)

        # Set control states
        csel = exe_ch.GetStringSelection()
        exe_ch.SetItems(cmds)
        util.Log("[Launch][info] Found commands %s" % str(cmds))
        if handler.GetName() != handlers.DEFAULT_HANDLER and len(self.GetFile()):
            exe_ch.Enable()
            args_txt.Enable()
            run_btn.Enable()
            if self._config['lang'] == self._config['prelang'] and len(csel):
                exe_ch.SetStringSelection(csel)
            else:
                exe_ch.SetStringSelection(handler.GetDefault())
            self.GetControlBar().Layout()
        else:
            run_btn.Disable()
            args_txt.Disable()
            exe_ch.Disable()

    def SetFile(self, fname):
        """Set the script file that will be run
        @param fname: file path

        """
        self._config['file'] = fname
        sname = os.path.split(fname)[1]
        self._slbl.SetLabel(_("file") + ": " + sname)
        self.GetControlBar().Layout()

    def SetLangId(self, langid):
        """Set the language id value(s)
        @param langid: syntax.synglob lang id

        """
        self._config['prelang'] = self._config['lang']
        self._config['lang'] = langid

    def SetProcessRunning(self, running=True):
        """Set the state of the window into either process running mode
        or process not running mode.
        @keyword running: Is a process running or not

        """
        rbtn = self.FindWindowById(ID_RUN)
        self._busy = running
        if running:
            self._config['last'] = self._config['file']
            self._config['lastlang'] = self._config['lang']
            self._config['cfile'] = self._config['file']
            self._config['clang'] = self._config['lang']
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
            # If the buffer was changed while this was running we should
            # update to the new buffer now that it has stopped.
            self.SetFile(self._config['cfile'])
            self.SetLangId(self._config['clang'])
            self.RefreshControlBar()

        self.GetControlBar().Layout()
        rbtn.Refresh()

    def SetupControlBar(self, ctrl):
        """Set the state of the controlbar based data found in the buffer
        passed in.
        @param ctrl: EdStc

        """
        fname = ctrl.GetFileName()
        lang_id = ctrl.GetLangId()

        # Don't update the bars status if the buffer is busy
        if self._buffer.IsRunning():
            self._config['cfile'] = fname
            self._config['clang'] = lang_id
        else:
            self.SetFile(fname)
            self.SetLangId(lang_id)

            # Refresh the control bars view
            self.RefreshControlBar()

    def UpdateBufferColors(self):
        """Update the buffers colors"""
        colors = dict()
        for color in ('defaultf', 'defaultb', 'errorf', 'errorb',
                      'infof', 'infob', 'warnf', 'warnb'):
            val = self._prefs.get(color, None)
            if val is not None:
                colors[color] = wx.Color(*val)
            else:
                colors[color] = val

        self._buffer.SetDefaultColor(colors['defaultf'], colors['defaultb'])
        self._buffer.SetErrorColor(colors['errorf'], colors['errorb'])
        self._buffer.SetInfoColor(colors['infof'], colors['infob'])
        self._buffer.SetWarningColor(colors['warnf'], colors['warnb'])

#-----------------------------------------------------------------------------#

class OutputDisplay(outbuff.OutputBuffer, outbuff.ProcessBufferMixin):
    """Main output buffer display"""
    def __init__(self, parent):
        outbuff.OutputBuffer.__init__(self, parent)
        outbuff.ProcessBufferMixin.__init__(self)

        # Attributes
        self._mw = parent.GetMainWindow()
        self._cfile = ''

        # Setup
        font = Profile_Get('FONT1', 'font', wx.Font(11, wx.FONTFAMILY_MODERN,
                                                    wx.FONTSTYLE_NORMAL,
                                                    wx.FONTWEIGHT_NORMAL))
        self.SetFont(font)

    def ApplyStyles(self, start, txt):
        """Apply any desired output formatting to the text in
        the buffer.
        @param start: Start position of new text
        @param txt: the new text that was added to the buffer

        """
        handler = self.GetCurrentHandler()
        handler.StyleText(self, start, txt)

    def DoFilterInput(self, txt):
        """Filter the incoming input
        @param txt: incoming text to filter

        """
        handler = self.GetCurrentHandler()
        return handler.FilterInput(txt)

    def DoHotSpotClicked(self, pos, line):
        """Pass hotspot click to the filetype handler for processing
        @param pos: click position
        @param line: line the click happened on
        @note: overridden from L{outbuff.OutputBuffer}

        """
        fname, lang_id = self.GetParent().GetLastRun()
        handler = handlers.GetHandlerById(lang_id)
        handler.HandleHotSpot(self._mw, self, line, fname)
        self.GetParent().SetupControlBar(GetTextBuffer(self._mw))

    def DoProcessExit(self, code=0):
        """Do all that is needed to be done after a process has exited"""
        self.AppendUpdate(">>> %s: %d%s" % (_("Exit Code"), code, os.linesep))
        self.Stop()
        self.GetParent().SetProcessRunning(False)

    def DoProcessStart(self, cmd=''):
        """Do any necessary preprocessing before a process is started"""
        self.GetParent().SetProcessRunning(True)
        self.AppendUpdate(">>> %s%s" % (cmd, os.linesep))

    def GetCurrentHandler(self):
        """Get the current filetype handler
        @return: L{handlers.FileTypeHandler} instance

        """
        lang_id = self.GetParent().GetLastRun()[1]
        handler = handlers.GetHandlerById(lang_id)
        return handler

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
    return nb.GetCurrentCtrl()
