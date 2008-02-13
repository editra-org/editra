###############################################################################
# Name: taglib.py                                                             #
# Purpose: Common api for tag generators                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE:
AUTHOR:
LANGUAGE: Python
SUMMARY:

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies

#--------------------------------------------------------------------------#
# Globals

#--------------------------------------------------------------------------#
class Scope(object):
    def __init__(self, name, line, scope=None):
        """Create the Scope object
        @param name: Items Name
        @param line: Line in buffer item is found on
        @keyword scope: The name of the scope the object belongs to or None
                        for top level.

        """
        object.__init__(self)
        self.name = name
        self.line = line
        self.scope = scope

    def __str__(self):
        if self.scope is not None:
            return u"%s.%s" % (self.scope, self.name)
        else:
            return self.name

    def GetLine(self):
        return self.line

    def GetName(self):
        return self.name

    def GetScope(self):
        return self.scope

class Class(Scope):
    def __init__(self, name, line, scope=None):
        Scope.__init__(self, name, line, scope)
        self.methods = list()

    def GetMethods(self):
        return self.methods

    def AddMethod(self, method):
        self.methods.append(method)

class Method(Scope):
    pass

class Function(Scope):
    pass

class Variable(Scope):
    pass


class DocStruct(object):
    def __init__(self):
        object.__init__(self)
        self.classes = dict()
        self.variables = dict()
        self.functions = dict()
        self.lastclass = None

    def AddClass(self, cobj):
        """@param cobj: L{Class} object"""
        self.lastclass = cobj.GetName()
        self.classes[self.lastclass] = cobj

    def AddFunction(self, fobj):
        """@param fobj: L{Function} object"""
        self.functions[fobj.GetName] = fobj

    def AddVariable(self, vobj):
        """@param vobj: L{Variable} object"""
        self.variables[vobj.GetName()] = vobj

    def GetClasses(self):
        return [ self.classes[key] for key in sorted(self.classes.keys()) ]

    def GetFunctions(self):
        return [ self.functions[key] for key in sorted(self.functions.keys()) ]

    def GetLastClass(self):
        """@return: L{Class}"""
        return self.classes.get(self.lastclass, None)
