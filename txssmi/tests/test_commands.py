from twisted.trial.unittest import TestCase

from txssmi.builder import SSMIRequest, SSMICommandException


class SSMICommandTestCase(TestCase):

    def test_valid_fields(self):
        LoginRequest = SSMIRequest.create('LOGIN', {})
        login = LoginRequest(username='foo', password='bar')
        self.assertEqual(login.username, 'foo')
        self.assertEqual(login.password, 'bar')

    def test_defaults(self):
        LoginRequest = SSMIRequest.create('LOGIN', {'username': 'foo'})
        login = LoginRequest(password='bar')
        self.assertEqual(login.username, 'foo')
        self.assertEqual(login.password, 'bar')

    def test_missing_fields(self):
        LoginRequest = SSMIRequest.create('LOGIN', {'username': 'foo'})
        self.assertRaisesRegexp(
            SSMICommandException, 'Missing fields: password', LoginRequest)

    def test_unsupported_field(self):
        LoginRequest = SSMIRequest.create('LOGIN', {})
        self.assertRaisesRegexp(
            SSMICommandException, 'Unsupported fields: foo',
            LoginRequest, foo='foo')

    def test_parse(self):
        LoginRequest = SSMIRequest.create('LOGIN')
        expected_cmd = LoginRequest(username='foo', password='bar')
        cmd = SSMIRequest.parse('SSMI,1,foo,bar')
        self.assertEqual(cmd, expected_cmd)

    def test_parse_missing_fields(self):
        self.assertRaisesRegexp(
            SSMICommandException,
            'Too few parameters for command: LOGIN \(expected 2 got 1\)',
            SSMIRequest.parse, 'SSMI,1,foo')
