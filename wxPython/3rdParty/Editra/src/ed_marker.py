###############################################################################
# Name: ed_marker.py                                                          #
# Purpose: StyledTextCtrl Markers                                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Classes to represent Markers and associated data in a StyledTextCtrl

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
import wx
import wx.stc
from extern.embeddedimage import PyEmbeddedImage

# NOTE: Must be 1 char per pixel for Scintilla to display
_BookmarkBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDAQA0GON3MFgAAAEG"
    "SURBVDjL7ZK9SgNBFIW/nd1SO1EbBUHQgD+g+AKSN9E2nY+RztfxOSwCAUEIFlHUsLPB7L3H"
    "YjdjTBqxFG91mLnzzTlzB/4rA+j2+vpJ893tTba8VszF/dU1uQRWg2cU7uAiyMFgfTig2+tr"
    "GRLmIjeDmVGYKGojmBHMoXawmsnuHs8n5ytuE4AyEqoSjxGmEY8VXpUQI0wrqCLvW9uMD4+4"
    "XICkCDZ6BAQmXI19JILUaBMB5y0PTDrHKU4C+OgB97bZmwuCOyaBQ46n/YOX1/SgCfAxHIAc"
    "1LpzgQA5OWJmgMTp2sa3aXxFGD81Qu1BFzlqUzkIznY6K6NMgIvN/V/9gz9Qn2ObnTkNCjcr"
    "AAAAAElFTkSuQmCC")

_ArrowBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAQCAYAAADJViUEAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDAQEBO+Lj6asAAADR"
    "SURBVCjPpZItEgIxDIUfTA+B3CNEItsbrOAQDIojLA6J4hSI3KDBIeOwOygEzOwNFgP7A/2B"
    "Ia5pvte+eQH+qEmoycytqgIAiAhlWQbnpillEYGqgpnbn+GcgGHmtmmaUXN49n4H59adnaEF"
    "o6oQkeTrMQEzHIgXwXv9EDDvQ2kBwLk+kRF8P+ezPewFi9XT8/DidsnDy62FtRZE1MPHTfzL"
    "szlwPQGV9ODIcyU2CFZWgiAAGCJCURQfUF3XXYQhMLvbLzgEfrWeMTALp0AAeAAUy3GCxymX"
    "vQAAAABJRU5ErkJggg==")

_BreakpointBmp = PyEmbeddedImage(
     "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDEgMQBqh6qrUAAAEf"
    "SURBVDjLpZPNTsJQEIW/CxgJUStWJTRqEBZEiZqY6AOY2FdiaVz2Adz6IiY+gHFHGn82yI9V"
    "UjUWFkKh1lUx1VKvYZZzc76cOzMHpiwR1axWND+qb5iW+BNQrWj+qrLE/maZQnYFgNeew63V"
    "oGY9/IKIn+Kj3UP0wlak3fvnFudXlyGICIl3DtDzxdg/t95szq6/IalAnF9U0bMa9PuxgPXM"
    "PMcbZQDfMC2RCh6214q89Bypye+peS6ad4wdAKhzCgnXl9vdaMTCzGwYMHCHdPsjaUAwvDGg"
    "030n4yWlAc5wEAbU7UeU9LKUvvPRJXKNpVxJCvBkNzmpNUTkIeWS8S4cr8epWRexp4yXnpAc"
    "F+OmLf4RpgT4gPicGKap6ws0jWfqOADTLwAAAABJRU5ErkJggg==")

_BreakpointDisabledBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDEgMRGEtuppcAAABy"
    "SURBVDjLY2TAAcq1pf4j8zuvPmPEpo6RGM2EDMHQjM0AXOIkKcIrT5QNuNQRqxmbekYYg6gA"
    "whLQTAwUgoE3gOJAJCsaG3Xl/5OdkOq1FYlIjbqqmElZQ+l/uabMfxIzExMDw38GBgbGfzgz"
    "EyOl2RkAwXRPWcN07zMAAAAASUVORK5CYII=")

_ErrorBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAc5J"
    "REFUOI11kzFP20AUx3/nEBGLRFUr5CEIieoGhkRtVJVI3uIROiBgYWLzxgco3SulysjIF8iC"
    "UJaspjOtRIEODKZZihBClcABW0I5d2h8shP3P53e6f977929J4RRIK3PahQLIciTEcd8NAqZ"
    "S5EGtNUorklJy3VzAccHB/z0/QxEA9Lm3ycnPPt+xjxvmpTX16cgxqR50O3mZr8LQ4a9Hk3b"
    "piYlbTWKAYzJzEUpebm/T1FKbS5KidXvc1+tonyflutqiKGEoOW6DHs9nn2fhZUVAMzNTYpS"
    "amASuwtDBt0uTdtGCcFMusTkod4sLlJyHEqOo6uIPI+HTmf6ZyYDS5UKD50Okedl4nnmXEDS"
    "czo7wNL2tj4PggA1/qUMYN40Mz1HnqcredrZwarXGQQBszc32jMD8HRxAcCv01MWdne1OV12"
    "yXGIVleZPTqirJSOiy8Q16Skadv4h4cAvFpb40+/D8DQMCgrhdza4sfYXFleJri85DiK/k1i"
    "W43iD40GVr2uIYkSQKLE/DUM2TMKIjPK7+bmeLuxMQVJ9LrR4PzsjO+Pj+yNRzl3md5bFvfV"
    "Ki+urzOAb7e3nF9d8UkY08uUhqj/rLOIY5050V9UfNMzpyji5gAAAABJRU5ErkJggg==")

#-----------------------------------------------------------------------------#

__markerId = -1
def NewMarkerId():
    """Get a new marker id
    @note: limited by stc to 16 possible ids. will assert when this threshold
           is passed.

    """
    global __markerId
    __markerId += 1
    assert __markerId < 24, "No more marker Ids available!"
    return __markerId

#-----------------------------------------------------------------------------#

class Marker(object):
    """Marker Base class"""
    _ids = list()
    _symbols = list()
    def __init__(self):
        super(Marker, self).__init__()

        # Attributes
        self._line = -1
        self._handle = -1
        self._bmp = wx.NullBitmap
        self._fore = wx.NullColour   # Foreground colour
        self._back = wx.NullColour   # Background colour

    Line = property(lambda self: self._line,
                    lambda self, line: setattr(self, '_line', line))
    Handle = property(lambda self: self._handle,
                      lambda self, handle: setattr(self, '_handle', handle))
    Bitmap = property(lambda self: self._bmp,
                      lambda self, bmp: setattr(self, '_bmp', bmp))
    Foreground = property(lambda self: self._fore,
                          lambda self, fore: setattr(self, '_fore', fore))
    Background = property(lambda self: self._back,
                          lambda self, back: setattr(self, '_back', back))

    @classmethod
    def AnySet(cls, stc, line):
        """Is any breakpoint set on the line"""
        if not cls.IsSet(stc, line):
            # Check subclasses
            for bpoint in cls.__subclasses__():
                if bpoint.IsSet(stc, line):
                    return True
            return False
        else:
            return True

    @classmethod
    def GetIds(cls):
        """Get the list of marker IDs."""
        return cls._ids

    @classmethod
    def GetSymbols(cls):
        """Get the list of symbols"""
        return cls._symbols

    @classmethod
    def IsSet(cls, stc, line):
        """Is the marker set on the given line"""
        mask = stc.MarkerGet(line)
        return True in [ bool(1<<marker & mask) for marker in cls.GetIds() ]

    def Set(self, stc, line, delete=False):
        """Add/Delete the marker to the stc at the given line"""
        for marker in self.GetIds():
            if delete:
                mask = stc.MarkerGet(line)
                if (1<<marker & mask):
                    stc.MarkerDelete(line, marker)
            else:
                handle = stc.MarkerAdd(line, marker)
                if self.Handle < 0:
                    self.Line = line
                    self.Handle = handle

    def DeleteAll(self, stc):
        """Remove all instances of this bookmark from the stc"""
        for marker in self.GetIds():
            stc.MarkerDeleteAll(marker)

    def RegisterWithStc(self, stc):
        """Setup the STC to use this marker"""
        ids = self.GetIds()
        if self.Bitmap.IsNull():
            symbols = self.GetSymbols()
            if len(ids) == len(symbols):
                markers = zip(ids, symbols)
                for marker, symbol in markers:
                    stc.MarkerDefine(marker, symbol,
                                     self.Foreground, self.Background)
        elif len(ids) == 1 and not self.Bitmap.IsNull():
            stc.MarkerDefineBitmap(ids[0], self.Bitmap)
        else:
            assert False, "Invalid Marker!"

#-----------------------------------------------------------------------------#

class Bookmark(Marker):
    """Class to store bookmark data"""
    _ids = [NewMarkerId(),]
    def __init__(self):
        super(Bookmark, self).__init__()

        # Attributes
        self._name = u""        # Bookmark alias name
        self._fname = u""       # Filename
        self.Bitmap = _BookmarkBmp.Bitmap

    def __eq__(self, other):
        return (self.Filename, self.Line) == (other.Filename, other.Line)

    #---- Properties ----#
    Name = property(lambda self: self._name,
                    lambda self, name: setattr(self, '_name', name))
    Filename = property(lambda self: self._fname,
                        lambda self, name: setattr(self, '_fname', name))

