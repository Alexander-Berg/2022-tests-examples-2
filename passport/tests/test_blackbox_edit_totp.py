# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings_hosts,
)

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestEditTotpParse(BaseBlackboxRequestTestCase):

    def test_ok(self):
        self.set_blackbox_response_value('{ "status": true, "secret": "SECRET" }')

        response = self.blackbox.edit_totp(
            operation='create',
            uid=123,
            pin=4567,
            secret_id=1,
            secret='SECRET',
            otp='otp123',
        )
        eq_(
            response,
            dict(
                status=True,
                secret='SECRET',
            ),
        )

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value(
            '''{"exception":{"value":"ACCESS_DENIED","id":21},
            "error":"BlackBox error: Access denied: EditSession"}''',
        )
        self.blackbox.edit_totp(
            operation='create',
            uid=123,
            pin=4567,
            secret_id=1,
            secret='SECRET',
            otp='otp123',
        )


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestEditTotpRequest(BaseBlackboxTestCase):

    def test_create(self):
        request_info = Blackbox().build_edit_totp_request(
            operation='create',
            uid=123,
            pin=4567,
            secret_id=1,
            secret='SECRET',
            otp='otp123',
        )
        eq_(request_info.url, 'http://localhost/blackbox/')
        eq_(
            request_info.post_args,
            {
                'format': 'json',
                'method': 'edit_totp',
                'op': 'create',
                'uid': 123,
                'pin': 4567,
                'secret_id': 1,
                'secret': 'SECRET',
                'password': 'otp123',
            },
        )

    def test_replace(self):
        request_info = Blackbox().build_edit_totp_request(
            operation='replace',
            uid=123,
            old_secret_id=0,
            new_secret_id=1,
            secret='SECRET',
            otp='otp123',
        )
        eq_(request_info.url, 'http://localhost/blackbox/')
        eq_(
            request_info.post_args,
            {
                'format': 'json',
                'method': 'edit_totp',
                'op': 'replace',
                'uid': 123,
                'old_secret_id': 0,
                'secret_id': 1,
                'secret': 'SECRET',
                'password': 'otp123',
            },
        )

    @raises(ValueError)
    def test_unknown_operation(self):
        Blackbox().build_edit_totp_request(
            operation='guess',
            uid=123,
            pin=4567,
            secret_id=1,
            secret='SECRET',
            otp='otp123',
        )
