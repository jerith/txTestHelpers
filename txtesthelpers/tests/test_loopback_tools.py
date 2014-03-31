from twisted.internet import defer
from twisted.internet.error import CannotListenError
from twisted.internet.interfaces import IAddress, IListeningPort
from twisted.internet.protocol import Protocol
from twisted.protocols import loopback
from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject

from txtesthelpers.loopback_tools import LoopbackPort, LoopbackListener


class BufferProtocol(Protocol):
    side = None

    def __init__(self):
        self.data = ''
        self.closed = False
        self.closed_reason = None

    def dataReceived(self, data):
        self.data += data

    def connectionLost(self, reason):
        self.closed = True
        self.closed_reason = reason


class ServerBufferProtocol(BufferProtocol):
    side = 'server'


class ClientBufferProtocol(BufferProtocol):
    side = 'client'


class TestLoopbackPort(TestCase):
    def test_implements_interface(self):
        """
        LoopbackPort should implement the IListeningPort interface.
        """
        verifyObject(IListeningPort, LoopbackPort(None))

    def test_create_LoopbackPort(self):
        """
        A new LoopbackPort should know its server factory and have no
        connections.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        self.assertEqual(listening_port.protocol_connections, [])
        self.assertEqual(listening_port.server_factory, server_factory)

    def test_getHost(self):
        """
        LoopbackPort.getHost() should return a fake address object.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        verifyObject(IAddress, listening_port.getHost())

    def test_startListening_not_listening(self):
        """
        LoopbackPort.startListening() should start listening.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        self.assertEqual(listening_port.listening, False)
        listening_port.startListening()
        self.assertEqual(listening_port.listening, True)

    def test_startListening_already_listening(self):
        """
        LoopbackPort.startListening() should raise an exception if already
        listening.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        listening_port.startListening()
        self.assertEqual(listening_port.listening, True)
        self.assertRaises(CannotListenError, listening_port.startListening)

    def test_stopListening(self):
        """
        LoopbackPort.stopListening() should stop listening and return a
        Deferred.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        listening_port.startListening()
        self.assertEqual(listening_port.listening, True)
        self.assertIsInstance(listening_port.stopListening(), defer.Deferred)
        self.assertEqual(listening_port.listening, False)

    def test_stopListening_not_listening(self):
        """
        LoopbackPort.stopListening() should stop listening and return a
        Deferred even if not listening.
        """
        server_factory = object()
        listening_port = LoopbackPort(server_factory)
        self.assertEqual(listening_port.listening, False)
        self.assertIsInstance(listening_port.stopListening(), defer.Deferred)
        self.assertEqual(listening_port.listening, False)


class TestLoopbackListener(TestCase):
    def test_create_LoopbackListener(self):
        """
        A new LoopbackListener should have no listening port and use a default
        pump policy.
        """
        listener = LoopbackListener()
        self.assertEqual(listener.listening_port, None)
        self.assertEqual(listener.pump_policy, loopback.identityPumpPolicy)

    def test_create_LoopbackListener_with_pump_policy(self):
        """
        A new LoopbackListener should use the specified pump policy, if any.
        """
        listener = LoopbackListener(pump_policy=loopback.collapsingPumpPolicy)
        self.assertEqual(listener.listening_port, None)
        self.assertEqual(listener.pump_policy, loopback.collapsingPumpPolicy)

    def test_listen(self):
        """
        LoopbackListener.listen() should create a new LoopbackPort, start it,
        and remember it.
        """
        listener = LoopbackListener()
        server_factory = object()
        self.assertEqual(listener.listening_port, None)
        listening_port = listener.listen(server_factory)
        self.assertEqual(listener.listening_port, listening_port)
        self.assertEqual(listening_port.server_factory, server_factory)
        self.assertEqual(listening_port.listening, True)

    def test_listen_already_listening(self):
        """
        LoopbackListener.listen() should raise a CannotListenError if it is
        already listening.
        it.
        """
        listener = LoopbackListener()
        listener.listen(None)
        self.assertRaises(CannotListenError, listener.listen, None)
