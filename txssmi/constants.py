SSMI_HEADER = u"SSMI"

COMMANDS = {
    u"1": ("LOGIN", ["username", "password"]),
}


COMMAND_NAMES = dict([(cmd_id, cmd_tuple[0])
                      for cmd_id, cmd_tuple in COMMANDS.items()])
COMMAND_IDS = dict([(value, key)
                    for key, value in COMMAND_NAMES.items()])
COMMAND_FIELDS = dict(value for key, value in COMMANDS.items())


SSMI_USSD_TYPE_NEW = u"1"
SSMI_USSD_TYPE_EXISTING = u"2"
SSMI_USSD_TYPE_END = u"3"
SSMI_USSD_TYPE_TIMEOUT = u"4"
SSMI_USSD_TYPE_REDIRECT = u"5"
SSMI_USSD_TYPE_NI = u"6"

ack_reason = {
    "1": "Login OK",
    "2": "Link check response",
}

nack_reason = {
    "1": "Invalid username/password combination",
    "2": "Invalid/unknown message type",
    "3": "Could not parse message",
    "4": "Account suspended (non-payment or abuse)",
}

# "SEQ": u"100",
# "TEXT_MESSAGE": u"103",
# "DELIVERY_MESSAGE": u"104",
# "FREEFORM_MESSAGE": u"105",
# "BINARY_MESSAGE": u"106",
# "PREMIUMRATED_MESSAGE": u"107",
# "BINARY_PREMIUMRATED_MESSAGE": u"108",
# "USSD_EXTENDED": u"111",
# "EXTENDED_RETURN": u"113",
# "EXTENDED_RETURN_BINARY": u"116",
# "EXTENDED_PREMIUMRATED_MESSAGE": u"117",
# "EXTENDED_BINARY_PREMIUMRATED_MESSAGE": u"118",
