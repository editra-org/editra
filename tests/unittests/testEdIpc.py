###############################################################################
# Name: testEdIpc.py                                                          #
# Purpose: Unit tests for the IPC features from ed_ipc                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the IPC functionality"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import time
import unittest

# Local modules
import common

# Module to test
import ed_ipc

#-----------------------------------------------------------------------------#
# Test Class

class EdIpcTest(unittest.TestCase):
    """Tests for the ipc functions of ed_ipc"""
    def setUp(self):
        self.handler = wx.EvtHandler()
        port = ed_ipc.EDPORT + 1
        self.server = ed_ipc.EdIpcServer(self.handler, "foo", port)

        self.handler.Bind(ed_ipc.EVT_COMMAND_RECV, self.OnIpcMsg)

    def tearDown(self):
        self.server.Shutdown()
        time.sleep(.5) # Give server time to shutdown
        self.handler.Unbind(ed_ipc.EVT_COMMAND_RECV)

    def OnIpcMsg(self, event):
        print "EVENT RECIEVED"

    #---- Functional Tests ----#

    def testIpcCommand(self):
        xmlobj = ed_ipc.IPCCommand()
        xmlobj.SetArgs([("-g", 22),]) # GOTO line is only supported now
        xmlobj.SetFiles(["fileone.txt", "filetwo.txt"])
        serialized = xmlobj.GetXml()
        self.assertTrue(isinstance(serialized, basestring))

        newobj = ed_ipc.IPCCommand()
        newobj.LoadFromString(serialized)
        flist = newobj.GetFiles()
        self.assertTrue(isinstance(flist, list))
        self.assertEquals(xmlobj.GetFiles(), flist)
        args = newobj.GetArgs()
        self.assertEquals(args, xmlobj.GetArgs())

#-----------------------------------------------------------------------------#
