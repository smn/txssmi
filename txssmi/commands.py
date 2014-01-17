# -*- test-case-name: txssmi.tests.test_commands -*-

from txssmi.builder import SSMICommand


Login = SSMICommand.create('LOGIN')
Ack = SSMICommand.create('ACK')
SendSMS = SSMICommand.create('SEND_SMS', {'validity': 0})
LinkCheck = SSMICommand.create('LINK_CHECK')
