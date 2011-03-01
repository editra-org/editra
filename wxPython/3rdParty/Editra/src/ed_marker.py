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
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
import wx
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

class Marker(object):
    """Marker Base class"""
    def __init__(self, line, handle=-1):
        super(Marker, self).__init__()

        # Attributes
        self._line = line
        self._handle = handle

    Line = property(lambda self: self._line,
                    lambda self, line: setattr(self, '_line', line))
    Handle = property(lambda self: self._handle,
                      lambda self, handle: setattr(self, '_handle', handle))

    @staticmethod
    def GetBitmap():
        return wx.NullBitmap

#-----------------------------------------------------------------------------#

class BookMark(Marker):
    """Class to store bookmark data"""
    def __init__(self, fname, line, handle=-1):
        super(BookMark, self).__init__(line, handle)

        # Attributes
        self._name = u""        # Bookmark alias name
        self._fname = fname

    def __eq__(self, other):
        return (self.FileName, self.Line) == (other.FileName, other.Line)

    #---- Properties ----#
    Name = property(lambda self: self._name,
                    lambda self, name: setattr(self, '_name', name))
    FileName = property(lambda self: self._fname,
                        lambda self, name: setattr(self, '_fname', name))

    @staticmethod
    def GetBitmap():
        return _BookmarkBmp.Bitmap

#-----------------------------------------------------------------------------#

class Breakpoint(Marker):
    @staticmethod
    def GetBitmap():
        return _BreakpointBmp.Bitmap

class BreakpointDisabled(Breakpoint):
    @staticmethod
    def GetBitmap():
        return _BreakpointDisabledBmp.Bitmap

class BreakpointTriggered(Breakpoint):
    @staticmethod
    def GetBitmap():
        return _BreakpointActiveBmp.Bitmap
