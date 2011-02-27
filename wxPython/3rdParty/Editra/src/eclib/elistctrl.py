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
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ["EBaseListCtrl", "ECheckListCtrl", "EEditListCtrl", 
           "EToggleEditListCtrl"]

#--------------------------------------------------------------------------#
# Dependencies
import wx
import wx.lib.mixins.listctrl as listmix

# Local Imports
import elistmix

#--------------------------------------------------------------------------#

class EBaseListCtrl(elistmix.ListRowHighlighter,
                    listmix.ListCtrlAutoWidthMixin,
                    wx.ListCtrl):
    """Base listctrl class that provides automatic row highlighting"""
    def __init__(self, parent, _id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.LC_REPORT, validator=wx.DefaultValidator,
                 name="EListCtrl"):
        wx.ListCtrl.__init__(self, parent, _id, pos, size,
                             style, validator, name)
        elistmix.ListRowHighlighter.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def GetSelections(self):
        """Get a list of all the selected items in the list
        @return: list of ints

        """
        items = [ idx for idx in range(self.GetItemCount())
                  if self.IsSelected(idx) ]
        return items

class ECheckListCtrl(listmix.CheckListCtrlMixin,
                     EBaseListCtrl):
     """ListCtrl with CheckBoxes in the first column"""
     def __init__(self, *args, **kwargs):
         EBaseListCtrl.__init__(self, *args, **kwargs)
         listmix.CheckListCtrlMixin.__init__(self)

class EEditListCtrl(listmix.TextEditMixin,
                    EBaseListCtrl):
    """ListCtrl with Editable cells"""
    def __init__(self, *args, **kwargs):
        EBaseListCtrl.__init__(self, *args, **kwargs)
        listmix.TextEditMixin.__init__(self)

class EToggleEditListCtrl(listmix.CheckListCtrlMixin,
                          listmix.TextEditMixin,
                          EBaseListCtrl):
    """ListCtrl with Editable cells and images that can be toggled in the
    the first column.

    """
    def __init__(self, *args, **kwargs):
        EBaseListCtrl.__init__(self, *args, **kwargs)
        listmix.TextEditMixin.__init__(self)
        listmix.CheckListCtrlMixin.__init__(self)

    def GetCheckedItems(self):
        """Get the list of checked indexes"""
        count = self.GetItemCount()
        return [item for item in range(count) if self.IsChecked(item)]

    def SetCheckedBitmap(self, bmp):
        """Set the bitmap to use for the Checked state
        @param bmp: wx.Bitmap

        """
        assert isinstance(bmp, wx.Bitmap) and bmp.IsOk()
        imgl = self.GetImageList(wx.IMAGE_LIST_SMALL)
        imgl.Replace(self.check_image, bmp)

    def SetUnCheckedBitmap(self, bmp):
        """Set the bitmap to use for the un-Checked state
        @param bmp: wx.Bitmap

        """
        assert isinstance(bmp, wx.Bitmap) and bmp.IsOk()
        imgl = self.GetImageList(wx.IMAGE_LIST_SMALL)
        imgl.Replace(self.uncheck_image, bmp)
