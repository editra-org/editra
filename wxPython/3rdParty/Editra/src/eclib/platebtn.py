###############################################################################
# Name: platebtn.py                                                           #
# Purpose: Flat label button with support for bitmaps and drop menu           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
The PlateButton is an owner drawn button control
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.imageutils as imageutils

# Used on OSX to get access to carbon api constants
if wx.Platform == '__WXMAC__':
    import Carbon.Appearance

#-----------------------------------------------------------------------------#
# Button States
PLATE_NORMAL = 0
PLATE_PRESSED = 1
PLATE_HIGHLIGHT = 2

# Button Styles
PB_STYLE_DEFAULT  = 1   # Normal Flat Background
PB_STYLE_GRADIENT = 2   # Gradient Filled Background
PB_STYLE_SQUARE   = 4   # Use square corners instead of rounded

#-----------------------------------------------------------------------------#
# Utility Functions
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
    end_color = wx.WHITE
    rdif = end_color.Red() - color.Red()
    gdif = end_color.Green() - color.Green()
    bdif = end_color.Blue() - color.Blue()
    high = 100

    # We take the percent way of the color from color -. white
    red = color.Red() + ((percent * rdif) / high)
    green = color.Green() + ((percent * gdif) / high)
    blue = color.Blue() + ((percent * bdif) / high)
    return wx.Colour(max(red, 0), max(green, 0), max(blue, 0), alpha)

def BestLabelColour(color):
    """Get the best color to use for the label that will be drawn on
    top of the given color.
    @param color: background color that text will be drawn on

    """
    avg = sum(color.Get()) / 3
    txt_color = avg > 128 and AdjustColour(color, -95) or AdjustColour(color, 95)
    return txt_color

def GetHighlightColour():
    if wx.Platform == '__WXMAC__':
        brush = wx.Brush(wx.BLACK)
        # kThemeBrushButtonPressedLightHighlight
        brush.MacSetTheme(Carbon.Appearance.kThemeBrushFocusHighlight)
        return brush.GetColour()
    else:
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)

#-----------------------------------------------------------------------------#

