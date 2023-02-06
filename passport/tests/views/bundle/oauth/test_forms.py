# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.oauth import forms
from passport.backend.core.test.test_utils.utils import with_settings


DEFAULT_DEVICE_FORM = {
    'am_version': None,
    'am_version_name': None,
    'app_id': None,
    'app_platform': None,
    'app_version': None,
    'app_version_name': None,
    'device_id': None,
    'device_name': None,
    'deviceid': None,
    'ifv': None,
    'manufacturer': None,
    'model': None,
    'os_version': None,
    'uuid': None,
}


@with_settings(
    PORTAL_LANGUAGES=('ru', 'en'),
)
class TestForms(unittest.TestCase):
    def test_client_edited_form(self):
        invalid_params = [
            (
                {},
                ['client_id.empty', 'client_title.empty'],
            ),
            (
                {
                    'client_id': ' ',
                    'client_title': '  ',
                },
                ['client_id.empty', 'client_title.empty'],
            ),
        ]
        valid_params = [
            (
                {
                    'client_id': 'deadbeef',
                    'client_title': ' My Mail ',
                },
                {
                    'uid': None,
                    'client_id': 'deadbeef',
                    'client_title': 'My Mail',
                    'redirect_uris_changed': False,
                    'scopes_changed': False,
                },
            ),
            (
                {
                    'uid': '123',
                    'client_id': 'deadbeef',
                    'client_title': ' My Mail ',
                    'redirect_uris_changed': 'yes',
                    'scopes_changed': '1',
                },
                {
                    'uid': 123,
                    'client_id': 'deadbeef',
                    'client_title': 'My Mail',
                    'redirect_uris_changed': True,
                    'scopes_changed': True,
                },
            ),
        ]

        check_form(forms.ClientEditedForm(), invalid_params, valid_params, None)

    def test_submit_or_commit_form(self):
        invalid_params = [
            (
                {},
                ['language.empty', 'code.empty'],
            ),
            (
                {
                    'language': '  ',
                    'code': '   ',
                    'uid': '   ',
                },
                ['language.empty', 'code.empty', 'uid.empty'],
            ),
            (
                {
                    'language': 'ru',
                    'code': '42',
                    'uid': '-1',
                },
                ['uid.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'language': 'ru',
                    'code': '42',
                },
                dict(
                    DEFAULT_DEVICE_FORM,
                    language='ru',
                    code='42',
                    uid=None,
                ),
            ),
            (
                {
                    'language': 'ru',
                    'code': '42',
                    'uid': '1',
                    'device_id': 'device_id',
                },
                dict(
                    DEFAULT_DEVICE_FORM,
                    language='ru',
                    code='42',
                    uid=1,
                    device_id='device_id',
                ),
            )
        ]

        check_form(forms.DeviceAuthorizeSubmitOrCommitForm(), invalid_params, valid_params, None)
