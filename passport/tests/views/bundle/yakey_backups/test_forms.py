# -*- coding: utf-8 -*-
from hamcrest import assert_that
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BACKUP,
    TEST_COUNTRY_CODE,
    TEST_PHONE_NUMBER,
)
from passport.backend.api.views.bundle.yakey_backups import forms
from passport.backend.core.test.form.common_matchers import raises_invalid
from passport.backend.core.test.form.deep_eq_matcher import deep_eq
from passport.backend.core.test.form.submitted_form_matcher import submitted_with
from passport.backend.core.test.test_utils import with_settings
import pytest


DEFAULT_FORM = {
    # для AM
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
    # специфичное для ручки
    'country': None,

}


@pytest.mark.parametrize(
    'invalid_params',
    [
        {},
        {'backup': ''},
        {'backup': None},
        {'backup': TEST_BACKUP, 'force_update': 'invalid'},
        {'backup': TEST_BACKUP, 'number': ''},
        {'backup': TEST_BACKUP, 'number': None},
        {'backup': TEST_BACKUP, 'number': '123'},
        {'backup': TEST_BACKUP, 'number': TEST_PHONE_NUMBER.original, 'country': 'wonderland'},
        {'backup': u'фыр-фыр-фыр', 'force_update': 'no', 'number': TEST_PHONE_NUMBER.original},
        {'backup': 'a' * (200 * 1024 + 1), 'number': TEST_PHONE_NUMBER.original},
        {'backup': 123, 'number': TEST_PHONE_NUMBER.original},
        {'backup': '123', 'number': TEST_PHONE_NUMBER.original, 'force_update': ''},
        {'backup': '123', 'number': TEST_PHONE_NUMBER.original, 'force_update': 'tf'},
    ],
)
@with_settings()
def test_invalid_form(invalid_params):
    assert_that(forms.UploadCommitForm(), submitted_with(invalid_params, raises_invalid()))


@pytest.mark.parametrize(
    ('valid_params', 'expected'),
    [
        (
            {
                'backup': TEST_BACKUP,
                'number': TEST_PHONE_NUMBER.original,
            },
            dict(
                DEFAULT_FORM,
                backup=TEST_BACKUP,
                force_update=False,
                number=TEST_PHONE_NUMBER,
            ),
        ),
        (
            {
                'backup': TEST_BACKUP,
                'force_update': '0',
                'number': TEST_PHONE_NUMBER.e164,
                'country': TEST_COUNTRY_CODE,
            },
            dict(
                DEFAULT_FORM,
                backup=TEST_BACKUP,
                force_update=False,
                number=TEST_PHONE_NUMBER,
                country=TEST_COUNTRY_CODE,
            ),
        ),
        (
            {
                'backup': TEST_BACKUP,
                'force_update': '1',
                'number': TEST_PHONE_NUMBER.digital,
                'country': TEST_COUNTRY_CODE,
            },
            dict(
                DEFAULT_FORM,
                backup=TEST_BACKUP,
                force_update=True,
                number=TEST_PHONE_NUMBER,
                country=TEST_COUNTRY_CODE,
            ),
        ),
        (
            {
                'backup': '123',
                'force_update': 'true',
                'number': TEST_PHONE_NUMBER.digital,
            },
            dict(
                DEFAULT_FORM,
                backup='123',
                force_update=True,
                number=TEST_PHONE_NUMBER,
            ),
        ),
        (
            {
                'backup': '123 321',
                'force_update': 'on',
                'number': TEST_PHONE_NUMBER.digital,
            },
            dict(
                DEFAULT_FORM,
                backup='123 321',
                force_update=True,
                number=TEST_PHONE_NUMBER,
            ),
        ),
    ],
)
@with_settings()
def test_valid_form(valid_params, expected):
    assert_that(forms.UploadCommitForm(), submitted_with(valid_params, deep_eq(expected)))
