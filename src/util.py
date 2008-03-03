###############################################################################
# Name: util.py                                                               #
# Purpose: Misc utility functions used through out Editra                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: util.py
LANGUAGE: Python

SUMMARY:
This file contains various helper functions and utilities that the
program uses. Basically a random library of misfit functions.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import stat
import codecs
import urllib2
import wx

# Editra Libraries
import ed_glob
import ed_event
import ed_crypt
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class DropTargetFT(wx.PyDropTarget):
    """Drop target capable of accepting dropped files and text
    @todo: has some issues with the clipboard on windows under certain
           conditions. They arent fatal but need fixing.

    """
    def __init__(self, window, textcallback=None, filecallback=None):
        """Initializes the Drop target
        @param window: window to recieve drop objects

        """
        wx.PyDropTarget.__init__(self)
        self.window = window
        self._data = dict(data=None, fdata=None, tdata=None,
                          tcallb=textcallback, fcallb=filecallback)
        self._tmp = None
        self._lastp = None
        self.InitObjects()

    def CreateDragString(self, txt):
        """Creates a bitmap of the text that is being dragged
        @todo: possibly set colors to match highlighting of text
        @todo: generalize this to be usable by other widgets besides stc

        """
        if not issubclass(self.window.__class__, wx.stc.StyledTextCtrl):
            return

        stc = self.window
        txt = txt.split(stc.GetEOLChar())
        longest = (0, 0)
        for line in txt:
            ext = stc.GetTextExtent(line)
            if ext[0] > longest[0]:
                longest = ext

        cords = [ (0, x * longest[1]) for x in xrange(len(txt)) ]
        mdc = wx.MemoryDC(wx.EmptyBitmap(longest[0] + 5,
                                         longest[1] * len(txt), 32))
        mdc.SetBackgroundMode(wx.TRANSPARENT)
        mdc.SetTextForeground(stc.GetDefaultForeColour())
        mdc.SetFont(stc.GetDefaultFont())
        mdc.DrawTextList(txt, cords)
        self._tmp = wx.DragImage(mdc.GetAsBitmap())

    def InitObjects(self):
        """Initializes the text and file data objects
        @postcondition: all data objects are initialized

        """
        self._data['data'] = wx.DataObjectComposite()
        self._data['tdata'] = wx.TextDataObject()
        self._data['fdata'] = wx.FileDataObject()
        self._data['data'].Add(self._data['tdata'], True)
        self._data['data'].Add(self._data['fdata'], False)
        self.SetDataObject(self._data['data'])

    def OnEnter(self, x_cord, y_cord, drag_result):
        """Called when a drag starts
        @return: result of drop object entering window

        """
        # GetData seems to happen automatically on msw, calling it again
        # causes this to fail the first time.
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            return wx.DragCopy

        if wx.Platform == '__WXMAC__':
            try:
                self.GetData()
            except wx.PyAssertionError:
                return wx.DragError

        self._lastp = (x_cord, y_cord)
        files = self._data['fdata'].GetFilenames()
        text = self._data['tdata'].GetText()
        if len(files):
            self.window.SetCursor(wx.StockCursor(wx.CURSOR_COPY_ARROW))
        else:
            self.CreateDragString(text)
        return drag_result

    def OnDrop(self, x_cord=0, y_cord=0):
        """Gets the drop cords
        @keyword x: x cord of drop object
        @keyword y: y cord of drop object
        @todo: implement snapback when drop is out of range

        """
        self._tmp = None
        self._lastp = None
        return True

    def OnDragOver(self, x_cord, y_cord, drag_result):
        """Called when the cursor is moved during a drag action
        @return: result of drag over
        @todo: For some reason the carrat postion changes which can be seen
               by the brackets getting highlighted. However the actual carrat
               is not moved.

        """
        if self._tmp is None:
            return drag_result
        else:
            stc = self.window
            point = wx.Point(x_cord, y_cord)
            self._tmp.BeginDrag(point - self._lastp, stc)
            self._tmp.Hide()
            stc.GotoPos(stc.PositionFromPoint(point))
            stc.Refresh()
            stc.Update()
            self._tmp.Move(point)
            self._tmp.Show()
            self._tmp.RedrawImage(self._lastp, point, True, True)
            self._lastp = point
            return drag_result

    def OnData(self, x_cord, y_cord, drag_result):
        """Gets and processes the dropped data
        @postcondition: dropped data is processed

        """
        self.window.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        if self.window.HasCapture():
            self.window.ReleaseMouse()

        try:
            data = self.GetData()
        except wx.PyAssertionError:
            wx.PostEvent(self.window.GetTopLevelParent(), \
                        ed_event.StatusEvent(ed_event.edEVT_STATUS, -1,
                                             _("Unable to open dropped file or "
                                               "text")))
            data = False
            drag_result = wx.DragCancel

        if data:
            files = self._data['fdata'].GetFilenames()
            text = self._data['tdata'].GetText()
            if len(files) > 0 and self._data['fcallb'] is not None:
                self._data['fcallb'](files)
            elif(len(text) > 0):
                if SetClipboardText(text):
                    win = self.window
                    pos = win.PositionFromPointClose(x_cord, y_cord)
                    if pos != wx.stc.STC_INVALID_POSITION:
                        win.SetSelection(pos, pos)
                        win.Paste()
                    else:
                        drag_result = wx.DragCancel
        self.InitObjects()
        return drag_result

    def OnLeave(self):
        """Handles the event of when the drag object leaves the window
        @postcondition: Cursor is set back to normal state

        """
        self.window.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        if self.window.HasCapture():
            self.window.ReleaseMouse()

        if self._tmp is not None:
            try:
                self._tmp.EndDrag()
            except wx.PyAssertionError, msg:
                Log("[droptargetft][err] %s" % str(msg))

