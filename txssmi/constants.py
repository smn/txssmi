SSMI_HEADER = 'SSMI'

SSMI_REQUESTS = {
    '1': ('LOGIN', ['username', 'password']),
    '2': ('SEND_SMS', ['validity', 'msisdn', 'message']),
    '3': ('LINK_CHECK', []),
    '4': ('SEND_BINARY_SMS', ['validity', 'msisdn', 'pid', 'coding',
                              'hex_msg']),
    '99': ('LOGOUT', []),
    '110': ('SEND_USSD_MESSAGE', ['msisdn', 'type', 'message']),
    '111': ('SEND_MMS_MESSAGE', ['msisdn', 'subject', 'name', 'content']),
    '112': ('SEND_WAP_PUSH_MESSAGE', ['msisdn', 'subject', 'url']),
    '120': ('SEND_EXTENDED_USSD_MESSAGE', ['msisdn', 'type', 'genfields',
                                           'message']),
    '600': ('IMSI_LOOKUP', ['sequence', 'msisdn', 'imsi'])
}

REQUEST_NAMES = dict([(cmd_id, cmd_tuple[0])
                      for cmd_id, cmd_tuple in SSMI_REQUESTS.items()])
REQUEST_IDS = dict([(value, key)
                    for key, value in REQUEST_NAMES.items()])
REQUEST_FIELDS = dict(value for key, value in SSMI_REQUESTS.items())

SSMI_RESPONSES = {
    '100': ('SEQ', ['msisdn', 'sequence']),
    '101': ('ACK', ['ack_type']),
    '102': ('NACK', ['nack_type']),
    '103': ('MO', ['msisdn', 'sequence', 'message']),
    '104': ('DR', ['msisdn', 'sequence', 'ret_code']),
    '105': ('FREE_FORM', ['text']),
    '106': ('BINARY_MO', ['msisdn', 'sequence', 'pid', 'coding', 'hex_msg']),
    '107': ('PREMIUM_MO', ['msisdn', 'sequence', 'destination', 'message']),
    '108': ('PREMIUM_BINARY_MO', ['msisdn', 'sequence', 'pid', 'coding',
                                  'destination', 'hex_msg']),
    '110': ('USSD_MESSAGE', ['msisdn', 'type', 'phase', 'message']),
    '111': ('EXTENDED_USSD_MESSAGE', ['msisdn', 'type', 'phase', 'genfields',
                                      'message']),
    '199': ('LOGOUT', ['ip']),
    '600': ('IMSI_LOOKUP_REPLY', ['sequence', 'msisdn', 'imsi', 'spid']),
}

RESPONSE_NAMES = dict([(cmd_id, cmd_tuple[0])
                       for cmd_id, cmd_tuple in SSMI_RESPONSES.items()])
RESPONSE_IDS = dict([(value, key)
                     for key, value in RESPONSE_NAMES.items()])
RESPONSE_FIELDS = dict(value for key, value in SSMI_RESPONSES.items())


CODING_7BIT = '0'
CODING_8BIT = '246'

PROTOCOL_STANDARD = '0'
PROTOCOL_ENHANCED = '15'

USSD_NEW = '1'
USSD_RESPONSE = '2'
USSD_END = '3'
USSD_TIMEOUT = '4'
USSD_REDIRECT = '5'
USSD_INITIATE = '6'

USSD_PHASE_UNKNOWN = '0'
USSD_PHASE_1 = '1'
USSD_PHASE_2 = '2'

ACK_LOGIN_OK = '1'
ACK_LINK_CHECK_RESPONSE = '2'

DR_SUCCESS = '0'
DR_MESSAGE_EXPIRED = '1'
DR_SIM_FULL = '2'
DR_DEST_BARRED = '3'
DR_INV_DEST_ADDR = '4'
DR_DEST_BLACKLISTED = '5'