class PlateButton(wx.PyControl):
    def __init__(self, parent, id=wx.ID_ANY, label='',
                 bmp=None, state=PLATE_NORMAL, style=PB_STYLE_DEFAULT):
        wx.PyControl.__init__(self, parent, id,
                              style=wx.BORDER_NONE|wx.TRANSPARENT_WINDOW)

        # Attributes
        self.InheritAttributes()
        self._bmp = dict(enable=bmp)
        if bmp is not None:
            img = wx.ImageFromBitmap(bmp)
            img.SetMask(True)
            img.ConvertAlphaToMask()
            imageutils.grayOut(img)
            self._bmp['disable'] = wx.BitmapFromImage(img)
        else:
            self._bmp['disable'] = None

        self._menu = None
        self.SetLabel(label)
        self._style = style
        self._pstate = state        # Previous State
        self._state = state         # Current State
        color = GetHighlightColour() #wx.Colour(33, 33, 33, 150)
        pcolor = AdjustColour(color, -20, 150)
        bcolour = self.GetBackgroundBrush().GetColour()
        self._color = dict(hlight=color, 
                           press=pcolor,
                           htxt=BestLabelColour(self.GetForegroundColour()),
                           ptxt=BestLabelColour(bcolour),
                           bkgrd=pcolor)

        # Setup
        self.__CalcBestSize()

        # Event Handlers
        self.Bind(wx.EVT_PAINT, lambda evt: self.__RefreshButton())
        self.Bind(wx.EVT_SET_FOCUS, lambda evt: self.SetState(PLATE_HIGHLIGHT))
        self.Bind(wx.EVT_KILL_FOCUS, lambda evt: self.SetState(PLATE_NORMAL))
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)

        # Mouse Events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DCLICK, lambda evt: self.ToggleState())
        self.Bind(wx.EVT_ENTER_WINDOW,
                  lambda evt: self.SetState(PLATE_HIGHLIGHT))
        self.Bind(wx.EVT_LEAVE_WINDOW,
                  lambda evt: wx.CallLater(120, self.SetState, PLATE_NORMAL))

    def __CalcBestSize(self):
        """Calculate and set the best size of the control based on its
        contents.
        @postcondition: Control is resized to best fitting size
        
        """
        width = 4
        height = 6
        if self.GetLabel():
            lsize = self.GetTextExtent(self.GetLabel())
            width += lsize[0]
            height += lsize[1]
            
        if self._bmp['enable'] is not None:
            bsize = self._bmp['enable'].GetSize()
            width += (bsize[0] + 10)
            if height <= bsize[1]:
                height = bsize[1] + 6
            else:
                height += 3
        else:
            width += 10

        if self._menu is not None:
            width += 12

        if self.GetSizeTuple() != (width, height):
            self.SetSizeHints(width, height, width, height)
            self.SetSize((width, height))
            self.Refresh()

    def __DrawBitmap(self, gc):
        """Draw the bitmap if one has been set
        @param gc: GCDC to draw with
        @return: x cordinate to draw text at

        """
        if self.IsEnabled():
            bmp = self._bmp['enable']
        else:
            bmp = self._bmp['disable']

        if bmp is not None and bmp.IsOk():
            bw, bh = bmp.GetSize()
            gc.DrawBitmap(bmp, 6, 3, bmp.GetMask() != None)
            return bw + 6
        else:
            return 6

    def __DrawDropArrow(self, gc, xpos, ypos):
        """Draw a drop arrow if needed and restore pen/brush after finished
        @param gc: GCDC to draw with
        @param xpos: x cord to start at
        @param ypos: y cord to start at

        """
        if self._menu is not None:
            # Positioning needs a little help on Windows
            if wx.Platform == '__WXMSW__':
                xpos -= 2
            tripoints = [(xpos, ypos), (xpos + 6, ypos), (xpos + 3, ypos + 5)]
            brush_b = gc.GetBrush()
            pen_b = gc.GetPen()
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush(gc.GetTextForeground()))
            gc.DrawPolygon(tripoints)
            gc.SetBrush(brush_b)
            gc.SetPen(pen_b)
        else:
            pass

    def __DrawHighlight(self, gc, width, height):
        """Draw the main highlight/pressed state
        @param gc: GCDC to draw with
        @param width: width of highlight
        @param height: height of highlight

        """
        if self._state == PLATE_PRESSED:
            color = self._color['press']
        else:
            color = self._color['hlight']

        if self._style & PB_STYLE_SQUARE:
            rad = 0
        else:
            rad = (height - 3) / 2

        if self._style & PB_STYLE_GRADIENT:
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            rgc = gc.GetGraphicsContext()
            brush = rgc.CreateLinearGradientBrush(0, 1, 0, height,
                                                  color, AdjustAlpha(color, 45))
            rgc.SetBrush(brush)
        else:
            gc.SetBrush(wx.Brush(color))

        gc.DrawRoundedRectangle(1, 1, width - 2, height - 2, rad)

    def __RefreshButton(self):
        """Draw the button"""
        dc = wx.PaintDC(self)
        gc = wx.GCDC(dc)

        # Setup
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetFont(self.GetFont())
        gc.SetBackgroundMode(wx.TRANSPARENT)

        if wx.Platform == '__WXGTK__':
            gc.SetBackground(self.GetBackgroundBrush(gc))
            gc.Clear()

        # Calc Object Positions
        width, height = self.GetSize()
        tw, th = gc.GetTextExtent(self.GetLabel())
        txt_y = max((height - th) / 2, 1)

        if self._state == PLATE_HIGHLIGHT:
            gc.SetTextForeground(self._color['htxt'])
            gc.SetPen(wx.TRANSPARENT_PEN)
            self.__DrawHighlight(gc, width, height)
        elif self._state == PLATE_PRESSED:
            gc.SetTextForeground(self._color['ptxt'])

            if wx.Platform == '__WXMAC__':
                brush = wx.Brush(wx.BLACK)
                brush.MacSetTheme(Carbon.Appearance.kThemeBrushFocusHighlight)
                pen = wx.Pen(AdjustAlpha(brush.GetColour(), 220), 1, wx.SOLID)
            else:
                pen = wx.Pen(AdjustColour(self._color['press'], -80, 220), 1)
            gc.SetPen(pen)

            txt_x = self.__DrawBitmap(gc)
            gc.DrawText(self.GetLabel(), txt_x + 2, txt_y)
            self.__DrawDropArrow(gc, txt_x + tw + 6, (height / 2) - 2)
            self.__DrawHighlight(gc, width, height)
        else:
            if self.IsEnabled():
                gc.SetTextForeground(self.GetForegroundColour())
            else:
                gc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))

        # Draw bitmap and text
        if self._state != PLATE_PRESSED:
            txt_x = self.__DrawBitmap(gc)
            gc.DrawText(self.GetLabel(), txt_x + 2, txt_y)
            self.__DrawDropArrow(gc, txt_x + tw + 6, (height / 2) - 2) 

    #---- End Private Member Function ----#

    def Disable(self):
        """Disable the control"""
        wx.PyControl.Disable(self)
        self.Refresh()

    def Enable(self, enable=True):
        """Enable/Disable the control"""
        wx.PyControl.Enable(self, enable)
        self.Refresh()

    def GetBackgroundBrush(self, gc=None):
        """Get the brush for drawing the background of the button
        @return: wx.Brush

        """
        bkgrd = self.GetBackgroundColour()
        brush = wx.Brush(bkgrd, wx.SOLID)
        my_attr = self.GetDefaultAttributes()
        p_attr = self.GetParent().GetDefaultAttributes()
        my_def = bkgrd == my_attr.colBg
        p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
        if my_def and p_def and wx.Platform != '__WXGTK__':
            brush = wx.TRANSPARENT_BRUSH
        elif my_def and not p_def:
            bkgrd = self.GetParent().GetBackgroundColour()
            brush = wx.Brush(bkgrd, wx.SOLID)
        return brush

    def HasTransparentBackground(self):
        """Override setting of background fill"""
        return True

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent
        on windows.
        @param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    def OnLeftDown(self, evt):
        pos = evt.GetPositionTuple()
        self.SetState(PLATE_PRESSED)
        size = self.GetSizeTuple()
        if self._menu is not None and pos[0] >= size[0] - 16:
            if wx.Platform == '__WXMAC__':
                adj = 3
            else:
                adj = 0
            self.PopupMenu(self._menu, (2, size[1] + adj))
            
    def OnLeftUp(self, evt):
        """Post a button event if the control was previously in a
        pressed state.
        @param evt: wx.MouseEvent

        """
        if self._state == PLATE_PRESSED:
            wx.PostEvent(self.GetParent(), wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId()))
        self.SetState(PLATE_HIGHLIGHT)

    def OnMenuClose(self, evt):
        mpos = wx.GetMousePosition()
        if self.HitTest(self.ScreenToClient(mpos)) != wx.HT_WINDOW_OUTSIDE:
            self.SetState(PLATE_HIGHLIGHT)
        else:
            self.SetState(PLATE_NORMAL)
        evt.Skip()

    def SetBitmap(self, bmp):
        """Set the bitmap displayed in the button
        @param bmp: wx.Bitmap

        """
        self._bmp['enable'] = bmp
        img = wx.ImageFromBitmap(bmp)
        img.ConvertToGreyscale()
        self._bmp['disable'] = wx.BitmapFromImage(img)
        self.__CalcBestSize()

    def SetFont(self, font):
        """Adjust size of control when font changes"""
        wx.PyControl.SetFont(self, font)
        self.__CalcBestSize()

    def SetLabel(self, label):
        """Set the label of the button
        @param label: lable string

        """
        wx.PyControl.SetLabel(self, label)
        self.__CalcBestSize()

    def SetMenu(self, menu):
        """Set the menu that can be shown when clicking on the
        drop arrow of the button.
        @param menu: wxMenu to use as a PopupMenu
        @note: Arrow is not drawn unless a menu is set

        """
        if self._menu is not None:
            self.Unbind(wx.EVT_MENU_CLOSE)

        self._menu = menu
        self.Bind(wx.EVT_MENU_CLOSE, self.OnMenuClose)
        self.__CalcBestSize()

    def SetPressColor(self, color):
        """Set the color used for highlighting the pressed state
        @param color: wx.Color

        """
        self._color['hlight'] = AdjustAlpha(color, 150)
        self._color['press'] = AdjustColour(color, -20, 165)
        self._color['htxt'] = BestLabelColour(self._color['hlight'])
        self._color['ptxt'] = BestLabelColour(self._color['bkgrd'])
        self.Refresh()

    def SetState(self, state):
        """Manually set the state of the button
        @param state: one of the PLATE_STATE_* values
        @note: the state may be altered by mouse actions

        """
        self._pstate = self._state
        self._state = state
        self.GetParent().RefreshRect(self.GetRect(), False)

    def SetWindowVariant(self, variant):
        """Set the variant/font size of this control"""
        wx.PyControl.SetWindowVariant(self, variant)
        self.__CalcBestSize()

    def ShouldInheritColours(self):
        """Overridden base class virtual.  If the parent has non-default
        colours then we want this control to inherit them.

        """
        return True

    def ToggleState(self):
        """Toggle button state"""
        if self._state != PLATE_PRESSED:
            self.SetState(PLATE_PRESSED)
        else:
            self.SetState(PLATE_HIGHTLIGHT)