#---- End FileDropTarget ----#

#---- Misc Common Function Library ----#
# Used for holding the primary selection on mac/msw
FAKE_CLIPBOARD = None

def GetClipboardText():
    """Get the primary selection from the clipboard if there is one
    @return: str or None

    """
    if wx.Platform in '__WXGTK__':
        wx.TheClipboard.UsePrimarySelection(True)
    else:
        # Fake the primary selection on mac/msw
        global FAKE_CLIPBOARD
        return FAKE_CLIPBOARD
    text_obj = wx.TextDataObject()
    rtxt = None
    if wx.TheClipboard.Open():
        if wx.TheClipboard.GetData(text_obj):
            rtxt = text_obj.GetText()
        wx.TheClipboard.Close()
    return rtxt

def SetClipboardText(txt, primary=False):
    """Copies text to the clipboard
    @param txt: text to put in clipboard
    @keyword primary: Set txt as primary selection (x11)

    """
    if primary:
        if wx.Platform == '__WXGTK__':
            wx.TheClipboard.UsePrimarySelection(True)
        else:
            # Fake the primary selection on mac/msw
            global FAKE_CLIPBOARD
            FAKE_CLIPBOARD = txt
            return True

    data_o = wx.TextDataObject()
    data_o.SetText(txt)
    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(data_o)
        wx.TheClipboard.Close()
        return True
    else:
        return False

def FilterFiles(file_list):
    """Filters a list of paths and returns a list of paths
    that can probably be opened in the editor.
    @param file_list: list of files/folders to filter for good files in

    """
    good = list()
    for path in file_list:
        # Filter out directories and some common filetypes that can't
        # be opened.
        if not os.path.exists(path) or os.path.isdir(path) or \
           GetExtension(path).lower() in ['gz', 'tar', 'bz2', 'zip', 'rar',
                                          'ace', 'png', 'jpg', 'gif', 'jpeg',
                                          'bmp', 'exe', 'pyc', 'pyo', 'psd',
                                          'a', 'o', 'dll', 'ico', 'icns']:
            continue
        else:
            good.append(path)
    return good

def GetFileModTime(file_name):
    """Returns the time that the given file was last modified on
    @param file_name: path of file to get mtime of

    """
    try:
        mod_time = os.path.getmtime(file_name)
    except EnvironmentError:
        mod_time = 0
    return mod_time

def GetFileReader(file_name, enc='utf-8'):
    """Returns a file stream reader object for reading the
    supplied file name. It returns a file reader using the encoding
    (enc) which defaults to utf-8. If lookup of the reader fails on
    the host system it will return an ascii reader.
    If there is an error in creating the file reader the function
    will return a negative number.
    @param file_name: name of file to get a reader for
    @keyword enc: encoding to use for reading the file
    @return file reader, or int if error.

    """
    try:
        file_h = file(file_name, "rb")
    except (IOError, OSError):
        dev_tool.DEBUGP("[file_reader] Failed to open file %s" % file_name)
        return -1

    try:
        reader = codecs.getreader(enc)(file_h)
    except (LookupError, IndexError, ValueError):
        dev_tool.DEBUGP('[file_reader] Failed to get %s Reader' % enc)
        reader = file_h
    return reader

