# -*- test-case-name: txssmi.tests.test_commands -*-

from txssmi.builder import SSMIRequest, SSMIResponse
from txssmi.constants import CODING_7BIT, PROTOCOL_STANDARD


Login = SSMIRequest.create('LOGIN')
SendSMS = SSMIRequest.create('SEND_SMS', {'validity': 0})
SendBinarySMS = SSMIRequest.create('SEND_BINARY_SMS', {
    'validity': 0,
    'coding': CODING_7BIT,
    'pid': PROTOCOL_STANDARD,
})
SendUSSDMessage = SSMIRequest.create('SEND_USSD_MESSAGE')
SendWAPPushMessage = SSMIRequest.create('SEND_WAP_PUSH_MESSAGE')
SendMMSMessage = SSMIRequest.create('SEND_MMS_MESSAGE')
SendExtendedUSSDMessage = SSMIRequest.create('SEND_EXTENDED_USSD_MESSAGE')
IMSILookup = SSMIRequest.create('IMSI_LOOKUP', {
    'imsi': '',
})
LinkCheck = SSMIRequest.create('LINK_CHECK')
Logout = SSMIRequest.create('LOGOUT')

Ack = SSMIResponse.create('ACK')
Seq = SSMIResponse.create('SEQ')
IMSILookupReply = SSMIResponse.create('IMSI_LOOKUP_REPLY')
