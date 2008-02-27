###############################################################################
# Name: actionscript.py                                                       #
# Purpose: Define ActionScript syntax for highlighting and other features     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: actionscript.py                                                                
@author: Cody Precord                                                       
                                                                         
SUMMARY:                                                                    
Lexter configuration file for ActionScript                          
                                                                         
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependencies
import synglob
import cpp

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# ActionScript Keywords 0
AS_KEYWORDS = ("break case catch continue default do each else finally for if "
               "in label new return super switch throw while with "
               # Attribute Keywords
               "dynamic final internal native override private protected "
               "public static "
               # Definition Keywords
               "class const extends function get implements interface "
               "namespace package set var "
               # Directives
               "import include use "
               # Primary Expression Keywords
               "false null this true "
               # Special Types
               "void Null")


# ActionScript Keywords 1
#AS_TYPES = ()

#---- Syntax Style Specs ----#
# Same as cpp

#---- Extra Properties ----#
# Same as cpp

#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    if lang_id == synglob.ID_LANG_AS:
        return [(0, AS_KEYWORDS)]
    else:
        return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_AS:
        return cpp.SYNTAX_ITEMS
    else:
        return list()

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    if lang_id == synglob.ID_LANG_AS:
        return [cpp.FOLD, cpp.FOLD_PRE]
    else:
        return list()

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    if lang_id == synglob.ID_LANG_AS:
        return [u'//']
    else:
        return list()

#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