def GetFileWriter(file_name, enc='utf-8'):
    """Returns a file stream writer object for reading the
    supplied file name. It returns a file writer in the supplied
    encoding if the host system supports it other wise it will return
    an ascii reader. The default will try and return a utf-8 reader.
    If there is an error in creating the file reader the function
    will return a negative number.
    @param file_name: path of file to get writer for
    @keyword enc: encoding to write text to file with

    """
    try:
        file_h = file(file_name, "wb")
    except IOError:
        dev_tool.DEBUGP("[file_writer][err] Failed to open file %s" % file_name)
        return -1
    try:
        writer = codecs.getwriter(enc)(file_h)
    except (LookupError, IndexError, ValueError):
        dev_tool.DEBUGP('[file_writer][err] Failed to get %s Writer' % enc)
        writer = file_h
    return writer

def GetUniqueName(path, name):
    """Make a file name that will be unique in case a file of the
    same name already exists at that path.
    @param path: Root path to folder of files destination
    @param name: desired file name base
    @return: string

    """
    tmpname = os.path.join(path, name)
    if os.path.exists(tmpname):
        if '.' not in name:
            ext = ''
            fbase = name
        else:
            ext = '.' + name.split('.')[-1]
            fbase = name[:-1 * len(ext)]

        inc = len([x for x in os.listdir(path) if x.startswith(fbase)])
        tmpname = os.path.join(path, "%s-%d%s" % (fbase, inc, ext))
        while os.path.exists(tmpname):
            inc = inc + 1
            tmpname = os.path.join(path, "%s-%d%s" % (fbase, inc, ext))

    return tmpname

def GetPathName(path):
    """Gets the path minus filename
    @param path: full path to get base of

    """
    return os.path.split(path)[0]

def GetFileManagerCmd():
    """Get the file manager open command for the current os. Under linux
    it will check for nautilus and konqueror and return which one it finds
    first or 'nautilus' (Gnome) if it finds neither.
    @return: string command

    """
    if wx.Platform == '__WXMAC__':
        return 'open'
    elif wx.Platform == '__WXMSW__':
        return 'explorer'
    else:
        for cmd in ('nautilus', 'konqueror'):
            result = os.system("which %s > /dev/null" % cmd)
            if result == 0:
                return cmd
        else:
            return 'nautilus'

def GetFileName(path):
    """Gets last atom on end of string as filename
    @param path: full path to get filename from

    """
    return os.path.split(path)[-1]

def GetFileSize(path):
    """Get the size of the file at a given path
    @param path: Path to file
    @return: long

    """
    try:
        return os.stat(path)[stat.ST_SIZE]
    except:
        return 0

def GetExtension(file_str):
    """Gets last atom at end of string as extension if
    no extension whole string is returned
    @param file_str: path or file name to get extension from

    """
    return file_str.split('.')[-1]

def MakeNewFile(path, name):
    """Make a new file at the given path with the given name.
    If the file already exists, the given name will be changed to
    a unique name in the form of name + -NUMBER + .extension
    @param path: path to directory to create file in
    @param name: desired name of file
    @return: Tuple of (success?, Path of new file OR Error message)

    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    fname = GetUniqueName(path, name)

    try:
        open(fname, 'w').close()
    except (IOError, OSError), msg:
        return (False, str(msg))

    return (True, fname)

def MakeNewFolder(path, name):
    """Make a new folder at the given path with the given name.
    If the folder already exists, the given name will be changed to
    a unique name in the form of name + -NUMBER.
    @param path: path to create folder on
    @param name: desired name for folder
    @return: Tuple of (success?, new dirname OR Error message)

    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    folder = GetUniqueName(path, name)
    try:
        os.mkdir(folder)
    except (OSError, IOError), msg:
        return (False, str(msg))

    return (True, folder)

def ResolvAbsPath(rel_path):
    """Takes a relative path and converts it to an
    absolute path.
    @param rel_path: path to construct absolute path for

    """
    cwd = os.getcwd()
    pieces = rel_path.split(os.sep)
    cut = 0

    for token in pieces:
        if token == "..":
            cut += 1

        if cut > 0:
            rpath = os.sep.join(pieces[cut:])
            cut *= -1
            cwd = cwd.split(os.sep)
            apath = os.sep.join(cwd[0:cut])
        else:
            rpath = rel_path
            apath = cwd

    return apath + os.sep + rpath

def HasConfigDir(loc=u""):
    """ Checks if the user has a config directory and returns True
    if the config directory exists or False if it does not.
    @return: whether config dir in question exists on an expected path

    """
    if os.path.exists(u"%s%s.%s%s%s" % (wx.GetHomeDir(), os.sep,
                                        ed_glob.PROG_NAME, os.sep, loc)):
        return True
    else:
        return False

