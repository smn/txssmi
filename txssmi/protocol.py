# -*- test-case-name: txssmi.tests.test_protocol -*-

from functools import partial

from twisted.protocols.basic import LineReceiver
from twisted.python import log

from smspdu import gsm0338

from txssmi.commands import Login

gsm = gsm0338()


class SSMIProtocol(LineReceiver):

    delimeter = '\r'
    noisy = False

    def emit(self, prefix, msg):
        if self.noisy:
            log.msg('%s %s' % (prefix, msg))

    def send_command(self, command):
        self.emit('>>', '%s: %s' % (command.command_name, command.values))
        return self.sendLine(str(command))

    def login(self, username, password):
        self.send_command(Login(username=username, password=password))
