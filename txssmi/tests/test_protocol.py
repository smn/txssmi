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
            commands = self.transport.value().split(self.protocol.delimiter)
            if clear:
                self.transport.clear()
            d.callback(map(SSMICommand.parse, filter(None, commands)))

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
