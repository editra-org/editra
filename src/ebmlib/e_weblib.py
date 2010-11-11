###############################################################################
# Name: weblib.py                                                             #
# Purpose: Web an network utilties                                            #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: Web Utilities

Utility functions for working with web and other networking protocols

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['SOAPMessage',]

#-----------------------------------------------------------------------------#
# imports
import httplib

#-----------------------------------------------------------------------------#
_SOAP_TPL = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">
<soap12:Body>
    %(msg)s
</soap12:Body>
</soap12:Envelope>"""

_SM_TPL = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope 
SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"  
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Body>
    %(msg)s
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

#-----------------------------------------------------------------------------#

class SOAPMessage(object):
    """Class for creating and sending a message
    using the SOAP protocol.

    """
    def __init__(self, host, msg):
        """Create the message object
        @param host: host the message will be sent to (url)
        @param msg: XML Body text

        """
        assert len(host), "Must specify a valid host"
        super(SOAPMessage, self).__init__()

        # Attributes
        self._host = host
        self._msg = msg
        self._http = httplib.HTTP(self._host,80)

    def Send(self):
        """Send the message"""
        # Create the SOAP message
#        soapmsg = _SOAP_TPL % dict(msg=self._msg)
        soapmsg = _SM_TPL % dict(msg=self._msg)

        # Setup Headers
        self._http.putrequest("POST", "/rcx-ws/rcx")
        self._http.putheader("Host", self._host)
        self._http.putheader("User-Agent", "Python post")
        self._http.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        self._http.putheader("Content-length", "%d" % len(soapmsg))
        self._http.putheader("SOAPAction", "\"\"")
        self._http.endheaders()

        # Send it
        self._http.send(self._msg)

    def GetReply(self):
        """Get the reply (may block for a long time)
        @return: (statuscode, statusmessage, header)

        """
        return self._http.getreply()

