# -*- coding: utf-8 -*-
###############################################################################
# Name: launchxml.py                                                          #
# Purpose: Launch Xml Interface                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Launch Xml Interface

"""

xml_spec = """
<launch version="1">

   <handler name="Python">

      <commandlist default="python">
         <command name="python" execute="python2.5 -u"/>
         <command name="pylint" execute="/usr/local/bin/pylint"/>
      </commandlist>

      <error pattern="File &quot;(.+)&quot;, line ([0-9]+)"/>  

   </handler>
</launch>
"""

#       <error pattern="File "(.+)", line ([0-9]+)"/>

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
import xml.sax as sax
import os
import sys
sys.path.insert(0, os.path.abspath('../../../src/'))

# Editra Imports
import syntax

#-----------------------------------------------------------------------------#
# Globals

# Tags
EXML_LAUNCH      = u"launch"
EXML_HANDLER     = u"handler"
EXML_COMMANDLIST = u"commandlist"
EXML_COMMAND     = u"command"
EXML_ERROR       = u"error"

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
            self._current = Handler(lang)
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

#-----------------------------------------------------------------------------#

class Handler(syntax.EditraXml):
    """Handler object data"""
    def __init__(self, lang):
        syntax.EditraXml.__init__(self)

        # Attributes
        self._lang = lang
        self._commands = CommandList()
        self._errpat = None

        # Setup
        self.SetName(EXML_HANDLER)
        self.RegisterHandler(self._commands)

    def startElement(self, name, attrs):
        if name == EXML_ERROR:
            pattern = attrs.get(EXML_PATTERN, None)
            if pattern is not None:
                self._errpat = pattern
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

    def GetErrorPattern(self):
        """Get the error pattern string
        @return: string or None

        """
        return self._errpat

#-----------------------------------------------------------------------------#

class CommandList(syntax.EditraXml):
    """Handler object data"""
    def __init__(self):
        syntax.EditraXml.__init__(self)

        # Attributes
        self._commands = dict()

        # Setup
        self.SetName(EXML_COMMANDLIST)

    def startElement(self, name, attrs):
        if name == EXML_COMMAND:
            alias = attrs.get(syntax.EXML_NAME, None)
            cmd = attrs.get(EXML_EXECUTE, None)
            if None not in (alias, cmd):
                self._commands[alias] = cmd

    #---- External Api ----#

    def GetCommands(self):
        return self._commands

#-----------------------------------------------------------------------------#

# Test
if __name__ == '__main__':
    h = LaunchXml()
    sax.parseString(xml_spec, h)
    hndlr = h.GetHandler('Python')
    print hndlr.GetCommands()
    print hndlr.GetErrorPattern()

