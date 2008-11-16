###############################################################################
# Name: FileInfo.py                                                           #
# Purpose: Display information about files/folders                            #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FileInfo.py

Dialog for displaying information about a path

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import os
import time
import stat
import mimetypes
import wx

# Editra Library Modules
import syntax.syntax as syntax
import syntax.synglob as synglob

#--------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

PERM_MAP = { '0' : '---', '1' : '--x', '2' : '-w-', '3' : '-wx',
             '4' : 'r--', '5' : 'r-x', '6' : 'rw-', '7' : 'rwx'}

#--------------------------------------------------------------------------#

class FileInfoDlg(wx.MiniFrame):
    """Dialog for displaying information about a file"""
    def __init__(self, parent, fname='', ftype=None, bmp=wx.NullBitmap):
        """Create the dialog with the information of the given file
        @param parent: Parent Window
        @keyword fname: File Path
        @keyword ftype: Filetype label (leave None to automatically determine)
        @keyword bmp: wxBitmap

        """
        self._fname = fname.split(os.path.sep)[-1]
        wx.MiniFrame.__init__(self, parent,
                              title="%s  %s" % (self._fname, _("Info")),
                              style=wx.DEFAULT_DIALOG_STYLE)

        # Attributes
        self._file = fname
        self._ftype = ftype
        self.panel = wx.Panel(self)
        if bmp.IsNull():
            bmp = FileIcon.Image.GetBitmap()
        self._bmp = wx.StaticBitmap(self.panel, bitmap=bmp)
        self._ftxt = wx.StaticText(self.panel)

        try:
            fstat = os.stat(fname)
            perm = oct(stat.S_IMODE(fstat[stat.ST_MODE])).lstrip('0')
            permstr = ''
            for bit in perm:
                permstr += (PERM_MAP.get(bit, '---') + " ")
            self._fstat = dict(mtime=time.asctime(time.localtime(fstat[stat.ST_MTIME])),
                               ctime=time.asctime(time.localtime(fstat[stat.ST_CTIME])),
                               size=CalcSize(fstat[stat.ST_SIZE]),
                               perm=permstr)
        except Exception, msg:
            self.__DoErrorLayout(str(msg))
        else:
            self.__DoLayout()

        self.panel.SetAutoLayout(True)
        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(fsizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __DoErrorLayout(self, msg):
        """Set the dialogs display up for when an error happened in
        the stat call.

        """
        # Top Info
        top = wx.BoxSizer(wx.HORIZONTAL)
        head = wx.BoxSizer(wx.VERTICAL)
        bmp = wx.StaticBitmap(self.panel, bitmap=FileIcon.Image.GetBitmap())
        lbl = wx.StaticText(self.panel, label=self._fname)
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        if wx.Platform == '__WXMSW__':
            font.SetPointSize(12)
        else:
            font.SetPointSize(13)
        lbl.SetFont(font)
        head.Add(lbl, 0, wx.ALIGN_LEFT)

        errlbl = wx.StaticText(self.panel, label=_("File Stat Failed"))
        if wx.Platform == '__WXMSW__':
            font.SetPointSize(10)
        else:
            font.SetPointSize(11)
        font.SetWeight(wx.FONTWEIGHT_LIGHT)
        errlbl.SetFont(font)
        head.Add((5, 5), 0)
        head.Add(errlbl, 0, wx.ALIGN_LEFT)
        top.AddMany([((5, 5),), (bmp, 0, wx.ALIGN_LEFT), ((12, 12),), 
                     (head, 0, wx.ALIGN_LEFT), ((5, 5),)])

        # Central Area
        csizer = wx.BoxSizer(wx.VERTICAL)
        errbmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_CMN_DIALOG)
        errbmp = wx.StaticBitmap(self.panel, bitmap=errbmp)
        errmsg = wx.StaticText(self.panel, label=msg)
        errmsg.SetFont(font)
        errmsg.Wrap(225)
        errsz = wx.BoxSizer(wx.HORIZONTAL)
        errsz.AddMany([((8, 8)), (errmsg, 0, wx.ALIGN_LEFT), ((8, 8))])
        csizer.AddMany([((10, 10)), (top, 1, wx.EXPAND), ((10, 10)),
                        (wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND),
                        ((20, 20)), (errbmp, 0, wx.ALIGN_CENTER),
                        ((10, 10)), (errsz, 0, wx.ALIGN_CENTER), ((10, 10)),
                        (wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND),
                        ((10, 10))])
        self.panel.SetSizer(csizer)

    def __DoLayout(self):
        """Layout the dialog"""
        # Top Info
        top = wx.BoxSizer(wx.HORIZONTAL)
        head = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(self.panel, label=self._fname)
        fszlbl = wx.StaticText(self.panel, label=self._fstat['size'])
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        if wx.Platform == '__WXMSW__':
            font.SetPointSize(12)
        else:
            font.SetPointSize(13)
        lbl.SetFont(font)
        fszlbl.SetFont(font)
        head.Add(lbl, 0, wx.ALIGN_LEFT)
        head.AddStretchSpacer(2)
        head.Add(fszlbl, 1, wx.ALIGN_RIGHT)

        modlbl = wx.StaticText(self.panel, label="%s:  %s" % (_("Modified"),
                                                        self._fstat['mtime']))
        if wx.Platform == '__WXMSW__':
            font.SetPointSize(10)
        else:
            font.SetPointSize(11)

        font.SetWeight(wx.FONTWEIGHT_LIGHT)
        modlbl.SetFont(font)
        lblsize = wx.BoxSizer(wx.VERTICAL)
        lblsize.AddMany([(head, 1, wx.ALIGN_LEFT), ((3, 3),), 
                         (modlbl, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)])

        top.AddMany([((5, 5)),
                     (self._bmp, 0, wx.ALIGN_LEFT),
                     ((12, 12)), (lblsize, 0, wx.ALIGN_LEFT), ((5, 5))])

        # Central Info
        center = wx.FlexGridSizer(5, 2, 3, 5)
        tlbl = wx.StaticText(self.panel, label=_("Kind") + ":")

        if self._ftype is None:
            self._ftxt.SetLabel(GetFileType(self._file))
        else:
            self._ftxt.SetLabel(self._ftype)

        szlbl = wx.StaticText(self.panel, label=_("Size") + ":")
        szval = wx.StaticText(self.panel, label=self._fstat['size'])
        loclbl = wx.StaticText(self.panel, label=_("Where") + ":")
        locval = wx.StaticText(self.panel, label=self._FormatLabel(self._file))
        ctime = wx.StaticText(self.panel, label=_("Created") + ":")
        cval = wx.StaticText(self.panel, label=self._fstat['ctime'])
        mtime = wx.StaticText(self.panel, label=_("Modified") + ":")
        mval = wx.StaticText(self.panel, label=self._fstat['mtime'])
        perm = wx.StaticText(self.panel, label=_("Permissions") + ":")
        pval = wx.StaticText(self.panel, label=self._fstat['perm'])
        for lbl in (tlbl, self._ftxt, szlbl, szval, loclbl, 
                    locval, ctime, cval, mtime, mval, perm, pval):
            lbl.SetFont(font)
            lbl.Wrap(200)
        center.AddMany([(tlbl, 0, wx.ALIGN_RIGHT), (self._ftxt, 0, wx.ALIGN_LEFT),
                        (szlbl, 0, wx.ALIGN_RIGHT), (szval, 0, wx.ALIGN_LEFT),
                        (loclbl, 0, wx.ALIGN_RIGHT), (locval, 0, wx.ALIGN_LEFT),
                        (ctime, 0, wx.ALIGN_RIGHT), (cval, 0, wx.ALIGN_LEFT),
                        (mtime, 0, wx.ALIGN_RIGHT), (mval, 0, wx.ALIGN_LEFT),
                        (perm, 0, wx.ALIGN_RIGHT), (pval, 0, wx.ALIGN_LEFT)])
        cmain = wx.BoxSizer(wx.HORIZONTAL)
        cmain.AddMany([((8, 8),), (center, 0, wx.ALIGN_CENTER), ((8, 8),)])

        # Main Layout
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([((10, 10)), (top, 0, wx.ALIGN_CENTER), ((10, 10),),
                        (wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 1,
                                                    wx.EXPAND|wx.ALIGN_CENTER),
                        ((10, 10),), (cmain, 0, wx.ALIGN_TOP|wx.ALIGN_CENTER),
                        ((10, 10),),
                        (wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 1,
                                                    wx.EXPAND|wx.ALIGN_CENTER),
                        ((10, 10),),
                        ])
        self.panel.SetSizer(msizer)

    def _FormatLabel(self, lbl):
        """Format the label to a suitable width wrapping as necessary"""
        lbl_len = len(lbl)
        part = self.GetTextExtent(lbl)[0] / 200
        if part > 1:
            split = lbl_len / part
            pieces = list()
            for chunk in xrange(part):
                if chunk == part - 1:
                    pieces.append(lbl[chunk * split:])
                else:
                    pieces.append(lbl[chunk * split:(chunk * split + split)])
            return os.linesep.join(pieces)
        return lbl

    def OnClose(self, evt):
        """Destroy ourselves on closer"""
        self.Destroy()
        evt.Skip()

    def SetBitmap(self, bmp):
        """Set the dialog bitmap
        @param bmp: wxBitmap

        """
        self._bmp.SetBitmap(bmp)
        self._bmp.Refresh()
        self._panel.Layout()

    def SetFileTypeLabel(self, lbl):
        """Set the file type label
        @param lbl: string

        """
        self._ftype = lbl
        self._ftxt.SetLabel(lbl)
        self._panel.Layout()

