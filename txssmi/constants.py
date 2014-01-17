SSMI_HEADER = 'SSMI'

COMMANDS = {
    '1': ('LOGIN', ['username', 'password']),
    '2': ('SEND_SMS', ['validity', 'msisdn', 'message']),
    '3': ('LINK_CHECK', []),
    '4': ('SEND_BINARY_SMS', ['validity', 'msisdn', 'pid', 'coding',
                              'hex_msg']),
    '99': ('LOGOUT', []),
    '101': ('ACK', ['ack_type']),
    '110': ('SEND_USSD_MESSAGE', ['msisdn', 'type', 'message']),
    '111': ('SEND_MMS_MESSAGE', ['msisdn', 'subject', 'name', 'content']),
    '112': ('SEND_WAP_PUSH_MESSAGE', ['msisdn', 'subject', 'url'])
}


COMMAND_NAMES = dict([(cmd_id, cmd_tuple[0])
                      for cmd_id, cmd_tuple in COMMANDS.items()])
COMMAND_IDS = dict([(value, key)
                    for key, value in COMMAND_NAMES.items()])
COMMAND_FIELDS = dict(value for key, value in COMMANDS.items())

CODING_7BIT = '0'
CODING_8BIT = '246'

PROTOCOL_STANDARD = '0'
PROTOCOL_ENHANCED = '15'

USSD_RESPONSE = '2'
USSD_END = '3'
USSD_REDIRECT = '5'
USSD_INITIATE = '6'

ACK_LOGIN_OK = '1'
ACK_LINK_CHECK_RESPONSE = '2'
