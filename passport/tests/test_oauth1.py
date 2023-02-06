# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.misc import urllib_quote
from passport.backend.social.common.oauth1 import (
    OAUTH1_SIGNATURE_TYPE_AUTH_HEADER,
    OAUTH1_SIGNATURE_TYPE_QUERY,
    Oauth1RequestSigner,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_SECRET2,
    APPLICATION_TOKEN1,
    AUTHORIZATION_CODE1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    RETPATH2,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.useragent import Request


OAUTH_NONCE1 = 'nonce'
OAUTH_NONCE2 = 'nonce2'
OAUTH_TIMESTAMP1 = '12345'
OAUTH_TIMESTAMP2 = '23451'


class Oauth1RequestSignerTestCase(TestCase):
    def _build_request(self, **values):
        defaults = dict(
            method='GET',
            url='https://www.yandex.ru',
            headers=None,
            params={'bar': 'bar'},
            data={'spam': 'spam'},
            timeout=0.1,
            retries=1,
            not_quotable_params=None,
        )
        for key in defaults:
            values.setdefault(key, defaults[key])
        return Request(**values)

    def _build_authorization_args(self, values=None):
        defaults = {
            'oauth_version': '1.0',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_signature': '',
        }
        values = values or dict()
        for key in defaults:
            values.setdefault(key, defaults[key])
        return values

    def _build_authorization_header(self, values=None):
        values = self._build_authorization_args(values)
        bits = [
            'oauth_nonce="%s"' % values['oauth_nonce'],
            'oauth_timestamp="%s"' % values['oauth_timestamp'],
            'oauth_version="%s"' % values['oauth_version'],
            'oauth_signature_method="%s"' % values['oauth_signature_method'],
            'oauth_consumer_key="%s"' % values['oauth_consumer_key'],
        ]
        if 'oauth_callback' in values:
            bits.append('oauth_callback="%s"' % values['oauth_callback'])
        if 'oauth_token' in values:
            bits.append('oauth_token="%s"' % values['oauth_token'])
        if 'oauth_verifier' in values:
            bits.append('oauth_verifier="%s"' % values['oauth_verifier'])
        bits += [
            'oauth_signature="%s"' % values['oauth_signature'],
        ]
        return 'OAuth ' + ', '.join(bits)


class TestOauth1RequestSignerRequest(Oauth1RequestSignerTestCase):
    DEFAULT_SIGNATURE = 'Q1Rm5hm8UHqZWuxUd7xUk48FWWI%3D'

    def setUp(self):
        super(TestOauth1RequestSignerRequest, self).setUp()
        self._signer = Oauth1RequestSigner(
            client_id=EXTERNAL_APPLICATION_ID1,
            client_secret=APPLICATION_SECRET1,
            oauth_nonce=OAUTH_NONCE1,
            oauth_timestamp=OAUTH_TIMESTAMP1,
        )

    def _build_authorization_args(self, values=None):
        defaults = {
            'oauth_nonce': OAUTH_NONCE1,
            'oauth_timestamp': OAUTH_TIMESTAMP1,
            'oauth_consumer_key': EXTERNAL_APPLICATION_ID1,
        }
        values = values or dict()
        for key in defaults:
            values.setdefault(key, defaults[key])
        return super(TestOauth1RequestSignerRequest, self)._build_authorization_args(values)

    def test_default(self):
        request = self._build_request()
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={'Authorization': self._build_authorization_header({'oauth_signature': self.DEFAULT_SIGNATURE})},
            ),
        )

    def test_headers(self):
        # Заголовки не подписываются
        request = self._build_request(headers={'plato': 'greek'})
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({'oauth_signature': self.DEFAULT_SIGNATURE}),
                    'plato': 'greek',
                },
            ),
        )

    def test_get(self):
        request = self._build_request(method='GET')
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                method='GET',
                headers={'Authorization': self._build_authorization_header({'oauth_signature': self.DEFAULT_SIGNATURE})},
            ),
        )

    def test_post(self):
        request = self._build_request(method='POST')
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                method='POST',
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'VvihmlJR9Zj64ppHOo6EG7MS%2F7E%3D'})},
            ),
        )

    def test_http(self):
        request = self._build_request(url='http://www.foo.bar/')
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                url='http://www.foo.bar/',
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'yrdFzFbEThSb1eg6GoOTQlaez3w%3D'})},
            ),
        )

    def test_https(self):
        request = self._build_request(url='https://www.foo.bar/')
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                url='https://www.foo.bar/',
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'haC0eRScwXpA5jfmiJAPRpKjRPQ%3D'})},
            ),
        )

    def test_url(self):
        request = self._build_request(url='http://www.notfoo.bar/')
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                url='http://www.notfoo.bar/',
                headers={'Authorization': self._build_authorization_header({'oauth_signature': '9ycA7w2WG9aKi9VFiwWI7AQENLE%3D'})},
            ),
        )

    def test_params(self):
        request = self._build_request(params={'mr': 'krab'})
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                params={'mr': 'krab'},
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'd09prxXcMB%2F%2BdAU6IjbSDV8ANAg%3D'})},
            ),
        )

    def test_data(self):
        request = self._build_request(method='POST', data={'mr': 'krab'})
        signed_request = self._signer.get_signed_request(request)
        self.assertEqual(
            signed_request,
            self._build_request(
                method='POST',
                data={'mr': 'krab'},
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'HIPKSUUsl4hMFG%2BIN6VisBoQQRI%3D'})},
            ),
        )


