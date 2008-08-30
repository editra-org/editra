###############################################################################
# Name: ed_pages.py                                                           #
# Purpose: The main editor notebook                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This file defines the notebook for containing the text controls for
for editing text in Editra. The note book is a custom sublclass of
FlatNotebook that allow for automatic page images and drag and dropping
of tabs between open editor windows. The notebook is also primarly in
charge of opening files that are requested by the user and setting up the
text control to use them. For more information on the text controls used
in the notebook see ed_stc.py

@summary: Editra's main notebook class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import glob
import wx

# Editra Libraries
import ed_glob
from profiler import Profile_Get
import ed_stc
import syntax.synglob as synglob
import syntax.syntax as syntax
import ed_search
import util
import doctools
import ed_msg
import ed_txt
import ed_mdlg
import ed_menu
import eclib.encdlg as encdlg
from extern import flatnotebook as FNB

#--------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class EdPages(FNB.FlatNotebook):
    """Editras editor buffer botebook
    @todo: allow for tab styles to be configurable (maybe)

    """
    def __init__(self, parent, id_num):
        """Initialize a notebook with a blank text control in it
        @param parent: parent window of the notebook
        @param id_num: this notebooks id

        """
        FNB.FlatNotebook.__init__(self, parent, id_num,
                                  style=FNB.FNB_FF2 |
                                        FNB.FNB_X_ON_TAB |
                                        FNB.FNB_SMART_TABS |
                                        FNB.FNB_BACKGROUND_GRADIENT |
                                        FNB.FNB_DROPDOWN_TABS_LIST |
                                        FNB.FNB_ALLOW_FOREIGN_DND
                            )

        # Notebook attributes
        self.LOG = wx.GetApp().GetLog()
        self._searchctrl = ed_search.SearchController(self, self.GetCurrentCtrl)
        self.DocMgr = doctools.DocPositionMgr(ed_glob.CONFIG['CACHE_DIR'] + \
                                              os.sep + u'positions')
        self.pg_num = -1              # Track new pages (aka untitled docs)
        self.control = None
        self.frame = self.GetTopLevelParent() # MainWindow
        self._index = dict()          # image list index
        self._ses_load = False
        self._menu = None

        # Set Additional Style Parameters
        self.SetNonActiveTabTextColour(wx.Colour(102, 102, 102))
        ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.png"
        self.SetNavigatorIcon(wx.Bitmap(ed_icon, wx.BITMAP_TYPE_PNG))

        # Setup the ImageList and the default image
        imgl = wx.ImageList(16, 16)
        txtbmp = wx.ArtProvider.GetBitmap(str(synglob.ID_LANG_TXT), wx.ART_MENU)
        self._index[synglob.ID_LANG_TXT] = imgl.Add(txtbmp)
        self.SetImageList(imgl)

        # Notebook Events
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnUpdatePageText)
        self._pages.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnTabMenu)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Message handlers
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_NOTEBOOK)

        # Add a blank page
        self.NewPage()

    #---- End Init ----#

    def OnTabMenu(self, evt):
        """Show the tab context menu"""
        # Destroy any existing menu
        if self._menu is not None:
            self._menu.Destroy()
            self._menu = None
        cidx = self.GetSelection()
        ptxt = self.GetPageText(cidx)

        # Construct the menu
        self._menu = ed_menu.EdMenu()
        self._menu.Append(ed_glob.ID_SAVE, _("Save \"%s\"") % ptxt)
        self._menu.AppendSeparator()
        self._menu.Append(ed_glob.ID_NEW, _("New Tab"))
        self._menu.AppendSeparator()
        self._menu.Append(ed_glob.ID_CLOSE, _("Close \"%s\"") % ptxt)
        self._menu.Append(ed_glob.ID_CLOSEALL, _("Close All"))
        #self._menu.AppendSeparator()
        
        self.PopupMenu(self._menu)

    #---- Function Definitions ----#
    def _HandleEncodingError(self, control):
        """Handle trying to reload the file the file with a different encoding
        Until it suceeds or gives up.
        @param control: stc
        @return: bool

        """
        # Loop while the load fails prompting to try a new encoding
        tried = None
        fname = control.GetFileName().strip(os.sep)
        fname = fname.split(os.sep)[-1]
        while True:
            doc = control.GetDocument()
            doc.ClearLastError()
            if tried is None:
                enc = doc.GetEncoding()
                if enc is None:
                    enc = ed_txt.DEFAULT_ENCODING
            else:
                enc = tried

            msg = _("The correct encoding of '%s' could not be determined.\n\n"
                    "Choose an encoding and select Ok to open the file with the chosen encoding.\n"
                    "Click Cancel to abort opening the file") % fname
            dlg = encdlg.EncodingDialog(self, msg=msg,
                                        title=_("Choose an Encoding"),
                                        default=enc)
            dlg.CenterOnParent()
            result = dlg.ShowModal()
            enc = dlg.GetEncoding()
            dlg.Destroy()

            # Don't want to open it in another encoding
            if result == wx.ID_CANCEL:
                return False
            else:
                control.SetEncoding(enc)
                tried = enc
                ok = control.LoadFile(control.GetFileName())
                if ok:
                    return True
                else:
                    # Artifically add a short pause, because if its not there
                    # the dialog will be shown again so fast it wont seem
                    # like reloading the file was even tried.
                    wx.Sleep(1)

    def _NeedOpen(self, path):
        """Check if a file needs to be opened. If the file is already open in
        the notebook a dialog will be opened to ask if the user wants to reopen
        the file again. If the file is not open and exists or the user chooses
        to reopen the file again the function will return True else it will
        return False.
        @param path: file to check for
        @return: bool

        """
        result = wx.ID_YES
        if self.HasFileOpen(path):
            mdlg = wx.MessageDialog(self,
                                    _("File is already open in an existing "
                                      "page.\nDo you wish to open it again?"),
                                    _("Open File") + u"?",
                                    wx.YES_NO | wx.NO_DEFAULT | \
                                    wx.ICON_INFORMATION)
            result = mdlg.ShowModal()
            mdlg.Destroy()
            if result == wx.ID_NO:
                self.GotoPage(path)
        elif os.path.exists(path) and not os.path.isfile(path):
            result = wx.ID_NO
        else:
            pass

        return result == wx.ID_YES

    def GetCurrentCtrl(self):
        """Returns the control of the currently selected
        page in the notebook.
        @return: window object contained in current page or None

        """
        if hasattr(self, 'control'):
            return self.control
        else:
            return None

    def GetFileNames(self):
        """Gets the name of all open files in the notebook
        @return: list of file names

        """
        rlist = list()
        for buff in self.GetTextControls():
            fname = buff.GetFileName()
            if fname != wx.EmptyString:
                rlist.append(fname)
        return rlist

    def GetMenuHandlers(self):
        """Get the (id, evt_handler) tuples that this window should
        handle.
        @return: list of tuples

        """
        rlist = [(ed_glob.ID_FIND, self._searchctrl.OnShowFindDlg),
                 (ed_glob.ID_FIND_REPLACE, self._searchctrl.OnShowFindDlg),
                 (ed_glob.ID_FIND_NEXT, self._searchctrl.OnFind)]
        return rlist

    def GetUiHandlers(self):
        """Get the update ui handlers that this window supplies
        @return: list of tuples

        """
        return [(ed_glob.ID_FIND_NEXT, self._searchctrl.OnUpdateFindUI),]

    def LoadSessionFiles(self):
        """Load files from saved session data in profile
        @postcondition: Files saved from previous session are
                        opened. If no files were found then only a
                        single blank page is opened.

        """
        self._ses_load = True
        files = Profile_Get('LAST_SESSION')
        if files is not None:
            for fname in files:
                if os.path.exists(fname) and os.access(fname, os.R_OK):
                    self.OpenPage(os.path.dirname(fname),
                                  os.path.basename(fname))
                    self.Update() # Give feedback as files are loaded
        self._ses_load = False

        if self.GetPageCount() == 0:
            self.NewPage()

    def NewPage(self):
        """Create a new notebook page with a blank text control
        @postcondition: a new page with an untitled document is opened

        """
        self.GetTopLevelParent().Freeze()
        self.pg_num += 1
        self.control = ed_stc.EditraStc(self, wx.ID_ANY)
        self.control.SetEncoding(Profile_Get('ENCODING'))
        self.LOG("[ed_pages][evt] New Page Created ID: %d" % self.control.GetId())
        self.AddPage(self.control, u"Untitled - %d" % self.pg_num)
        self.SetPageImage(self.GetSelection(), str(self.control.GetLangId()))

        # Set the control up the the preferred default lexer
        dlexer = Profile_Get('DEFAULT_LEX', 'str', 'Plain Text')
        ext_reg = syntax.ExtensionRegister()
        ext_lst = ext_reg.get(dlexer, ['txt', ])
        self.control.FindLexer(ext_lst[0])
        self.GetTopLevelParent().Thaw()

    def OnThemeChanged(self, msg):
        """Update icons when the theme has changed
        @param msg: Message Object

        """
        self.UpdateAllImages()

    def OpenPage(self, path, filename, quiet=False):
        """Open a File Inside of a New Page
        @param path: files base path
        @param filename: name of file to open
        @keyword quiet: Open/Switch to the file quietly if
                        it is already open.

        """
        path2file = os.path.join(path, filename)

        # Check if file needs to be opened
        # TODO: these steps could be combined together with some
        #       refactoring of the _NeedOpen method. Requires extra
        #       testing though to check for dependancies on current
        #       behavior.
        if quiet and self.HasFileOpen(path2file):
            self.GotoPage(path2file)
            return
        elif not self._NeedOpen(path2file):
            return

        # Create new control to place text on if necessary
        self.GetTopLevelParent().Freeze()
        new_pg = True
        if self.GetPageCount():
            if self.control.GetModify() or self.control.GetLength() or \
               self.control.GetFileName() != u'':
                control = ed_stc.EditraStc(self, wx.ID_ANY)
                control.Hide()
            else:
                new_pg = False
                control = self.control
        else:
            control = ed_stc.EditraStc(self, wx.ID_ANY)
            control.Hide()

        # Open file and get contents
        result = False
        if os.path.exists(path2file):
            try:
                result = control.LoadFile(path2file)
            except Exception, msg:
                self.LOG("[ed_pages][err] Failed to open file %s\n" % path2file)
                self.LOG("[ed_pages][err] %s" % msg)

                # File could not be opened/read give up
                # Don't raise a dialog during a session load error as if the
                # dialog is shown before the mainwindow is ready it can cause
                # the app to freeze.
                if not self._ses_load:
                    ed_mdlg.OpenErrorDlg(self, path2file, msg)
                control.GetDocument().ClearLastError()
                control.SetFileName('') # Reset the file name

                if new_pg:
                    control.Destroy()

                self.GetTopLevelParent().Thaw()
                return
        else:
            control.SetFileName(path2file)
            result = True

        # Check if there was encoding errors
        if not result and not self._ses_load:
            result = self._HandleEncodingError(control)

        # Cleanup after errors
        if not result:
            if new_pg:
                # We created a new one so destroy it
                control.Destroy()
            else:
                # We where using an existing buffer so reset it
                control.SetText('')
                control.SetDocument(ed_txt.EdFile())
                control.SetSavePoint()

            self.GetTopLevelParent().Thaw()
            return

        # Put control into page an place page in notebook
        if new_pg:
            control.Show()
            self.control = control

        # Setup Document
        self.control.FindLexer()
        self.control.CheckEOL()
        self.control.EmptyUndoBuffer()

        if Profile_Get('SAVE_POS'):
            self.control.GotoPos(self.DocMgr.GetPos(self.control.GetFileName()))

        # Add the buffer to the notebook
        if new_pg:
            self.AddPage(self.control, filename)

        self.frame.SetTitle("%s - file://%s" % (filename,
                                                self.control.GetFileName()))
        self.frame.AddFileToHistory(path2file)
        self.SetPageText(self.GetSelection(), filename)
        self.LOG("[ed_pages][evt] Opened Page: %s" % filename)

        # Set tab image
        self.SetPageImage(self.GetSelection(), str(self.control.GetLangId()))

        # Refocus on selected page
        self.GoCurrentPage()
        self.GetTopLevelParent().Thaw()
        ed_msg.PostMessage(ed_msg.EDMSG_FILE_OPENED, self.control.GetFileName())

    def GoCurrentPage(self):
        """Move Focus to Currently Selected Page.
        @postcondition: focus is set to current page

        """
        current_page = self.GetSelection()
        if current_page < 0:
            return current_page

        control = self.GetPage(current_page)
        control.SetFocus()
        self.control = control
        return current_page

    def GotoPage(self, fname):
        """Go to the page containing the buffer with the given file.
        @param fname: file path (string)

        """
        for page in xrange(self.GetPageCount()):
            ctrl = self.GetPage(page)
            if fname == ctrl.GetFileName():
                self.ChangePage(page)
                break

    def GetPageText(self, pg_num):
        """Gets the tab text from the given page number, stripping
        the * mark if there is one.
        @param pg_num: index of page to get tab text from
        @return: the tabs text

        """
        # Often times this raises an index error in the flatnotebook code
        # even though the pg_num here is one that is obtained by calling
        # GetSelection which should return a valid index.
        try:
            txt = FNB.FlatNotebook.GetPageText(self, pg_num)
        except IndexError:
            txt = ''

        if not txt or txt[0] != u"*":
            return txt
        return txt[1:]

    def GetTextControls(self):
        """Gets all the currently opened text controls
        @return: list containing reference to all stc controls opened in the
                 notebook.

        """
        pages = [self.GetPage(page) for page in xrange(self.GetPageCount())]
        return [page for page in pages 
                if getattr(page, '__name__', '') == "EditraTextCtrl"]

    def HasFileOpen(self, fpath):
        """Checks if one of the currently active buffers has
        the named file in it.
        @param fpath: full path of file to check
        @return: bool indicating whether file is currently open or not

        """
        for ctrl in self.GetTextControls():
            if fpath == ctrl.GetFileName():
                return True
        return False

    #---- Event Handlers ----#
    def OnDrop(self, files):
        """Opens dropped files
        @param files: list of file paths
        @postcondition: all files that could be properly opend are added to
                        the notebook

        """
        # Check file properties and make a "clean" list of file(s) to open
        valid_files = list()
        for fname in files:
            self.LOG("[ed_pages][evt] File(s) Dropped: %s" % fname)
            if not os.path.exists(fname):
                self.frame.PushStatusText(_("Invalid file: %s") % fname, \
                                          ed_glob.SB_INFO)
            elif os.path.isdir(fname):
                dcnt = glob.glob(os.path.join(fname, '*'))
                dcnt = util.FilterFiles(dcnt)
                dlg = None
                if not len(dcnt):
                    dlg = wx.MessageDialog(self,
                                           _("There are no files that Editra"
                                             " can open in %s") % fname,
                                           _("No Valid Files to Open"),
                                           style=wx.OK | wx.CENTER | \
                                                 wx.ICON_INFORMATION)
                elif len(dcnt) > 5:
                    # Warn when the folder contains many files
                    dlg = wx.MessageDialog(self,
                                           _("Do you wish to open all %d files"
                                             " in this directory?\n\nWarning"
                                             " opening many files at once may"
                                             " cause the editor to temporarly "
                                             " freeze.") % len(dcnt),
                                           _("Open Directory?"),
                                           style=wx.YES | wx.NO | \
                                                 wx.ICON_INFORMATION)
                if dlg is not None:
                    result = dlg.ShowModal()
                    dlg.Destroy()
                else:
                    result = wx.ID_YES

                if result == wx.ID_YES:
                    valid_files.extend(dcnt)
                else:
                    pass
            else:
                valid_files.append(fname)

        for fname in valid_files:
            pathname = util.GetPathName(fname)
            the_file = util.GetFileName(fname)
            self.OpenPage(pathname, the_file)
            self.frame.PushStatusText(_("Opened file: %s") % fname, \
                                      ed_glob.SB_INFO)
        return

    def OnIdle(self, evt):
        """Update tabs and check if files have been modified
        @param evt: Event that called this handler
        @type evt: wx.IdleEvent

        """
        if wx.GetApp().IsActive() and \
           Profile_Get('CHECKMOD') and self.GetPageCount():
            cfile = self.control.GetFileName()
            lmod = util.GetFileModTime(cfile)
            if self.control.GetModTime() and \
               not lmod and not os.path.exists(cfile):
                wx.CallAfter(PromptToReSave, self, cfile)
            elif self.control.GetModTime() < lmod:
                wx.CallAfter(AskToReload, self, cfile)
            else:
                return False

    def OnLeftUp(self, evt):
        """Traps clicks sent to page close buttons and
        redirects the action to the ClosePage function
        @param evt: Event that called this handler
        @type evt: wx.MouseEvent

        """
        cord = self._pages.HitTest(evt.GetPosition())[0]
        if cord == FNB.FNB_X:
            # Make sure that the button was pressed before
            if self._pages._nXButtonStatus != FNB.FNB_BTN_PRESSED:
                return
            self._pages._nXButtonStatus = FNB.FNB_BTN_HOVER
            self.ClosePage()
        elif cord == FNB.FNB_TAB_X:
            # Make sure that the button was pressed before
            if self._pages._nTabXButtonStatus != FNB.FNB_BTN_PRESSED:
                return
            self._pages._nTabXButtonStatus = FNB.FNB_BTN_HOVER
            self.ClosePage()
        else:
            evt.Skip()

    def OnPageChanging(self, evt):
        """Page changing event handler.
        @param evt: event that called this handler
        @type evt: flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGING

        """
        evt.Skip()
        pages = (evt.GetOldSelection(), evt.GetSelection())
        self.LOG("[ed_pages][evt] Control Changing from Page: "
                  "%d to Page: %d\n" % pages)
        ed_msg.PostMessage(ed_msg.EDMSG_UI_NB_CHANGING, (self,) + pages)

    def ChangePage(self, pg_num):
        """Change the page and focus to the the given page id
        @param pg_num: Page number to change 

        """
        if self.GetSelection() != pg_num:
            self.SetSelection(pg_num)

        # Get the window that is the current page
        window = self.GetPage(pg_num)
        window.SetFocus()
        self.control = window
        fname = self.control.GetFileName()

        # Update Frame Title
        if fname == "":
            fname = self.GetPageText(pg_num)
        self.frame.SetTitle("%s - file://%s" % (util.GetFileName(fname), fname))
        if not self.frame.IsExiting():
            ed_msg.PostMessage(ed_msg.EDMSG_UI_NB_CHANGED, (self, pg_num))

    def OnPageChanged(self, evt):
        """Actions to do after a page change
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED

        """
        cpage = evt.GetSelection()
        self.ChangePage(cpage)
        evt.Skip()
        self.LOG("[ed_pages][evt] Page Changed to %d" % cpage)
        self.LOG("[ed_pages][info] It has file named: %s" % \
                 self.control.GetFileName())
        self.control.PostPositionEvent()
        self.EnsureVisible(cpage)

    def OnPageClosing(self, evt):
        """Checks page status to flag warnings before closing
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING

        """
        self.LOG("[ed_pages][evt] Closing Page: #%d" % self.GetSelection())
        page = self.GetCurrentPage()
        if len(page.GetFileName()) > 1:
            self.DocMgr.AddRecord([page.GetFileName(), page.GetCurrentPos()])
        evt.Skip()
        ed_msg.PostMessage(ed_msg.EDMSG_UI_NB_CLOSING,
                           (self, self.GetSelection()))

    def OnPageClosed(self, evt):
        """Handles Paged Closed Event
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSED

        """
        cpage = self.GetSelection()
        evt.Skip()
        self.LOG("[ed_pages][evt] Closed Page: #%d" % cpage)
        ed_msg.PostMessage(ed_msg.EDMSG_UI_NB_CLOSED, (self, cpage))

    #---- End Event Handlers ----#

    def CloseAllPages(self):
        """Closes all open pages
        @postcondition: all pages in the notebook are closed

        """
        for page in xrange(self.GetPageCount()):
            result = self.ClosePage()
            if result == wx.ID_CANCEL:
                break

    def ClosePage(self):
        """Closes Currently Selected Page
        @postcondition: currently selected page is closed

        """
        self.GoCurrentPage()
        pg_num = self.GetSelection()
        result = wx.ID_OK

        if self.control.GetModify():
            result = self.frame.ModifySave()
            if result != wx.ID_CANCEL:
                self.DeletePage(pg_num)
                self.GoCurrentPage()
            else:
                pass
        else:
            self.DeletePage(pg_num)
            self.GoCurrentPage()

        # TODO this causes some flashing
        frame = self.GetTopLevelParent()
        if not self.GetPageCount() and \
           hasattr(frame, 'IsExiting') and not frame.IsExiting():
            self.NewPage()
        return result

    def SetPageImage(self, pg_num, lang_id):
        """Sets the page image by querying the ArtProvider based
        on the language id associated with the type of open document.
        Any unknown filetypes are associated with the plaintext page
        image.
        @param pg_num: page index to set image for
        @param lang_id: language id of file type to get mime image for

        """
        if not Profile_Get('TABICONS'):
            return

        imglst = self.GetImageList()
        if not self._index.has_key(lang_id):
            bmp = wx.ArtProvider.GetBitmap(lang_id, wx.ART_MENU)
            if bmp.IsNull():
                self._index.setdefault(lang_id, \
                                       self._index[synglob.ID_LANG_TXT])
            else:
                self._index[lang_id] = imglst.Add(wx.ArtProvider.\
                                              GetBitmap(lang_id, wx.ART_MENU))
        FNB.FlatNotebook.SetPageImage(self, pg_num, self._index[lang_id])

    def UpdateAllImages(self):
        """Reload and Reset all images in the notebook pages and
        the corresponding imagelist to match those of the current theme
        @postcondition: all images in control are updated

        """
        if not Profile_Get('TABICONS'):
            for page in xrange(self.GetPageCount()):
                FNB.FlatNotebook.SetPageImage(self, page, -1)
        else:
            imglst = self.GetImageList()
            for lang, index in self._index.iteritems():
                bmp = wx.ArtProvider.GetBitmap(str(lang), wx.ART_MENU)
                if bmp.IsNull():
                    self._index.setdefault(lang, \
                                           self._index[synglob.ID_LANG_TXT])
                else:
                    imglst.Replace(index, bmp)

            for page in xrange(self.GetPageCount()):
                self.SetPageImage(page, str(self.GetPage(page).GetLangId()))

        self.Refresh()

    def UpdatePageImage(self):
        """Updates the page tab image
        @postcondition: page image is updated to reflect any changes in ctrl

        """
        self.SetPageImage(self.GetSelection(), str(self.control.GetLangId()))

    def OnUpdatePageText(self, evt):
        """Update the title text of the current page
        @param evt: event that called this handler
        @type evt: stc.EVT_STC_MODIFY (unused)
        @note: this method must complete its work very fast it gets
               called everytime a character is entered or removed from
               the document.

        """
        try:
            e_id = evt.GetId()
            if self.control.GetId() == e_id:
                pg_num = self.GetSelection()
                title = self.GetPageText(pg_num)
                if self.control.GetModify():
                    title = u"*" + title

                # Only Update if the text has changed
                if title != FNB.FlatNotebook.GetPageText(self, pg_num):
                    self.SetPageText(pg_num, title)
                    ftitle = u"%s - file://%s" % (title, self.control.GetFileName())
                    self.frame.SetTitle(ftitle)
            else:
                # A background page has changed
                for page in range(self.GetPageCount()):
                    control = self.GetPage(page)
                    if control.GetId() == e_id:
                        title = self.GetPageText(page)
                        if control.GetModify():
                            title = u"*" + title
                        if title != FNB.FlatNotebook.GetPageText(self, page):
                            self.SetPageText(page, title)
        except wx.PyDeadObjectError:
            pass

    def UpdateTextControls(self, meth=None, args=list()):
        """Updates all text controls to use any new settings that have
        been changed since initialization.
        @postcondition: all stc controls in the notebook are reconfigured
                        to match profile settings

        """
        for control in self.GetTextControls():
            if meth is not None:
                getattr(control, meth)(*args)
            else:
                control.UpdateAllStyles()
                control.Configure()

