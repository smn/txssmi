# -*- test-case-name: txssmi.tests.test_protocol -*-

import binascii
import random
from collections import defaultdict

from twisted.internet import reactor
from twisted.internet.defer import (
    maybeDeferred, succeed, DeferredQueue, Deferred)
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.commands import (
    Login, SendSMS, LinkCheck, SendBinarySMS, Logout, SendUSSDMessage,
    SendWAPPushMessage, SendMMSMessage, IMSILookup, SendExtendedUSSDMessage,
    MoMessage)
from txssmi.constants import (
    RESPONSE_IDS, ACK_LOGIN_OK, CODING_7BIT, PROTOCOL_STANDARD, USSD_NEW,
    USSD_RESPONSE, USSD_END)
from txssmi.builder import SSMIResponse, SSMICommandException

gsm = gsm0338()


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False
    clock = reactor

    def __init__(self):
        self.authenticated = False
        self.event_queue = DeferredQueue()
        self.sequence_reply_map = defaultdict(lambda: DeferredQueue())
        self.imsi_lookup_reply_map = defaultdict(lambda: DeferredQueue())
        self.link_check = LoopingCall(self.send_link_request)
        self.link_check.clock = self.clock
        self.imsi_lookups = {}

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def lineReceived(self, line):
        command = SSMIResponse.parse(line)
        self.emit('<<', str(command))
        handler = getattr(self, 'handle_%s' % (command.command_name,))
        return maybeDeferred(handler, command)

    def send_command(self, command):
        self.emit('>>', str(command))
        self.sendLine(str(command))
        return succeed(command)

    def send_link_request(self):
        if not self.authenticated:
            return
        return self.send_command(LinkCheck())

    def wait_for_reply(self, msisdn):
        return self.sequence_reply_map[msisdn].get()

    def login(self, username, password):
        return self.send_command(Login(username=username, password=password))

    def logout(self):
        return self.send_command(Logout())

    def authenticate(self, username, password):
        d = self.login(username, password)
        d.addCallback(lambda _: self.event_queue.get())

        def cb(cmd):
            success = (cmd.command_id == RESPONSE_IDS['ACK'] and
                       cmd.ack_type == ACK_LOGIN_OK)
            self.authenticated = success
            return cmd

        d.addCallback(cb)
        return d

    def send_message(self, msisdn, message, validity=0):
        d = self.send_command(
            SendSMS(msisdn=msisdn, message=message, validity=validity))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def send_binary_message(self, msisdn, hex_message, validity=0,
                            protocol_id=PROTOCOL_STANDARD,
                            coding=CODING_7BIT):
        d = self.send_command(
            SendBinarySMS(msisdn=msisdn, hex_msg=hex_message,
                          validity=validity, pid=protocol_id, coding=coding))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def send_ussd_message(self, msisdn, message, session_type):
        d = self.send_command(
            SendUSSDMessage(msisdn=msisdn, message=message, type=session_type))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def send_extended_ussd_message(self, msisdn, message, session_type,
                                   genfields):
        if session_type not in [USSD_NEW, USSD_RESPONSE, USSD_END]:
            raise SSMICommandException(
                'Invalid session_type: %s' % (session_type,))
        d = self.send_command(
            SendExtendedUSSDMessage(msisdn=msisdn, message=message,
                                    type=session_type,
                                    genfields=':'.join(genfields)))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def send_wap_push_message(self, msisdn, subject, url):
        d = self.send_command(
            SendWAPPushMessage(msisdn=msisdn, subject=subject, url=url))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def send_mms_message(self, msisdn, subject, name, content):
        d = self.send_command(
            SendMMSMessage(msisdn=msisdn, subject=subject, name=name,
                           content=content))
        d.addCallback(lambda cmd: self.wait_for_reply(cmd.msisdn))
        return d

    def imsi_lookup(self, msisdn, sequence=None, imsi=None):
        if sequence is None:
            sequence = unicode(random.randint(0, 1000))
        d = self.send_command(IMSILookup(sequence=sequence, msisdn=msisdn,
                                         imsi=imsi))
        deferred = Deferred()
        self.imsi_lookup_reply_map[sequence] = deferred
        d.addCallback(lambda _: deferred)
        return d

    def handle_ACK(self, ack):
        return self.event_queue.put(ack)

    def handle_NACK(self, nack):
        return self.event_queue.put(nack)

    def handle_IMSI_LOOKUP_REPLY(self, resp):
        return self.imsi_lookup_reply_map[resp.sequence].callback(resp)

    def handle_SEQ(self, seq):
        return self.sequence_reply_map[seq.msisdn].put(seq)

    def handle_MO(self, mo):
        print 'mo', mo
