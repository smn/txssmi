# -*- test-case-name: txssmi.tests.test_protocol -*-

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred, succeed, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.commands import (
    Login, SendSMS, LinkCheck, SendBinarySMS, Logout, USSDMessage,
    WAPPushMessage)
from txssmi.constants import (
    COMMAND_IDS, ACK_LOGIN_OK, CODING_7BIT, PROTOCOL_STANDARD)
from txssmi.builder import SSMICommand

gsm = gsm0338()


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False
    clock = reactor

    def __init__(self):
        self.authenticated = False
        self.event_queue = DeferredQueue()
        self.link_check = LoopingCall(self.send_link_request)
        self.link_check.clock = self.clock

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def lineReceived(self, line):
        command = SSMICommand.parse(line)
        self.emit('<<', str(command))
        handler = getattr(self, 'handle_%s' % (command.command_name,))
        return maybeDeferred(handler, command)

    def send_command(self, command):
        self.emit('>>', str(command))
        return succeed(self.sendLine(str(command)))

    def send_link_request(self):
        if not self.authenticated:
            return
        return self.send_command(LinkCheck())

    def login(self, username, password):
        return self.send_command(Login(username=username, password=password))

    def logout(self):
        return self.send_command(Logout())

    def authenticate(self, username, password):
        d = self.login(username, password)
        d.addCallback(lambda _: self.event_queue.get())

        def cb(cmd):
            success = (cmd.command_id == COMMAND_IDS['ACK'] and
                       cmd.ack_type == ACK_LOGIN_OK)
            self.authenticated = success
            return cmd

        d.addCallback(cb)
        return d

    def send_message(self, msisdn, message, validity=0):
        return self.send_command(
            SendSMS(msisdn=msisdn, message=message, validity=validity))

    def send_binary_message(self, msisdn, hex_message, validity=0,
                            protocol_id=PROTOCOL_STANDARD,
                            coding=CODING_7BIT):
        return self.send_command(
            SendBinarySMS(msisdn=msisdn, hex_msg=hex_message,
                          validity=validity, pid=protocol_id, coding=coding))

    def send_ussd_message(self, msisdn, message, session_type):
        return self.send_command(
            USSDMessage(msisdn=msisdn, message=message, type=session_type))

    def send_wap_push_message(self, msisdn, subject, url):
        return self.send_command(
            WAPPushMessage(msisdn=msisdn, subject=subject, url=url))

    def handle_ACK(self, ack):
        return self.event_queue.put(ack)

    def handle_NACK(self, nack):
        return self.event_queue.put(nack)
