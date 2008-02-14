###############################################################################
# Name: cbrowser.py                                                           #
# Purpose: ClassBrowser UI                                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE:
AUTHOR:
LANGUAGE: Python
SUMMARY:

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import StringIO
import wx

# Editra Libraries
import ed_glob
from profiler import Profile_Get, Profile_Set
import ed_msg
import syntax.synglob as synglob

# Local Imports
import gentag.taglib as taglib
import gentag.pytags as pytags
import gentag.shtags as shtags
import IconFile

#--------------------------------------------------------------------------#
# Globals
ID_CLASSBROWSER = wx.NewId()
ID_BROWSER = wx.NewId()
PANE_NAME = u"ClassBrowser"

SHELL_IDS = [synglob.ID_LANG_BASH, synglob.ID_LANG_KSH, synglob.ID_LANG_CSH]

#--------------------------------------------------------------------------#

class ClassBrowserTree(wx.TreeCtrl):
    def __init__(self, parent, id=ID_BROWSER,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._mw = parent
        self.icons = dict()
        self.il = None

        # Setup
        self._SetupImageList()
        viewm = self._mw.GetMenuBar().GetMenuByName("view")
        self._mi = viewm.InsertAlpha(ID_CLASSBROWSER, _("Class Browser"), 
                                     _("Open Class Browser Sidepanel"),
                                     wx.ITEM_CHECK,
                                     after=ed_glob.ID_PRE_MARK)

        self.root = self.AddRoot('ClassBrowser')
        self.SetPyData(self.root, None)
        self.SetItemImage(self.root, self.icons['class'], wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, self.icons['class'], wx.TreeItemIcon_Expanded)
        self.nodes = dict(globals=None, classes=None, funct=None)

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated)
        ed_msg.Subscribe(self.OnUpdateTree, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnUpdateTree, ed_msg.EDMSG_FILE_OPENED)
        ed_msg.Subscribe(self.OnUpdateTree, ed_msg.EDMSG_FILE_SAVED)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnUpdateTree)

    def _GetCurrentCtrl(self):
        """Get the current buffer"""
        return self._mw.GetNotebook().GetCurrentCtrl()

    def _SetupImageList(self):
        """Setup the image list for the tree"""
        imglst = wx.ImageList(16, 16)
        if Profile_Get('ICONS', 'Default') != 'Default':
            globe = wx.ArtProvider.GetBitmap(str(ed_glob.ID_WEB), wx.ART_MENU)
            self.icons['globals'] = imglst.Add(globe)
        else:
            self.icons['globals'] = imglst.Add(IconFile.GetGlobalBitmap())
        self.icons['class'] = imglst.Add(IconFile.GetBricksBitmap())
        self.icons['function'] = imglst.Add(IconFile.GetBrickGoBitmap())
        self.icons['variable'] = imglst.Add(IconFile.GetBrickBitmap())
        self.SetImageList(imglst)
        # NOTE: Must save reference to the image list or tree will crash!!!
        self.il = imglst

    def AppendClass(self, cobj):
        """Append a class node to the tree
        @param cobj: Class item object

        """
        if self.nodes['classes'] is None:
            croot = self.AppendItem(self.GetRootItem(), _("Class Definitions"))
            self.SetItemHasChildren(croot)
            self.SetPyData(croot, None)
            self.SetItemImage(croot, self.icons['class'])
            self.nodes['classes'] = croot

        croot = self.AppendItem(self.nodes['classes'], cobj.GetName())
        self.SetItemHasChildren(croot)
        self.SetPyData(croot, cobj.GetLine())
        self.SetItemImage(croot, self.icons['class'])
        for meth in cobj.GetVariables() + cobj.GetMethods():
            item = self.AppendItem(croot, meth.GetName())
            self.SetPyData(item, meth.GetLine())
            if isinstance(meth, taglib.Method):
                self.SetItemImage(item, self.icons['function'])
            else:
                self.SetItemImage(item, self.icons['variable'])

    def AppendGlobal(self, gobj):
        """Append a global variable/object to the Globals node
        @param gobj: Object derived from Scope

        """
        if self.nodes['globals'] is None:
            self.nodes['globals']  = self.AppendItem(self.GetRootItem(),
                                                     _("Global Variables"))
            self.SetItemHasChildren(self.nodes['globals'])
            self.SetPyData(self.nodes['globals'], None)
            self.SetItemImage(self.nodes['globals'], self.icons['globals'])

        item = self.AppendItem(self.nodes['globals'], gobj.GetName())
        self.SetPyData(item, gobj.GetLine())
        self.SetItemImage(item, self.icons['variable'])

    def AppendFunction(self, sobj):
        """Append a toplevel function to the tree
        @param sobj: Code object derived from Scope

        """
        if self.nodes['funct'] is None:
            froot = self.AppendItem(self.GetRootItem(),
                                    _("Function Definitions"))
            self.SetItemHasChildren(froot)
            self.SetPyData(froot, None)
            self.SetItemImage(froot, self.icons['function'])
            self.nodes['funct'] = froot

        croot = self.AppendItem(self.nodes['funct'], sobj.GetName())
        self.SetPyData(croot, sobj.GetLine())
        self.SetItemImage(croot, self.icons['function'])

    def DeleteChildren(self, item):
        """Delete the children of a given node"""
        wx.TreeCtrl.DeleteChildren(self, item)
        self.nodes['globals'] = None
        self.nodes['classes'] = None
        self.nodes['funct'] = None

    def OnActivated(self, evt):
        """Handle when an item is clicked on
        @param evt: wx.TreeEvent

        """
        line = self.GetItemPyData(evt.GetItem())
        if line is not None:
            ctrl = self._mw.GetNotebook().GetCurrentCtrl()
            ctrl.GotoLine(line)
            ctrl.SetFocus()

    def OnUpdateTree(self, msg):
        page = self._GetCurrentCtrl()
        lang_id = page.GetLangId()
        if lang_id == synglob.ID_LANG_PYTHON:
            tags = pytags.GenerateTags(StringIO.StringIO(page.GetText()))
        elif lang_id in SHELL_IDS:
            tags = shtags.GenerateTags(StringIO.StringIO(page.GetText()))
        else:
            self.DeleteChildren(self.root)
            return

        self.UpdateAll(tags)

    def OnShowBrowser(self, evt):
        if evt.GetId() == ID_CLASSBROWSER:
            mgr = self._mw.GetFrameManager()
            pane = mgr.GetPane(PANE_NAME)
            if pane.IsShown():
                pane.Hide()
#                Profile_Set('SHOW_FB', False)
            else:
                pane.Show()
#                Profile_Set('SHOW_FB', True)
            mgr.Update()
        else:
            evt.Skip()

    def UpdateAll(self, tags):
        """Update the entire tree
        @param tags: DocStruct object

        """
        self.DeleteChildren(self.root)
        for var in tags.GetVariables():
            self.AppendGlobal(var)

        for cls in tags.GetClasses():
            self.AppendClass(cls)

        for fun in tags.GetFunctions():
            self.AppendFunction(fun)

#--------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    import StringIO
    import gentag.pytags as pytags
    fhandle = open(__file__)
    txt = fhandle.read()
    fhandle.close()
    tags = pytags.GenerateTags(StringIO.StringIO(txt))

    app = wx.App(False)
    frame = wx.Frame(None, title="ClassBrowser Test")
    tree = ClassBrowserTree(frame)

    for fun in tags.GetFunctions():
        tree.AppendStatement(fun)

    for cls in tags.GetClasses():
        tree.AppendClass(cls)

    frame.Show()
    app.MainLoop()
