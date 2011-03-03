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

_BookmarkBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDAQA0GON3MFgAAAEG"
    "SURBVDjL7ZK9SgNBFIW/nd1SO1EbBUHQgD+g+AKSN9E2nY+RztfxOSwCAUEIFlHUsLPB7L3H"
    "YjdjTBqxFG91mLnzzTlzB/4rA+j2+vpJ893tTba8VszF/dU1uQRWg2cU7uAiyMFgfTig2+tr"
    "GRLmIjeDmVGYKGojmBHMoXawmsnuHs8n5ytuE4AyEqoSjxGmEY8VXpUQI0wrqCLvW9uMD4+4"
    "XICkCDZ6BAQmXI19JILUaBMB5y0PTDrHKU4C+OgB97bZmwuCOyaBQ46n/YOX1/SgCfAxHIAc"
    "1LpzgQA5OWJmgMTp2sa3aXxFGD81Qu1BFzlqUzkIznY6K6NMgIvN/V/9gz9Qn2ObnTkNCjcr"
    "AAAAAElFTkSuQmCC")

_BreakpointBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sCGAMVMT9tMisAAAJE"
    "SURBVCjPZdPRSxRRFMfx7+bsdHVnZy+zY46x0RJbDFIR6YNkxBJB9RbiQ0/hHyAS0WP0F4hI"
    "f0NEkIRPZSCx1Bo+SEiWDGKxkMUEY1xdt724g/bgMmrdx8P5XA7n/m5ql8d7HDpvXl9hfv4d"
    "QRAQhhGe5+L7PkND17h5+8PhVlKH8eSERRCsUi6XAcjnXTY2IgAqlQq+f44HD7cTfOxfWJQ2"
    "RWlTHuznwtnTlAf7k1oQrDI5YSXYAHg5fZGp++NcLZUQhQLhwiJ6YS1pUihEGLK9vs7U7CuK"
    "008YHvm0j6vVKr6wkGGIWtcECwpXmAmO9A6aCGkofGFRrVYZxt4fe+7pM0oGuJEgq1JY8ZEd"
    "YsV7dNe7cCNBydjvT8Y2tMKNC3R32OSyEldmMUQmwbFoEKk61IF4C0PXDrArLCSSXNamVzpk"
    "pI0jcgn+o+ukSQPQ4hiusGC7jYWUpOu79J5yyEtJl8hyQtp0cRyAX7ojuWjzu0JICVEbW4UC"
    "+nOTPWGSl5Ie4ZBKd5LOdIKO6QGQoNlF15pYhQKstd95ZGycZdEk1g2yIoMpbdL5bpAOSIkp"
    "HbIiQ0NtsSyajIyNH4RESgfle8yEXwiDr7QarfaQJgiTVqOJqv3gRbiE8j2kdA4W5nkud0fv"
    "EQQrPHo+y8D7GpdkEV94BDpkSdVYJOT86C3Kfh+e5x7N9sfFOwTBCrXaN6LoN3G8g9Y7CGFi"
    "GCau61AsnsH3+7g8MPP/xwB4O1cmDH+i1GZSkzKH553k+o3KkfD8BZeW03dkWsHXAAAAAElF"
    "TkSuQmCC")

_BreakpointActiveBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDAQEEDskn2c0AAAIn"
    "SURBVCjPjZNBSFRRFIa/qTfDFZ/TZXzRwwYawuoiOli6kAQZKqhwE+WijbRwqbmItrqZRS5E"
    "hlYtXUQEibgREySGmCkXQw2N2WWwmEXFXYzxKsWHjtpCmdGC8F8eznf+c869J7DD6C4HND93"
    "mWz2NVprjCnjug5KKbq7e7h+883BVAIH4YlxG62LJBIJABobHVZXywCk02mUOs+Dh2tV+Njf"
    "YEyGickwia4O2s6dIdHVUY1pXWRi3D4MT0/FSaVSrK0UEcZgFnPoyTn05Bynt+OYxRzCGNZW"
    "iqRSKaan4gBYAJlMBiVspDF4X330oocjQgBc7Yc7/Y8Y6b2ItDyUsMlkMtwmvOe88PQZzRY4"
    "ZUGDF8CuHNohAMnZ9zhlQbO1l191tnwPpxIlmS3wPyWznxjpbcPyS7WZHWEjkRxFydkCjrBr"
    "sJCS4O+dI8GPe7oRUtbatqNR/KUN5gcGuOA2cUpECATrCNbXcfz+vSqYHRzE336LHY3Cyr5z"
    "39AwBbFBxV+nQdQTkmGCjSdBRqrganKMde8XBbFB39BwrW0pI3jKZcZ8xOjPbK1v7SN7z+WP"
    "PcErfeOFyeMpF7lfNLDD6O7yUh/5/Ae0Xmbp+Us6cWmXMZRw0b4h75XIYWi9ewOlWmhvj9PS"
    "OlX72+9yt9B6mVLpC+XyDyqVTXx/EyFCWFYIx4kQi51FqRYudc78exgArxYSGPMdz/tZjUl5"
    "Atdt4sq19KHN/wHycs935XJd2QAAAABJRU5ErkJggg==")

_BreakpointDisabledBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sDAQQDD/eqvXcAAAJi"
    "SURBVCjPhZNPSFMBHMc/b27jqdNe9sSndZCSfA0zGztlSMRAyyIPO0gEHRQSrAgRwsgRWOZB"
    "pFsdduoQQSZWWBoRIS2hbI2m9gyrRRaPeNXLHBtzbh3cRAzse/v9+H1+f/kJKXysUc7Yo30X"
    "A4HxS5qmBXXduK8oMqqqCrW1ddQfenEFSAJpACGFz5Ix5IF+x3dNe4/1+Tjrldxfh6ruDHZ0"
    "LnoAE0hnYftAvyM25/evjT8GzAKbgYmss6K1lY7OxWLAsAD2ocHqQBascLvxeJsveL1tj73e"
    "ttnr9z699nibjwD1AHN+P0OD1WPZtvM6zi1E46MPAZCTUqmIrMuiHYBTd0cA6G7cW2FYzQTw"
    "WWw4zMC1QsECJFZBQ9xTYAq6I5n+Z+aekTdzsiFuA8jEl1qB1EpFBz2BcJgN1BN496q7cTeG"
    "dREgbQEKASQksifYQEsZEEC3wApl+5MCsPwHFnb9KruVNazAPEB8OcZYS8v5SqXsaolYhGDL"
    "xZafS86Zk6tkoL19a3x54ripKKCtVFr2XO4lLMZIxqO9BWK+0y4VYttSDFLRKvijp68qai58"
    "CYsxvKfPBoE8CyBIUlHQVBWG9Wl07cP0UnSpC1DAbgV2xPtudJmRr+E7eghTVZAySYUUvpyZ"
    "Ke/NUOitqmkzrqnbo7hRqJHKUUUFLa4TMiNMolPV3ICqOqmpqRacVYMIKXwCkA5ONuVp2kxJ"
    "JPLxhGH8bEomEw/i8cRRUbS7rFY7slxEefl2VNXZ5nIP+4FlYf1XPX1ywKXr3+ZN83cl8BJA"
    "kjZtUpQy46Dn2VJ260D+X/sD6TmP1rU1AAAAAElFTkSuQmCC")

#-----------------------------------------------------------------------------#

__markerId = -1
def NewMarkerId():
    """Get a new marker id
    @note: limited by stc to 16 possible ids. will assert when this threshold
           is passed.

    """
    global __markerId
    __markerId += 1
    assert __markerId < 16, "No more marker Ids available!"
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
        if not cls().IsSet(stc, line):
            for bpoint in cls.__subclasses__():
                if bpoint().IsSet(stc, line):
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

    def IsSet(self, stc, line):
        """Is the marker set on the given line"""
        mask = stc.MarkerGet(line)
        return True in [ bool(1<<marker & mask) for marker in self.GetIds() ]

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
    _ids = [NewMarkerId(),]
    def __init__(self):
        super(Breakpoint, self).__init__()
        self.Bitmap = _BreakpointBmp.Bitmap

class BreakpointDisabled(Breakpoint):
    _ids = [NewMarkerId(),]
    def __init__(self):
        super(Breakpoint, self).__init__()
        self.Bitmap = _BreakpointDisabledBmp.Bitmap

class BreakpointTriggered(Breakpoint):
    _ids = [NewMarkerId(), NewMarkerId()] # compound marker
    def __init__(self):
        super(Breakpoint, self).__init__()
        self.Bitmap = _BreakpointActiveBmp.Bitmap

    def DeleteAll(self, stc):
        """Overrode to handle refresh issue"""
        super(BreakpointTriggered, self).DeleteAll(stc)
        stc.Colourise(0, stc.GetLength())

    def RegisterWithStc(self, stc):
        ids = self.GetIds()
        stc.MarkerDefineBitmap(ids[0], self.Bitmap)
        stc.MarkerDefine(ids[1], wx.stc.STC_MARK_BACKGROUND, 
                         background=self.Background)

    def Set(self, stc, line, delete=False):
        """Add/Delete the marker to the stc at the given line
        @note: overrode to handle refresh issue.

        """
        super(BreakpointTriggered, self).Set(stc, line, delete)
        start = stc.GetLineEndPosition(max(line-1, 0))
        end = stc.GetLineEndPosition(line)
        if start == end:
            start = 0
        stc.Colourise(start, end) # Refresh for background marker

#-----------------------------------------------------------------------------#

class FoldMarker(Marker):
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