#---- End Function Definitions ----#

#-----------------------------------------------------------------------------#

#---- Utility Function Definitions ----#
def PromptToReSave(win, cfile):
    """Show a dialog prompting to resave the current file
    @param win: Window to prompt dialog on top of
    @param cfile: the file in question

    """
    mdlg = wx.MessageDialog(win.frame,
                            _("%s has been deleted since its "
                              "last save point.\n\nWould you "
                              "like to save it again?") % cfile,
                            _("Resave File?"),
                            wx.YES_NO | wx.ICON_INFORMATION)
    mdlg.CenterOnParent()
    result = mdlg.ShowModal()
    mdlg.Destroy()
    if result == wx.ID_YES:
        result = win.control.SaveFile(cfile)
    else:
        win.control.SetModTime(0)

def AskToReload(win, cfile):
    """Show a dialog asking if the file should be reloaded
    @param win: Window to prompt dialog on top of
    @param cfile: the file to prompt for a reload of

    """
    mdlg = wx.MessageDialog(win.frame,
                            _("%s has been modified by another "
                              "application.\n\nWould you like "
                              "to Reload it?") % cfile,
                              _("Reload File?"),
                              wx.YES_NO | wx.ICON_INFORMATION)
    mdlg.CenterOnParent()
    result = mdlg.ShowModal()
    mdlg.Destroy()
    if result == wx.ID_YES:
        ret, rmsg = win.control.ReloadFile()
        if not ret:
            errmap = dict(filename=cfile, errmsg=rmsg)
            mdlg = wx.MessageDialog(win.frame,
                                    _("Failed to reload %(filename)s:\n"
                                      "Error: %(errmsg)s") % errmap,
                                    _("Error"),
                                    wx.OK | wx.ICON_ERROR)
            mdlg.ShowModal()
            mdlg.Destroy()
    else:
        win.control.SetModTime(util.GetFileModTime(cfile))
