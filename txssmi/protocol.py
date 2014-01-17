# -*- test-case-name: txssmi.tests.test_protocol -*-

from twisted.internet.defer import maybeDeferred, succeed, DeferredQueue
from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.commands import Login, SSMICommand
from txssmi.constants import COMMAND_IDS, ACK_TYPES

gsm = gsm0338()


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False

    def __init__(self):
        self.command_queue = DeferredQueue()

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def lineReceived(self, line):
        cmd = SSMICommand.parse(line)
        handler = getattr(self, 'handle_%s' % (cmd.command_name,))
        return maybeDeferred(handler, cmd)

    def send_command(self, command):
        self.emit('>>', '%s: %s' % (command.command_name, command.values))
        return succeed(self.sendLine(str(command)))

    def login(self, username, password):
        return self.send_command(Login(username=username, password=password))

    def authenticate(self, username, password):
        d = self.login(username, password)
        d.addCallback(lambda _: self.command_queue.get())
        d.addCallback(lambda cmd: (cmd.command_id == COMMAND_IDS['ACK'] and
                                   cmd.ack_type == ACK_TYPES['LOGIN_OK']))
        return d

    def handle_ACK(self, ack):
        return self.command_queue.put(ack)
