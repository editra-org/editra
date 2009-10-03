# -*- coding: utf-8 -*-
###############################################################################
# Name: synxml.py                                                             #
# Purpose: Syntax Mode Xml Interface                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

""" Interface for extending language support through the use of xml files

@summary: Editra Xml implementation

"""

xml_spec = """
<editra version="1">
   <syntax lang="Python" lexer="STC_LEX_PYTHON">

      <keywordlist>
         <keywords value="0">
             if else elif for while in
         </keywords>
         <keywords value="1">
             str len setattr getattr
         </keywords>
      </keywordlist>

      <syntaxspeclist>
         <syntaxspec value="STC_P_DEFAULT" tag="default_style"/>
         <syntaxspec value="STC_P_WORD" tag="keyword_style"/>
      </syntaxspeclist>

      <propertylist>
         <property value="fold" enable="1"/>
         <property value="tab.timmy.whinge.level" enable="1"/>
      </propertylist>

      <commentpattern value="#"/>

      <!-- TODO -->
      <extensionlist>
         <extension method="AutoIndenter" source="myextension.py"/>
         <!-- <extension method="StyleText" source="myextension.py"/> -->
      </extensionlist>

   </syntax>

   <launch>
   </launch>
</editra>

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#----------------------------------------------------------------------------#
# Imports
from xml import sax
import wx.stc as stc

#----------------------------------------------------------------------------#
# Tag Definitions
EXML_START       = u"editra"
EXML_SYNTAX      = u"syntax"
EXML_KEYWORDLIST = u"keywordlist"
EXML_KEYWORDS    = u"keywords"
EXML_SYNSPECLIST = u"syntaxspeclist"
EXML_SYNTAXSPEC  = u"syntaxspec"
EXML_PROPERYLIST = u"propertylist"
EXML_PROPERTY    = u"property"
EXML_COMMENTPAT  = u"commentpattern"
EXML_FEATURELIST = u"extensionlist"
EXML_FEATURE     = u"extension"

# Attributes
EXML_ENABLE  = u"enable"
EXML_LANG    = u"language"
EXML_LEXER   = u"lexer"
EXML_METHOD  = u"method"
EXML_SOURCE  = u"source"
EXML_TAG     = u"tag"
EXML_VALUE   = u"value"
EXML_VERSION = u"version"

#----------------------------------------------------------------------------#

class EditraXml(sax.ContentHandler):
    """Base class for all Editra syntax xml objects"""
    def __init__(self):
        sax.ContentHandler.__init__(self)

        # Attributes
        self.name = u''             # Tag name

        self._context = None         # Current parse context
        self._reg_handler = dict()   # Registered parse handlers

    #---- Internal Parser Api ----#

    def startElement(self, name, attrs):
        if self._context is not None:
            # Delegate to current context
            self._context.startElement(name, attrs)
        elif name in self._reg_handler:
            self._context = self._reg_handler.get(name)
            self._context.startElement(name, attrs)
        else:
            # Unknown tag
            # raise?
            pass

    def endElement(self, name):
        if self._context is not None:
            if self._context.Name == name:
                self._context = None
            else:
                # Delegate to registered handler
                self._context.endElement(name)
        else:
            # Unknown tag ending
            pass

    def characters(self, chars):
        if not chars.isspace():
            if self._context is not None:
                self._context.characters(chars)
            else:
                # No current context or context is self
                pass

    #---- External Api ----#

    @property
    def Context(self):
        return self._context

    def GetHandler(self, tag):
        """Get the handler associated with the given tag
        @param tag: string
        @return: EditraXml object or None

        """
        return self.reg_handler.get(tag, None)

    def GetName(self):
        """Get the tag name for the handler
        @return: string

        """
        return self.name

    @property
    def Name(self):
        return self.name

    def SetName(self, tag):
        """Set this handlers tag name used for identifying the open and
        end tags.
        @param tag: string

        """
        self.name = tag

    def RegisterHandler(self, handler):
        """Register a handler for a tag. Parsing will be delegated to the
        the registered handler untill its end tag is encountered.
        @param handler: EditraXml instance

        """
        tag = handler.GetName()
        assert tag not in self._reg_handler, "%s already registered!" % tag
        self._reg_handler[tag] = handler

#----------------------------------------------------------------------------#

class FileTypeHandler(EditraXml):
    """Main Xml interface to extending filetype handling support"""
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self._start = False
        self._version = 0
        self.syntax = Syntax()

        # Setup
        self.SetName(EXML_START)
        self.RegisterHandler(self.syntax)

    def startElement(self, name, attrs):
        if self._start:
            EditraXml.startElement(self, name, attrs)
        elif name == EXML_START:
            self._version = attrs.get(EXML_VERSION, 0)
            self._start = True

    def endElement(self, name):
        if name == EXML_START:
            self._start = False
        else:
            EditraXml.endElement(self, name)

    #---- Get External Api ----#

    # Properties
    @property
    def CommentPattern(self):
        return self.GetCommentPattern()

    @property
    def Keywords(self):
        return self.GetKeywords()

    @property
    def Properties(self):
        return self.GetProperties()

    @property
    def SyntaxSpec(self):
        return self.GetSyntaxSpec()

    # Getters
    def GetCommentPattern(self):
        """Get the comment pattern list
        @return: list of strings

        """
        return self.syntax.GetCommentPattern()

    def GetKeywords(self):
        """Get the keyword list
        @return: list of tuples [(idx, ['word', 'word2',]),]

        """
        kwxml = self.syntax.GetKeywordXml()
        return kwxml.GetKeywords()

    def GetFeature(self, fet):
        """Get the callable associated with the given feature
        @param fet: string
        @return: callable or None

        """
        fetxml = self.syntax.GetFeatureXml()
        return fetxml.GetFeature(fet)

    def GetSyntaxSpec(self):
        """Get the syntax spec
        @return: list of tuples [(style_id, "style_tag")]

        """
        spxml = self.syntax.GetSyntaxSpecXml()
        return spxml.GetStyleSpecs()

    def GetProperties(self):
        """Get the property defs
        @return: list of tuples [("fold", "1"),]

        """
        propxml = self.syntax.GetPropertiesXml()
        return propxml.GetProperties()

#----------------------------------------------------------------------------#

class Syntax(EditraXml):
    """Syntax definition for intializing a Scintilla Lexer"""
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self.language = u"Plain Text"
        self.lexer = stc.STC_LEX_NULL

        # Sub Xml Objects
        self.keywords = KeywordList()
        self.synspec = SyntaxSpecList()
        self.props = PropertyList()
        self.comment = list()

        # Setup
        self.SetName(EXML_SYNTAX)
        self.RegisterHandler(self.keywords)
        self.RegisterHandler(self.synspec)
        self.RegisterHandler(self.props)

    def startElement(self, name, attrs):
        """Parse the Syntax Xml"""
        if name == EXML_COMMENTPAT:
            self.comment = attrs.get(EXML_VALUE, '').split()
        elif name == self.Name:
            lang = attrs.get(EXML_LANG, u"Plain Text")
            lexer = attrs.get(EXML_LEXER, 'STC_LEX_NULL')
            lexval = getattr(stc, lexer, None)
            assert lexval is not None, "Invalid Lexer: %s" % lexer
            self.language = lang
            self.lexer = lexval
        else:
            EditraXml.startElement(self, name, attrs)

    #---- External Api ----#

    def GetCommentPattern(self):
        """Get the comment pattern
        @return: list of strings ["/*", "*/"]

        """
        return self.comment

    def GetKeywordXml(self):
        """Get the Keyword Xml object"""
        return self.keywords

    def GetLanguage(self):
        """Get the language description/name
        @return: string

        """
        return self.language

    def GetLexer(self):
        """Get the lexer to use for this language
        @return: stc.STC_LEX_FOO

        """
        return self.lexer

    def GetSyntaxSpecXml(self):
        """Get the Syntax Spec Xml object"""
        return self.synspec

    def GetPropertiesXml(self):
        """Get the properties xml object"""
        return self.props

#----------------------------------------------------------------------------#

class KeywordList(EditraXml):
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self._current = None
        self._keywords = dict() # { index : word_list }

        # Setup
        self.SetName(EXML_KEYWORDLIST)

    def startElement(self, name, attrs):
        if name == EXML_KEYWORDS:
            idx = attrs.get(EXML_VALUE, None)
            assert idx is not None, "value attribute not set"
            idx = int(idx)
            assert idx not in self._keywords, "Duplicate index set %d" % idx
            self._keywords[idx] = list()
            self._current = self._keywords[idx]
        else:
            pass

    def endElement(self, name):
        if name == EXML_KEYWORDS:
            self._current = None

    def characters(self, chars):
        chars = chars.strip().split()
        if self._current is not None:
            if len(chars):
                self._current.extend(chars)

    #---- External Api ----#

    def GetKeywords(self):
        """Get the list of keyword strings
        @return: list of tuples [(kw_idx, [word1, word2,])]

        """
        keys = sorted(self._keywords.keys())
        keywords = [ (idx, self._keywords[idx]) for idx in keys ]
        return keywords

    def GetKeywordList(self, idx):
        """Get the list of keywords associated with the given index
        @return: list of strings

        """
        return self._keywords.get(idx, None)

#----------------------------------------------------------------------------#

class SyntaxSpecList(EditraXml):
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self._specs = list()

        # Setup
        self.SetName(EXML_SYNSPECLIST)

    def startElement(self, name, attrs):
        """Parse all syntaxspec elements in the list"""
        if name == EXML_SYNTAXSPEC:
            lid = attrs.get(EXML_VALUE, '')
            assert len(lid), "Style Id not specified"
            if lid.isdigit():
                style_id = int(lid)
            else:
                # Scintilla Value
                style_id = getattr(stc, lid, None)
                assert style_id is not None, "Invalid STC Value: %s" % lid

            self._specs.append((style_id, attrs.get(EXML_TAG, 'default_style')))
        else:
            # Unknown Tag
            # Raise?
            pass

    #---- External Api ----#

    def GetStyleSpecs(self):
        """Get the list of keyword strings
        @return: list of tuples [(style_id, "style_tag"),]

        """
        return self._specs

#----------------------------------------------------------------------------#

class PropertyList(EditraXml):
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self.properties = list()

        # Setup
        self.SetName(EXML_PROPERYLIST)

    def startElement(self, name, attrs):
        if name == EXML_PROPERTY:
            prop = attrs.get(EXML_VALUE, '')
            if prop:
                enable = attrs.get(EXML_ENABLE, '0')
                self.properties.append((prop, enable))
        else:
            pass

    def endElement(self, name):
        pass

    def characters(self, chars):
        pass

    #---- External Api ----#

    def GetProperties(self):
        return self.properties

#----------------------------------------------------------------------------#

class FeatureList(EditraXml):
    def __init__(self):
        EditraXml.__init__(self)

        # Attributes
        self._features = dict()

        # Setup
        self.SetName(EXML_FEATURELIST)

    def startElement(self, name, attrs):
        if name == EXML_FEATURE:
            meth = attrs.get(EXML_METHOD, None)
            assert meth is not None, "method not defined"
            mod = attrs.get(EXML_SOURCE, None)
            assert mod is not None, "source not defined"
            
            self._features[meth] = mod
        else:
            EditraXml.startElement(self, name, attrs)

    #---- External Api ----#

    def GetFeature(self, fet):
        """Get the callable feature by name
        @param fet: string

        """
        feature = None
        src = self._features.get(fet, None)
        if src is not None:
            feature = src
        return feature

#----------------------------------------------------------------------------#

def LoadHandler():
    """Load and intialize a FileTypeHandler from an on disk xml config file
    @return: FileTypeHandler instance

    """
    # TODO
    pass

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    h = FileTypeHandler()
    sax.parseString(xml_spec, h)
    print h.GetKeywords()
    print h.GetProperties()
    print h.GetSyntaxSpec()
    print h.GetCommentPattern()
