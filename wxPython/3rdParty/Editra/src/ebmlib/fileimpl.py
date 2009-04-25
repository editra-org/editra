###############################################################################
# Name: Cody Precord                                                          #
# Purpose: File Object Interface Implementation                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Buisness Model Library: FileObjectImpl

Implementation of a file object interface class. Objects and methods inside
of this library expect a file object that derives from this interface.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports

#--------------------------------------------------------------------------#

class FileObjectImpl(object):
    """File Object Interface implementation base class"""
    def __init__(self):
        object.__init__(self)

    