def MakeConfigDir(name):
    """Makes a user config directory
    @param name: name of config directory to make in user config dir

    """
    config_dir = wx.GetHomeDir() + os.sep + u"." + ed_glob.PROG_NAME
    try:
        os.mkdir(config_dir + os.sep + name)
    except (OSError, IOError):
        pass

def CreateConfigDir():
    """ Creates the user config directory its default sub
    directories and any of the default config files.
    @postcondition: all default configuration files/folders are created

    """
    #---- Resolve Paths ----#
    config_dir = u"%s%s.%s" % (wx.GetHomeDir(), os.sep, ed_glob.PROG_NAME)
    profile_dir = u"%s%sprofiles" % (config_dir, os.sep)
    dest_file = u"%s%sdefault.ppb" % (profile_dir, os.sep)
    ext_cfg = ["cache", "styles", "plugins"]

    #---- Create Directories ----#
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)

    for cfg in ext_cfg:
        if not HasConfigDir(cfg):
            MakeConfigDir(cfg)

    import profiler
    profiler.Profile().LoadDefaults()
    profiler.Profile_Set("MYPROFILE", dest_file)
    profiler.UpdateProfileLoader()

def ResolvConfigDir(config_dir, sys_only=False):
    """Checks for a user config directory and if it is not
    found it then resolves the absolute path of the executables
    directory from the relative execution path. This is then used
    to find the location of the specified directory as it relates
    to the executable directory, and returns that path as a
    string.
    @param config_dir: name of config directory to resolve
    @keyword sys_only: only get paths of system config directory or user one
    @note: This method is probably much more complex than it needs to be but
           the code has proven itself.

    """
    if not sys_only:
        # Try to look for a user dir
        user_config = u"%s%s.%s%s%s" % (wx.GetHomeDir(), os.sep,
                                        ed_glob.PROG_NAME, os.sep,
                                        config_dir)
        if os.path.exists(user_config):
            return user_config + os.sep

    # The following lines are used only when Editra is being run as a
    # source package. If the found path does not exist then Editra is
    # running as as a built package.
    path = __file__
    path = os.sep.join(path.split(os.sep)[:-2])
    path =  path + os.sep + config_dir + os.sep
    if os.path.exists(path):
        return path

    # If we get here we need to do some platform dependant lookup
    # to find everything.
    path = sys.argv[0]

    # If it is a link get the real path
    if os.path.islink(path):
        path = os.path.realpath(path)

    # Tokenize path
    pieces = path.split(os.sep)

    if os.sys.platform == 'win32':
        # On Windows the exe is in same dir as config directories
        pro_path = os.sep.join(pieces[:-1])

        if os.path.isabs(pro_path):
            pass
        elif pro_path == "":
            pro_path = os.getcwd()
            pieces = pro_path.split(os.sep)
            pro_path = os.sep.join(pieces[:-1])
        else:
            pro_path = ResolvAbsPath(pro_path)
    else:
        pro_path = os.sep.join(pieces[:-2])

        if pro_path.startswith(os.sep):
            pass
        elif pro_path == "":
            pro_path = os.getcwd()
            pieces = pro_path.split(os.sep)
            if pieces[-1] not in [ed_glob.PROG_NAME.lower(), ed_glob.PROG_NAME]:
                pro_path = os.sep.join(pieces[:-1])
        else:
            pro_path = ResolvAbsPath(pro_path)

    if os.sys.platform == "darwin":
        # On OS X the config directories are in the applet under Resources
        pro_path = u"%s%sResources%s%s%s" % (pro_path, os.sep, os.sep,
                                             config_dir, os.sep)
    else:
        pro_path = pro_path + os.sep + config_dir + os.sep

    return os.path.normpath(pro_path) + os.sep

def GetResources(resource):
    """Returns a list of resource directories from a given toplevel config dir
    @param resource: config directory name
    @return: list of resource directory that exist under the given resource path

    """
    rec_dir = ResolvConfigDir(resource)
    if os.path.exists(rec_dir):
        rec_lst = [ rec.title() for rec in os.listdir(rec_dir)
                    if os.path.isdir(rec_dir + rec) and rec[0] != u"." ]
        return rec_lst
    else:
        return -1

