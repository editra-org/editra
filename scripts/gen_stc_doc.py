#!/usr/bin/env python
###############################################################################
# Name: gen_lexer_doc.py                                                      #
# Purpose: Generate html for lexer docuemntation                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Lexer Documentation Generator

Generates html documentation for the STC lexers and style flags.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.stc as stc

#-----------------------------------------------------------------------------#

# Special case lexer to syntax spec mappings
LEXMAP = { 'BASH'     : ['SH',],
           'BATCH'    : ['BAT',],
           'CPP'      : ['C',],
           'F77'      : ['F',],
           'FLAGSHIP' : ['FS',],
           'FORTRAN'  : ['F',],
           'GUI4CLI'  : ['GC',],
           'HASKELL'  : ['HA',],
           'HTML'     : ['H', 'HJ', 'HJA'],
           'INNOSETUP': ['INNO',],
           'LATEX'    : ['TEX',],
           'MAKEFILE' : ['MAKE',],
           'OCTAVE'   : ['MATLAB',],
           'PASCAL'   : ['C',],
           'PERL'     : ['PL',],
           'PROPERTIES' : ['PROPS',],
           'PYTHON'   : ['P',],
           'RUBY'     : ['RB',],
           'SMALLTALK': ['ST',],
           'VB'       : ['B',],
           'VBSCRIPT' : ['B',],
           'VERILOG'  : ['V',],
           'XML'      : ['H',],
          }

#-----------------------------------------------------------------------------#
# HTML objects

class Title(object):
    """Represents a title tag"""
    def __init__(self, title):
        assert isinstance(title, basestring)
        object.__init__(self)

        # Attributes
        self._title = title

    def __str__(self):
        val = "<h3 id=\"%s\">%s:</h3>\n" % (self._title, self._title)
        return val

class LexerLabel(object):
    """Represents a lexer id label"""
    def __init__(self, lexer):
        assert isinstance(lexer, basestring)
        object.__init__(self)

        # Attributes
        self._lexer = lexer

    def __str__(self):
        val = "<h4>Lexer Id: <em>%s</em></h4>\n" % self._lexer
        return val

class UnorderedList(object):
    """Represents a <ul> </ul> list"""
    def __init__(self, items):
        assert isinstance(items, list)
        object.__init__(self)

        # Attributes
        self._items = items

    def __str__(self):
        val = "<ul>\n%s\n</ul>" % self.FormatItems()
        return val

    def FormatItems(self):
        """Format the item list
        @return: string

        """
        tmpl = "<li>%s</li>\n"
        rval = ""
        for item in self._items:
            rval += tmpl % item
        return rval

class Index(object):
    """Represents the link index"""
    def __init__(self, langs):
        """@param langs: list of languages"""
        object.__init__(self)

        # Attrbutes
        self._langs = langs

    def __str__(self):
        """Create the html table"""
        tmpl = "<table cellpadding=\"3px\" cellspacing=\"0\" border=\"0\" width=\"100%%\">"
        tmpl += "<tr valign=\"top\">"
        tmpl += "<td>%s</td><td>%s</td><td>%s</td>\n"
        tmpl += "</tr>\n</table>\n<hr/>\n"
        div = len(self._langs) / 3
        items1 = self.makeLinks(self._langs[:div])
        items2 = self.makeLinks(self._langs[div:div+div])
        items3 = self.makeLinks(self._langs[-1*div:])
        return tmpl % (UnorderedList(items1), UnorderedList(items2), UnorderedList(items3))

    def makeLinks(self, items):
        """Make a list of anchor links
        @param items: list of strings
        @return: list of string

        """
        return ["<a href=\"#%s\">%s</a>" % (item, item) for item in items]

class Intro(object):
    def __init__(self):
        object.__init__(self)

        # Attributes

    def __str__(self):
        rval = "<h1>StyledTextCtrl Quick Reference</h1>"
        rval += "\n<hr/>\n"
        return rval

class SubSection(object):
    """Represents a subsection for a given language type"""
    def __init__(self, lang, lex):
        assert isinstance(lang, basestring)
        object.__init__(self)

        # Attributes
        self.langid = lang.upper()
        self.title = Title(lang.title())
        self.lexer = LexerLabel(lex)

    def __str__(self):
        tmpl = "%s%s%s\n<hr/>"
        styles = self.GetStyleList()
        return tmpl % (self.title, self.lexer, styles)

    def GetStyleList(self):
        """Get the list of styles available for this subsections language
        @return: UnorderedList

        """
        langids = LEXMAP.get(self.langid, [self.langid,])
        slist = list()
        for langid in langids:
            sid = "STC_%s_" % langid
            for item in dir(stc):
                if item.startswith(sid):
                    slist.append(item)
        slist.sort()
        return UnorderedList(slist)

#-----------------------------------------------------------------------------#

def collectLexers():
    """Get all the lexer identifiers
    @return: list of strings

    """
    rlist = list()
    for item in dir(stc):
        if item.startswith('STC_LEX_'):
            rlist.append(item)
    rlist.sort()
    return rlist

def deriveLanguageNames(lexlist):
    """Derive the language names from the lexer identifier list
    @return: list of strings

    """
    rlist = list()
    for item in lexlist:
        lang = item.rsplit('_', 1)[-1]
        rlist.append(lang)
    return rlist

#-----------------------------------------------------------------------------#

def generateOutput():
    """Generates the html output
    @return: list of html objects

    """
    lexers = collectLexers()
    langs = deriveLanguageNames(lexers)
    lang2lex = zip(langs, lexers)
    output = [Intro(), Index([lang.title() for lang in langs]),]
    for lang, lex in lang2lex:
        sub = SubSection(lang, lex)
        output.append(sub)
    return output

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    output = generateOutput()
    f = open('stcdoc.html', 'wb')
    for obj in output:
        f.write(str(obj))
    f.close()
