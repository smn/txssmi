# -*- test-case-name: txssmi.tests.test_commands -*-

from txssmi.builder import SSMICommand
from txssmi.constants import CODING_7BIT, PROTOCOL_STANDARD


Login = SSMICommand.create('LOGIN')
Ack = SSMICommand.create('ACK')
SendSMS = SSMICommand.create('SEND_SMS', {'validity': 0})
SendBinarySMS = SSMICommand.create('SEND_BINARY_SMS', {
    'validity': 0,
    'coding': CODING_7BIT,
    'pid': PROTOCOL_STANDARD,
})
SendUSSDMessage = SSMICommand.create('SEND_USSD_MESSAGE')
SendWAPPushMessage = SSMICommand.create('SEND_WAP_PUSH_MESSAGE')
SendMMSMessage = SSMICommand.create('SEND_MMS_MESSAGE')
LinkCheck = SSMICommand.create('LINK_CHECK')
Logout = SSMICommand.create('LOGOUT')
