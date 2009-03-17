###############################################################################
# Name: autocomp.py                                                           #
# Purpose: Provides the front end interface for autocompletion services for   #
#          the editor.                                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Provides an interface/service for getting autocompletion/calltip data
into an stc control. This is a data provider only it does not do provide
any UI functionality or calls. The user called object from this library
is intended to be the AutoCompService. This service provides the generic
interface into the various language specific autocomplete services, and
makes the calls to the other support objects/functions in this library.

@summary: Autocompletion support interface implementation

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx.stc as stc

# TODO: Make dynamic load mechanism and manager for completer classes.
#--------------------------------------------------------------------------#

class AutoCompService(object):
    """Interface to retrieve and provide autcompletion and
    calltip information to an stc control. The plain text
    (empty) completion provider is built in. All other provders
    are loaded from external modules on request.

    """
    def __init__(self):
        """Initializes the autocompletion service
        @param parent: parent of this service object

        """
        object.__init__(self)

    @staticmethod
    def GetCompleter(buff):
        lex_value = buff.GetLexer()
        if lex_value == stc.STC_LEX_PYTHON:
            import pycomp
            completer = pycomp.Completer(buff)
        elif lex_value in (stc.STC_LEX_HTML, stc.STC_LEX_XML):
            import htmlcomp
            completer = htmlcomp.Completer(buff)
        elif lex_value == stc.STC_LEX_CSS:
            import csscomp
            completer = csscomp.Completer(buff)
        else:
            import simplecomp
            completer = simplecomp.Completer(buff)

        return completer
