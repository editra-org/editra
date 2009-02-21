###############################################################################
# Name: ctrlbox.py                                                            #
# Purpose: Container Window helper class                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: ControlBox

Sizer managed panel class with support for a toolbar like control that can be
placed on the top/bottom of the main window area, multiple control bars are also
possible.

Class ControlBar:

Toolbar like control with automatic item spacing and layout.

Styles:
  - CTRLBAR_STYLE_DEFAULT: Plain background
  - CTRLBAR_STYLE_GRADIENT: Draw the bar with a vertical gradient.
  - CTRLBAR_STYLE_BORDER_BOTTOM: add a border to the bottom
  - CTRLBAR_STYLE_BORDER: add a border to the top

Class ControlBox:

The ControlBox is a sizer managed panel that supports easy creation of windows
that require a sandwich like layout.

+---------------------------------------+
| ControlBar                            |
+---------------------------------------+
|                                       |
|                                       |
|          MainWindow Area              |
|                                       |
|                                       |
|                                       |
+---------------------------------------+
| ControlBar                            |
+---------------------------------------+

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ["ControlBar", "ControlBarEvent", "ControlBox",
           "CTRLBAR_STYLE_DEFAULT", "CTRLBAR_STYLE_GRADIENT",
           "EVT_CTRLBAR", "edEVT_CTRLBAR"]

#--------------------------------------------------------------------------#
# Dependancies
import wx

#--------------------------------------------------------------------------#
# Globals

#-- Control Name Strings --#
CTRLBAR_NAME_STR = u'EditraControlBar'
CTRLBOX_NAME_STR = u'EditraControlBox'

#-- Control Style Flags --#

# ControlBar
CTRLBAR_STYLE_DEFAULT       = 0
CTRLBAR_STYLE_GRADIENT      = 1     # Paint the bar with a gradient
CTRLBAR_STYLE_BORDER_BOTTOM = 2     # Add a border to the bottom
CTRLBAR_STYLE_BORDER_TOP    = 4     # Add a border to the top

#CTRLBAR_STYLE_FOLDABLE = 2  # Add a fold button to the bar.

# ControlBar event for items added by AddTool
edEVT_CTRLBAR = wx.NewEventType()
EVT_CTRLBAR = wx.PyEventBinder(edEVT_CTRLBAR, 1)
class ControlBarEvent(wx.PyCommandEvent):
    """ControlBar Button Event"""

#--------------------------------------------------------------------------#

