# -*- test-case-name: txssmi.tests.test_protocol -*-

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred, succeed, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.commands import Login, SendSMS, LinkCheck
from txssmi.constants import COMMAND_IDS, ACK_TYPES
from txssmi.builder import SSMICommand

gsm = gsm0338()


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False
    clock = reactor

    def __init__(self):
        self.authenticated = False
        self.command_queue = DeferredQueue()
        self.link_check = LoopingCall(self.send_link_request)
        self.link_check.clock = self.clock

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def lineReceived(self, line):
        command = SSMICommand.parse(line)
        self.emit('<<', repr(command))
        handler = getattr(self, 'handle_%s' % (command.command_name,))
        return maybeDeferred(handler, command)

    def send_command(self, command):
        self.emit('>>', repr(command))
        return succeed(self.sendLine(str(command)))

    def send_link_request(self):
        return self.send_command(LinkCheck())

    def login(self, username, password):
        return self.send_command(Login(username=username, password=password))

    def authenticate(self, username, password):
        d = self.login(username, password)
        d.addCallback(lambda _: self.command_queue.get())
        d.addCallback(lambda cmd: (cmd.command_id == COMMAND_IDS['ACK'] and
                                   cmd.ack_type == ACK_TYPES['LOGIN_OK']))

        def cb(result):
            self.authenticated = result
            return result

        d.addCallback(cb)
        return d

    def send_sms(self, msisdn, message, validity=0):
        return self.send_command(
            SendSMS(msisdn=msisdn, message=message, validity=validity))

    def handle_ACK(self, ack):
        return self.command_queue.put(ack)
