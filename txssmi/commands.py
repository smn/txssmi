# -*- test-case-name: txssmi.tests.test_commands -*-

from txssmi.builder import SSMIRequest, SSMIResponse
from txssmi.constants import CODING_7BIT, PROTOCOL_STANDARD


Login = SSMIRequest.create('LOGIN')
SendSMS = SSMIRequest.create('SEND_SMS', {'validity': '0'})
SendBinarySMS = SSMIRequest.create('SEND_BINARY_SMS', {
    'validity': '0',
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
ClientLogout = SSMIRequest.create('LOGOUT')

Ack = SSMIResponse.create('ACK')
Nack = SSMIResponse.create('NACK')
Seq = SSMIResponse.create('SEQ')
MoMessage = SSMIResponse.create('MO')
DrMessage = SSMIResponse.create('DR')
FFMessage = SSMIResponse.create('FREE_FORM')
BMoMessage = SSMIResponse.create('BINARY_MO')
PremiumMoMessage = SSMIResponse.create('PREMIUM_MO')
PremiumBMoMessage = SSMIResponse.create('PREMIUM_BINARY_MO')
IMSILookupReply = SSMIResponse.create('IMSI_LOOKUP_REPLY')
USSDMessage = SSMIResponse.create('USSD_MESSAGE')
ExtendedUSSDMessage = SSMIResponse.create('EXTENDED_USSD_MESSAGE')
ServerLogout = SSMIResponse.create('LOGOUT')
