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
# Code Object Base Classes

class Code(object):
    """Code representation objects base class all code types should
    be decendants of this object.

    """
    def __init__(self, name, line, obj="code", scope=None):
        """Create the Code Object
        @param name: Items Name
        @param line: Line in buffer item is found on
        @keyword obj: Object type
        @keyword scope: The name of the scope the object belongs to or None
                        for top level.

        """
        object.__init__(self)
        self.name = name
        self.line = line
        self.type = obj
        self.scope = scope

    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        if self.scope is not None:
            return u"%s.%s" % (self.scope, self.name)
        else:
            return self.name

    def GetLine(self):
        """Returns the line of the code object
        @return: int

        """
        return self.line

    def GetName(self):
        """Get the name of this code object
        @return: string

        """
        return self.name

    def GetScope(self):
        """Get the scope this object belongs to, if it returns None
        the scope of the object is at the global/top level.
        @return: string

        """
        return self.scope


class Scope(Code):
    """Scope object base class used for creating container code types"""
    def __init__(self, name, line, obj="scope", scope=None):
        Code.__init__(self, name, line, obj, scope)
        self.elements = dict()
        self.descript = dict()

    def AddElement(self, obj, element):
        """Add an element to this scope
        @param obj: object indentifier string
        @param element: L{Code} object to add to this scope

        """
        if not self.elements.has_key(obj):
            self.elements[obj] = list()
        self.elements[obj].append(element)

    def GetElementDescription(self, obj):
        """Get the description of a given element
        @param obj: object identifier string

        """
        return self.descript.get(obj, obj)

    def GetElements(self):
        """Return the dictionary of elements contained in this scope
        @return: dict

        """
        return self.elements

    def GetElementType(self, obj):
        """Get the list of element types in this object that match the
        given identifier string.
        @param obj: object identifier string
        @return: list

        """
        return self.elements.get(obj, list())

    def SetElementDescription(self, obj, desc):
        """Set the description string for a type of element
        @param obj: object identifier string
        @param desc: description string

        """
        self.descript[obj] = desc

#-----------------------------------------------------------------------------#
# Common Code Object Types for use in Tag Generator Modules
#-----------------------------------------------------------------------------#

class Class(Scope):
    """Class Object Representation"""
    def __init__(self, name, line, scope=None):
        Scope.__init__(self, name, line, "class", scope)

    def AddMethod(self, method):
        """Add a class method to the class object
        @param method: L{Method} object

        """
        self.AddElement('method', method)

    def AddVariable(self, var):
        """Add a class variable to the class object
        @param var: L{Variable} object

        """
        self.AddElement('variable', var)

    def GetElements(self):
        """Get the elements of this Class object sorted by
        Variables, Methods, other...
        @return: list

        """
        elements = Scope.GetElements(self)
        vars = sorted(elements.get('variable', list()))
        methods = sorted(elements.get('method', list()))
        rlist = vars + methods
        other = [ element for element in elements
                  if element not in ['variable', 'method'] ]
        for obj in other:
            rlist.extend(sorted(elements.get(obj, list())))
        return rlist

class Namespace(Scope):
    """Namespace Representation"""
    def __init__(self, name, line, scope=None):
        Scope.__init__(self, name, line, "namespace", scope)

class Section(Scope):
    """Section Representation"""
    def __init__(self, name, line, scope=None):
        Scope.__init__(self, name, line, "section", scope)

class Method(Code):
    """Class Method object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "method", scope)

class Function(Code):
    """Function object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "function", scope)

class Macro(Code):
    """Macro Object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "macro", scope)

class Variable(Code):
    """Variable object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "variable", scope)

#-----------------------------------------------------------------------------#
# Top level code representation object. All tag generators should return an
# instance of this object that contains the structure of the document they
# parsed.

class DocStruct(Scope):
    """Code Document Representation Object
    Captures the structure of the code in a document, this structure can
    then be easily used to represent the document in a number of differen't
    formats.

    """
    def __init__(self):
        Scope.__init__(self, 'docstruct', None)
        self.lastclass = None

    def AddClass(self, cobj):
        """Convenience function for adding a class to the document
        @param cobj: L{Class} object

        """
        self.lastclass = cobj
        self.AddElement('class', cobj)

    def AddFunction(self, fobj):
        """Convenience for adding a function to the document
        @param fobj: L{Function} object

        """
        self.AddElement('function', fobj)

    def AddVariable(self, vobj):
        """Convenience for adding a (global) variable to the document
        @param vobj: L{Variable} object

        """
        self.AddElement('variable', vobj)

    def GetClasses(self):
        """Get all classes in the document and return them as
        a sorted list.

        """
        return sorted(self.GetElementType('class'))

    def GetFunctions(self):
        """Get all top level functions defined in a document and 
        return them as a sorted list.

        """
        return sorted(self.GetElementType('function'))

    def GetVariables(self):
        """Get all global variables defined in a document and 
        return them as a sorted list.

        """
        return sorted(self.GetElementType('variable'))

    def GetLastClass(self):
        """Gets the last class that was added to the document
        @return: L{Class}

        """
        return self.lastclass
