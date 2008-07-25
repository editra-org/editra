###############################################################################
# Name: ctrlbox.py                                                            #
# Purpose: Container Window helper class                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: ControlBox

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

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
CTRLBAR_STYLE_DEFAULT  = 0
CTRLBAR_STYLE_GRADIENT = 1  # Paint the bar with a gradient
CTRLBAR_STYLE_FOLDABLE = 2  # Add a fold button to the bar.

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
        self._ctrlbar = None
        self._main = None

        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)

    def CreateControlBar(self, pos=wx.TOP):
        """Create a ControlBar at the given position if one does not
        already exist.
        @keyword pos: wx.TOP (default) or wx.BOTTOM
        @postcondition: A top aligned L{ControlBar} is created.

        """
        if self._ctrlbar is None:
            self._ctrlbar = ControlBar(self, size=(-1, 24),
                                       style=CTRLBAR_STYLE_GRADIENT)
            self._sizer.Insert(0, self._ctrlbar, 0, wx.EXPAND)

    def GetControlBar(self):
        """Get the L{ControlBar} used by this window
        @return: ControlBar or None

        """
        return self._ctrlbar

    def GetWindow(self):
        """Get the main display window
        @return: Window or None

        """
        return self._main

    def SetControlBar(self, ctrlbar):
        """Set the ControlBar used by this ControlBox
        @param ctrlbar: L{ControlBar}

        """
        if self._ctrlbar is not None:
            self._sizer.Replace(self._ctrlbar, ctrlbar)
            try:
                self._ctrlbar.Destroy()
            except wx.PyDeadObjectError:
                pass
        else:
            self._sizer.Insert(0, ctrlbar, 0, wx.EXPAND)
        self._ctrlbar = ctrlbar

    def SetWindow(self, window):
        """Set the main window control portion of the box. This will be the
        main central item shown in the box
        @param window: Any window/panel like object

        """
        if self._main is None:
            self._main = window
            self._sizer.Add(self._main, 1, wx.EXPAND)
        else:
            self._sizer.Replace(self._main, window)
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
            self._sizer.Add((5, 5), 0)
            self._sizer.Add(control, stretch, align|wx.ALIGN_CENTER_VERTICAL)
        else:
            self._sizer.Add(control, stretch, align|wx.ALIGN_CENTER_VERTICAL)
            self._sizer.Add((5, 5), 0)

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
            spacer = (5, 5)
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
        if not self._style & CTRLBAR_STYLE_GRADIENT:
            evt.Skip()
            return

        # Paint the gradient
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col2 = AdjustColour(col1, 30)
        col1 = AdjustColour(col1, -20)
        rect = self.GetClientRect()
        grad = gc.CreateLinearGradientBrush(0, .5, 0, rect.height, col2, col1)

        pen_col = tuple([min(190, x) for x in AdjustColour(col1, -25)])
        gc.SetPen(gc.CreatePen(wx.Pen(pen_col, 1)))
        gc.SetBrush(grad)
        gc.DrawRectangle(0, 0, rect.width - 0.5, rect.height - 0.5)

        evt.Skip()

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

#--------------------------------------------------------------------------#
# Test
if __name__ == '__main__':

    # Setup Display
    def MakeTestFrame():
        frame = wx.Frame(None, title="Test ControlBox")
        fsizer = wx.BoxSizer(wx.VERTICAL)

        cbox = ControlBox(frame)
        cbox.CreateControlBar()

        cbar = cbox.GetControlBar()
        cbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU, (16, 16)), "hello world")
        cbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MENU, (16, 16)), "warning")
        cbar.AddStretchSpacer()
        cbar.AddControl(wx.Choice(cbar, wx.ID_ANY, choices=[str(x) for x in range(10)]), wx.ALIGN_RIGHT)
        cbar.AddControl(wx.Button(cbar, label="New Frame"), wx.ALIGN_RIGHT)

        cbox.SetWindow(wx.TextCtrl(cbox, style=wx.TE_MULTILINE))
        cbox.Bind(EVT_CTRLBAR, OnControlBar)
        cbox.Bind(wx.EVT_BUTTON, OnButton)

        fsizer.Add(cbox, 1, wx.EXPAND)
        return frame

    def OnControlBar(evt):
        print "ControlBarEvent", evt.GetId()

    def OnButton(evt):
        print "Button tool clicked"
        frame = MakeTestFrame()
        frame.Show()

    APP = wx.App(False)
    FRAME = MakeTestFrame()
    FRAME.Show()
    APP.MainLoop()
