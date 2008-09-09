###############################################################################
# Name: testSearchEngine                                                      #
# Purpose: Unittest for ed_search.SearchEngine                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import sys
import os
import unittest

# Module to test
sys.path.insert(0, os.path.abspath("../../src"))
import ed_search

#-----------------------------------------------------------------------------#
# Search Pool

# NOTE: changeing this string requires changing the related tests that use it
POOL = ("Test string to use for the find tests. The find tests work on strings"
        " while the search methods work on files. Here is some more random"
        " strings to search in. def foo(param1, param2): print param1, param2"
        " 123 + 754 / 5 = $x. $var1 = TEST_STRING; $var2=test_string;")

#-----------------------------------------------------------------------------#
# Test Class

class SearchEngineTest(unittest.TestCase):
    def setUp(self):
        """Setup the test items"""
        self._def_eng = ed_search.SearchEngine(u"", regex=False, down=True,
                                               matchcase=False, wholeword=False)
        self._ww_eng = ed_search.SearchEngine(u"", regex=False, down=True,
                                              matchcase=False, wholeword=True)
        self._mc_eng = ed_search.SearchEngine(u"", regex=False, down=True,
                                              matchcase=True, wholeword=False)
        self._regex_eng = ed_search.SearchEngine(u"", regex=True, down=True,
                                                 matchcase=False, wholeword=False)
        self._regexmc_eng = ed_search.SearchEngine(u"", regex=True, down=True,
                                                  matchcase=True, wholeword=False)
        self._regww_eng = ed_search.SearchEngine(u"", regex=True, down=True,
                                                 matchcase=False, wholeword=True)
        self._all_eng = ed_search.SearchEngine(u"", regex=True, down=True,
                                               matchcase=True, wholeword=True)

    def tearDown(self):
        pass

    #---- Method Tests ----#
    def testIsRegEx(self):
        """Test if the regex flag is properly set"""
        self.assertTrue(self._regex_eng.IsRegEx(), "Regex Engine is not Regex")
        self.assertFalse(self._def_eng.IsRegEx(), "Default Engine is Regex")

    def testIsMatchCase(self):
        """Test if the match case flag is properly set"""
        self.assertTrue(self._mc_eng.IsMatchCase())
        self.assertFalse(self._def_eng.IsMatchCase())
        self.assertTrue(self._all_eng.IsMatchCase())
        
    def testIsWholeWord(self):
        """Test if the whole word flag is properly set"""
        self.assertTrue(self._ww_eng.IsWholeWord())
        self.assertFalse(self._def_eng.IsWholeWord())
        self.assertTrue(self._all_eng.IsWholeWord())

    def testNormalFind(self):
        """Test find procedure to see if it acuratly returns the correct
        positions in the search pool

        """
        # Test default search
        self._def_eng.SetSearchPool(POOL)
        self._def_eng.SetQuery('test')
        t1 = self._def_eng.Find(0)
        self.assertTrue(t1 is not None, "Find failed")
        self.assertEquals(t1[0], 0, "Find got wrong postion")
        self.assertEquals(t1[1] - t1[0], 4, "Find returned wrong span")

        # Find Next
        t2 = self._def_eng.Find(t1[1])
        self.assertTrue(t2 is not None, "Find next failed")
        self.assertEquals(t2[0] + t1[1], 32, "Find next: %d != 32" % t2[0])

        # Test not found
        self._def_eng.SetQuery('gyoza')
        t3 = self._def_eng.Find(0)
        self.assertTrue(t3 is None)

    def testWholeWordFind(self):
        """Test find procedure to see if it acuratly returns the correct
        positions in the search pool

        """
        # Test default search
        self._ww_eng.SetSearchPool(POOL)
        self._ww_eng.SetQuery('test')
        t1 = self._ww_eng.Find(0)
        self.assertTrue(t1 is not None, "Find failed")
        self.assertEquals(t1[0], 0, "Find got wrong postion")
        self.assertEquals(t1[1] - t1[0], 4, "Find returned wrong span")

        # Find Next (Should be None)
        t2 = self._ww_eng.Find(t1[1])
        self.assertTrue(t2 is None, "Find next failed")

    def testMatchCaseFind(self):
        """Test find procedure to see if it acuratly returns the correct
        positions in the search pool

        """
        # Test default search
        self._mc_eng.SetSearchPool(POOL)
        self._mc_eng.SetQuery('test')
        t1 = self._mc_eng.Find(0)
        self.assertTrue(t1 is not None, "Find failed")
        self.assertEquals(t1[0], 32, "Find got wrong postion")
        self.assertEquals(t1[1] - t1[0], 4, "Find returned wrong span")

        # Find Next
        t2 = self._mc_eng.Find(t1[1])
        self.assertTrue(t2 is not None, "Find next failed")
        self.assertEquals(t2[0] + t1[1], 48, "Find next: %d != 48" % t2[0])

        # Test not found
        self._mc_eng.SetQuery('TeSt')
        t3 = self._mc_eng.Find(0)
        self.assertTrue(t3 is None)

    def testRegexFind(self):
        """Test find procedure to see if it acuratly returns the correct
        positions in the search pool

        """
        # Test Regex search
        self._regex_eng.SetSearchPool(POOL)
        self._regex_eng.SetQuery('t[a-u]+')
        t1 = self._regex_eng.Find(0)
        self.assertFalse(t1 is None, "Regex find failed")

        # Find Next
        t2 = self._regex_eng.Find(t1[1])
        self.assertTrue(t2 is not None, "Find next failed")
        self.assertEquals(t2[0] + t1[1], 6, "Find next: %d != 6" % t2[0])

        # Test not found
        self._regex_eng.SetQuery('test{10,10}')
        t3 = self._regex_eng.Find(0)
        self.assertTrue(t3 is None)

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    unittest.main()
