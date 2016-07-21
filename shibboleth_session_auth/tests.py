"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User, Group

TEST_GROUP = "Example Staff"
TEST_SHIBBOLETH_SESSION_AUTH = {
    'IDP_ATTRIBUTE': 'HTTP_SHIB_IDENTITY_PROVIDER',
    'AUTHORIZED_IDPS': [
        'https://idp.example.com/idp/shibboleth',
    ],
    'USER_ATTRIBUTES': [
        ('HTTP_MAIL', 'username', True),
        ('HTTP_MAIL', 'email', True),
        ('HTTP_GIVENNAME', 'first_name', False),
        ('HTTP_SN', 'last_name', False),
    ],
    'GROUPS_BY_IDP': {
        'https://idp.example.com/idp/shibboleth': [
            TEST_GROUP,
        ],
    },
    'GROUP_ATTRIBUTE': 'HTTP_OU',
}

#@override_settings(
#   ROOT_URLCONF=TEST_URL_CONF,
#   SHIBBOLETH_SESSION_AUTH=TEST_SHIBBOLETH_SESSION_AUTH
#)
class TestShibInteractions(TestCase):
    urls = 'shibboleth_session_auth.test_urls'

    def setUp(self):
        settings.SHIBBOLETH_SESSION_AUTH = TEST_SHIBBOLETH_SESSION_AUTH

        self.shib_user_attr = {
            'HTTP_MAIL': 'alice@example.com',
            'HTTP_GIVENNAME': 'Alice',
            'HTTP_SN': 'Alice',
        }
        self.shib_user_attr[TEST_SHIBBOLETH_SESSION_AUTH['IDP_ATTRIBUTE']] = \
            TEST_SHIBBOLETH_SESSION_AUTH['AUTHORIZED_IDPS'][0]
        self.alice = User.objects.create(
            username=self.shib_user_attr['HTTP_MAIL'],
            email=self.shib_user_attr['HTTP_MAIL'],
            first_name=self.shib_user_attr['HTTP_GIVENNAME'],
            last_name=self.shib_user_attr['HTTP_SN'],
        )

        self.common_group = Group.objects.create(name=TEST_GROUP)
        self.alice.groups.add(self.common_group)

        self.shib_new_user_attr = {
            'HTTP_MAIL': 'bob@example.com',
            'HTTP_GIVENNAME': 'Bob',
            'HTTP_SN': 'Bob',
            'HTTP_OU': 'foo;bar',
        }
        self.shib_new_user_attr[TEST_SHIBBOLETH_SESSION_AUTH['IDP_ATTRIBUTE']] = \
            TEST_SHIBBOLETH_SESSION_AUTH['AUTHORIZED_IDPS'][0]


    def test_invalid_idp_response(self):
        """Test for invalid IdP context"""
        c = Client()
        r = c.get("/")
        self.assertEqual(r.status_code, 400)

    def test_unauthorized_idp(self):
        """Test for an unauthorized IdP"""
        d = {}
        d[TEST_SHIBBOLETH_SESSION_AUTH['IDP_ATTRIBUTE']] = 'WRONG'
        c = Client(**d)
        r = c.get("/")
        self.assertEqual(r.status_code, 403)

    def test_missing_attributes(self):
        """Test for missing required attributes"""
        d = {}
        d[TEST_SHIBBOLETH_SESSION_AUTH['IDP_ATTRIBUTE']] = TEST_SHIBBOLETH_SESSION_AUTH['AUTHORIZED_IDPS'][0]
        c = Client(**d)
        r = c.get("/")
        self.assertEqual(r.status_code, 400)

    def test_existing_user(self):
        """Try authenticating an existing user."""
        c = Client(**self.shib_user_attr)
        r = c.get("/")
        self.assertEqual(r.status_code, 302)

    def test_existing_user_add_group(self):
        """Ensure existing user is a member of the right groups."""
        self.alice.groups.remove(self.common_group)
        c = Client(**self.shib_user_attr)
        r = c.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertTrue(self.common_group in self.alice.groups.all())

    def test_new_user(self):
        """Create Django User if does not exist."""
        c = Client(**self.shib_new_user_attr)
        r = c.get("/")
        self.assertEqual(r.status_code, 302)
        bob = User.objects.filter(email=self.shib_new_user_attr['HTTP_MAIL'])
        self.assertEqual(bob.count(), 1)
        bob = bob[0]
        self.assertTrue(self.common_group in bob.groups.all())
        bob_group_names = [ x.name for x in bob.groups.all() ]
        self.assertIn('foo', bob_group_names)
        self.assertIn('bar', bob_group_names)
