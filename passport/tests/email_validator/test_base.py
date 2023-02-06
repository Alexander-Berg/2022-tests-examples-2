# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.email_validator.base import (
    determine_validator_error_response,
    dispatch_operations,
    EMPTY_RESPONSE,
)
from passport.backend.api.email_validator.exceptions import (
    EmailAlreadyConfirmedError,
    EmailIncorrectKeyError,
    EmailIsNativeError,
)
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.api.views.bundle.exceptions import (
    SessionidInvalidError,
    ValidationFailedError,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base_test_data import (
    TEST_ADDRESS,
    TEST_CODE,
    TEST_NATIVE_ADDRESS,
    TEST_SESSIONID,
    TEST_UID,
)


BASIC_INVALID_ARGUMENT_RESPONSE = '''<?xml version="1.0" encoding="windows-1251"?>
<page>
  <validator-invalid-argument/>
</page>
'''

EMAIL_IS_NATIVE_ERROR_RESPONSE = '''<?xml version="1.0" encoding="windows-1251"?>
<page>
  <validator-invalid-argument>Address %s valid as native.</validator-invalid-argument>
</page>
''' % TEST_NATIVE_ADDRESS

INVALID_KEY_ERROR_RESPONSE = '''<?xml version="1.0" encoding="windows-1251"?>
<page>
  <validator-key-error uid="%s">%s</validator-key-error>
</page>
''' % (TEST_UID, TEST_CODE)

ALREADY_VALIDATED_RESPONSE = '''<?xml version="1.0" encoding="windows-1251"?>
<page>
  <validator-key-already-validated uid="%s" address="%s">%s</validator-key-already-validated>
</page>
''' % (TEST_UID, TEST_ADDRESS, TEST_CODE)

SESSIONID_INVALID_RESPONSE = '''<?xml version="1.0" encoding="windows-1251"?>
<page>
  <validator-invalid-argument sessionid="%s" address="%s"/>
</page>
''' % (TEST_SESSIONID, TEST_ADDRESS)


@with_settings_hosts()
class TestDispatchView(BaseMdapiTestCase):

    def test_no_operation_empty_response(self):
        dispatcher = dispatch_operations({})

        with self.env.client.application.test_request_context():
            resp = dispatcher()
            eq_(resp, EMPTY_RESPONSE)


@with_settings_hosts()
class TestBaseValidatorView(BaseMdapiTestCase):

    def test_empty_form_fields_lead_to_empty_response(self):
        exception = ValidationFailedError([
            'field.empty',
        ])

        resp = determine_validator_error_response(exception, {})
        eq_(resp, EMPTY_RESPONSE)

    def test_specific_errors(self):
        values = {
            'email': TEST_ADDRESS,
            'uid': str(TEST_UID),
            'sessionid': TEST_SESSIONID,
        }

        for exception, expected_reply in (
            (
                EmailIsNativeError(TEST_NATIVE_ADDRESS),
                EMAIL_IS_NATIVE_ERROR_RESPONSE,
            ),
            (
                SessionidInvalidError(),
                SESSIONID_INVALID_RESPONSE,
            ),
            (
                EmailIncorrectKeyError(TEST_UID, TEST_CODE),
                INVALID_KEY_ERROR_RESPONSE,
            ),
            (
                EmailAlreadyConfirmedError(TEST_ADDRESS, TEST_UID, TEST_CODE),
                ALREADY_VALIDATED_RESPONSE,
            ),
        ):
            resp = determine_validator_error_response(exception, values)
            actual_reply = resp.data.decode('utf8')
            eq_(
                actual_reply,
                expected_reply,
                'Unexpected reply for "%s":\n%s\n!=\n\n%s' % (
                    exception.__class__.__name__,
                    actual_reply,
                    expected_reply,
                ),
            )
