SSMI_HEADER = "SSMI"

COMMANDS = {
    "1": ("LOGIN", ["username", "password"]),
    "101": ("ACK", ["ack_type"]),
}


COMMAND_NAMES = dict([(cmd_id, cmd_tuple[0])
                      for cmd_id, cmd_tuple in COMMANDS.items()])
COMMAND_IDS = dict([(value, key)
                    for key, value in COMMAND_NAMES.items()])
COMMAND_FIELDS = dict(value for key, value in COMMANDS.items())

ACK_TYPES = {
    "LOGIN_OK": "1",
    "LINK_CHECK_RESPONSE": "2",
}
