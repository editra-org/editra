#!/usr/bin/env python
###############################################################################
# Name: Editra.py                                                             #
# Purpose: Implements Editras App object and the Main method                  #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE:  Editra.py
AUTHOR: Cody Precord
LANGUAGE: Python

SUMMARY:
This module defines the Editra Application object and the Main method
for running Editra.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import getopt
import wx

# Due to some methods that were added in 2.8.3 being used in a large number
# of places Editra has become incompatable with wxPython 2.8.1.1 and earlier.
# TODO: add a message dialog to display this, or look into the cause of the
#       issues of using wxversion on windows.
if not hasattr(sys, 'frozen') and wx.VERSION < (2, 8, 3, ''):
    print "VersionError: Editra requires wxPython 2.8.3 or higher"
    print "              Your version is %s" % wx.VERSION_STRING

# Try and import a system installed version of pkg_resources else fallback to
# the one bundled with Editra's source.
try:
    from pkg_resources import resource_filename
except ImportError:
    from extern.pkg_resources import resource_filename

# Editra Libraries
import ed_glob
import ed_i18n
import profiler
import util
import dev_tool
import ed_main
import ed_art
import ed_txt
import plugin
import extern.events as events

#--------------------------------------------------------------------------#
# Global Variables

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class Editra(wx.App, events.AppEventHandlerMixin):
    """The Editra Application Object
    @see: L{wx.App}

    """
    def __init__(self, *args, **kargs):
        """Initialize that main app and its attributes
        @postcondition: application is created and ready to be run in mainloop

        """
        wx.App.__init__(self, *args, **kargs)
        events.AppEventHandlerMixin.__init__(self)

        # Attributes
        self._log = dev_tool.DEBUGP
        self._lock = False
        self._windows = dict()

        # Setup Locale
        self.locale = wx.Locale(ed_i18n.GetLangId(profiler.Profile_Get('LANG')))
        if self.locale.GetCanonicalName() in ed_i18n.GetAvailLocales():
            self.locale.AddCatalogLookupPathPrefix(ed_glob.CONFIG['LANG_DIR'])
            self.locale.AddCatalog(ed_glob.PROG_NAME)
        else:
            del self.locale
            self.locale = None

        # Setup Plugins after locale as they may have resource that need to
        # be loaded.
        self._pluginmgr = plugin.PluginManager()

        self._log("[app][info] Registering Editra's ArtProvider")
        wx.ArtProvider.PushProvider(ed_art.EditraArt())

    def AddMessageCatalog(self, name, path):
        """Add a catalog lookup path to the app
        @param name: name of catalog (i.e 'projects')
        @param path: catalog lookup path

        """
        if self.locale is not None:
            path = resource_filename(path, 'locale')
            self.locale.AddCatalogLookupPathPrefix(path)
            self.locale.AddCatalog(name)

    def OnInit(self):
        """Initialize the Editor
        @note: this gets called before __init__
        @postcondition: custom artprovider and plugins are loaded

        """
        self.SetAppName(ed_glob.PROG_NAME)
        self._log = dev_tool.DEBUGP
        self._log("[app][info] Editra is Initializing")

        if profiler.Profile_Get('REPORTER', 'bool', True):
            sys.excepthook = dev_tool.ExceptionHook

        #---- Bind Events ----#
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        self.Bind(wx.EVT_MENU, self.OnNewWindow, id=ed_glob.ID_NEW_WINDOW)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow)

        return True

    def Exit(self, force=False):
        """Exit the program
        @postcondition: If no toplevel windows are present program will exit.
        @postcondition: Program may remain open if an open window is locking.

        """
        self._pluginmgr.WritePluginConfig()
        profiler.Profile().Write(profiler.Profile_Get('MYPROFILE'))
        if not self._lock or force:
            wx.App.Exit(self)

    def GetLocaleObject(self):
        """Get the locale object owned by this app. Use this method to add
        extra catalogs for lookup.
        @return: wx.Locale or None

        """
        return self.locale

    def GetLog(self):
        """Returns the logging function used by the app
        @return: the logging function of this program instance

        """
        return self._log

    def GetMainWindow(self):
        """Returns reference to the instance of the MainWindow
        that is running if available, and None if not.
        @return: the L{MainWindow} of this app if it is open

        """
        self._log("[app][warn] Editra::GetMainWindow is deprecated")
        for window in self._windows:
            if not hasattr(self._windows[window][0], '__name__'):
                continue

            if self._windows[window][0].__name__ == "MainWindow":
                return self._windows[window][0]
        return None

    def GetActiveWindow(self):
        """Returns the active main window if there is one else it will
        just return some main window or none if there are no main windows
        @return: frame instance or None

        """
        awin = None
        for win in self.GetMainWindows():
            if win.IsActive():
                awin = win
                break

        if awin is None:
            if len(self.GetMainWindows()):
                awin = self.GetMainWindows()[0]

        return awin

    def GetMainWindows(self):
        """Returns a list of all open main windows
        @return: list of L{MainWindow} instances of this app (list may be empty)

        """
        mainw = list()
        for window in self._windows:
            try:
                if self._windows[window][0].__name__ == "MainWindow":
                    mainw.append(self._windows[window][0])
            except AttributeError:
                continue
        return mainw

    def GetOpenWindows(self):
        """Returns a list of open windows
        @return: list of all open windows owned by app

        """
        return self._windows

    def GetPluginManager(self):
        """Returns the plugin manager used by this application
        @return: Apps plugin manager
        @see: L{plugin}

        """
        return self._pluginmgr

    def GetWindowInstance(self, wintype):
        """Get an instance of an open window if one exists
        @param wintype: Class type of window to look for
        @precondition: Window must have called L{RegisterWindow}
        @return: Instance of window or None

        """
        for win in self._windows:
            if isinstance(self._windows[win][0], wintype):
                return self._windows[win][0]
        return None

    def IsLocked(self):
        """Returns whether the application is locked or not
        @return: whether a window has locked the app from closing or not

        """
        return self._lock

    def Lock(self):
        """Locks the app from exiting
        @postcondition: program is locked from exiting

        """
        self._lock = True

    def MacOpenFile(self, filename):
        """Macintosh Specific code for opening files that are associated
        with the editor and double clicked on after the editor is already
        running.
        @param filename: file path string
        @postcondition: if L{MainWindow} is open file will be opened in notebook

        """
        window = self.GetTopWindow()
        if getattr(window, '__name__', '') == "MainWindow":
            try:
                encoding = sys.getfilesystemencoding()
                window.DoOpen(ed_glob.ID_COMMAND_LINE_OPEN,
                              ed_txt.DecodeString(filename, encoding))
                self._log("[app][info] MacOpenFile Fired")
            except Exception, msg:
                self._log("[app][err] Failed to open drop file: %s" % str(msg))
                pass
        else:
            pass

    def OnActivate(self, evt):
        """Activation Event Handler
        @param evt: event that called this handler
        @type evt: wx.ActivateEvent

        """
        if evt.GetActive():
            self._log("[app][info] I'm Awake!!")
        else:
            self._log("[app][info] Going to sleep")
        evt.Skip()

    def OnExit(self, evt=None, force=False):
        """Handle application exit request
        @param evt: event that called this handler

        """
        e_id = -1
        if evt:
            e_id = evt.GetId()

        if e_id == ed_glob.ID_EXIT:
            # First loop is to ensure current top window is
            # closed first
            for win in self.GetMainWindows():
                if win.IsActive():
                    result = win.Close()
                    if result:
                        break
                    return
            for win in self.GetMainWindows():
                win.Raise()
                result = win.Close()
                if not result:
                    break
            self.Exit(force)
        else:
            if evt:
                evt.Skip()

    def OnNewWindow(self, evt):
        """Create a new editing window
        @param evt: wx.EVT_MENU

        """
        if evt.GetId() == ed_glob.ID_NEW_WINDOW:
            frame = evt.GetEventObject().GetMenuBar().GetFrame()
            self.OpenNewWindow(caller=frame)
        else:
            evt.Skip()

    def OnCloseWindow(self, evt):
        """Close the currently active window
        @param evt: wx.MenuEvent

        """
        if evt.GetId() in [ed_glob.ID_CLOSE, ed_glob.ID_CLOSE_WINDOW]:
            for window in self._windows.values():
                if hasattr(window[0], 'IsActive') and window[0].IsActive():
                    if hasattr(window[0], 'Close'):
                        window[0].Close()
                    break
        else:
            evt.Skip()

    def OpenNewWindow(self, fname=u'', caller=None):
        """Open a new window
        @keyword fname: Open a file in the new window

        """
        frame = ed_main.MainWindow(None, wx.ID_ANY,
                                   profiler.Profile_Get('WSIZE'),
                                   ed_glob.PROG_NAME)
        if caller:
            pos = caller.GetPosition()
            frame.SetPosition((pos.x + 22, pos.y + 22))

        self.RegisterWindow(repr(frame), frame, True)
        self.SetTopWindow(frame)
        if isinstance(fname, basestring) and fname != u'':
            frame.DoOpen(ed_glob.ID_COMMAND_LINE_OPEN, fname)
        frame.Show(True)

        # Ensure frame gets an Activate event when shown
        # this doesn't happen automatically on windows
        if wx.Platform == '__WXMSW__':
            wx.PostEvent(frame, wx.ActivateEvent(wx.wxEVT_ACTIVATE, True))

    def RegisterWindow(self, name, window, can_lock=False):
        """Registers winows with the app. The name should be the
        repr of window. The can_lock parameter is a boolean stating
        whether the window can keep the main app running after the
        main frame has exited.
        @param name: name of window
        @param window: reference to window object
        @keyword can_lock: whether window can lock exit or not

        """
        self._windows[name] = (window, can_lock)

    def ReloadArtProvider(self):
        """Reloads the custom art provider onto the artprovider stack
        @postcondition: artprovider is removed and reloaded

        """
        try:
            wx.ArtProvider.PopProvider()
        finally:
            wx.ArtProvider.PushProvider(ed_art.EditraArt())

    def UnLock(self):
        """Unlocks the application
        @postcondition: application is unlocked so it can exit

        """
        self._lock = False

    def UnRegisterWindow(self, name):
        """Unregisters a named window with the app if the window
        was the top window and if other windows that can lock are
        registered in the window stack it will promote the next one
        it finds to be the top window. If no windows that fit this
        criteria are found it will close the application.
        @param name: name of window to unregister

        """
        if self._windows.has_key(name):
            self._windows.pop(name)
            cur_top = self.GetTopWindow()
            if not len(self._windows):
                self._log("[app][info] No more open windows shutting down")
                self.Exit()
                return

            if name == repr(cur_top):
                found = False
                for key in self._windows:
                    if self._windows[key][1]:
                        self._log("[app][info] Promoting %s to top" % key)
                        try:
                            self.SetTopWindow(self._windows[key][0])
                        except Exception:
                            continue
                        found = True
                        break

                if not found:
                    self._log("[app][info] No more top windows exiting app")
                    self.UnLock()
                    self.Exit()
            else:
                self._log("[app][info] UnRegistered %s" % name)
        else:
            self._log("[app][warn] The window %s is not registered" % name)

    def WindowCanLock(self, winname):
        """Checks if a named window can lock the application or
        not. The window must have been previously registered with
        a call to RegisterWindow for this function to have any
        real usefullness.
        @param winname: name of window to query

        """
        if self._windows.has_key(winname):
            return self._windows[winname][1]
        else:
            self._log("[app][warn] the window %s has "
                      "not been registered" % winname)
            return False