#-----------------------------------------------------------------------------#

class Breakpoint(Marker):
    """Marker object to represent a breakpoint in the EditraBaseStc"""
    _ids = [NewMarkerId(),]
    def __init__(self):
        super(Breakpoint, self).__init__()
        self.Bitmap = _BreakpointBmp.Bitmap

class BreakpointDisabled(Breakpoint):
    """Marker object to represent a disabled breakpoint in the EditraBaseStc"""
    _ids = [NewMarkerId(),]
    def __init__(self):
        super(BreakpointDisabled, self).__init__()
        self.Bitmap = _BreakpointDisabledBmp.Bitmap

class BreakpointStep(Breakpoint):
    """Marker object to represent debugger step breakpoint in the EditraBaseStc"""
    _ids = [NewMarkerId(), NewMarkerId()]
    def __init__(self):
        super(BreakpointStep, self).__init__()
        self.Bitmap = _ArrowBmp.Bitmap

    def DeleteAll(self, stc):
        """Overrode to handle refresh issue"""
        super(BreakpointStep, self).DeleteAll(stc)
        stc.Colourise(0, stc.GetLength())

    def RegisterWithStc(self, stc):
        """Register this compound marker with the given StyledTextCtrl"""
        ids = self.GetIds()
        stc.MarkerDefineBitmap(ids[0], self.Bitmap)
        stc.MarkerDefine(ids[1], wx.stc.STC_MARK_BACKGROUND, 
                         background=self.Background)

    def Set(self, stc, line, delete=False):
        """Add/Delete the marker to the stc at the given line
        @note: overrode to ensure only one is set in a buffer at a time

        """
        self.DeleteAll(stc)
        super(BreakpointStep, self).Set(stc, line, delete)
        start = stc.GetLineEndPosition(max(line-1, 0))
        end = stc.GetLineEndPosition(line)
        if start == end:
            start = 0
        stc.Colourise(start, end) # Refresh for background marker

#-----------------------------------------------------------------------------#

class FoldMarker(Marker):
    """Marker object class for managing the code folding markers"""
    _ids = [wx.stc.STC_MARKNUM_FOLDEROPEN, wx.stc.STC_MARKNUM_FOLDER,
            wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARKNUM_FOLDERTAIL,
            wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARKNUM_FOLDEROPENMID,
            wx.stc.STC_MARKNUM_FOLDERMIDTAIL]
    _symbols = [wx.stc.STC_MARK_BOXMINUS, wx.stc.STC_MARK_BOXPLUS, 
                wx.stc.STC_MARK_VLINE, wx.stc.STC_MARK_LCORNER, 
                wx.stc.STC_MARK_BOXPLUSCONNECTED, 
                wx.stc.STC_MARK_BOXMINUSCONNECTED, wx.stc.STC_MARK_TCORNER]

    def RegisterWithStc(self, stc):
        super(FoldMarker, self).RegisterWithStc(stc)
        stc.SetFoldMarginHiColour(True, self.Foreground)
        stc.SetFoldMarginColour(True, self.Foreground)

#-----------------------------------------------------------------------------#

class ErrorMarker(Marker):
    """Marker object to indicate an error line in the EditraBaseStc"""
    _ids = [NewMarkerId(), NewMarkerId()]
    def __init__(self):
        super(ErrorMarker, self).__init__()
        self.Bitmap = _ErrorBmp.Bitmap

    def DeleteAll(self, stc):
        """Overrode to handle refresh issue"""
        super(ErrorMarker, self).DeleteAll(stc)
        stc.Colourise(0, stc.GetLength())

    def RegisterWithStc(self, stc):
        """Register this compound marker with the given StyledTextCtrl"""
        ids = self.GetIds()
        stc.MarkerDefineBitmap(ids[0], self.Bitmap)
        stc.MarkerDefine(ids[1], wx.stc.STC_MARK_BACKGROUND, 
                         # foreground=self.Foreground, #TODO
                         background=self.Foreground)

    def Set(self, stc, line, delete=False):
        """Add/Delete the marker to the stc at the given line
        @note: overrode to ensure only one is set in a buffer at a time

        """
        super(ErrorMarker, self).Set(stc, line, delete)
        start = stc.GetLineEndPosition(max(line-1, 0))
        end = stc.GetLineEndPosition(line)
        if start == end:
            start = 0
        stc.Colourise(start, end) # Refresh for background marker
