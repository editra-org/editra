###############################################################################
# Name: elistctrl.py                                                          #
# Purpose: Base ListCtrl                                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: EListCtrl

Class EBaseListCtrl:
Base Report mode ListCtrl class that highlights alternate rows

Class ECheckListCtrl:
Child class of L{EBaseListCtrl} that also provides CheckBoxes in the first
column of the control.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: $"
__revision__ = "$Revision: $"

__all__ = ["EBaseListCtrl", "ECheckListCtrl"]

#--------------------------------------------------------------------------#
# Dependencies
import wx
import wx.lib.mixins.listctrl as listmix

# Local Imports
import elistmix

#--------------------------------------------------------------------------#

class EBaseListCtrl(elistmix.ListRowHighlighter,
                    wx.ListCtrl):
    """Base listctrl class that provides automatic row highlighting"""
    def __init__(self, parent, _id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.LC_REPORT, validator=wx.DefaultValidator,
                 name="EListCtrl"):
        wx.ListCtrl.__init__(self, parent, _id, pos, size,
                             style, validator, name)
        elistmix.ListRowHighlighter.__init__()

class ECheckListCtrl(listmix.CheckListCtrlMixin,
                     EBaseListCtrl):
     """ListCtrl with CheckBoxes in the first column"""
     def __init__(self, parent, *args, **kwargs):
         EBaseListCtrl.__init__(self, parent, *args, **kwargs)
         listmix.CheckListCtrlMixin.__init__(self)
