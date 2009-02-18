###############################################################################
# Name: testProfile.py                                                        #
# Purpose: Unittest for settings persistance.                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

"""
Unittest for User Profile and settings persistance.

"""

#-----------------------------------------------------------------------------#
# Imports
import unittest

# Module to test
import profiler

#-----------------------------------------------------------------------------#

class LogMsgTest(unittest.TestCase):
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
        pass

    def testChangeValue(self):
        """Test changing an existing profile value."""
        pass

    def testNewValue(self):
        """Test creating a new profile value."""
        pass

    def testDeleteValue(self):
        """Test removing a value from the object."""
        pass

    def testLoadProfile(self):
        """Test loading a stored profile."""
        pass

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
