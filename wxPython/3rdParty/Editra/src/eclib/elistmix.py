###############################################################################
# Name: elistmix.py                                                           #
# Purpose: Custom Mixins for a wxListCtrl                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: EListMixins

Class ListRowHighlighter:
This mixin class can be used to add automatic highlighting of alternate rows
in a ListCtrl.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx

#--------------------------------------------------------------------------#
# Globals
HIGHLIGHT_ODD = 1   # Highlight the Odd rows
HIGHLIGHT_EVEN = 2  # Highlight the Even rows

#--------------------------------------------------------------------------#

class ListRowHighlighter:
    """This mixin can be used to add automatic highlighting of alternate rows
    in a list control.

    """
    def __init__(self, color=None, mode=HIGHLIGHT_EVEN):
        """Initialize the highlighter
        @keyword color: Set a custom highlight color (default uses system color)
        @keyword mode: HIGHLIGHT_EVEN (default) or HIGHLIGHT_ODD

        """
        # Attributes
        self._color = color
        self._defaultb = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        self._mode = mode

        # Event Handlers
        # TODO: instead of updating all rows it would be better for
        #       performance reasons to only update the item before and
        #       all the items after the changed item if its near the bottom
        #       and visa versa if the item is near the top of the list.
        self.Bind(wx.EVT_LIST_INSERT_ITEM, lambda evt: self.RefreshRows())
        self.Bind(wx.EVT_LIST_DELETE_ITEM, lambda evt: self.RefreshRows())

    def RefreshRows(self):
        """Re-color all the rows"""
        for row in xrange(self.GetItemCount()):
            if self._defaultb is None:
                self._defaultb = self.GetItemBackgroundColour(row)

            if self._mode & HIGHLIGHT_EVEN:
                dohlight = not row % 2
            else:
                dohlight = row % 2

            if dohlight:
                if self._color is None:
                    if wx.Platform in ['__WXGTK__', '__WXMSW__']:
                        color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DLIGHT)
                    else:
                        color = wx.Colour(238, 255, 255)

                else:
                    color = self._color
            else:
                color = self._defaultb

            self.SetItemBackgroundColour(row, color)

    def SetHighlightColor(self, color):
        """Set the color used to highlight the rows. Call L{RefreshRows} after
        this if you wish to update all the rows highlight colors.
        @param color: wx.Color or None to set default

        """
        self._color = color

    def SetHighlightMode(self, mode):
        """Set the highlighting mode to either HIGHLIGHT_EVEN or to
        HIGHLIGHT_ODD. Call L{RefreshRows} afterwards to update the list
        state.
        @param mode: HIGHLIGHT_* mode value

        """
        self._mode = mode

#--------------------------------------------------------------------------#
# Utilities
def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.
    @param color: color object to adjust
    @type color: wx.Color
    @param percent: percent to adjust +(brighten) or -(darken)
    @type percent: int
    @keyword alpha: Value to adjust alpha channel to

    """
    radj, gadj, badj = [ int(val * (abs(percent) / 100.))
                         for val in color.Get() ]

    if percent < 0:
        radj, gadj, badj = [ val * -1 for val in [radj, gadj, badj] ]
    else:
        radj, gadj, badj = [ val or percent for val in [radj, gadj, badj] ]

    red = min(color.Red() + radj, 255)
    green = min(color.Green() + gadj, 255)
    blue = min(color.Blue() + badj, 255)
    return wx.Colour(red, green, blue, alpha)
