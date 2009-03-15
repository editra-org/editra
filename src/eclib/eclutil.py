###############################################################################
# Name: eclutil.py                                                            #
# Purpose: Common library utilities.                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library: Editra Control Library Utility

Miscellaneous utility functions and gui helpers

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['AdjustAlpha', 'AdjustColour', 'BestLabelColour', 'HexToRGB',
           'GetHighlightColour']

#-----------------------------------------------------------------------------#
# Imports
import wx

if wx.Platform == '__WXMAC__':
    try:
        import Carbon.Appearance
    except ImportError:
        CARBON = False
    else:
        CARBON = True

#-----------------------------------------------------------------------------#
# Colour Utilities

def AdjustAlpha(colour, alpha):
    """Adjust the alpha of a given colour"""
    return wx.Colour(colour.Red(), colour.Green(), colour.Blue(), alpha)

def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.
    @param color: color object to adjust
    @type color: wx.Color
    @param percent: percent to adjust +(brighten) or -(darken)
    @type percent: int
    @keyword alpha: amount to adjust alpha channel

    """
    radj, gadj, badj = [ int(val * (abs(percent) / 100.))
                         for val in color.Get() ]

    if percent < 0:
        radj, gadj, badj = [ val * -1 for val in [radj, gadj, badj] ]
    else:
        radj, gadj, badj = [ val or 255 for val in [radj, gadj, badj] ]

    red = min(color.Red() + radj, 255)
    green = min(color.Green() + gadj, 255)
    blue = min(color.Blue() + badj, 255)
    return wx.Colour(red, green, blue, alpha)

def BestLabelColour(color):
    """Get the best color to use for the label that will be drawn on
    top of the given color.
    @param color: background color that text will be drawn on

    """
    avg = sum(color.Get()) / 3
    if avg > 192:
        txt_color = wx.BLACK
    elif avg > 128:
        txt_color = AdjustColour(color, -95)
    elif avg < 64:
        txt_color = wx.WHITE
    else:
        txt_color = AdjustColour(color, 95)
    return txt_color

def GetHighlightColour():
    """Get the default highlight color
    @return: wx.Colour

    """
    if wx.Platform == '__WXMAC__':
        if CARBON:
            if wx.VERSION < (2, 9, 0, 0, ''):
                # kThemeBrushButtonPressedLightHighlight
                brush = wx.Brush(wx.BLACK)
                brush.MacSetTheme(Carbon.Appearance.kThemeBrushFocusHighlight)
                return brush.GetColour()
            else:
                color = wx.Colour(Carbon.Appearance.kThemeBrushFocusHighlight)
                return color

    # Fallback to text highlight color
    return wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)

def HexToRGB(hex_str):
    """Returns a list of red/green/blue values from a
    hex string.
    @param hex_str: hex string to convert to rgb

    """
    hexval = hex_str
    if hexval[0] == u"#":
        hexval = hexval[1:]
    ldiff = 6 - len(hexval)
    hexval += ldiff * u"0"
    # Convert hex values to integer
    red = int(hexval[0:2], 16)
    green = int(hexval[2:4], 16)
    blue = int(hexval[4:], 16)
    return [red, green, blue]