class ControlBox(wx.PyPanel):
    """Simple managed panel helper class that allows for adding and
    managing the position of a small toolbar like panel.
    @see: L{ControlBar}

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL|wx.NO_BORDER,
                 name=CTRLBOX_NAME_STR):
        wx.PyPanel.__init__(self, parent, id, pos, size, style, name)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._topb = None
        self._main = None
        self._botb = None

        # Layout
        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)

    def CreateControlBar(self, pos=wx.TOP):
        """Create a ControlBar at the given position if one does not
        already exist.
        @keyword pos: wx.TOP (default) or wx.BOTTOM
        @postcondition: A top aligned L{ControlBar} is created.

        """
        cbar = self.GetControlBar(pos)
        if cbar is None:
            cbar = ControlBar(self, size=(-1, 24),
                              style=CTRLBAR_STYLE_GRADIENT)

            self.SetControlBar(cbar, pos)

    def GetControlBar(self, pos=wx.TOP):
        """Get the L{ControlBar} used by this window
        @param pos: wx.TOP or wx.BOTTOM
        @return: ControlBar or None

        """
        if pos == wx.TOP:
            cbar = self._topb
        else:
            cbar = self._botb

        return cbar

    def GetWindow(self):
        """Get the main display window
        @return: Window or None

        """
        return self._main

    def ReplaceControlBar(self, ctrlbar, pos=wx.TOP):
        """Replace the L{ControlBar} at the given position
        with the given ctrlbar and return the bar that was
        replaced or None.
        @param ctrlbar: L{ControlBar}
        @keyword pos: Postion
        @return: L{ControlBar} or None

        """
        tbar = self.GetControlBar(pos)
        rbar = None
        if pos == wx.TOP:
            if tbar is None:
                self._sizer.Insert(0, ctrlbar, 0, wx.EXPAND)
            else:
                self._sizer.Replace(self._topb, ctrlbar)
                rbar = self._topb

            self._topb = ctrlbar
        else:
            if tbar is None:
                self._sizer.Add(ctrlbar, 0, wx.EXPAND)
            else:
                self._sizer.Replace(self._botb, ctrlbar)
                rbar = self._botb

            self._botb = ctrlbar

        return rbar

    def SetControlBar(self, ctrlbar, pos=wx.TOP):
        """Set the ControlBar used by this ControlBox
        @param ctrlbar: L{ControlBar}
        @keyword pos: wx.TOP/wx.BOTTOM

        """
        tbar = self.GetControlBar(pos)
        if pos == wx.TOP:
            if tbar is None:
                self._sizer.Insert(0, ctrlbar, 0, wx.EXPAND)
            else:
                self._sizer.Replace(self._topb, ctrlbar)

                try:
                    self._topb.Destroy()
                except wx.PyDeadObjectError:
                    pass

            self._topb = ctrlbar
        else:
            if tbar is None:
                self._sizer.Add(ctrlbar, 0, wx.EXPAND)
            else:
                self._sizer.Replace(self._botb, ctrlbar)

                try:
                    self._botb.Destroy()
                except wx.PyDeadObjectError:
                    pass

            self._botb = ctrlbar

    def SetWindow(self, window):
        """Set the main window control portion of the box. This will be the
        main central item shown in the box
        @param window: Any window/panel like object

        """
        if self.GetWindow() is None:
            if self._topb is None:
                self._sizer.Add(window, 1, wx.EXPAND)
            else:
                self._sizer.Insert(1, window, 1, wx.EXPAND)
        else:
            self._sizer.Replace(self._main, window)

            try:
                self._main.Destroy()
            except wx.PyDeadObjectError:
                pass

        self._main = window

#--------------------------------------------------------------------------#

class ControlBar(wx.PyPanel):
    """Toolbar like control container for use with a L{ControlBox}. It
    uses a panel with a managed sizer as a convenient way to add a small
    bar with various controls in it to any window.

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=CTRLBAR_STYLE_DEFAULT,
                 name=CTRLBAR_NAME_STR):
        wx.PyPanel.__init__(self, parent, id, pos, size,
                            wx.TAB_TRAVERSAL|wx.NO_BORDER, name)

        # Attributes
        self._style = style
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tools = dict(simple=list())
        self._spacing = (5, 5)

        # Drawing related
        color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        self._color2 = AdjustColour(color, 30)
        self._color = AdjustColour(color, -20)
        pcolor = tuple([min(190, x) for x in AdjustColour(self._color, -25)])
        self._pen = wx.Pen(pcolor, 1)

        # Setup
        msizer = wx.BoxSizer(wx.VERTICAL)
        spacer = (0, 0)
        msizer.Add(spacer, 0)
        msizer.Add(self._sizer, 1, wx.EXPAND)
        msizer.Add(spacer, 0)
        self.SetSizer(msizer)
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self._DispatchEvent)

    def _DispatchEvent(self, evt):
        """Translate the button events generated by the controls added by
        L{AddTool} to L{ControlBarEvent}'s.

        """
        e_id = evt.GetId()
        if e_id in self._tools['simple']:
            cb_evt = ControlBarEvent(edEVT_CTRLBAR, e_id)
            wx.PostEvent(self.GetParent(), cb_evt)
        else:
            evt.Skip()

    def AddControl(self, control, align=wx.ALIGN_LEFT, stretch=0):
        """Add a control to the bar
        @param control: The control to add to the bar
        @keyword align: wx.ALIGN_LEFT or wx.ALIGN_RIGHT
        @keyword stretch: The controls proportions 0 for normal, 1 for expand

        """
        if wx.Platform == '__WXMAC__':
            if hasattr(control, 'SetWindowVariant'):
                control.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        if align == wx.ALIGN_LEFT:
            self._sizer.Add(self._spacing, 0)
            self._sizer.Add(control, stretch, align|wx.ALIGN_CENTER_VERTICAL)
        else:
            self._sizer.Add(control, stretch, align|wx.ALIGN_CENTER_VERTICAL)
            self._sizer.Add(self._spacing, 0)

        self.Layout()

    def AddSpacer(self, width, height):
        """Add a fixed size spacer to the control bar
        @param width: width of the spacer
        @param height: height of the spacer

        """
        self._sizer.Add((width, height), 0)

    def AddStretchSpacer(self):
        """Add an expanding spacer to the bar that will stretch and
        contract when the window changes size.

        """
        self._sizer.AddStretchSpacer(2)

    def AddTool(self, tid, bmp, help='', align=wx.ALIGN_LEFT):
        """Add a simple bitmap button tool to the control bar
        @param tid: Tool Id
        @param bmp: Tool bitmap
        @keyword help: Short help string
        @keyword align: wx.ALIGN_LEFT or wx.ALIGN_RIGHT

        """
        tool = wx.BitmapButton(self, tid, bmp, style=wx.NO_BORDER)
        if wx.Platform == '__WXGTK__':
            tool.SetMargins(0, 0)
            spacer = (0, 0)
        else:
            spacer = self._spacing
        tool.SetToolTipString(help)

        self._tools['simple'].append(tool.GetId())
        if align == wx.ALIGN_LEFT:
            self._sizer.Add(spacer, 0)
            self._sizer.Add(tool, 0, align|wx.ALIGN_CENTER_VERTICAL)
        else:
            self._sizer.Add(spacer, 0)
            self._sizer.Add(tool, 0, align|wx.ALIGN_CENTER_VERTICAL)

    def OnPaint(self, evt):
        """Paint the background to match the current style
        @param evt: wx.PaintEvent

        """
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        dc.SetPen(wx.Pen(self._color, 1))

        # Add a border to the bottom
        if self._style & CTRLBAR_STYLE_BORDER_BOTTOM:
            dc.DrawLine(0, rect.height-1, rect.width, rect.height-1)

        # Add a border to the top
        if self._style & CTRLBAR_STYLE_BORDER_TOP:
            dc.DrawLine(0, 1, rect.width, 1)

        # Paint the gradient
        if self._style & CTRLBAR_STYLE_GRADIENT:
            gc = wx.GraphicsContext.Create(dc)
            grad = gc.CreateLinearGradientBrush(0, .5, 0, rect.height,
                                                self._color2, self._color)

            gc.SetPen(gc.CreatePen(self._pen))
            gc.SetBrush(grad)
            gc.DrawRectangle(0, 0, rect.width - 0.5, rect.height - 0.5)

        evt.Skip()

    def SetToolSpacing(self, px):
        """Set the spacing to use between tools/controls.
        @param px: int (number of pixels)
        @todo: dynamically update existing layouts

        """
        self._spacing = (px, px)

    def SetVMargin(self, top, bottom):
        """Set the Vertical margin used for spacing controls from the
        top and bottom of the bars edges.
        @param top: Top margin in pixels
        @param bottom: Bottom maring in pixels

        """
        sizer = self.GetSizer()
        sizer.GetItem(0).SetSpacer((top, top))
        sizer.GetItem(2).SetSpacer((bottom, bottom))
        sizer.Layout()

    def SetWindowStyle(self, style):
        """Set the style flags of this window
        @param style: long

        """
        self._style = style
        self.Refresh()

#--------------------------------------------------------------------------#

#class SegmentBar(wx.PyPanel):
#    """Simple toolbar like control that displays bitmaps and optionaly
#    labels below each bitmap. The bitmaps are turned into a toggle button
#    where only one segment in the bar can be selected at one time.

#    """
#    def __init__(self, parent, id=wx.ID_ANY,
#                 pos=wx.DefaultPosition, size=wx.DefaultSize,
#                 style=CTRLBAR_STYLE_DEFAULT,
#                 name=CTRLBAR_NAME_STR):
#        wx.PyPanel.__init__(self, parent, id, pos, size,
#                            wx.TAB_TRAVERSAL|wx.NO_BORDER, name)

#        # Attributes
        

#        # Event Handlers
#        self.Bind(wx.EVT_PAINT, self.OnPaint)

#    def OnPaint(self, evt):
#        """Paint the control"""
#        dc = wx.PaintDC(self)

#--------------------------------------------------------------------------#

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
