###############################################################################
# Name: csscomp.py                                                            #
# Purpose: Simple input assistant for CSS                                     #
# Author: Cody Precord                                                        #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Simple autocompletion support for Cascading Style Sheets.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import re
import wx
import wx.stc

# Local Imports
import completer

#--------------------------------------------------------------------------#
# Standard Html Tags
TAGS = ['!--', 'a', 'abbr', 'accept', 'accesskey', 'acronym', 'action',
        'address', 'align', 'alink', 'alt', 'applet', 'archive', 'area', 'axis',
        'b', 'background', 'base', 'basefont', 'bdo', 'bgcolor', 'big',
        'blockquote', 'body', 'border', 'bordercolor', 'br', 'button',
        'caption', 'cellpadding', 'cellspacing', 'center', 'char', 'charoff',
        'charset', 'checked', 'cite', 'cite', 'class', 'classid', 'clear',
        'code', 'codebase', 'codetype', 'col', 'colgroup', 'color', 'cols',
        'colspan', 'compact', 'content', 'coords', 'data', 'datetime', 'dd',
        'declare', 'defer', 'del', 'dfn', 'dir', 'dir', 'disabled', 'div', 'dl',
        'dt', 'dtml-call', 'dtml-comment', 'dtml-if', 'dtml-in', 'dtml-let',
        'dtml-raise', 'dtml-tree', 'dtml-try', 'dtml-unless', 'dtml-var',
        'dtml-with', 'em', 'enctype', 'face', 'fieldset', 'font', 'for', 'form',
        'frame', 'gutter', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head',
        'headers', 'height', 'hr', 'href', 'hreflang', 'hspace', 'html',
        'http-equiv', 'i', 'id', 'iframe', 'img', 'input', 'ins', 'isindex',
        'ismap', 'kbd', 'label', 'lang', 'language', 'legend', 'li', 'link',
        'link', 'longdesc', 'lowsrc', 'map', 'marginheight', 'marginwidth',
        'maxlength', 'menu', 'meta', 'method', 'multiple', 'name', 'nohref',
        'noscript', 'nowrap', 'object', 'ol', 'optgroup', 'option', 'p',
        'param', 'pre', 'profile', 'prompt', 'q', 'readonly', 'rel', 'rev',
        'rows', 'rowspan', 'rules', 's', 'samp', 'scheme', 'scope', 'script',
        'scrolling', 'select', 'selected', 'shape', 'size', 'small', 'span',
        'src', 'standby', 'start', 'strike', 'strong', 'style', 'sub',
        'summary', 'sup', 'tabindex', 'table', 'target', 'tbody', 'td', 'text',
        'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'type', 'u',
        'ul', 'url', 'usemap', 'valign', 'value', 'valuetype', 'var', 'version',
        'vlink', 'vspace', 'width', 'wrap', 'xmp']

# Tags that usually have a new line inbetween them
NLINE_TAGS = ('body', 'head', 'html', 'ol', 'style', 'table', 'tbody', 'ul')

# Regular Expressions
RE_LINK_PSEUDO = re.compile('a:(link|visited|active|hover|focus)*')

#--------------------------------------------------------------------------#

class Completer(completer.BaseCompleter):
    """Code completer provider"""
    def __init__(self, stc_buffer):
        completer.BaseCompleter.__init__(self, stc_buffer)

        # Setup
        self.SetAutoCompKeys([ord(':'), ])
        self.SetAutoCompStops(' {}')
        self.SetAutoCompFillups('')
        self.SetCallTipKeys([ord('('), ])
        self.SetCallTipCancel([ord(')'), wx.WXK_RETURN])
        self.SetAutoCompAfter(False) # Insert Text after cursor on completions

    def GetAutoCompList(self, command):
        """Returns the list of possible completions for a
        command string. If namespace is not specified the lookup
        is based on the locals namespace
        @param command: commadn lookup is done on
        @keyword namespace: namespace to do lookup in

        """
        buff = self.GetBuffer()
        keywords = buff.GetKeywords()
        if command in [None, u'']:
            return keywords

        cpos = buff.GetCurrentPos()
        cline = buff.GetCurrentLine()
        tmp = buff.GetLine(cline).rstrip()

        # Check for the case of a pseudo class
        if IsPsuedoClass(command, tmp):
            return [u'link', u'visited', u'active', u'hover', u'focus']

        return keywords

    def GetCallTip(self, command):
        """Returns the formated calltip string for the command.
        If the namespace command is unset the locals namespace is used.

        """
        if command == u'url':
            return u'url(\'../path\')'
        else:
            return u''

    def ShouldCheck(self, cpos):
        """Should completions be attempted
        @param cpos: current buffer position
        @return: bool

        """
        buff = self.GetBuffer()
        rval = True
        if buff is not None:
            if buff.IsComment(cpos):
                rval =  False
        return rval

#--------------------------------------------------------------------------#

def IsPsuedoClass(cmd, line):
    """Check the line to see if its a link pseudo class
    @param cmd: current command
    @param line: line of the command
    @return: bool

    """
    if cmd.endswith(u':'):
        token = line.split()[-1]
        pieces = token.split(u":")
        if pieces[0] == 'a':
            return True
    return False
