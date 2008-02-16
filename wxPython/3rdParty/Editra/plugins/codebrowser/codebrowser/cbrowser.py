###############################################################################
# Name: cbrowser.py                                                           #
# Purpose: CodeBrowser UI                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: cbrowser.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
    CodeBrowser UI

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
from tagload import TagLoader

import IconFile

#--------------------------------------------------------------------------#
# Globals
ID_CODEBROWSER = wx.NewId()
ID_BROWSER = wx.NewId()
PANE_NAME = u"CodeBrowser"

#--------------------------------------------------------------------------#

class CodeBrowserTree(wx.TreeCtrl):
    def __init__(self, parent, id=ID_BROWSER,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._mw = parent
        self._cdoc = None   # Current DocStruct
        self.icons = dict()
        self.il = None

        # Setup
        self._SetupImageList()
        viewm = self._mw.GetMenuBar().GetMenuByName("view")
        self._mi = viewm.InsertAlpha(ID_CODEBROWSER, _("Code Browser"), 
                                     _("Open Code Browser Sidepanel"),
                                     wx.ITEM_CHECK,
                                     after=ed_glob.ID_PRE_MARK)

        self.root = self.AddRoot('CodeBrowser')
        self.SetPyData(self.root, None)
        self.SetItemImage(self.root, self.icons['class'])
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

    def _ShouldUpdate(self):
        """Check whether the tree should do an update or not
        @return: bool

        """
        pane = self._mw.GetFrameManager().GetPane(PANE_NAME)
        if self._mw.IsExiting() or not pane.IsShown():
            return False
        else:
            return True

    def AppendClass(self, cobj):
        """Append a class node to the tree
        @param cobj: Class item object

        """
        if self.nodes.get('classes', None) is None:
            croot = self.AppendItem(self.GetRootItem(), _("Class Definitions"))
            self.SetItemHasChildren(croot)
            self.SetPyData(croot, None)
            self.SetItemImage(croot, self.icons['class'])
            self.nodes['classes'] = croot

        croot = self.AppendCodeObj(self.nodes['classes'], cobj, self.icons['class'])
#        self.SetItemHasChildren(croot)
#        for meth in cobj.GetElements():
#            if isinstance(meth, taglib.Method):
#                img = self.icons['function']
#            else:
#                img = self.icons['variable']
#            self.AppendCodeObj(croot, meth, img)

    def AppendCodeObj(self, node, cobj, img):
        """Append a code object to the given node and set its data
        @param node: node to attach object to
        @param cobj: code object
        @return: tree item id

        """
        item_id = self.AppendItem(node, cobj.GetName(), img)
        self.SetPyData(item_id, cobj.GetLine())
        # If the item is a scope it may have sub items
        if isinstance(cobj, taglib.Scope):
            elements = cobj.GetElements()
            if len(elements):
                self.SetItemHasChildren(item_id)
                for elem in elements: # Ordered list of dict objects
                    img = self.icons.get(elem.keys()[0], None) # one key each
                    if img is None:
                        img = self.icons['variable']
                    for otype in elem[elem.keys()[0]]:
                        item = self.AppendItem(item_id, otype.GetName(), img)
                        self.SetPyData(item, otype.GetLine())
        return item_id

    def AppendGlobal(self, gobj):
        """Append a global variable/object to the Globals node
        @param gobj: Object derived from Scope

        """
        if self.nodes.get('globals', None) is None:
            self.nodes['globals']  = self.AppendItem(self.GetRootItem(),
                                                     _("Global Variables"))
            self.SetItemHasChildren(self.nodes['globals'])
            self.SetPyData(self.nodes['globals'], None)
            self.SetItemImage(self.nodes['globals'], self.icons['globals'])

        self.AppendCodeObj(self.nodes['globals'], gobj, self.icons['variable'])

    def AppendElement(self, obj):
        """Append a general code object to the document
        @param obj: Code object

        """
        # Check if there is a node for this Code object
        if self.nodes.get(obj.type, None) is None:
            # Look for a description to use as catagory title
            if self._cdoc is not None:
                desc = self._cdoc.GetElementDescription(obj.type).title()
            else:
                desc = obj.type.title()

            self.nodes[obj.type] = self.AppendItem(self.GetRootItem(), desc,
                                                   self.icons['variable'])
            self.SetItemHasChildren(self.nodes[obj.type])
            self.SetPyData(self.nodes[obj.type], None)

        self.AppendCodeObj(self.nodes[obj.type], obj, self.icons['variable'])

    def AppendFunction(self, sobj):
        """Append a toplevel function to the tree
        @param sobj: Code object derived from Scope

        """
        if self.nodes.get('function', None) is None:
            froot = self.AppendItem(self.GetRootItem(),
                                    _("Function Definitions"),
                                    self.icons['function'])
            self.SetPyData(froot, None)
            self.SetItemHasChildren(froot)
            self.nodes['function'] = froot

        self.AppendCodeObj(self.nodes['function'], sobj, self.icons['function'])

    def DeleteChildren(self, item):
        """Delete the children of a given node"""
        wx.TreeCtrl.DeleteChildren(self, item)
        for key in self.nodes.keys():
            self.nodes[key] = None

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
        """Update the tree when an action message is sent
        @param msg: Message Obect

        """
        page = self._GetCurrentCtrl()
        genfun = TagLoader.GetGenerator(page.GetLangId())
        if genfun is not None and self._ShouldUpdate():
            tags = genfun(StringIO.StringIO(page.GetText()))
            self.UpdateAll(tags)
        else:
            self._cdoc = None
            self.DeleteChildren(self.root)
            return

    def OnShowBrowser(self, evt):
        """Show the browser pane
        @param evt: wx.MenuEvent

        """
        if evt.GetId() == ID_CODEBROWSER:
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
        self._cdoc = tags
        self.DeleteChildren(self.root)
        # Check and add any common types in the document first

        # Global Variables
        for var in tags.GetVariables():
            self.AppendGlobal(var)

        # Class Definitions
        for cls in tags.GetClasses():
            self.AppendClass(cls)

        # Function Definitions
        for fun in tags.GetFunctions():
            self.AppendFunction(fun)

        # Check for any remaining custom types of code objects to add
        for element in tags.GetElements():
            print "ELEMENT: ", element
            for elem in element.values():
                print "KEYS:", element.keys(), elem
                if element.keys()[0] not in ['class', 'function', 'variable']:
                    for item in elem:
                        self.AppendElement(item)

#--------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    import gentag.pytags as pytags
    fhandle = open(__file__)
    txt = fhandle.read()
    fhandle.close()
    tags = pytags.GenerateTags(StringIO.StringIO(txt))

    app = wx.App(False)
    frame = wx.Frame(None, title="CodeBrowser Test")
    tree = CodeBrowserTree(frame)

    for fun in tags.GetFunctions():
        tree.AppendStatement(fun)

    for cls in tags.GetClasses():
        tree.AppendClass(cls)

    frame.Show()
    app.MainLoop()
