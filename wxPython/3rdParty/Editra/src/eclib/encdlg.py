###############################################################################
# Name: encdlg.py                                                             #
# Purpose: Encoding Dialog                                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: Encoding Dialog

A simple choice dialog for selecting a file encoding type from. The dialog
can work with either a passed in list of choices to display or by default will
list all encodings found on the system using their normalized names.

@summary: Encoding choice dialog

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['EncodingDialog', 'GetAllEncodings']

#--------------------------------------------------------------------------#
# Imports
import locale
import encodings
import wx

#--------------------------------------------------------------------------#
# Globals
EncodingDialogNameStr = u"EncodingDialog"

#--------------------------------------------------------------------------#

class EncodingDialog(wx.Dialog):
    """Dialog for choosing an file encoding from the list of available
    encodings on the system.

    """
    def __init__(self, parent, id=wx.ID_ANY, msg=u'', title=u'',
                  elist=None,default=u'',
                  style=wx.DEFAULT_DIALOG_STYLE, pos=wx.DefaultPosition):
        """Create the encoding dialog
        @keyword msg: Dialog Message
        @keyword title: Dialog Title
        @keyword encodings: list of encodings to use or None to use all
        @keyword default: Default selected encoding

        """
        wx.Dialog.__init__(self, parent, id, title, style=style,
                           pos=pos, name=EncodingDialogNameStr)

        # Attributes
        self._encpanel = EncodingPanel(self, msg=msg,
                                       elist=elist, default=default)

        # Layout
        self.__DoLayout()

        # Event Handlers
        

    def __DoLayout(self):
        """Layout the dialogs controls"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._encpanel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()

    def GetEncoding(self):
        """Get the selected encoding
        @return: string

        """
        return self._encpanel.GetEncoding()

#--------------------------------------------------------------------------#

class EncodingPanel(wx.Panel):
    """Panel that holds encoding selection choices"""
    def __init__(self, parent, msg=u'', elist=None, default=u''):
        """Create the panel
        @keyword msg: Display message
        @keyword elist: list of encodings to show or None to show all
        @keyword default: default encoding selection

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self._msg = msg
        self._encs = wx.Choice(self, wx.ID_ANY)
        self._selection = default

        # Setup
        if elist is None:
            elist = GetAllEncodings()

        self._encs.SetItems(elist)
        default = encodings.normalize_encoding(default)
        if default and default.lower() in elist:
            self._encs.SetStringSelection(default)
        else:
            self._encs.SetStringSelection(locale.getpreferredencoding(False))
            self._selection = self._encs.GetStringSelection()

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self._encs)

    def __DoLayout(self):
        """Layout the panel"""
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        caption = wx.StaticText(self, label=self._msg)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.AddMany([((100, 10), 1, wx.EXPAND),
                        (wx.Button(self, wx.ID_OK), 0, wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5), 0),
                        (wx.Button(self, wx.ID_CANCEL), 0, wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5), 0)])
        vsizer.AddMany([((10, 10), 0), (caption, 0), ((5, 5), 0),
                        (self._encs, 1, wx.EXPAND), ((10, 10), 0), (bsizer, 1),
                        ((10, 10), 0)])
        hsizer.AddMany([((10, 10), 0), (vsizer, 1), ((10, 10), 0)])

        self.SetSizer(hsizer)
        self.SetInitialSize()
        self.SetAutoLayout(True)

    def GetEncoding(self):
        """Get the chosen encoding
        @return: string

        """
        return self._selection

    def OnChoice(self, evt):
        """Update the selection
        @param evt: wx.EVT_CHOICE
        @type evt: wx.CommandEvent

        """
        if evt.GetEventObject() == self._encs:
            self._selection = self._encs.GetStringSelection()
        else:
            evt.Skip()

#--------------------------------------------------------------------------#
# Utilities

def GetAllEncodings():
    """Get all encodings found on the system
    @return: list of strings

    """
    elist = encodings.aliases.aliases.values()
    elist = list(set(elist))
    elist.sort()
    elist = [ enc for enc in elist if not enc.endswith('codec') ]
    return elist

#--------------------------------------------------------------------------#

# Test
if __name__ == '__main__':
    app = wx.App(False)
    dlg = EncodingDialog(None, msg="Choose an Encoding",
                         title="Encodings", default="utf-8")
    dlg.ShowModal()
    print dlg, dlg.GetEncoding()
    app.MainLoop()
