import binascii

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.task import Clock
from twisted.test.proto_helpers import StringTransport
from twisted.trial.unittest import TestCase

from txssmi.builder import SSMIRequest
from txssmi.commands import (
    Login, Ack, IMSILookupReply, Seq, MoMessage, DrMessage, FFMessage,
    BMoMessage, PremiumMoMessage, PremiumBMoMessage, USSDMessage,
    ExtendedUSSDMessage, ServerLogout, Nack)
from txssmi.protocol import SSMIProtocol
from txssmi.constants import (
    CODING_8BIT, PROTOCOL_ENHANCED, USSD_INITIATE, USSD_NEW, DR_SUCCESS,
    USSD_PHASE_2, USSD_TIMEOUT)


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
            commands = map(SSMIRequest.parse, filter(None, lines))
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
        yield self.send(Ack(ack_type='1'))
        self.assertTrue((yield d))
        self.assertTrue(self.protocol.authenticated)

    @inlineCallbacks
    def test_send_message(self):
        self.protocol.send_message('2700000000', 'hi there!', validity='2')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_SMS')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.message, 'hi there!')
        self.assertEqual(cmd.validity, '2')

    @inlineCallbacks
    def test_send_message_with_comma(self):
        self.protocol.send_message('2700000000', 'foo, bar', validity='2')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_SMS')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.message, 'foo, bar')
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
    def test_send_binary_message(self):
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

    @inlineCallbacks
    def test_send_ussd_message(self):
        self.protocol.send_ussd_message(
            '2700000000', 'hello world', USSD_INITIATE)
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_USSD_MESSAGE')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.type, USSD_INITIATE)
        self.assertEqual(cmd.message, 'hello world')

    @inlineCallbacks
    def test_wap_push_message(self):
        self.protocol.send_wap_push_message(
            '2700000000', 'foo', 'http://bar/baz.gif')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_WAP_PUSH_MESSAGE')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.subject, 'foo')
        self.assertEqual(cmd.url, 'http://bar/baz.gif')

    @inlineCallbacks
    def test_send_mms_message(self):
        self.protocol.send_mms_message(
            '2700000000', 'subject', 'name.gif',
            binascii.hexlify('hello world'))
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_MMS_MESSAGE')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.subject, 'subject')
        self.assertEqual(cmd.name, 'name.gif')
        self.assertEqual(cmd.content, binascii.hexlify(u'hello world'))

    @inlineCallbacks
    def test_imsi_lookup(self):
        d = self.protocol.imsi_lookup('2700000000', imsi='12345')
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'IMSI_LOOKUP')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.imsi, '12345')
        sequence = cmd.sequence
        reply_cmd = IMSILookupReply(sequence=sequence, msisdn=cmd.msisdn,
                                    imsi=cmd.imsi, spid='spid')
        yield self.send(reply_cmd)
        response = yield d
        self.assertEqual(response, reply_cmd)

    @inlineCallbacks
    def test_send_extended_ussd_message(self):
        self.protocol.send_extended_ussd_message(
            '2700000000', message='hello world',
            session_type=USSD_NEW,
            genfields=['foo', 'bar', 'baz'])
        [cmd] = yield self.receive(1)
        self.assertEqual(cmd.command_name, 'SEND_EXTENDED_USSD_MESSAGE')
        self.assertEqual(cmd.msisdn, '2700000000')
        self.assertEqual(cmd.message, 'hello world')
        self.assertEqual(cmd.type, USSD_NEW)
        self.assertEqual(cmd.genfields, 'foo:bar:baz')

    @inlineCallbacks
    def test_received_sequence_message(self):
        d = self.protocol.send_binary_message('2700000000', 'foo')
        [cmd] = yield self.receive(1)
        yield self.send(Seq(msisdn='2700000000', sequence='bar'))
        resp = yield d
        self.assertEqual(resp.sequence, 'bar')
        self.assertEqual(resp.msisdn, '2700000000')

    @inlineCallbacks
    def test_mo(self):
        calls = []
        self.patch(self.protocol_class, 'handle_MO', calls.append)
        cmd = MoMessage(msisdn='2700000000', sequence='1',
                        message='foo')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_mo_with_comma(self):
        calls = []
        self.patch(self.protocol_class, 'handle_MO', calls.append)
        cmd = MoMessage(msisdn='2700000000', sequence='1',
                        message='foo, bar')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_dr(self):
        calls = []
        self.patch(self.protocol_class, 'handle_DR', calls.append)
        cmd = DrMessage(msisdn='2700000000', sequence='1', ret_code=DR_SUCCESS)
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_free_form(self):
        calls = []
        self.patch(self.protocol_class, 'handle_FREE_FORM', calls.append)
        cmd = FFMessage(text='foo')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_binary_mo(self):
        calls = []
        self.patch(self.protocol_class, 'handle_BINARY_MO', calls.append)
        cmd = BMoMessage(msisdn='2700000000', sequence='1',
                         coding=CODING_8BIT, pid=PROTOCOL_ENHANCED,
                         hex_msg=binascii.hexlify('hello'))
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_premium_mo(self):
        calls = []
        self.patch(self.protocol_class, 'handle_PREMIUM_MO', calls.append)
        cmd = PremiumMoMessage(msisdn='2700000000', sequence='1',
                               destination='foo', message='bar')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_premium_binary_mo(self):
        calls = []
        self.patch(self.protocol_class, 'handle_PREMIUM_BINARY_MO',
                   calls.append)
        cmd = PremiumBMoMessage(msisdn='2700000000', sequence='1',
                                coding=CODING_8BIT, pid=PROTOCOL_ENHANCED,
                                hex_msg=binascii.hexlify('hello'),
                                destination='foo')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_ussd_message(self):
        calls = []
        self.patch(self.protocol_class, 'handle_USSD_MESSAGE', calls.append)
        cmd = USSDMessage(msisdn='2700000000', type=USSD_TIMEOUT,
                          phase=USSD_PHASE_2, message='foo')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_extended_ussd_message(self):
        calls = []
        self.patch(self.protocol_class, 'handle_EXTENDED_USSD_MESSAGE',
                   calls.append)
        cmd = ExtendedUSSDMessage(msisdn='2700000000', type=USSD_NEW,
                                  phase=USSD_PHASE_2, message='*100#',
                                  genfields='655011234567890:1::')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_server_logout(self):
        calls = []
        self.patch(self.protocol_class, 'handle_LOGOUT', calls.append)
        cmd = ServerLogout(ip='127.0.0.1')
        yield self.send(cmd)
        self.assertEqual([cmd], calls)

    @inlineCallbacks
    def test_nack(self):
        cmd = Nack(nack_type='1')
        yield self.send(cmd)
        nack = yield self.protocol.event_queue.get()
        self.assertEqual(str(cmd), 'SSMI,102,1')