#--------------------------------------------------------------------------#

def InitConfig():
    """Initializes the configuration data
    @postcondition: all configuration data is set

    """
    ed_glob.CONFIG['PROFILE_DIR'] = util.ResolvConfigDir("profiles")
    profile_updated = False
    if util.HasConfigDir():
        if profiler.ProfileIsCurrent():
            profiler.Profile().Load(profiler.GetProfileStr())
        else:
            dev_tool.DEBUGP("[InitConfig][info] Updating Profile to current version")

            # Load and update profile
            pstr = profiler.GetProfileStr()
            profiler.Profile().Load(pstr)
            profiler.Profile().Update()

            #---- Temporary Profile Adaptions ----#
            ## Force some default values to be set on an upgrade
            if wx.Platform == '__WXGTK__':
                profiler.Profile_Set('ICONS', 'Default')
            else:
                profiler.Profile_Set('ICONS', 'Tango')

            # GUI_DEBUG mode removed in 0.2.5
            mode = profiler.Profile_Get('MODE')
            if mode == 'GUI_DEBUG':
                profiler.Profile_Set('MODE', 'DEBUG')

            #---- End Temporary Profile Adaptions ----#

            # Write out updated profile
            profiler.Profile().Write(pstr)

            # When upgrading from an older version make sure all
            # config directories are available.
            for cfg in ["cache", "styles", "plugins", "profiles"]:
                if not util.HasConfigDir(cfg):
                    util.MakeConfigDir(cfg)

            profile_updated = True
    else:
        # Fresh install
        util.CreateConfigDir()

        # Set default eol for windows
        if wx.Platform == '__WXMSW__':
            profiler.Profile_Set('EOL', 'Windows (\\r\\n)')

    # Set debug mode
    if 'DEBUG' in profiler.Profile_Get('MODE'):
        ed_glob.DEBUG = True

    # Resolve resource locations
    ed_glob.CONFIG['CONFIG_DIR'] = util.ResolvConfigDir("")
    ed_glob.CONFIG['SYSPIX_DIR'] = util.ResolvConfigDir("pixmaps", True)
    ed_glob.CONFIG['PLUGIN_DIR'] = util.ResolvConfigDir("plugins")
    ed_glob.CONFIG['THEME_DIR'] = util.ResolvConfigDir(os.path.join("pixmaps",
                                                                    "theme"))
    ed_glob.CONFIG['LANG_DIR'] = util.ResolvConfigDir("locale", True)
    ed_glob.CONFIG['STYLES_DIR'] = util.ResolvConfigDir("styles")
    ed_glob.CONFIG['SYS_PLUGIN_DIR'] = util.ResolvConfigDir("plugins", True)
    ed_glob.CONFIG['SYS_STYLES_DIR'] = util.ResolvConfigDir("styles", True)
    ed_glob.CONFIG['TEST_DIR'] = util.ResolvConfigDir(os.path.join("tests",
                                                                   "syntax"),
                                                                   True)
    if not util.HasConfigDir("cache"):
        util.MakeConfigDir("cache")
    ed_glob.CONFIG['CACHE_DIR'] = util.ResolvConfigDir("cache")

    return profile_updated

