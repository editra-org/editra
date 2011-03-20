# -*- coding: utf-8 -*-
###############################################################################
# Name: launchxml.py                                                          #
# Purpose: Launch Xml Interface                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Launch Xml Interface
Interface to add new filetype support to launch or to override existing support.

"""

xml_spec = """
<launch version="1">

   <handler name="Python" id="ID_LANG_PYTHON">

      <commandlist default="python">
         <command name="python" execute="python2.5 -u"/>
         <command name="pylint" execute="/usr/local/bin/pylint"/>
      </commandlist>

      <error pattern="File &quot;(.+)&quot;, line ([0-9]+)"/>  

   </handler>

</launch>
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import xml.sax as sax
import re
import os
import sys

# Editra Imports
import syntax
from syntax import synglob

#-----------------------------------------------------------------------------#
# Globals

# Tags
EXML_LAUNCH      = u"launch"
EXML_HANDLER     = u"handler"
EXML_COMMANDLIST = u"commandlist"
EXML_COMMAND     = u"command"
EXML_ERROR       = u"error"
EXML_HOTSPOT     = u"hotspot"

# Attributes
EXML_DEFAULT = u"default"
EXML_EXECUTE = u"execute"
EXML_PATTERN = u"pattern"

#-----------------------------------------------------------------------------#

class LaunchXml(syntax.EditraXml):
    """Launch Xml Handler"""
    def __init__(self):
        syntax.EditraXml.__init__(self)

        # Attributes
        self._current = None
        self._handlers = dict()

        # Setup
        self.SetName(EXML_LAUNCH)

    #---- Xml Implementation ----#

    def startElement(self, name, attrs):
        if name == EXML_HANDLER:
            lang = attrs.get(syntax.EXML_NAME, None)
            assert lang is not None, "lang attribute must be defined"
            id_ = attrs.get(syntax.EXML_ID, None)
            assert id_ is not None, "lang id is not specified"
            assert hasattr(synglob, id_), "Undefined language id: %s" % id_
            self._current = Handler(lang, getattr(synglob, id_))
            self._handlers[lang] = self._current
        elif self._current is not None:
            self._current.startElement(name, attrs)
        else:
            pass

    def endElement(self, name):
        if name == EXML_HANDLER:
            self._current = None
        elif self._current is not None:
            self._current.endElement(name)
        else:
            pass

    #---- End Xml Implementation ----#

    #---- External Api ----#
    
    def GetHandler(self, name):
        """Get a handler by name
        @return: Handler instance or None

        """
        return self._handlers.get(name, None)

    def GetHandlers(self):
        """Get the whole dictionary of handlers
        @return: dict(name=Handler)

        """
        return self._handlers

    def HasHandler(self, name):
        """Is there a handler for the given file type
        @return: bool

        """
        return name in self._handlers

#-----------------------------------------------------------------------------#

class Handler(syntax.EditraXml):
    """Handler object data"""
    def __init__(self, lang, id_):
        """Create a new handler
        @param lang: language name string
        @param id_: language id (int)

        """
        syntax.EditraXml.__init__(self)

        # Attributes
        self._lang = lang
        self._langid = id_
        self._commands = CommandList()
        self._errpat = None
        self._hotspot = None

        # Setup
        self.SetName(EXML_HANDLER)
        self.RegisterHandler(self._commands)

    def startElement(self, name, attrs):
        if name == EXML_ERROR:
            pattern = attrs.get(EXML_PATTERN, None)
            if pattern is not None:
                self._errpat = re.compile(pattern)
        elif name == EXML_HOTSPOT:
            pattern = attrs.get(EXML_PATTERN, None)
            if pattern is not None:
                self._hotspot = re.compile(pattern)
        else:
            syntax.EditraXml.startElement(self, name, attrs)

    #---- External Api ----#

    def GetCommands(self):
        """Get the dictionary of commands
        @return: dict(alias="command string")

        """
        cmdxml = self.GetCommandsXml()
        return cmdxml.GetCommands()

    def GetCommandsXml(self):
        """Get the CommandList Xml object
        @return: CommandList

        """
        return self._commands

    def GetDefaultCommand(self):
        """Get the default command
        @return: string

        """
        cmdxml = self.GetCommandsXml()
        return cmdxml.GetDefault()

    def GetErrorPattern(self):
        """Get the error pattern object
        @return: re object or None

        """
        return self._errpat

    def GetHotSpotPattern(self):
        """Get the hotspot pattern object
        @return: re object or None

        """
        return self._hotspot

    def GetLang(self):
        """Get the language identifier string
        @return: string

        """
        return self._lang

    def GetLangId(self):
        """Get the language identifier
        @return: int

        """
        return self._langid

#-----------------------------------------------------------------------------#

class CommandList(syntax.EditraXml):
    """Handler object data"""
    def __init__(self):
        syntax.EditraXml.__init__(self)

        # Attributes
        self._default = u''
        self._commands = dict()

        # Setup
        self.SetName(EXML_COMMANDLIST)

    def startElement(self, name, attrs):
        if name == EXML_COMMAND:
            alias = attrs.get(syntax.EXML_NAME, None)
            cmd = attrs.get(EXML_EXECUTE, None)
            if None not in (alias, cmd):
                self._commands[alias] = cmd
        elif name == EXML_COMMANDLIST:
            default = attrs.get(EXML_DEFAULT, None)
            assert default is not None, "Default attribute not specified!"
            self._default = default

    #---- External Api ----#

    def GetCommands(self):
        """Get the mapping of command aliases to commands
        @return: dict

        """
        return self._commands

    def GetDefault(self):
        """Get the default command
        @return: string

        """
        return self._default

#-----------------------------------------------------------------------------#

# Test
#if __name__ == '__main__':
#    h = LaunchXml()
##    sax.parseString(xml_spec, h)
#    f = open("launch.xml", 'rb')
#    txt = f.read()
#    f.close()
#    sax.parseString(txt, h)
#    hndlr = h.GetHandler('Python')
#    print hndlr.GetCommands()
#    print hndlr.GetErrorPattern()
#    print hndlr.GetDefaultCommand()
#    print hndlr.GetHotSpotPattern()

#    print h.GetHandlers()

#    hndlr = h.GetHandler('C')
#    print hndlr.GetCommands()
