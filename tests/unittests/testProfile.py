###############################################################################
# Name: testProfile.py                                                        #
# Purpose: Unittest for settings persistance.                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Unittest for User Profile and settings persistance.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import unittest

# Module to test
import profiler

#-----------------------------------------------------------------------------#

class ProfileTest(unittest.TestCase):
    def setUp(self):
        # Create the singleton profile object
        self._profile = profiler.TheProfile

    def tearDown(self):
        pass

    #---- Begin Test Cases ----#

    def testIdentity(self):
        """Test that only one profile object can be created."""
        self.assertTrue(self._profile is profiler.Profile())

    def testLoadDefaultValues(self):
        """Test that default values are returned when no saved profile has been
        loaded.

        """
        # Load the default settings
        self._profile.LoadDefaults()

        # Try retrieving soem values from it
        self.assertEquals(self._profile.Get('EDGE'), profiler._DEFAULTS['EDGE'])

        # Test a value that doesn't exist
        self.assertTrue(self._profile.Get('FAKEKEYTOFETCH') is None)

        # Test fallback value
        self.assertEquals(self._profile.Get('FAKEKEYTOFETCH', default="hello"), "hello")

    def testChangeValue(self):
        """Test changing an existing profile value."""
        self.assertTrue(self._profile.Get('TEST1') is None)

        # Now change the value
        self._profile.Set('TEST1', 123)
        self.assertTrue(self._profile.Get('TEST1') == 123)

    def testDeleteValue(self):
        """Test removing a value from the object."""
        # Add a value
        self._profile.Set('TEST2', "myString")
        self.assertTrue(self._profile.Get('TEST2') == "myString")

        # Now try to delete it
        self._profile.DeleteItem('TEST2')
        self.assertTrue(self._profile.Get('TEST2') is None)

    def testLoadProfile(self):
        """Test loading a stored profile."""
        # Add some values to the profile
        #TODO: should re-org profile support functions to make testing this
        #      not require modifing the installed profile loader.
#        self._profile.Set('VALUE1', 25)
#        self._profile.Set('VALUE2', "string")
#        self._profile.Write(

    def testWrite(self):
        """Test writing the settings out to disk."""
        pass

    def testUpdate(self):
        """Test updating the profile from a dictionary."""
        pass

    #---- Tests for module level functions ----#

    def testCalcVersionValue(self):
        """Test the version value calculation function."""
        v1 = profiler.CalcVersionValue("1.0.0")
        v2 = profiler.CalcVersionValue("1.0.1")
        self.assertTrue(v1 < v2)
