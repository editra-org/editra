###############################################################################
# Name: ed_mpane.py                                                           #
# Purpose: Main panel containing notebook and command bar.                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This module provides the L{MainPanel} component. That contains the editors main
notebook and command bar. 

@summary: Main Panel

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import ed_pages
import ed_cmdbar
import eclib.ctrlbox as ctrlbox

#-----------------------------------------------------------------------------#

class MainPanel(ctrlbox.ControlBox):
    """Main panel view"""
    def __init__(self, parent):
        """Initialize the panel"""
        ctrlbox.ControlBox.__init__(self, parent)

        # Attributes
        self.nb = ed_pages.EdPages(self, wx.ID_ANY)
        self._cmdbar = ed_cmdbar.CommandBar(self, ed_glob.ID_COMMAND_BAR)

        # Layout
        self.SetWindow(self.nb)
        self.SetControlBar(self._cmdbar, wx.BOTTOM)

    def HideCommandBar(self):
        """Hide the command bar"""
        self._cmdbar.Hide()
        self.Layout()

    def ShowCommandControl(self, ctrlid):
        """Change the mode of the commandbar
        @param ctrlid: CommandBar control id

        """
        ctrld = { ed_glob.ID_QUICK_FIND : ed_cmdbar.ID_SEARCH_CTRL,
                  ed_glob.ID_GOTO_LINE : ed_cmdbar.ID_LINE_CTRL,
                  ed_glob.ID_COMMAND : ed_cmdbar.ID_CMD_CTRL }

        if ctrlid in ctrld:
            self._cmdbar.Show(ctrld[ctrlid])

        self.Layout()
