###############################################################################
# Name: testStyleItem                                                         #
# Purpose: Unittest for ed_style.StyleItem                                    #
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
import ed_style

#-----------------------------------------------------------------------------#
# Test Class

class StyleItemTest(unittest.TestCase):
    def setUp(self):
        self.item = ed_style.StyleItem("#FF0000,bold", "#000000", "Times", "10")
        self.itemstr = "fore:#FF0000,back:#000000,face:Times,size:10,modifiers:bold"

    def tearDown(self):
        pass

    #---- Method Tests ----#
    def testEquals(self):
        """Test that the equality operator is functioning correctly"""
        item2 = ed_style.StyleItem("#FF0000,bold", "#000000", "Times", "10")

        # Base Test
        self.assertEquals(self.item, item2)

        # Test 2
        item3 = ed_style.StyleItem("#FF0000", "#0000FF", "Arial", "10")
        self.assertNotEquals(self.item, item3,
                             "%s == %s" % (str(self.item), str(item2)))

    def testString(self):
        """Test that string conversion works properly"""
        items1 = sorted(str(self.item).split(','))
        items2 = sorted(self.itemstr.split(','))
        self.assertEquals(items1, items2)

    def testGetAsList(self):
        """Test getting the style item attributes as a list"""
        itemlst = self.item.GetAsList()
        ilen = len(itemlst)
        self.assertTrue(ilen == 5, "Lenght Was: %d" % ilen)

    def testGetBack(self):
        """Test retrieving the background color"""
        self.assertEquals(self.item.GetBack(), "#000000")

    def testGetFore(self):
        """Test retrieving the background color"""
        self.assertEquals(self.item.GetFore(), "#FF0000")

    def testGetFace(self):
        """Test retrieving the background color"""
        self.assertEquals(self.item.GetFace(), "Times")

    def testGetSize(self):
        """Test retrieving the background color"""
        self.assertEquals(self.item.GetSize(), "10")

    def testGetModifiers(self):
        """Test retrieving the extra modifier attributes"""
        self.assertEquals(self.item.GetModifiers(), "bold")

    def testGetModifierList(self):
        """Test retrieving the extra modifier attributes list"""
        self.assertEquals(self.item.GetModifierList()[0], "bold")

    def testGetNamedAttr(self):
        """Test GetNamedAttr"""
        self.assertEquals(self.item.GetNamedAttr("fore"), self.item.GetFore())
        self.assertEquals(self.item.GetNamedAttr("back"), self.item.GetBack())
        self.assertEquals(self.item.GetNamedAttr("face"), self.item.GetFace())
        self.assertEquals(self.item.GetNamedAttr("size"), self.item.GetSize())

    def testIsNull(self):
        """Test Null check"""
        self.assertFalse(self.item.IsNull())
        self.assertTrue(ed_style.NullStyleItem().IsNull())

    def testIsOk(self):
        """Test checker for if an item is Ok"""
        self.assertTrue(self.item.IsOk())
        self.assertFalse(ed_style.StyleItem().IsOk())

    def testNullify(self):
        """Test nullifying a style item"""
        item = ed_style.StyleItem("#000000", "#FFFFFF")
        self.assertFalse(item.IsNull(), "Item is already null")
        item.Nullify()
        self.assertTrue(item.IsNull(), "Item was not nullified")

    def testSetAttrFromString(self):
        """Test Setting attributes from a formatted string"""
        item = ed_style.StyleItem()
        item.SetAttrFromStr(self.itemstr)
        self.assertEquals(self.item, item,
                          "%s != %s" % (str(self.item), str(item)))

    #TODO: add set item tests after next revision of ed_style
#    def testSet
#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    unittest.main()