#-----------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    app = wx.PySimpleApp(False)
    frame = wx.Frame(None, title="PlateButton Test")
    panel = wx.Panel(frame)

    panel.SetBackgroundColour(wx.BLUE)
    pbtn = PlateButton(panel, 
                       bmp=wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU),#, (16, 16)),
                       label="Bitmap/Label")
#     pbtn.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
    pbtn.Disable()
    pbtn2 = PlateButton(panel,label="No Bitmap", style=PB_STYLE_SQUARE)
    pbtn2.SetPressColor(wx.RED)
    pbtn2.SetLabel('HELLO WORLD')
#     pbtn2.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MENU))
    pbtn3 = PlateButton(panel, label="Small Font", style=PB_STYLE_GRADIENT)
    pbtn3.SetFont(wx.SMALL_FONT)
    pbtn4 = PlateButton(panel, 
                        bmp=wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU, (16, 16)),
                        label="Small Bmp/Small Font")
    pbtn4.SetFont(wx.SMALL_FONT)
    menu = wx.Menu("HELLO")
    menu.Append(wx.ID_ANY, "PopupMenu Item 1")
    menu.Append(wx.ID_ANY, "PopupMenu Item 2")
    pbtn4.SetMenu(menu)


    def OnButton(evt):
        print "Button Pressed Id: ", evt.GetId()
        pbtn.Enable(not pbtn.IsEnabled())

    def OnMenu(evt):
        print "Menu Event: ", evt.GetId()

    panel.Bind(wx.EVT_BUTTON, OnButton)
    panel.Bind(wx.EVT_MENU, OnMenu)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    msizer = wx.BoxSizer(wx.VERTICAL)
    sizer.AddMany([((30, 30)), (pbtn, 1, wx.ALIGN_LEFT),
                   ((15, 15)), (pbtn2, 0, wx.ALIGN_RIGHT),
                   ((15, 15)), (pbtn3, 0, wx.ALIGN_RIGHT),
                   ((15, 15)), (pbtn4, 0, wx.ALIGN_RIGHT), ((30, 30))])
    msizer.AddMany([((30, 30)), (sizer, 0, wx.ALIGN_CENTER), ((30, 30))])
    panel.SetSizer(msizer)
    fsizer = wx.BoxSizer(wx.HORIZONTAL)
    fsizer.Add(panel)
    frame.SetSizer(fsizer)
    frame.SetInitialSize()
    frame.Show()
    app.MainLoop()
