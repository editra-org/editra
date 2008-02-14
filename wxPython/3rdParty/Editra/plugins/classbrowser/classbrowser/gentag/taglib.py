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
    """Code representation objects base class"""
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
    """Class object"""
    def __init__(self, name, line, scope=None):
        Scope.__init__(self, name, line, scope)
        self.methods = list()   # Class Methods
        self.variables = list() # Class Variables

    def GetMethods(self):
        return self.methods

    def GetVariables(self):
        return self.variables

    def AddMethod(self, method):
        """Add a class method to the class object
        @param method: L{Method} object

        """
        self.methods.append(method)

    def AddVariable(self, var):
        """Add a class variable to the class object
        @param var: L{Variable} object

        """
        self.variables.append(var)

class Method(Scope):
    """Class Method object"""
    pass

class Function(Scope):
    """Function object"""
    pass

class Variable(Scope):
    """Variable object"""
    pass


class DocStruct(object):
    """Code Document Representation Object
    Captures the structure of the code in a document, this structure can
    then be easily used to represnt the document in a number of differen't
    formats such as a Tree.

    """
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
        """Get all classes in the document and return them as
        a sorted list.

        """
        return [ self.classes[key] for key in sorted(self.classes.keys()) ]

    def GetFunctions(self):
        """Get all top level functions defined in a document and 
        return them as a sorted list.

        """
        return [ self.functions[key] for key in sorted(self.functions.keys()) ]

    def GetVariables(self):
        """Get all global variables defined in a document and 
        return them as a sorted list.

        """
        return [ self.variables[key] for key in sorted(self.variables.keys()) ]

    def GetLastClass(self):
        """Gets the last class that was added to the document
        @return: L{Class}

        """
        return self.classes.get(self.lastclass, None)
