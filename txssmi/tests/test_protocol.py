from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet import reactor
from twisted.test.proto_helpers import StringTransport

from txssmi.builder import SSMICommand
from txssmi.commands import Login, Ack
from txssmi.protocol import SSMIProtocol


class ProtocolTestCase(TestCase):

    timeout = 1

    def setUp(self):
        self.protocol = SSMIProtocol()
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
        d = self.protocol.authenticate('username', 'password')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'LOGIN')
        yield self.send(Ack(ack_type=1))
        self.assertTrue((yield d))

    @inlineCallbacks
    def test_send_sms(self):
        self.protocol.send_sms('2700000000', 'hi there!', validity=2)
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_SMS')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.message, 'hi there!')
        self.assertEqual(cmd.validity, '2')
