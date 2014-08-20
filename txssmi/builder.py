from txssmi.constants import (
    SSMI_HEADER,
    REQUEST_IDS, REQUEST_NAMES, REQUEST_FIELDS,
    RESPONSE_IDS, RESPONSE_NAMES, RESPONSE_FIELDS)


class SSMIException(Exception):
    pass


class SSMICommandException(SSMIException):
    pass


class SSMICommand(object):

    command_name = None
    command_id = None
    fields = []
    defaults = {}
    command_name_map = {}
    command_id_map = {}
    command_field_map = {}

    def __init__(self, **kwargs):
        self.values = self.defaults.copy()
        self.values.update(kwargs)

        fields = set(self.values.keys())
        known_fields = set(self.fields)

        unsupported_fields = fields - known_fields
        if unsupported_fields:
            raise SSMICommandException(
                'Unsupported fields: %s' % (', '.join(unsupported_fields),))

        missing_fields = known_fields - fields
        if missing_fields:
            raise SSMICommandException(
                'Missing fields: %s' % (', '.join(missing_fields),))

    def __iter__(self):
        parts = [SSMI_HEADER, self.command_id]
        parts.extend([self.values.get(fn) for fn in self.fields])
        return iter(parts)

    def __str__(self):
        return ','.join(self)

    def __eq__(self, other):
        return str(other) == str(self)

    def __getattr__(self, attr):
        if attr in self.fields:
            return self.values[attr]

    def __repr__(self):
        return '<%s command_id=%s values=%r>' % (
            self.command_name, self.command_id,
            self.values)

    @classmethod
    def create(cls, command_name, defaults={}):
        return type('%s%s' % (command_name.title(), cls.__name__), (cls,), {
            'command_name': command_name,
            'command_id': cls.command_id_map[command_name],
            'fields': cls.command_field_map[command_name],
            'defaults': defaults,
        })

    @classmethod
    def parse(cls, command_string):
        header, _, command_string = command_string.partition(',')
        if header != SSMI_HEADER:
            raise SSMICommandException('Unknown header: %s.' % (SSMI_HEADER,))
        command_id, _, command_values = command_string.partition(',')
        command_name = cls.command_name_map.get(command_id)
        if command_name is None:
            raise SSMICommandException(
                'Unknown command id: %s.' % (command_id,))
        command_fields = cls.command_field_map[command_name]
        command_values = command_values.split(',', len(command_fields) - 1)
        if len(command_values) < len(command_fields):
            raise SSMICommandException(
                'Too few parameters for command: %s (expected %s got %s)' % (
                    command_name, len(command_fields), len(command_values)))
        values = dict(zip(command_fields, command_values))
        command_cls = cls.create(command_name)
        return command_cls(**values)


class SSMIRequest(SSMICommand):
    command_id_map = REQUEST_IDS
    command_name_map = REQUEST_NAMES
    command_field_map = REQUEST_FIELDS


class SSMIResponse(SSMICommand):
    command_id_map = RESPONSE_IDS
    command_name_map = RESPONSE_NAMES
    command_field_map = RESPONSE_FIELDS