#-----------------------------------------------------------------------------#
# Utility Functions

def CalcSize(bits):
    """Calculate the best display version of the size of a given file
    1024 = 1KB, 1024KB = 1MB, ...
    @param bits: size of file returned by stat
    @return: formatted string representation of value

    """
    val = ['bytes', 'KB', 'MB', 'GB', 'TB']
    ind = 0
    while bits > 1024:
        bits = float(bits) / 1024.0
        ind += 1

    rval = "%.2f" % bits
    rval = rval.rstrip('.0')
    if not rval:
        rval = '0'
    rval = "%s %s" % (rval, val[min(ind, 4)])
    return rval

def GetFileType(fname):
    """Get what the type of the file is as Editra sees it
    in a formatted string.

    """
    if os.path.isdir(fname):
        return _("Folder")

    eguess = syntax.GetTypeFromExt(fname.split('.')[-1])
    if eguess == synglob.LANG_TXT and fname.split('.')[-1] == 'txt':
        return _("Text Document")
    elif eguess == synglob.LANG_TXT:
        mtype = mimetypes.guess_type(fname)[0]
        if mtype is not None:
            return mtype
        else:
            return _("Unknown")
    else:
        return _("%s Source File") % eguess

#-----------------------------------------------------------------------------#
# Default Icon
from extern.embeddedimage import PyEmbeddedImage

