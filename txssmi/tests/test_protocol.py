import binascii

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.task import Clock
from twisted.test.proto_helpers import StringTransport
from twisted.trial.unittest import TestCase

from txssmi.builder import SSMICommand
from txssmi.commands import Login, Ack
from txssmi.protocol import SSMIProtocol
from txssmi.constants import CODING_8BIT, PROTOCOL_ENHANCED


class ProtocolTestCase(TestCase):

    protocol_class = SSMIProtocol
    timeout = 1

    def setUp(self):
        self.clock = Clock()
        self.patch(self.protocol_class, 'clock', self.clock)
        self.protocol = self.protocol_class()
        self.protocol.noisy = True
        self.transport = StringTransport()
        self.protocol.makeConnection(self.transport)

    def send(self, command):
        return self.protocol.lineReceived(str(command))

    def receive(self, count, clear=True):
        d = Deferred()

        def check_for_input():
            if not self.transport.value():
                reactor.callLater(0, check_for_input)
                return

            lines = self.transport.value().split(self.protocol.delimiter)
            commands = map(SSMICommand.parse, filter(None, lines))
            if len(commands) == count:
                d.callback(commands)
                if clear:
                    self.transport.clear()

        check_for_input()

        return d

    @inlineCallbacks
    def test_login(self):
        self.protocol.login('username', 'password')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd, Login(username='username', password='password'))

    @inlineCallbacks
    def test_authenticate(self):
        self.assertFalse(self.protocol.authenticated)
        d = self.protocol.authenticate('username', 'password')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'LOGIN')
        yield self.send(Ack(ack_type=1))
        self.assertTrue((yield d))
        self.assertTrue(self.protocol.authenticated)

    @inlineCallbacks
    def test_send_message(self):
        self.protocol.send_message('2700000000', 'hi there!', validity=2)
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_SMS')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.message, 'hi there!')
        self.assertEqual(cmd.validity, '2')

    @inlineCallbacks
    def test_link_check(self):
        self.assertFalse(self.transport.value())
        self.protocol.authenticated = False
        self.protocol.link_check.start(60)
        self.assertEqual(self.transport.value(), '')
        self.protocol.authenticated = True
        self.clock.advance(60)
        [check1] = yield self.receive(1)
        self.clock.advance(60)
        [check2] = yield self.receive(1)
        self.assertEqual(check1.command_name, 'LINK_CHECK')
        self.assertEqual(check2.command_name, 'LINK_CHECK')

    @inlineCallbacks
    def test_send_binary_sms(self):
        self.protocol.send_binary_message(
            '2700000000', binascii.hexlify('hello world'),
            protocol_id=PROTOCOL_ENHANCED, coding=CODING_8BIT)
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_BINARY_SMS')
        self.assertEqual(binascii.unhexlify(cmd.hex_msg), 'hello world')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.pid, PROTOCOL_ENHANCED)
        self.assertEqual(cmd.coding, CODING_8BIT)

    @inlineCallbacks
    def test_logout(self):
        self.protocol.logout()
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'LOGOUT')
