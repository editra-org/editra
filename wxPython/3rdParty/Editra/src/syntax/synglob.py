###############################################################################
# Name: synglob.py                                                            #
# Purpose: Acts as a registration point for all supported languages.          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: synglob.py
AUTHOR: Cody Precord
@summary: Provides configuration and basic API functionality to all the syntax
          modules. It also acts  as a configuration file for the syntax
          management code. When support for a new languages is added it must
          have a registration entry in the below L{LANG_MAP} dictionary in
          order to be loadable by the syntax module.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependencies
import wx.stc as stc

# The language identifiers and the EXT_MAP have been moved out of this
# module in order to be independent of Editra and wx, but they are
# still needed here...
from synextreg import *

#-----------------------------------------------------------------------------#
# Feature Identifiers
FEATURE_AUTOINDENT = u"AutoIndenter"
FEATURE_STYLETEXT = u"StyleText"

#-----------------------------------------------------------------------------#

# Maps file types to syntax definitions
LANG_MAP = {LANG_4GL    : (ID_LANG_4GL,    stc.STC_LEX_SQL,      '_progress'),
            LANG_68K    : (ID_LANG_68K,    stc.STC_LEX_ASM,      '_asm68k'),
            LANG_ADA    : (ID_LANG_ADA,    stc.STC_LEX_ADA,      '_ada'),
            LANG_APACHE : (ID_LANG_APACHE, stc.STC_LEX_CONF,     '_apache'),
            LANG_AS     : (ID_LANG_AS,     stc.STC_LEX_CPP,      '_actionscript'),
            LANG_BASH   : (ID_LANG_BASH,   stc.STC_LEX_BASH,     '_sh'),
            LANG_BATCH  : (ID_LANG_BATCH,  stc.STC_LEX_BATCH,    '_batch'),
            LANG_BOO    : (ID_LANG_BOO,    stc.STC_LEX_PYTHON,   '_boo'),
            LANG_C      : (ID_LANG_C,      stc.STC_LEX_CPP,      '_cpp'),
            LANG_CAML   : (ID_LANG_CAML,   stc.STC_LEX_CAML,     '_caml'),
            LANG_COBRA  : (ID_LANG_COBRA,  stc.STC_LEX_PYTHON,   '_cobra'),
            LANG_COLDFUSION : (ID_LANG_COLDFUSION, stc.STC_LEX_HTML, '_html'),
            LANG_CPP    : (ID_LANG_CPP,    stc.STC_LEX_CPP,      '_cpp'),
            LANG_CSH    : (ID_LANG_CSH,    stc.STC_LEX_BASH,     '_sh'),
            LANG_CSHARP : (ID_LANG_CSHARP, stc.STC_LEX_CPP,      '_cpp'),
            LANG_CSS    : (ID_LANG_CSS,    stc.STC_LEX_CSS,      '_css'),
            LANG_D      : (ID_LANG_D,      stc.STC_LEX_CPP,      '_d'),
            LANG_DIFF   : (ID_LANG_DIFF,   stc.STC_LEX_DIFF,     '_diff'),
            LANG_DJANGO : (ID_LANG_DJANGO, stc.STC_LEX_CONTAINER, '_django'),
            LANG_DOT    : (ID_LANG_DOT,    stc.STC_LEX_CPP,      '_dot'),
            LANG_EDJE   : (ID_LANG_EDJE,   stc.STC_LEX_CPP,      '_edje'),
            LANG_EIFFEL : (ID_LANG_EIFFEL, stc.STC_LEX_EIFFEL,   '_eiffel'),
            LANG_ERLANG : (ID_LANG_ERLANG, stc.STC_LEX_ERLANG,   '_erlang'),
            LANG_ESS    : (ID_LANG_ESS,    stc.STC_LEX_CSS,      '_editra_ss'),
            LANG_F77    : (ID_LANG_F77,    stc.STC_LEX_F77,      '_fortran'),
            LANG_F95    : (ID_LANG_F95,    stc.STC_LEX_FORTRAN,  '_fortran'),
            LANG_FERITE : (ID_LANG_FERITE, stc.STC_LEX_CPP,      '_ferite'),
            LANG_FLAGSHIP: (ID_LANG_FLAGSHIP, stc.STC_LEX_FLAGSHIP, '_flagship'),
            LANG_GUI4CLI : (ID_LANG_GUI4CLI, stc.STC_LEX_GUI4CLI, '_gui4cli'),
            LANG_HASKELL : (ID_LANG_HASKELL, stc.STC_LEX_HASKELL, '_haskell'),
            LANG_HAXE   : (ID_LANG_HAXE, stc.STC_LEX_CPP,        '_haxe'),
            LANG_HTML   : (ID_LANG_HTML,   stc.STC_LEX_HTML,     '_html'),
            LANG_INNO   : (ID_LANG_INNO,   stc.STC_LEX_INNOSETUP, '_inno'),
            LANG_ISSL   : (ID_LANG_ISSL,   stc.STC_LEX_CONTAINER, '_issuelist'),
            LANG_JAVA   : (ID_LANG_JAVA,   stc.STC_LEX_CPP,      '_java'),
            LANG_JS     : (ID_LANG_JS,     stc.STC_LEX_CPP,      '_javascript'),
            LANG_KIX    : (ID_LANG_KIX,    stc.STC_LEX_KIX,      '_kix'),
            LANG_KSH    : (ID_LANG_KSH,    stc.STC_LEX_BASH,     '_sh'),
            LANG_LATEX  : (ID_LANG_LATEX,  stc.STC_LEX_LATEX,    '_latex'),
            LANG_LISP   : (ID_LANG_LISP,   stc.STC_LEX_LISP,     '_lisp'),
            LANG_LOUT   : (ID_LANG_LOUT,   stc.STC_LEX_LOUT,     '_lout'),
            LANG_LUA    : (ID_LANG_LUA,    stc.STC_LEX_LUA,      '_lua'),
            LANG_MAKE   : (ID_LANG_MAKE,   stc.STC_LEX_MAKEFILE, '_make'),
            LANG_MAKO   : (ID_LANG_MAKO,   stc.STC_LEX_CONTAINER, '_mako'),
            LANG_MASM   : (ID_LANG_MASM,   stc.STC_LEX_ASM,      '_masm'),
            LANG_MATLAB : (ID_LANG_MATLAB, stc.STC_LEX_MATLAB,   '_matlab'),
            LANG_MSSQL  : (ID_LANG_MSSQL,  stc.STC_LEX_MSSQL,    '_mssql'),
            LANG_NASM   : (ID_LANG_NASM,   stc.STC_LEX_ASM,      '_nasm'),
            LANG_NEWLISP: (ID_LANG_NEWLISP, stc.STC_LEX_LISP,    '_lisp'),
            LANG_NSIS   : (ID_LANG_NSIS,   stc.STC_LEX_NSIS,     '_nsis'),
            LANG_OBJC   : (ID_LANG_OBJC,   stc.STC_LEX_CPP,      '_cpp'),
            LANG_OCTAVE : (ID_LANG_OCTAVE, stc.STC_LEX_OCTAVE,   '_matlab'),
            LANG_PASCAL : (ID_LANG_PASCAL, stc.STC_LEX_PASCAL,   '_pascal'),
            LANG_PERL   : (ID_LANG_PERL,   stc.STC_LEX_PERL,     '_perl'),
            LANG_PHP    : (ID_LANG_PHP,    stc.STC_LEX_HTML,     '_php'),
            LANG_PIKE   : (ID_LANG_PIKE,   stc.STC_LEX_CPP,      '_pike'),
            LANG_PLSQL  : (ID_LANG_PLSQL,  stc.STC_LEX_SQL,      '_sql'),
            LANG_PROPS  : (ID_LANG_PROPS,  stc.STC_LEX_PROPERTIES, '_props'),
            LANG_PS     : (ID_LANG_PS,     stc.STC_LEX_PS,        '_postscript'),
            LANG_PYTHON : (ID_LANG_PYTHON, stc.STC_LEX_PYTHON,    '_python'),
            LANG_R      : (ID_LANG_R,      stc.STC_LEX_CONTAINER, '_s'),
            LANG_RUBY   : (ID_LANG_RUBY,   stc.STC_LEX_RUBY,      '_ruby'),
            LANG_S      : (ID_LANG_S,      stc.STC_LEX_CONTAINER, '_s'),
            LANG_SCHEME : (ID_LANG_SCHEME, stc.STC_LEX_LISP,      '_lisp'),
            LANG_SQL    : (ID_LANG_SQL,    stc.STC_LEX_SQL,       '_sql'),
            LANG_SQUIRREL : (ID_LANG_SQUIRREL, stc.STC_LEX_CPP,   '_squirrel'),
            LANG_ST     : (ID_LANG_ST,     stc.STC_LEX_SMALLTALK, '_smalltalk'),
            LANG_STATA : (ID_LANG_STATA,  stc.STC_LEX_CPP,        '_stata'),
            LANG_SYSVERILOG : (ID_LANG_SYSVERILOG, stc.STC_LEX_VERILOG, '_verilog'),
            LANG_TCL    : (ID_LANG_TCL,    stc.STC_LEX_TCL,      '_tcl'),
            LANG_TXT    : (ID_LANG_TXT,    stc.STC_LEX_NULL,     None),
            LANG_VALA   : (ID_LANG_VALA,   stc.STC_LEX_CPP,      '_cpp'),
            LANG_VB     : (ID_LANG_VB,     stc.STC_LEX_VB,       '_visualbasic'),
            LANG_VBSCRIPT : (ID_LANG_VBSCRIPT, stc.STC_LEX_VBSCRIPT, '_vbscript'),
            LANG_VERILOG: (ID_LANG_VERILOG, stc.STC_LEX_VERILOG,   '_verilog'),
            LANG_VHDL   : (ID_LANG_VHDL,   stc.STC_LEX_VHDL,       '_vhdl'),
            LANG_XML    : (ID_LANG_XML,    stc.STC_LEX_XML,        '_xml'),
            LANG_YAML   : (ID_LANG_YAML,   stc.STC_LEX_YAML,       '_yaml'),
            LANG_GROOVY : (ID_LANG_GROOVY,   stc.STC_LEX_CPP,      '_groovy'),
            LANG_XTEXT  : (ID_LANG_XTEXT,   stc.STC_LEX_CONTAINER, '_xtext')
            }

# Dynamically finds the language description string that matches the given
# language id.
# Used when manually setting lexer from a menu/dialog
def GetDescriptionFromId(lang_id):
    """Get the programming languages description string from the given
    lanugage id. If no correspoding language is found the plain text
    description is returned.
    @param lang_id: Language Identifier ID
    @note: requires that all languages are defined in ID_LANG_NAME, LANG_NAME
           pairs to work properly.

    """
    rval = LANG_TXT
    for key, val in globals().iteritems():
        if val == lang_id and key.startswith('ID_LANG'):
            rval = globals().get(key[3:], globals()['LANG_TXT'])
            break
    return rval
