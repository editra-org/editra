###############################################################################
# Name: histcache.py                                                          #
# Purpose: History Cache                                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: HistoryCache

History cache that acts as a stack for managing a history list o

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'HistoryCache', 'HIST_CACHE_UNLIMITED']

#-----------------------------------------------------------------------------#
# Imports

#-----------------------------------------------------------------------------#
# Globals
HIST_CACHE_UNLIMITED = -1

#-----------------------------------------------------------------------------#

class HistoryCache(object):
    def __init__(self, max_size=HIST_CACHE_UNLIMITED):
        object.__init__(self)

        # Attributes
        self._list = list()
        self.cpos = -1
        self.max_size = max_size

    def _Resize(self):
        """Adjust cache size based on max size setting"""
        if self.max_size != HIST_CACHE_UNLIMITED:
            lsize = len(self._list)
            if lsize:
                adj = self.max_size - lsize 
                if adj < 0:
                    self._list.pop(0)
                    self.cpos = len(self._list) - 1 

    def Clear(self):
        """Clear the history cache"""
        del self._list
        self._list = list()
        self.cpos = -1

    def GetSize(self):
        """Get the current size of the cache
        @return: int (number of items in the cache)

        """
        return len(self._list)

    def GetMaxSize(self):
        """Get the max size of the cache
        @return: int

        """
        return self.max_size

    def GetNextItem(self):
        """Get the next item in the history cache, moving the
        current postion towards the end of the cache.
        @return: object or None if at end of list

        """
        item = None
        if self.cpos < len(self._list) - 1:
            self.cpos += 1
            item = self._list[self.cpos]
        return item

    def GetPreviousItem(self):
        """Get the previous item in the history cache, moving the
        current postion towards the begining of the cache.
        @return: object or None if at start of list

        """
        item = None
        if self.cpos >= 0 and len(self._list) > 0:
            if self.cpos == len(self._list):
                self.cpos -= 1
            item = self._list[self.cpos]
            self.cpos -= 1
        return item

    def HasPrevious(self):
        """Are there more items to the left of the current position
        @return: bool

        """
        more = self.cpos >= 0
        return more

    def HasNext(self):
        """Are there more items to the right of the current position
        @return: bool

        """
        if self.cpos == -1 and len(self._list):
            more = True
        else:
            more = self.cpos >= 0 and self.cpos < len(self._list)
        return more

    def PutItem(self, item):
        """Put an item on the top of the cache
        @param item: object

        """
        if self.cpos != len(self._list) - 1:
            self._list = self._list[:self.cpos]
        self._list.append(item)
        self.cpos += 1
        self._Resize()

    def SetMaxSize(self, max_size):
        """Set the maximum size of the cache
        @param max_size: int (HIST_CACHE_UNLIMITED for unlimited size)

        """
        assert max_size > 0 or max_size == 1, "Invalid max size"
        self.max_size = max_size
        self._Resize()