class TestOauth1RequestSignerConstuctor(Oauth1RequestSignerTestCase):
    def setUp(self):
        super(TestOauth1RequestSignerConstuctor, self).setUp()
        self._request = self._build_request()

    def _build_signer(self, **kwargs):
        defaults = dict(
            client_id=EXTERNAL_APPLICATION_ID1,
            client_secret=APPLICATION_SECRET1,
            oauth_nonce=OAUTH_NONCE1,
            oauth_timestamp=OAUTH_TIMESTAMP1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Oauth1RequestSigner(**kwargs)

    def _build_authorization_args(self, values=None):
        defaults = {
            'oauth_nonce': OAUTH_NONCE1,
            'oauth_timestamp': OAUTH_TIMESTAMP1,
            'oauth_consumer_key': EXTERNAL_APPLICATION_ID1,
        }
        values = values or dict()
        for key in defaults:
            values.setdefault(key, defaults[key])
        return super(TestOauth1RequestSignerConstuctor, self)._build_authorization_args(values)

    def test_default(self):
        signer = self._build_signer()
        signed_request = signer.get_signed_request(self._request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'Q1Rm5hm8UHqZWuxUd7xUk48FWWI%3D'})},
            ),
        )

    def test_client_id(self):
        signer = self._build_signer(client_id=EXTERNAL_APPLICATION_ID2)
        signed_request = signer.get_signed_request(self._request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_consumer_key': EXTERNAL_APPLICATION_ID2,
                        'oauth_signature': 'Tr%2BBvBrCnHKTFSyPOjWtChfx5E4%3D',
                    }),
                },
            ),
        )

    def test_client_secret(self):
        signer = self._build_signer(client_secret=APPLICATION_SECRET2)
        signed_request = signer.get_signed_request(self._request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'qS0rKK13T2Zegj3nT%2FO5B8zJTFY%3D'})},
            ),
        )

    def test_signature_type_auth_header(self):
        signer = self._build_signer(signature_type=OAUTH1_SIGNATURE_TYPE_AUTH_HEADER)
        signed_request = signer.get_signed_request(self._request)
        self.assertEqual(
            signed_request,
            self._build_request(
                headers={'Authorization': self._build_authorization_header({'oauth_signature': 'Q1Rm5hm8UHqZWuxUd7xUk48FWWI%3D'})},
            ),
        )

    def test_signature_type_query(self):
        signer = self._build_signer(signature_type=OAUTH1_SIGNATURE_TYPE_QUERY)
        request = self._build_request(params={'foo': 'bar'})
        signed_request = signer.get_signed_request(request)

        params = {'foo': 'bar'}
        params.update(self._build_authorization_args({'oauth_signature': '/zWqxnGP7fcJ8piWUhHgmVUM58o='}))
        self.assertEqual(signed_request, self._build_request(params=params))

    def test_oauth_callback(self):
        signer = self._build_signer(oauth_callback=RETPATH2)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': '8SuzOu%2FuWSrMEX8yI6V9iAHfCtw%3D',
                        'oauth_callback': urllib_quote(RETPATH2, safe=''),
                    }),
                },
            ),
        )

    def test_oauth_token(self):
        signer = self._build_signer(oauth_token=APPLICATION_TOKEN1)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': 'hXAJrLZXFd5N1InvrniXOGJDo%2BU%3D',
                        'oauth_token': APPLICATION_TOKEN1,
                    }),
                },
            ),
        )

    def test_oauth_token_secret(self):
        signer = self._build_signer(oauth_token_secret=APPLICATION_SECRET1)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': 'tiRy8ryITWePhzVrh3QJOOyT%2FsA%3D',
                    }),
                },
            ),
        )

    def test_verifier(self):
        signer = self._build_signer(verifier=AUTHORIZATION_CODE1)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': 'qLdTH7rKAgwgbeag06hYkHbiQH4%3D',
                        'oauth_verifier': AUTHORIZATION_CODE1,
                    }),
                },
            ),
        )

    def test_oauth_nonce(self):
        signer = self._build_signer(oauth_nonce=OAUTH_NONCE2)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': '5ZU1W7WX32rsaotw9kay6Zeg7sY%3D',
                        'oauth_nonce': OAUTH_NONCE2,
                    }),
                },
            ),
        )

    def test_oauth_timestamp(self):
        signer = self._build_signer(oauth_timestamp=OAUTH_TIMESTAMP2)
        signed_request = signer.get_signed_request(self._request)

        self.assertEqual(
            signed_request,
            self._build_request(
                headers={
                    'Authorization': self._build_authorization_header({
                        'oauth_signature': 'NHu5lxiqrlNkjvNOc9utd7iTRUw%3D',
                        'oauth_timestamp': OAUTH_TIMESTAMP2,
                    }),
                },
            ),
        )


