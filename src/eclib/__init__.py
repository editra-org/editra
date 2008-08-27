###############################################################################
# Name: __init__.py                                                           #
# Purpose: Editra Control Library                                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library is library of custom controls developed for use in
Editra but are not tied to Editra's framework in anyway.

Controls:
  - PlateButton: Customizable flat button
  - ControlBox: Custom panel with easy layout and optional mini toolbar like
                control.
  - ControlBar: Custom mini toolbar like control used by ControlBox
  - OutputBuffer: Output display buffer that can be easily used with threads

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"


__all__ = ['colorsetter', 'ctrlbox', 'elistmix', 'encdlg', 'finddlg',
           'outbuff', 'platebtn', 'pstatbar']
