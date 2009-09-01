###############################################################################
# Name: demo.py                                                               #
# Purpose: main demo launcher                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library Demo / Test Application

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import wx
import wx.aui as aui

#-----------------------------------------------------------------------------#
# TODO
sys.path.insert(0, os.path.abspath('../../'))
import src.eclib as eclib
import IconFile

#-----------------------------------------------------------------------------#

class EclibDemoApp(wx.App):
    def OnInit(self):
        self.SetAppName("Eclib Demo")

        # Attributes
        self.frame = EclibDemoFrame("Eclib Demo")

        # Setup
        self.frame.Show()

        return True

#-----------------------------------------------------------------------------#

class EclibDemoFrame(wx.Frame):
    """Demo Main Window"""
    def __init__(self, title=u""):
        wx.Frame.__init__(self, None, title=title)

        # Attributes
        self.mgr = aui.AuiManager(self,
                                  aui.AUI_MGR_TRANSPARENT_HINT|\
                                  aui.AUI_MGR_ALLOW_ACTIVE_PANE|\
                                  aui.AUI_MGR_LIVE_RESIZE)
        self.tree = EclibDemoTree(self)
        self.pane = EclibDemoPanel(self)
        self._loader = ModuleLoader(FindDemoModules(os.path.abspath('.')))

        # Setup
        self.mgr.AddPane(self.tree,
                         aui.AuiPaneInfo().Left().Layer(0).\
                             Caption("Demos").CloseButton(False).\
                             MinSize((250,-1)))
        self.mgr.AddPane(self.pane,
                         aui.AuiPaneInfo().CenterPane().\
                             Layer(1).CloseButton(False))
        self.mgr.Update()

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSel)

    def OnTreeSel(self, evt):
        item = evt.GetItem()
        name = self.tree.GetItemText(item)
        module = self._loader.GetModule(name)
        if module:
            pane = module.TestPanel(self, TestLog())
            pi = self.mgr.AddPane(pane,
                                  aui.AuiPaneInfo().Center().\
                                      Layer(1).CloseButton(False).\
                                      Caption(name))
            self.mgr.DetachPane(self.pane)
            self.pane.Hide()
            self.pane.Destroy()
            self.pane = pane
            self.mgr.Update()

#-----------------------------------------------------------------------------#

class EclibDemoPanel(wx.Panel):
    """Main Window display panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes
        
        # Setup
        
        # Layout
        self.__DoLayout()

        # Event Handlers
        

    def __DoLayout(self):
        """Layout the panel"""
        

#-----------------------------------------------------------------------------#

class EclibDemoTree(wx.TreeCtrl):
    """Tree to show all demo modules"""
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent,
                             style=wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT)

        # Attributes
        self.root = self.AddRoot("Demos")

        # Setup
        self.PopulateTree()

        # Event Handlers

    def PopulateTree(self):
        modules = FindDemoModules(os.path.abspath('.'))
        for label, path in modules:
            item = self.AppendItem(self.root, label)
            self.SetItemPyData(item, path)

#-----------------------------------------------------------------------------#

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#-----------------------------------------------------------------------------#

class ModuleLoader(object):
    """Dynamic module loader cache"""
    _loaded = dict()
    def __init__(self, modules):
        """@param modules: list of tuples [(name, path),]"""
        object.__init__(self)

        # Attributes
        self.modules = modules

    def GetModule(self, modname):
        """

        """
        self.LoadModule(modname)
        if modname in ModuleLoader._loaded:
            return ModuleLoader._loaded[modname]

        return None

    def IsModLoaded(self, modname):
        """Checks if a module has already been loaded
        @param modname: name of module to lookup

        """
        if modname in sys.modules or modname in ModuleLoader._loaded:
            return True
        else:
            return False

    def LoadModule(self, modname):
        """Dynamically loads a module by name. The loading is only
        done if the modules data set is not already being managed

        """
        if modname == None:
            return False

        if not self.IsModLoaded(modname):
            try:
                ModuleLoader._loaded[modname] = __import__(modname, globals(), 
                                                         locals(), [''])
            except ImportError:
                return False
        return True

#-----------------------------------------------------------------------------#

def FindDemoModules(path):
    """Find all demo modules under the given path
    @param path: string
    @return: list of tuples [(filename, fullpath)]

    """
    demos = list()
    for demo in os.listdir(path):
        if demo.endswith('Demo.py'):
            demos.append((demo[:-3], os.path.join(path, demo)))
    return demos

#-----------------------------------------------------------------------------#

def Main():
    app = EclibDemoApp(False)
    app.MainLoop()

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    Main()
