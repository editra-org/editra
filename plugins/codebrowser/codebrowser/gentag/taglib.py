###############################################################################
# Name: taglib.py                                                             #
# Purpose: Common api for tag generators                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: taglib.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
    Basic api for creating tag generator module. Tag generator modules have two
requirements to fit into the api expected by the Editra's CodeBrowser.

  1. The method `GenerateTags` must be defined
  2. GenerateTags must return a L{DocStruct} that contains the code structure

Most common code elements have convinience classes defined in this module. If a
new generator module needs some type of element that is not available in this
module the generator module can derive a type to describe the element. The
derived class should inherit from L{Code} if it is a non container type code
element. If the code element can contain other elements it should instead
derive from L{Scope}. In either case it is important to set the type identifier
attribute that describes the type.

@see: L{Class} and L{Method} for examples


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Code Object Base Classes

class Code(object):
    """Code representation objects base class all code elements should
    inheirit from this class.

    """
    def __init__(self, name, line, obj="code", scope=None):
        """Create the Code Object
        @param name: Items Name
        @param line: Line in buffer item is found on
        @keyword obj: Object type identifier string
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
        """Return the dictionary of elements contained in this scope as an
        ordered list of single key dictionaries 
        @return: list of dict

        """
        rlist = list()
        for key, value in self.elements.iteritems():
            rlist.append({key:sorted(value)})
        return rlist

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
        """Convenience method for adding a L{Method} to the class object
        @param method: L{Method} object

        """
        self.AddElement('method', method)

    def AddVariable(self, var):
        """Convenience method for adding a L{Variable} to the class object
        @param var: L{Variable} object

        """
        self.AddElement('variable', var)

    def GetElements(self):
        """Get the elements of this Class object sorted by
        Variables, Methods, other...
        @return: list

        """
        rlist = list()
        rlist.append(dict(variable=sorted(self.elements.get('variable', list()))))
        rlist.append(dict(method=sorted(self.elements.get('method', list()))))
        other = [ element for element in self.elements
                  if element not in ['variable', 'method'] ]
        for obj in other:
            rlist.append({obj:sorted(self.elements.get(obj, list()))})
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
    """General Function Object, to create a function like object with
    a differen't type identifier, change the obj parameter to set the
    element type property.

    """
    def __init__(self, name, line, obj="function", scope=None):
        Code.__init__(self, name, line, obj, scope)

class Macro(Code):
    """Macro Object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "macro", scope)

class Procedure(Code):
    """Procedure object"""
    def __init__(self, name, line, scope=None):
        Code.__init__(self, name, line, "procedure", scope)

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
        self.prio = dict()

    def AddClass(self, cobj):
        """Convenience method for adding a L{Class} to the document
        @param cobj: L{Class} object

        """
        self.lastclass = cobj
        self.AddElement('class', cobj)

    def AddElement(self, obj, element):
        """Add an element to this scope
        @param obj: object indentifier string
        @param element: L{Code} object to add to this scope

        """
        Scope.AddElement(self, obj, element)
        if not self.prio.has_key(obj):
            self.prio[obj] = 0

    def AddFunction(self, fobj):
        """Convenience method for adding a L{Function} to the document
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

    def GetElements(self):
        """Return the dictionary of elements contained in this scope as an
        ordered list of single key dictionaries 
        @return: list of dict

        """
        def cmptup(x, y):
            if x[1] < y[1]:
                return -1
            elif x[1] == y[1]:
                return 0
            else:
                return 1

        sorder = [ key for key, val in sorted(self.prio.items(), cmptup, reverse=True) ]
        rlist = list()
        for key in sorder:
            if self.elements.has_key(key):
                rlist.append({key:sorted(self.elements[key])})
        return rlist

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
        """Gets the last L{Class} that was added to the document
        @return: L{Class}

        """
        return self.lastclass

    def SetElementPriority(self, obj, prio):
        """Set the priority of of an object in the document. The priority
        is used to decide the order of the list returned by L{GetElements}.
        A higher number means higher priorty (i.e listed earlier).
        @param obj: element identifier string
        @param prio: priority value (int)

        """
        self.prio[obj] = prio
