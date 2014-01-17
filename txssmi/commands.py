from txssmi.constants import (
    SSMI_HEADER, COMMAND_IDS, COMMAND_NAMES, COMMAND_FIELDS)


class SSMIException(Exception):
    pass


class SSMICommandException(SSMIException):
    pass


class SSMICommand(object):

    command_name = None
    request_type = None
    fields = []
    defaults = {}

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
        parts = [SSMI_HEADER, self.request_type]
        parts.extend([self.values.get(fn) for fn in self.fields])
        return iter(map(unicode, parts))

    def __unicode__(self):
        return u','.join(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return unicode(other) == unicode(self)

    def __getattr__(self, attr):
        if attr in self.fields:
            return self.values[attr]

    @classmethod
    def create(cls, command_name, defaults={}):
        return type('%sSSMICommand' % (command_name.title(),), (cls,), {
            'command_name': command_name,
            'request_type': COMMAND_IDS[command_name],
            'fields': COMMAND_FIELDS[command_name],
            'defaults': defaults,
        })

    @classmethod
    def parse(cls, command_string):
        parts = command_string.split(',')
        header = parts[0]
        if header != SSMI_HEADER:
            raise SSMICommandException('Unknown header: %s.' % (SSMI_HEADER,))
        command_id = parts[1]
        command_name = COMMAND_NAMES.get(command_id)
        if command_name is None:
            raise SSMICommandException(
                'Unknown command id: %s.' % (command_id,))
        command_values = parts[2:]
        command_fields = COMMAND_FIELDS[command_name]
        values = dict(zip(command_fields, command_values))
        command_cls = cls.create(command_name)
        return command_cls(**values)

Login = SSMICommand.create('LOGIN')