#--------------------------------------------------------------------------#

def Main():
    """Configures and Runs an instance of Editra
    @summary: Parses command line options, loads the user profile, creates
              an instance of Editra and starts the main loop.

    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dhv",
                                   ['debug', 'help', 'version'])
    except getopt.GetoptError, msg:
        dev_tool.DEBUGP("[main][err] %s" % str(msg))
        opts = list()
        args = list()

    # Process command line options
    if len(opts):
        if True in [x[0] in ['-h', '--help'] for x in opts]:
            print ("Editra - %s - Developers Text Editor\n"
                   "Cody Precord (2005-2007)\n\n"
                   "usage: Editra [arguments] [files... ]\n\n"
                   "Short Arguments:\n"
                   "  -d         Turn on console debugging\n"
                   "  -h         Show this help message\n"
                   "  -v         Print version number and exit\n"
                   "\nLong Arguments:\n"
                   "  --debug    Turn on console debugging\n"
                   "  --help     Show this help message\n"
                   "  --version  Print version number and exit\n"
                  ) % ed_glob.VERSION
            os._exit(0)

        if True in [x[0] in ['-v', '--version'] for x in opts]:
            print "%s - v%s - Developers Editor" % (ed_glob.PROG_NAME, \
                                                    ed_glob.VERSION)
            os._exit(0)

        if True in [x[0] in ['-d', '--debug'] for x in opts]:
            ed_glob.DEBUG = True

    # We are ready to run so fire up the config and launch the app
    profile_updated = InitConfig()

    # Create Application
    dev_tool.DEBUGP("[main][info] Initializing Application...")
    editra_app = Editra(False)

    if profile_updated:
        # Make sure window iniliazes to default position
        profiler.Profile_Del('WPOS')
        wx.MessageBox(_("Your profile has been updated to the latest "
                        "version") + u"\n" + \
                      _("Please check the preferences dialog to reset "
                        "your preferences"),
                      _("Profile Updated"))

    # Splash a warning if version is not a final version
    if profiler.Profile_Get('APPSPLASH') and int(ed_glob.VERSION[0]) < 1:
        import edimage
        splash_img = edimage.splashwarn.GetBitmap()
        splash = wx.SplashScreen(splash_img, wx.SPLASH_CENTRE_ON_PARENT | \
                                 wx.SPLASH_NO_TIMEOUT, 0, None, wx.ID_ANY)
        splash.Show()

    frame = ed_main.MainWindow(None, wx.ID_ANY, profiler.Profile_Get('WSIZE'),
                               ed_glob.PROG_NAME)
    editra_app.RegisterWindow(repr(frame), frame, True)
    editra_app.SetTopWindow(frame)

    # Load Session Data
    # But not if there are command line args for files to open
    if profiler.Profile_Get('SAVE_SESSION', 'bool', False) and not len(args):
        frame.GetNotebook().LoadSessionFiles()

    frame.Show(True)
    # Unlike wxMac/wxGTK Windows doesn't post an activate event when a window
    # is first shown, so do it manually to make sure all event handlers get
    # pushed.
    if wx.Platform == '__WXMSW__':
        wx.PostEvent(frame, wx.ActivateEvent(wx.wxEVT_ACTIVATE, True))

    if 'splash' in locals():
        splash.Destroy()

    for arg in args:
        try:
            arg = os.path.abspath(arg)
            fname = ed_txt.DecodeString(arg, sys.getfilesystemencoding())
            frame.DoOpen(ed_glob.ID_COMMAND_LINE_OPEN, fname)
        except IndexError:
            dev_tool.DEBUGP("[main][err] IndexError on commandline args")

    # 3. Start Applications Main Loop
    dev_tool.DEBUGP("[main][info] Starting MainLoop...")
    editra_app.MainLoop()
    dev_tool.DEBUGP("[main][info] MainLoop finished exiting application")
    os._exit(0)

#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    Main()
