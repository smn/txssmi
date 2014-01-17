# -*- test-case-name: txssmi.tests.test_protocol -*-

from functools import partial

from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.constants import SSMI_HEADER

gsm = gsm0338()


class Request(object):

    def __init__(self, request_type, *request_fields):
        self.request_type = request_type
        self.request_fields = request_fields

    def __iter__(self):
        parts = [SSMI_HEADER, self.request_type]
        parts.extend(self.request_fields)
        return iter(map(unicode, parts))

    def __unicode__(self):
        return u','.join(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return unicode(other) == unicode(self)

    @classmethod
    def create(cls, request_type):
        return partial(cls, request_type)


Login = Request.create(1)


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def send_command(self, command):
        self.emit('>>', command)
        return self.sendLine(str(command))

    def login(self, username, password):
        self.send_command(Login(username, password))
