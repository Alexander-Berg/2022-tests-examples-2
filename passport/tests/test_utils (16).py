# -*- coding: utf-8 -*
import base64

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.oauth.admin.admin.utils import (
    AmCredentialsManager,
    DecryptFailedError,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


TEST_SECRET = base64.b64encode(b'b' * 16).decode()


class AmCredentialsManagerTestcase(BaseTestCase):
    def setUp(self):
        super(AmCredentialsManagerTestcase, self).setUp()
        self.manager = AmCredentialsManager(b64_secret=TEST_SECRET)
        self.manager._make_random_text = mock.Mock(side_effect=lambda length: 'c' * length)
        self.cases = (
            ('a' * 32, 'DhuK/DPxVGL8YBY/HgyQ6YPU9ZTErWP+iOGo7hrFj+VgYyew1SoGzd6z/tM+18MW'),
        )

    def test_encrypt_ok(self):
        for from_, to_ in self.cases:
            eq_(
                self.manager.encrypt(from_),
                to_,
            )

    def test_decrypt_ok(self):
        for from_, to_ in self.cases:
            decrypted, padding = self.manager.decrypt(to_)
            eq_(
                decrypted,
                from_,
            )
            eq_(
                padding,
                'c' * (15 - len(from_) % 16),
            )

    def test_decrypt_error(self):
        for bad_value in (
            'foo',
            base64.b64encode(b'foo').decode(),
        ):
            with assert_raises(DecryptFailedError):
                self.manager.decrypt(bad_value)
