# -*- test-case-name: txssmi.tests.test_commands -*-

from txssmi.builder import SSMICommand


Login = SSMICommand.create('LOGIN')
Ack = SSMICommand.create('ACK')
