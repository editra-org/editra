###############################################################################
# Name: ecpickers.py                                                          #
# Purpose: Custom picker controls                                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: Editra Control Pickers

Collection of various custom picker controls

@summary: Various custom picker controls

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['PyFontPicker',]

#-----------------------------------------------------------------------------#
# Imports
import wx

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class PyFontPicker(wx.Panel):
    """A slightly enhanced wx.FontPickerCtrl that displays the choosen font in
    the text control using the choosen font as well as the font's size using
    nicer formatting.

    """
    def __init__(self, parent, id_=wx.ID_ANY, default=wx.NullFont):
        """Initializes the PyFontPicker
        @param default: The font to initialize as selected in the control

        """
        wx.Panel.__init__(self, parent, id_, style=wx.NO_BORDER)

        # Attributes
        if default == wx.NullFont:
            self._font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        else:
            self._font = default
        self._text = wx.TextCtrl(self, style=wx.TE_CENTER | wx.TE_READONLY)
        self._text.SetFont(default)
        self._text.SetValue(u"%s - %dpt" % (self._font.GetFaceName(), \
                                            self._font.GetPointSize()))
        self._text.Enable(False)
        self._button = wx.Button(self, label=_("Set Font") + u'...')

        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(self._text, 1, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (self._button, 0, wx.ALIGN_CENTER_VERTICAL)])
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, lambda evt: self.ShowFontDlg(), self._button)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.OnChange)

    def GetFontValue(self):
        """Gets the currently choosen font
        @return: wx.Font

        """
        return self._font

    def GetTextCtrl(self):
        """Gets the widgets text control
        @return: wx.TextCtrl

        """
        return self._text

    def OnChange(self, evt):
        """Updates the text control using our custom stylings after
        the font is changed.
        @param evt: The event that called this handler

        """
        font = evt.GetFont()
        if font.IsNull():
            return
        self._font = font
        self._text.Clear()
        self._text.SetFont(self._font)
        self._text.SetValue(u"%s - %dpt" % (font.GetFaceName(), \
                                            font.GetPointSize()))
        evt = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY,
                                         self.GetId(), self._font, self)
        wx.PostEvent(self.GetParent(), evt)

    def SetButtonLabel(self, label):
        """Sets the buttons label"""
        self._button.SetLabel(label)
        self._button.Refresh()

    def SetToolTipString(self, tip):
        """Sets the tooltip of the window
        @param tip: string

        """
        self._text.SetToolTipString(tip)
        self._button.SetToolTipString(tip)
        wx.Panel.SetToolTipString(self, tip)

    def ShowFontDlg(self):
        """Opens the FontDialog and processes the result"""
        fdata = wx.FontData()
        fdata.SetInitialFont(self._font)
        fdlg = wx.FontDialog(self.GetParent(), fdata)
        fdlg.ShowModal()
        fdata = fdlg.GetFontData()
        fdlg.Destroy()
        wx.PostEvent(self, wx.FontPickerEvent(self, self.GetId(),
                                              fdata.GetChosenFont()))