def GetResourceFiles(resource, trim=True, get_all=False):
    """Gets a list of resource files from a directory and trims the
    file extentions from the names if trim is set to True (default).
    If the get_all parameter is set to True the function will return
    a set of unique items by looking up both the user and system level
    files and combining them, the default behavior returns the user
    level files if they exist or the system level files if the
    user ones do not exist.
    @param resource: name of config directory
    @keyword trim: trim file extensions or not
    @keyword get_all: get a set of both system/user files or just user level


    """
    rec_dir = ResolvConfigDir(resource)
    if get_all:
        rec_dir2 = ResolvConfigDir(resource, True)
    rec_list = list()
    if not os.path.exists(rec_dir):
        return -1
    else:
        recs = os.listdir(rec_dir)
        if get_all and os.path.exists(rec_dir2):
            recs.extend(os.listdir(rec_dir2))

        for rec in recs:
            if os.path.isfile(rec_dir + rec) or \
              (get_all and os.path.isfile(rec_dir2 + rec)):
                # Trim the last part of an extension if one exists
                if trim:
                    rec = ".".join(rec.split(u".")[:-1]).strip()

                if len(rec):
                    rec = rec[0].upper() + rec[1:]
                    rec_list.append(rec)
        rec_list.sort()
        return list(set(rec_list))

def Log(msg):
    """Push the message to the apps log
    @param msg: message string to log

    """
    wx.GetApp().GetLog()(msg)

def GetProxyOpener(proxy_set):
    """Get a urlopener for use with a proxy
    @param proxy_set: proxy settings to use

    """
    Log("[util][info] Making proxy opener with %s" % str(proxy_set))
    proxy_info = dict(proxy_set)
    auth_str = "%(uname)s:%(passwd)s@%(url)s"
    url = proxy_info['url']
    if url.startswith('http://'):
        auth_str = "http://" + auth_str
        proxy_info['url'] = url.replace('http://', '')
    else:
        pass

    if len(proxy_info.get('port', '')):
        auth_str = auth_str + ":%(port)s"

    proxy_info['passwd'] = ed_crypt.Decrypt(proxy_info['passwd'],
                                            proxy_info['pid'])
    Log("[util][info] Formatted proxy request: %s" % \
        (auth_str.replace('%(passwd)s', '****') % proxy_info))
    proxy = urllib2.ProxyHandler({"http" : auth_str % proxy_info})
    opener = urllib2.build_opener(proxy, urllib2.HTTPHandler)
    return opener

#---- GUI helper functions ----#
def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.
    @param color: color object to adjust
    @type color: wx.Color
    @param percent: percent to adjust +(brighten) or -(darken)
    @type percent: int
    @keyword alpha: Value to adjust alpha channel to

    """
    radj, gadj, badj = [ int(val * (abs(percent) / 100.))
                         for val in color.Get() ]

    if percent < 0:
        radj, gadj, badj = [ val * -1 for val in [radj, gadj, badj] ]
    else:
        radj, gadj, badj = [ val or percent for val in [radj, gadj, badj] ]

    red = min(color.Red() + radj, 255)
    green = min(color.Green() + gadj, 255)
    blue = min(color.Blue() + badj, 255)
    return wx.Colour(red, green, blue, alpha)

def HexToRGB(hex_str):
    """Returns a list of red/green/blue values from a
    hex string.
    @param hex_str: hex string to convert to rgb

    """
    hexval = hex_str
    if hexval[0] == u"#":
        hexval = hexval[1:]
    ldiff = 6 - len(hexval)
    hexval += ldiff * u"0"
    # Convert hex values to integer
    red = int(hexval[0:2], 16)
    green = int(hexval[2:4], 16)
    blue = int(hexval[4:], 16)
    return [red, green, blue]

def SetWindowIcon(window):
    """Sets the given windows icon to be the programs
    application icon.
    @param window: window to set app icon for

    """
    try:
        if wx.Platform == "__WXMSW__":
            ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.ico"
            window.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_ICO))
        else:
            ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.png"
            window.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_PNG))
    finally:
        pass

#-----------------------------------------------------------------------------#

class IntValidator(wx.PyValidator):
    """A Generic integer validator"""
    def __init__(self, min_=0, max_=0):
        """Initialize the validator
        @keyword min: min value to accept
        @keyword max: max value to accept

        """
        wx.PyValidator.__init__(self)
        self._min = min_
        self._max = max_

        # Event managment
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """Clones the current validator
        @return: clone of this object

        """
        return IntValidator(self._min, self._max)

    def Validate(self, win):
        """Validate an window value
        @param win: window to validate

        """
        val = win.GetValue()
        return val.isdigit()

    def OnChar(self, event):
        """Process values as they are entered into the control
        @param event: event that called this handler

        """
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or \
           key > 255 or chr(key) in '0123456789':
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        return