class TestOauth1RequestSignerQueryRequest(Oauth1RequestSignerTestCase):
    NO_PARAMS_SIGNATURE = '2K9gCjl9Iun23S9UO0tPkRnWgmQ='

    def setUp(self):
        super(TestOauth1RequestSignerQueryRequest, self).setUp()
        self._signer = Oauth1RequestSigner(
            client_id=EXTERNAL_APPLICATION_ID1,
            client_secret=APPLICATION_SECRET1,
            oauth_nonce=OAUTH_NONCE1,
            oauth_timestamp=OAUTH_TIMESTAMP1,
            signature_type=OAUTH1_SIGNATURE_TYPE_QUERY,
        )

    def _build_authorization_args(self, values=None):
        defaults = {
            'oauth_nonce': OAUTH_NONCE1,
            'oauth_timestamp': OAUTH_TIMESTAMP1,
            'oauth_consumer_key': EXTERNAL_APPLICATION_ID1,
        }
        values = values or dict()
        for key in defaults:
            values.setdefault(key, defaults[key])
        return super(TestOauth1RequestSignerQueryRequest, self)._build_authorization_args(values)

    def _assert_param_not_effect_signature(self, param_name):
        request = self._build_request(params={param_name: '1234'})
        signed_request = self._signer.get_signed_request(request)

        params = self._build_authorization_args({'oauth_signature': self.NO_PARAMS_SIGNATURE})
        self.assertEqual(signed_request, self._build_request(params=params))

    def test_no_params(self):
        request = self._build_request(params=None)
        signed_request = self._signer.get_signed_request(request)

        params = self._build_authorization_args({'oauth_signature': self.NO_PARAMS_SIGNATURE})
        self.assertEqual(signed_request, self._build_request(params=params))

    def test_some_params(self):
        request = self._build_request(params={'foo': 'bar'})
        signed_request = self._signer.get_signed_request(request)

        params = {'foo': 'bar'}
        params.update(self._build_authorization_args({'oauth_signature': '/zWqxnGP7fcJ8piWUhHgmVUM58o='}))
        self.assertEqual(signed_request, self._build_request(params=params))

    def test_not_quotable_params(self):
        request = self._build_request(
            params={},
            not_quotable_params={'oauth_callback'},
        )
        signed_request = self._signer.get_signed_request(request)

        params = self._build_authorization_args({'oauth_signature': '2K9gCjl9Iun23S9UO0tPkRnWgmQ='})
        self.assertEqual(
            signed_request,
            self._build_request(
                params=params,
                not_quotable_params={'oauth_callback'},
            ),
        )

    def test_old_oauth_body_hash(self):
        self._assert_param_not_effect_signature('oauth_body_hash')

    def test_old_oauth_callback(self):
        self._assert_param_not_effect_signature('oauth_callback')

    def test_old_oauth_consumer_key(self):
        self._assert_param_not_effect_signature('oauth_consumer_key')

    def test_old_oauth_nonce(self):
        self._assert_param_not_effect_signature('oauth_nonce')

    def test_old_oauth_signature(self):
        self._assert_param_not_effect_signature('oauth_signature')

    def test_old_oauth_signature_method(self):
        self._assert_param_not_effect_signature('oauth_signature_method')

    def test_old_oauth_timestamp(self):
        self._assert_param_not_effect_signature('oauth_timestamp')

    def test_old_oauth_token(self):
        self._assert_param_not_effect_signature('oauth_token')

    def test_old_oauth_verifier(self):
        self._assert_param_not_effect_signature('oauth_verifier')

    def test_old_oauth_version(self):
        self._assert_param_not_effect_signature('oauth_version')
