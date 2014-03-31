# -*- test-case-name: txtesthelpers.tests.test_loopback_tools -*-

from twisted.internet import defer
from twisted.internet.error import CannotListenError
from twisted.internet.interfaces import IAddress, IListeningPort
from twisted.protocols import loopback
from zope.interface import implementer


@implementer(IAddress)
class _LoopbackListenerAddress(object):
    pass


@implementer(IListeningPort)
class LoopbackPort(object):
    def __init__(self, server_factory):
        self.listening = False
        self.protocol_connections = []
        self.server_factory = server_factory
        self._address = _LoopbackListenerAddress()

    def startListening(self):
        if self.listening:
            raise CannotListenError(None, None, "Already listening.")
        self.listening = True

    def stopListening(self):
        self.listening = False
        return defer.succeed(None)

    def getHost(self):
        return self._address


class LoopbackListener(object):
    listening_port = None
    pump_policy = None

    def __init__(self, pump_policy=loopback.identityPumpPolicy):
        self.pump_policy = pump_policy

    def listen(self, factory):
        if self.listening_port is not None:
            raise CannotListenError(None, None, "listen() already called.")
        self.listening_port = LoopbackPort(factory)
        self.listening_port.startListening()
        return self.listening_port
