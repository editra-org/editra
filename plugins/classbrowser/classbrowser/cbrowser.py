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
import ed_msg
import syntax.synglob as synglob

# Local Imports
import gentag.pytags as pytags

#--------------------------------------------------------------------------#
# Globals
ID_CLASSBROWSER = wx.NewId()
ID_BROWSER = wx.NewId()
PANE_NAME = u"ClassBrowser"

#--------------------------------------------------------------------------#

class ClassBrowserTree(wx.TreeCtrl):
    def __init__(self, parent, id=ID_BROWSER,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._mw = parent
        self.root = self.AddRoot('ClassBrowser')
        self.SetPyData(self.root, None)

        # Setup
        viewm = self._mw.GetMenuBar().GetMenuByName("view")
        self._mi = viewm.InsertAlpha(ID_CLASSBROWSER, _("Class Browser"), 
                                     _("Open Class Browser Sidepanel"),
                                     wx.ITEM_CHECK,
                                     after=ed_glob.ID_PRE_MARK)

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

    def AppendClass(self, cobj):
        """Append a class node to the tree
        @param cobj: Class item object

        """
        croot = self.AppendItem(self.GetRootItem(), cobj.GetName())
        self.SetPyData(croot, cobj.GetLine())
        for meth in cobj.GetMethods():
            item = self.AppendItem(croot, meth.GetName())
            self.SetPyData(item, meth.GetLine())

    def AppendStatement(self, sobj):
        """Append a toplevel item to the tree
        @param sobj: Code object derived from Scope

        """
        croot = self.AppendItem(self.GetRootItem(), sobj.GetName())
        self.SetPyData(croot, sobj.GetLine())

    def OnActivated(self, evt):
        """Handle when an item is clicked on
        @param evt: wx.TreeEvent

        """
        line = self.GetItemPyData(evt.GetItem())
        ctrl = self._mw.GetNotebook().GetCurrentCtrl()
        ctrl.GotoLine(line)
        ctrl.SetFocus()

    def OnUpdateTree(self, msg):
        page = self._GetCurrentCtrl()
        if page.GetLangId() == synglob.ID_LANG_PYTHON:
            tags = pytags.GenerateTags(StringIO.StringIO(page.GetText()))
            self.UpdateAll(tags)
        else:
            self.DeleteChildren(self.root)

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
        for fun in tags.GetFunctions():
            self.AppendStatement(fun)

        for cls in tags.GetClasses():
            self.AppendClass(cls)

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
