from twisted.trial.unittest import TestCase

from txssmi.commands import SSMICommand, SSMICommandException


class SSMICommandTestCase(TestCase):

    def test_valid_fields(self):
        LoginCommand = SSMICommand.create('LOGIN', {})
        login = LoginCommand(username='foo', password='bar')
        self.assertEqual(login.username, 'foo')
        self.assertEqual(login.password, 'bar')

    def test_defaults(self):
        LoginCommand = SSMICommand.create('LOGIN', {'username': 'foo'})
        login = LoginCommand(password='bar')
        self.assertEqual(login.username, 'foo')
        self.assertEqual(login.password, 'bar')

    def test_missing_fields(self):
        LoginCommand = SSMICommand.create('LOGIN', {'username': 'foo'})
        self.assertRaisesRegexp(
            SSMICommandException, 'Missing fields: password', LoginCommand)

    def test_unsupported_field(self):
        LoginCommand = SSMICommand.create('LOGIN', {})
        self.assertRaisesRegexp(
            SSMICommandException, 'Unsupported fields: foo',
            LoginCommand, foo='foo')

    def test_parse(self):
        LoginCommand = SSMICommand.create('LOGIN')
        expected_cmd = LoginCommand(username='foo', password='bar')
        cmd = SSMICommand.parse('SSMI,1,foo,bar')
        self.assertEqual(cmd, expected_cmd)