Image = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAABthJ"
    "REFUWIW9l21sVFkZgJ/7Pd8zLdOWQloiIA2WbiqBLWhhdw3IAhuyRqMxq64uv1B/GMJqYvzK"
    "qqkmfqx/3UiC7q4QN5o1UnbRPyVLgdYtCAjdju2Uwhbabmd6O9PpdO7H8Ud7h2lnaLv+8E1u"
    "zj3vnXPe57znfd9zRqJcIseOHXsxGo1W5fP5nOu6xQ+OIwAXT+e6LrZtUygUdE3T3O7u7pP9"
    "/f03K8y5egkGgy2maTpiBXEcR1iWJXK5nBgbGxPJZFJ0d3eL3bt3H/4w9qSlinA43NbT03O5"
    "oaGBdDoNgBAC13WLreM4xb4QAtu2SaVSzMzMEI/HOX78+KGLFy+eWw2AXEYkSWKhLdWhKAqy"
    "LCPLMoqiFPuSJKFpGrFYjImJCUzTpLOzs7O1tfXg/wTgGaz0eIZVVS2+eyC6rhOLxRgaGiIS"
    "idDV1dXZ0tKyIkQZgGVZopJxb/XeqksBvCcQCCCEIJPJEIlEuHLlSueOHTuWhajogVJjnkG3"
    "JA48AE3Tit7wtsHv99Pf38/g4CCWZXH27NnOtra2R0KoSxXV1dWKruvFrXDd+bRzhUC47iJv"
    "2LZDKGigqgqTqSy1tbVks1nOnDnDyMgIwWCQXbt20dHR0XnixImn+/r63l5qrywLDh48uP/0"
    "6dPnFUXBNE0cy0Lz+9Grq3EdB5jPfyc7Q33cRyo1zcR4hnhjPXmhUJjLk0gkGLpxA3t2ltm5"
    "ORobGzEMI3306NHHUqnUvWU9sHXr1ng4HMY0TRRFwRcIYOdymAMDyJqGNZmm1nCItGzm0nWT"
    "F37Yx8c32Jz8js34/TkwdOK2Q9W2baiBAIV8nkwmQ01NTVVTU9OnL126dHJZgLVr18a91DIM"
    "A7/fz8TwMOaXn6chGmBNewsDH32Cb/xxlOvvJWleU8vVbD2dL/+Zw9fOM2FaCOHi/OznRJub"
    "sSYmiMViyLJMLpfzrxgDmqb5AAzDQFEUAHyFAi2BAsqhw5xSW3n5wizbxACnmsdpbdV4IxNk"
    "w2QM4wOTUP8gbjhM1tBxFgqVYRgEAgE0TVtqrhzAsqwcgKIoxYj3r1vLXz73I875d3H15k1+"
    "teMuTwUNHiR0JmerOLAlTu+4Rr69HXfGxhEOuqZh6Dr5hSzy+/0YhlEWc2UAyWTyfXhYjKYn"
    "U3z/lb9zJRVAQqLev4XaDQ5EFLJOlM0HdnI7rfLcrx/Q9ewetoyNku4fJuTzEfL7wedDCIGq"
    "qchyedaXabq7uycymUyxPxeuYn+Dj4vSGxwI/pO3bmn8picMbU1sfuEQd2b8dLzyHx70K7yU"
    "qIP9e1nf+jFq6msxAJ/Ph67rqIpK6cn6SIBkMlnI5/MAFCyLGl2ifUcz6X/0ccT3Lvvb5kik"
    "6/nbhTR/Opei7bnXyZq3ee17Phx5kluBOq637OHUhQQaYPh8xYIFiBW3AJA8V3kb5kQi3Pv8"
    "19i+r4Uv3XufjrONvPhbhTX2X3n1x4+z75Nb4NYgz1h3MXqv8qrSzC97E3zxQDPBUDXZhQJW"
    "Sco8oKqqJMnzP/ZAFKDRdWBgki80zrK+apzEgxDPf7aVffubYFzCHpki2NWLoZnkwptI3A0x"
    "en9s0TyVYqDMA7ZtC89RHrWwHXJ3htHyc4RrdL7ZrnAnHeP1y2v5RPRdmqU8qgY8+yl+/2+D"
    "H/TYfGWPReO6mkXzrMoDpeIFjSRc3A8mcadSzF4e4EhdhiNtGW6PxXjtXzroM1ybinKgt56X"
    "+mf5ae0Ffnd8O1owTi6XWxagUgwgxOJYEbYNd+8iWRZzcwX87wi++pEC4ztruJbaxTPnrzI2"
    "PcxeaZQ3Iwl8l3sxx48SqlvsyVUBWJZVBChts/k8SiaDpRuEJoM0PxnDvHqf0fvDtFfd5CfG"
    "NVpHhsjcGGFQ1YjrKhEe1hOgWFlX9IAnkiThAqFNm1j/1jkkSSJSFeK9xCjf+sXbhKI+/vDt"
    "x2nZ+BnE0JOkbBc34KdOUQisW4dtO4sAVuWBpeLaNqphEN24sagbJc2e9ga++/XDoEQQgPtY"
    "I1EPHLALBWyrgFR+4q8M4BF7rXcT9t73bt/EUzu3AGDbNm5Jnns3ZSHmxwtAkh4d66sCmL+O"
    "C2D+WlawCsj24vshzOe5Bzs/VEIIgbxQV7xFfGiA+VYsTCYX/x94xh+CLh7vSaUCVPz2yC9L"
    "JvBWWwq5VCfLi2/SlWCWSpkHVFWVFg6ORYMrXSaWg60kmqatfB+wbduZmpoiHA4zPT1d1Jf+"
    "PxBCIFyBK9zyolXS9941TSMUClEoFMrO40r+qQ6FQk/Islznuq5NyREaCARkwzBk27ZFPp93"
    "LcsqO14fIaokSblMJvMOkFzlmP+P/BeZah5l10evBAAAAABJRU5ErkJggg==")


