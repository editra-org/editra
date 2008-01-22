###############################################################################
# Name: ed_mdlg.py                                                            #
# Purpose: Commonly used message dialogs                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: ed_msg.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
  This module provides a number of message dialogs that are commonly used
throughout Editra. Its purpose is to promote reuse of the common dialogs for
consistancy and reduction in redundant code.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx

#--------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

def SaveErrorDlg(parent, fname, err):
    """Show a file save error modal dialog
    @param parent: window that the dialog is the child of
    @param fname: name of file that error occured
    @param err: the err message/description
    @return: wxID_OK if dialog was shown and dismissed properly

    """
    dlg = wx.MessageDialog(parent, _("Failed to save file: %s\n\nError:\n%s") %\
                           (fname, err), _("Save Error"), wx.OK|wx.ICON_ERROR)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result
