###############################################################################
# Name: ed_mdlg.py                                                            #
# Purpose: Commonly used message dialogs                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
This module provides a number of message dialogs that are commonly used
throughout Editra. Its purpose is to promote reuse of the common dialogs for
consistancy and reduction in redundant code.

@summary: Common dialogs and related convenience functions

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

def OpenErrorDlg(parent, fname, err):
    """Show a file open error dialog
    @param parent: parent window
    @param fname: file that failed to open
    @param err: error message

    """
    argmap = dict(filename=fname, errormsg=err)
    dlg = wx.MessageDialog(parent,
                           _("Editra could not open %(filename)s\n\n"
                             "Error:\n%(errormsg)s") % \
                           argmap, _("Error Opening File"),
                           style=wx.OK|wx.CENTER|wx.ICON_ERROR)
    dlg.CenterOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    return result

def SaveErrorDlg(parent, fname, err):
    """Show a file save error modal dialog
    @param parent: window that the dialog is the child of
    @param fname: name of file that error occured
    @param err: the err message/description
    @return: wxID_OK if dialog was shown and dismissed properly

    """
    argmap = dict(filename=fname, errormsg=err)
    dlg = wx.MessageDialog(parent,
                           _("Failed to save file: %(filename)s\n\n"
                             "Error:\n%(errormsg)s") % argmap,
                           _("Save Error"), wx.OK|wx.ICON_ERROR)
    dlg.CenterOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    return result
