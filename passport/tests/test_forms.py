# -*- coding: utf-8 -*-
import unittest

from passport.backend.api import forms
from passport.backend.api.common.errors import format_errors
from passport.backend.api.test.utils import assert_errors
from passport.backend.core import validators
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.conf import settings
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.form_utils import check_equality
from passport.backend.core.test.test_utils.mock_objects import (
    mock_env,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types import birthday
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.phone_number import phone_number
from passport.backend.utils.common import merge_dicts
import pytz


def missing(keys):
    return {k: None for k in keys}


def build_params_builder(default_valid_params):
    def params_builder(params, expected):
        return (merge_dicts(default_valid_params, params), expected)
    return params_builder


@with_settings(
    PORTAL_LANGUAGES=['ru'],
    BLACKBOX_URL='localhost',
    BASIC_PASSWORD_POLICY_MIN_QUALITY=10,
)
class TestForms(unittest.TestCase):
    def setUp(self):
        self.track_id = "0a" * settings.TRACK_RANDOM_BYTES_COUNT + "00"

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.blackbox = FakeBlackbox()
        self.blackbox.start()

        self.grants = FakeGrants()
        self.grants.start()
        self.grants.set_grants_return_value(mock_grants())

    def tearDown(self):
        self.grants.stop()
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        del self.blackbox
        del self.grants

    def check_form(self, form, invalid_params, valid_params, state=None):
        for invalid_params, expected_errors in invalid_params:
            self.check_form_errors(form, invalid_params, expected_errors, state)
        for p in valid_params:
            check_equality(form, p, state)

    def check_form_errors(self, form, params, expected_errors, state=None):
        try:
            form.to_python(params, state)
            self.fail("Form (%s) validation expected to fail with params: %s" % (form.__class__.__name__, repr(params)))
        except validators.Invalid as e:
            assert_errors(format_errors(e), expected_errors)

    def test_consumer_form(self):
        invalid_params = [
            ({}, {'consumer': 'missingvalue'}),
            ({'consumer': 'DOES_NOT_EXIST'}, {'consumer': 'notin'}),
            ({'consumer': ''}, {'consumer': 'empty'}),
        ]

        valid_params = [
            ({'consumer': 'dev'}, {'consumer': 'dev'}),
        ]

        self.check_form(forms.ConsumerForm(), invalid_params, valid_params, None)

    def test_uid_form(self):
        invalid_params = [
            ({'consumer': 'dev'}, {'uid': 'missingvalue'}),
            ({'uid': 'a'}, [{'uid': 'integer'}, {'consumer': 'missingvalue'}]),
            ({'uid': 'a', 'consumer': 'dev'}, {'uid': 'integer'}),  # TODO поправить код integer в валидаторе
            ({'uid': '', 'consumer': 'dev'}, {'uid': 'empty'}),
            ({'uid': -1, 'consumer': 'dev'}, {'uid': 'toolow'}),
        ]

        valid_params = [
            ({'uid': '1', 'consumer': 'dev'}, {'uid': 1, 'consumer': 'dev'}),
        ]

        self.check_form(forms.UidForm(), invalid_params, valid_params, None)

    def test_tracked_consumer_form(self):
        invalid_params = [
            ({'track_id': 'a', 'consumer': 'dev'}, {'track_id': 'invalidid'}),
            ({'track_id': '', 'consumer': 'dev'}, {'track_id': 'empty'}),
        ]

        valid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev'},
             {'track_id': self.track_id, 'consumer': 'dev'}),
        ]

        self.check_form(forms.TrackedConsumerForm(), invalid_params, valid_params, None)

    def test_required_uid_tracked_consumer_form(self):
        invalid_params = [
            ({},
             [{'track_id': 'missingvalue'}, {'consumer': 'missingvalue'}, {'uid': 'missingvalue'}]),
            ({'track_id': '', 'consumer': '', 'uid': ''},
             [{'track_id': 'empty'}, {'consumer': 'empty'}, {'uid': 'empty'}]),
            ({'track_id': '1', 'consumer': 'bla', 'uid': 'sss'},
             [{'track_id': 'invalidid'}, {'consumer': 'notin'}, {'uid': 'integer'}]),
        ]

        valid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev', 'uid': '777'},
             {'track_id': self.track_id, 'consumer': 'dev', 'uid': 777}),
        ]

        self.check_form(forms.RequiredUidTrackedConsumerForm(), invalid_params, valid_params, None)

    def test_subscription(self):
        invalid_params = [
            ({'uid': '1', 'consumer': 'dev'}, {'service': 'missingvalue'}),
            ({'uid': '1'}, [{'consumer': 'missingvalue'}, {'service': 'missingvalue'}]),
            ({'uid': '', 'consumer': 'dev', 'service': 'dev'}, {'uid': 'empty'}),
            ({'uid': '1', 'login_rule': 1}, [{'consumer': 'missingvalue'}, {'service': 'missingvalue'}]),
            ({'uid': '1', 'consumer': 'dev', 'login_rule': 'a'},
             [{'login_rule': 'integer'}, {'service': 'missingvalue'}]),
            ({'uid': 'a', 'consumer': 'dev'},
             [{'uid': 'integer'}, {'service': 'missingvalue'}]),
            ({'uid': '1', 'consumer': 'dev', 'login_rule': 'a'},
             [{'login_rule': 'integer'}, {'service': 'missingvalue'}]),
            ({'uid': '1', 'consumer': 'dev', 'service': 'mail', 'wmode': '2'}, {'wmode': 'notempty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': 'mail', 'yastaff_login': 'aaa'}, {'yastaff_login': 'notempty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': '669'}, {'yastaff_login': 'empty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': '42'}, {'wmode': 'empty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': '669', 'yastaff_login': ''}, {'yastaff_login': 'empty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': '42', 'wmode': ''}, {'wmode': 'empty'}),
            ({'uid': '1', 'consumer': 'dev', 'service': '669', 'yastaff_login': '   '}, {'yastaff_login': 'empty'}),
        ]

        valid_params = [
            ({'uid': '1', 'consumer': 'dev', 'service': 'dev'},
             {'uid': 1, 'consumer': 'dev', 'login_rule': None, 'wmode': None,
              'yastaff_login': None, 'service': Service(slug='dev', sid='')}),
            ({'uid': '1', 'consumer': 'dev', 'service': '2'},
             {'uid': 1, 'consumer': 'dev', 'login_rule': None, 'wmode': None,
              'yastaff_login': None, 'service': Service(slug='mail', sid=2)}),
            ({'uid': '1', 'consumer': 'dev', 'service': 'mail'},
             {'uid': 1, 'wmode': None, 'login_rule': None,
              'yastaff_login': None, 'consumer': 'dev',
              'service': Service(slug='mail', sid=2)}),
            ({'uid': '1', 'service': 'wwwdgt', 'wmode': '2', 'login_rule': '1', 'consumer': 'dev'},
             {'uid': 1, 'wmode': 2, 'login_rule': 1, 'yastaff_login': None, 'consumer': 'dev',
              'service': Service(slug='wwwdgt', sid=42)}),
            ({'uid': '1', 'service': 'yastaff', 'yastaff_login': 'foo', 'consumer': 'dev'},
             {'uid': 1, 'yastaff_login': 'foo',
              'login_rule': None, 'wmode': None, 'consumer': 'dev',
              'service': Service(slug='yastaff', sid=669)}),
        ]

        self.check_form(forms.Subscription(), invalid_params, valid_params, None)

    def test_karma(self):
        invalid_params = [
            ({'uid': '1', 'consumer': 'dev'}, {'form': 'toofew'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '10'}, {'prefix': 'toohigh'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '-1'}, {'prefix': 'toolow'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': 'aaa'}, {'prefix': 'integer'}),
            ({'uid': 1, 'consumer': 'dev', 'suffix': 'aaa'}, {'suffix': 'integer'}),
            ({'uid': 1, 'consumer': 'dev', 'suffix': '-10'}, {'suffix': 'notin'}),
            ({'uid': 1, 'consumer': 'dev', 'suffix': '1000'}, {'suffix': 'notin'}),
            ({'uid': 1, 'consumer': 'dev', 'suffix': ''}, {'suffix': 'empty'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': ''}, {'prefix': 'empty'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '', 'suffix': ''},
             [{'suffix': 'empty'}, {'prefix': 'empty'}]),
            ({'uid': 1, 'consumer': 'dev', 'suffix': '100', 'admin_name': 'test-admin'},
             [{'form': 'invalidset'}]),
            ({'uid': 1, 'consumer': 'dev', 'suffix': '100', 'comment': 'test-comment'},
             [{'form': 'invalidset'}]),
        ]

        valid_params = [
            ({'uid': 1, 'consumer': 'dev', 'prefix': '1'},
             {'uid': 1, 'consumer': 'dev', 'prefix': 1, 'suffix': None, 'admin_name': None, 'comment': None}),
            ({'uid': 1, 'consumer': 'dev', 'suffix': '100', 'admin_name': 'test', 'comment': 'test-comment'},
             {'uid': 1, 'consumer': 'dev', 'prefix': None, 'suffix': 100, 'admin_name': 'test', 'comment': 'test-comment'}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '0', 'suffix': '75'},
             {'uid': 1, 'consumer': 'dev', 'prefix': 0, 'suffix': 75, 'admin_name': None, 'comment': None}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '0', 'suffix': '80'},
             {'uid': 1, 'consumer': 'dev', 'prefix': 0, 'suffix': 80, 'admin_name': None, 'comment': None}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '0', 'suffix': '85'},
             {'uid': 1, 'consumer': 'dev', 'prefix': 0, 'suffix': 85, 'admin_name': None, 'comment': None}),
            ({'uid': 1, 'consumer': 'dev', 'prefix': '0', 'suffix': '0'},
             {'uid': 1, 'consumer': 'dev', 'prefix': 0, 'suffix': 0, 'admin_name': None, 'comment': None}),
        ]
        self.check_form(forms.Karma(), invalid_params, valid_params, None)

    def test_account(self):
        invalid_params = [
            ({'uid': 1, 'consumer': 'dev'}, {'form': 'toofew'}),
            ({'uid': 'aaa', 'consumer': 'dev', 'is_enabled': 'fake'},
             [{'is_enabled': 'string'}, {'uid': 'integer'}]),
            ({'uid': '1', 'consumer': 'dev', 'is_enabled': ''},
             {'is_enabled': 'empty'}),
            ({'uid': '1', 'consumer': 'dev', 'is_enabled': '1', 'admin_name': 'neo'},
             {'form': 'invalidset'}),
            ({'uid': '1', 'consumer': 'dev', 'is_enabled': '1', 'comment': '#comment'},
             {'form': 'invalidset'}),
            ({'uid': '1', 'consumer': 'dev', 'is_enabled_app_password': 'bla'},
             {'is_enabled_app_password': 'string'}),
        ]
        valid_params = [
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': '1',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': True,
                    'is_enabled_app_password': None,
                    'admin_name': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': '0',
                    'admin_name': 'test',
                    'comment': 'twit',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': False,
                    'is_enabled_app_password': None,
                    'admin_name': 'test',
                    'comment': 'twit',
                },
            ),
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': 'False',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': False,
                    'is_enabled_app_password': None,
                    'admin_name': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': 'True',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': True,
                    'is_enabled_app_password': None,
                    'admin_name': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled_app_password': 'True',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': None,
                    'is_enabled_app_password': True,
                    'admin_name': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': 'False',
                    'is_enabled_app_password': '0',
                },
                {
                    'uid': 1,
                    'consumer': 'dev',
                    'is_enabled': False,
                    'is_enabled_app_password': False,
                    'admin_name': None,
                    'comment': None,
                },
            ),
        ]
        self.check_form(forms.Account(), invalid_params, valid_params, None)

    def test_person(self):
        invalid_params = [
            ({'uid': 1, 'consumer': 'dev'}, {'form': 'toofew'}),
            ({'uid': 1, 'consumer': 'dev', 'gender': 'lala'},
             {'gender': 'badgender'}),
            ({'uid': 1, 'consumer': 'dev', 'country': 'lala'},
             {'country': 'badcountrycode'}),
            ({'uid': 1, 'consumer': 'dev', 'language': 'lala'},
             {'language': 'unsupported'}),
            ({'uid': 1, 'consumer': 'dev', 'timezone': 'lala'},
             {'timezone': 'badtimezone'}),
            ({'uid': 1, 'consumer': 'dev', 'birthday': '0001-03-04'},
             {'birthday': 'badbirthday'}),
            ({'uid': 1, 'consumer': 'dev', 'contact_phone_number': 'abc'},
             {'contact_phone_number': 'badphonenumber'}),
            # Убеждаемся, что валидатор для contact_phone_number не учитывает страну
            ({'uid': 1, 'consumer': 'dev', 'country': 'ru',
              'contact_phone_number': '89261234567'}, {'contact_phone_number': 'badphonenumber'}),
        ]
        valid_params = [
            ({'uid': 1, 'consumer': 'dev', 'firstname': 'fname'},
             {'city': None, 'display_name': None, 'uid': 1, 'firstname': 'fname', 'lastname': None,
              'language': None, 'birthday': None, 'gender': None, 'timezone': None, 'country': None,
              'contact_phone_number': None,
              'force_clean_web': False,
              'consumer': 'dev'}),
            ({'uid': 1, 'consumer': 'dev', 'lastname': 'lname'},
             {'city': None, 'display_name': None, 'uid': 1, 'firstname': None, 'lastname': 'lname',
              'language': None, 'birthday': None, 'gender': None, 'timezone': None, 'country': None,
              'contact_phone_number': None,
              'force_clean_web': False,
              'consumer': 'dev'}),
            ({'uid': 1, 'consumer': 'dev', 'display_name': 'name', 'profile_id': 1, 'provider': 'fb',
              'contact_phone_number': '+79261234567'},
             {'city': None, 'display_name': 's:1:fb:name', 'uid': 1, 'firstname': None, 'lastname': None,
              'language': None, 'birthday': None, 'gender': None, 'timezone': None, 'country': None,
              'contact_phone_number': phone_number.PhoneNumber.parse('+79261234567'),
              'force_clean_web': False,
              'consumer': 'dev'}),
            ({'uid': 1, 'consumer': 'dev', 'firstname': None, 'lastname': 'aaa   aaa'},
             {'city': None, 'display_name': None, 'uid': 1, 'firstname': None,
              'lastname': 'aaa aaa', 'language': None, 'birthday': None, 'gender': None,
              'force_clean_web': False,
              'timezone': None, 'country': None, 'consumer': 'dev', 'contact_phone_number': None}),
        ]
        self.check_form(forms.Person(), invalid_params, valid_params, None)

    def test_create_track_start(self):
        invalid_params = [
            ({}, [{'consumer': 'missingvalue'}]),
            ({'consumer': 'dev', 'track_type': 'unknown'}, {'track_type': 'notin'}),
            ({'consumer': 'dev', 'track_type': 'register', 'process_name': 'foo'}, {'process_name': 'notin'}),
        ]

        valid_params = [
            ({'consumer': 'dev'}, {'consumer': 'dev', 'track_type': 'register', 'process_name': None}),
            ({'consumer': 'dev', 'track_type': 'register'},
             {'consumer': 'dev', 'track_type': 'register', 'process_name': None}),
            ({'consumer': 'dev', 'track_type': 'complete', 'extra_field': 'lala'},
             {'consumer': 'dev', 'track_type': 'complete', 'extra_field': 'lala', 'process_name': None}),
            ({'consumer': 'dev', 'track_type': 'register', 'process_name': 'restore'},
             {'consumer': 'dev', 'track_type': 'register', 'process_name': 'restore'}),
        ]
        self.check_form(forms.CreateTrackStartForm(), invalid_params, valid_params, None)

    def test_create_register_track(self):
        """
        Данный тест проверяет что трек, например, типа 'register' создаётся
        способом, отличным от трека типа 'complete'
        """
        invalid_params = [
            ({}, [{'consumer': 'missingvalue'}]),
            ({'consumer': 'dev', 'language': 'unsupported', 'display_language': 'unsupported',
              'country': 'unsupported'},
             [{'country': 'badcountrycode'}, {'display_language': 'unsupported'}, {'language': 'unsupported'}]),
            ({'consumer': 'dev', 'retpath': 'lala'}, {'retpath': 'nohost'}),
        ]

        default_form_params = {
            'am_version': None,
            'am_version_name': None,
            'app_id': None,
            'app_platform': None,
            'app_version': None,
            'app_version_name': None,
            'check_css_load': None,
            'check_js_load': None,
            'consumer': 'dev',
            'country': None,
            'device_app_uuid': None,
            'device_application': None,
            'device_cell_provider': None,
            'device_clid': None,
            'device_geo_coarse': None,
            'device_hardware_id': None,
            'device_hardware_model': None,
            'device_id': None,
            'device_language_sys': None,
            'device_locale': None,
            'device_name': None,
            'device_os_id': None,
            'deviceid': None,
            'display_language': None,
            'frontend_state': None,
            'ifv': None,
            'language': None,
            'manufacturer': None,
            'model': None,
            'origin': None,
            'os_version': None,
            'retpath': None,
            'scenario': None,
            'service': None,
            'uuid': None,
            'js_fingerprint': None,
        }

        valid_params = [
            # Проверяем форму, инициализированную с минимумом параметров
            (
                {'consumer': 'dev'},
                dict(default_form_params),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_language_sys': 'ru'},
                dict(default_form_params, device_language_sys='ru'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_locale': 'locale'},
                dict(default_form_params, device_locale='locale'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_geo_coarse': 'gc'},
                dict(default_form_params, device_geo_coarse='gc'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_app_uuid': 'uuid'},
                dict(default_form_params, device_app_uuid='uuid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_application': 'app'},
                dict(default_form_params, device_application='app'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_clid': 'clid'},
                dict(default_form_params, device_clid='clid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_id': 'id'},
                dict(default_form_params, device_hardware_id='id'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_model': 'model'},
                dict(default_form_params, device_hardware_model='model'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_os_id': 'os'},
                dict(default_form_params, device_os_id='os'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_cell_provider': 'cell'},
                dict(default_form_params, device_cell_provider='cell'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'scenario': 'scenario1'},
                dict(default_form_params, scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_css_load': 'True'},
                dict(default_form_params, check_css_load=1),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_js_load': 'True'},
                dict(default_form_params, check_js_load=1),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'display_language': 'ru',
                 'country': 'ru', 'retpath': 'http://ya.ru/path', 'origin': 'origin',
                 'service': 'service', 'device_language_sys': 'ls', 'device_locale': 'loc',
                 'device_geo_coarse': 'geo', 'device_hardware_id': 'hid', 'device_os_id': 'os',
                 'device_application': 'app', 'device_cell_provider': 'cell',
                 'device_hardware_model': 'hm', 'device_clid': 'clid', 'device_app_uuid': 'uuid',
                 'scenario': 'scenario1'},
                dict(default_form_params, language='ru', display_language='ru',
                     country='ru', retpath='http://ya.ru/path', origin='origin',
                     service='service', device_language_sys='ls', device_locale='loc',
                     device_geo_coarse='geo', device_hardware_id='hid', device_os_id='os',
                     device_application='app', device_cell_provider='cell', device_app_uuid='uuid',
                     device_hardware_model='hm', device_clid='clid', scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'origin': 'or   ', 'service': '   '},
                dict(default_form_params, consumer='dev', language='ru', origin='or', service=''),
            ),
            # Проверяем что форма инициируется только с известными ей полями
            (
                {'consumer': 'dev', 'blabla': '1234'},
                dict(default_form_params),
            ),
        ]
        self.check_form(forms.CreateRegisterTrackForm(), invalid_params, valid_params, None)

    def test_create_complete_track(self):
        invalid_params = [
            ({}, [{'consumer': 'missingvalue'}, {'token': 'missingvalue'}]),
            ({'consumer': 'dev'}, {'token': 'missingvalue'}),
            ({'consumer': 'dev', 'token': 'aaabbb', 'language': 'unsupported', 'display_language': 'unsupported',
              'country': 'unsupported'},
             [{'country': 'badcountrycode'}, {'display_language': 'unsupported'}, {'language': 'unsupported'}]),
            ({'consumer': 'dev', 'token': 'aaabbb', 'retpath': 'lala'}, {'retpath': 'nohost'}),
        ]

        default_form_params = {
            'am_version': None,
            'am_version_name': None,
            'app_id': None,
            'app_platform': None,
            'app_version': None,
            'app_version_name': None,
            'check_css_load': None,
            'check_js_load': None,
            'consumer': 'dev',
            'country': None,
            'device_app_uuid': None,
            'device_application': None,
            'device_cell_provider': None,
            'device_clid': None,
            'device_geo_coarse': None,
            'device_hardware_id': None,
            'device_hardware_model': None,
            'device_id': None,
            'device_language_sys': None,
            'device_locale': None,
            'device_name': None,
            'device_os_id': None,
            'deviceid': None,
            'display_language': None,
            'frontend_state': None,
            'ifv': None,
            'language': None,
            'manufacturer': None,
            'model': None,
            'origin': None,
            'os_version': None,
            'retpath': None,
            'scenario': None,
            'service': None,
            'uuid': None,
            'js_fingerprint': None,
        }

        valid_params = [
            # Проверяем что `token` сохраняется в форму
            ({'consumer': 'dev', 'token': 'aaabbb'},
             dict(default_form_params, token='aaabbb')),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_language_sys': 'ru'},
                dict(default_form_params, token='aaabbb', device_language_sys='ru'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_locale': 'locale'},
                dict(default_form_params, token='aaabbb', device_locale='locale'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_geo_coarse': 'gc'},
                dict(default_form_params, token='aaabbb', device_geo_coarse='gc'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_app_uuid': 'uuid'},
                dict(default_form_params, token='aaabbb', device_app_uuid='uuid'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_application': 'app'},
                dict(default_form_params, token='aaabbb', device_application='app'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_clid': 'clid'},
                dict(default_form_params, token='aaabbb', device_clid='clid'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_hardware_id': 'id'},
                dict(default_form_params, token='aaabbb', device_hardware_id='id'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_hardware_model': 'model'},
                dict(default_form_params, token='aaabbb', device_hardware_model='model'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_os_id': 'os'},
                dict(default_form_params, token='aaabbb', device_os_id='os'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'device_cell_provider': 'cell'},
                dict(default_form_params, token='aaabbb', device_cell_provider='cell'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'scenario': 'scenario1'},
                dict(default_form_params, token='aaabbb', scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'check_css_load': 'True'},
                dict(default_form_params, token='aaabbb', check_css_load=1),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'check_js_load': 'True'},
                dict(default_form_params, token='aaabbb', check_js_load=1),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'language': 'ru',
                 'display_language': 'ru', 'country': 'ru', 'retpath': 'http://ya.ru/path',
                 'origin': 'origin', 'service': 'service', 'device_language_sys': 'ls',
                 'device_locale': 'loc', 'device_geo_coarse': 'geo', 'device_hardware_id': 'hid',
                 'device_os_id': 'os', 'device_application': 'app', 'device_cell_provider': 'cell',
                 'device_hardware_model': 'hm', 'device_clid': 'clid', 'device_app_uuid': 'uuid',
                 'scenario': 'scenario1'},
                dict(default_form_params, token='aaabbb', language='ru', display_language='ru',
                     country='ru', retpath='http://ya.ru/path', origin='origin',
                     service='service', device_language_sys='ls', device_locale='loc',
                     device_geo_coarse='geo', device_hardware_id='hid', device_os_id='os',
                     device_application='app', device_cell_provider='cell', device_app_uuid='uuid',
                     device_hardware_model='hm', device_clid='clid', scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'token': 'aaabbb', 'consumer': 'dev', 'language': 'ru', 'origin': 'or   ', 'service': '   '},
                dict(default_form_params, token='aaabbb', consumer='dev', language='ru', origin='or', service=''),
            ),
            # Проверяем что форма инициируется только с известными ей полями
            (
                {'consumer': 'dev', 'token': 'aaabbb', 'blabla': '1234'},
                dict(default_form_params, token='aaabbb'),
            ),
        ]
        self.check_form(forms.CreateCompleteTrackForm(), invalid_params, valid_params, None)

    def test_create_other_track(self):
        invalid_params = [
            ({}, [{'consumer': 'missingvalue'}]),
            ({'consumer': 'dev', 'language': 'unsupported', 'display_language': 'unsupported',
              'country': 'unsupported'},
             [{'country': 'badcountrycode'}, {'display_language': 'unsupported'}, {'language': 'unsupported'}]),
            ({'consumer': 'dev', 'retpath': 'lala'}, {'retpath': 'nohost'}),
        ]

        default_form_params = {
            'am_version': None,
            'am_version_name': None,
            'app_id': None,
            'app_platform': None,
            'app_version': None,
            'app_version_name': None,
            'check_css_load': None,
            'check_js_load': None,
            'consumer': 'dev',
            'country': None,
            'device_app_uuid': None,
            'device_application': None,
            'device_cell_provider': None,
            'device_clid': None,
            'device_geo_coarse': None,
            'device_hardware_id': None,
            'device_hardware_model': None,
            'device_id': None,
            'device_language_sys': None,
            'device_locale': None,
            'device_name': None,
            'device_os_id': None,
            'deviceid': None,
            'display_language': None,
            'frontend_state': None,
            'ifv': None,
            'language': None,
            'manufacturer': None,
            'model': None,
            'origin': None,
            'os_version': None,
            'retpath': None,
            'scenario': None,
            'service': None,
            'uuid': None,
            'js_fingerprint': None,
        }

        valid_params = [
            # Проверяем форму, инициализированную с минимумом параметров
            (
                {'consumer': 'dev'},
                dict(default_form_params),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_language_sys': 'ru'},
                dict(default_form_params, device_language_sys='ru'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_locale': 'locale'},
                dict(default_form_params, device_locale='locale'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_geo_coarse': 'gc'},
                dict(default_form_params, device_geo_coarse='gc'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_app_uuid': 'uuid'},
                dict(default_form_params, device_app_uuid='uuid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_application': 'app'},
                dict(default_form_params, device_application='app'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_clid': 'clid'},
                dict(default_form_params, device_clid='clid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_id': 'id'},
                dict(default_form_params, device_hardware_id='id'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_model': 'model'},
                dict(default_form_params, device_hardware_model='model'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_os_id': 'os'},
                dict(default_form_params, device_os_id='os'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_cell_provider': 'cell'},
                dict(default_form_params, device_cell_provider='cell'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'scenario': 'scenario1'},
                dict(default_form_params, scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_css_load': 'True'},
                dict(default_form_params, check_css_load=1),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_js_load': 'True'},
                dict(default_form_params, check_js_load=1),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'display_language': 'ru',
                 'country': 'ru', 'retpath': 'http://ya.ru/path', 'origin': 'origin',
                 'service': 'service', 'device_language_sys': 'ls', 'device_locale': 'loc',
                 'device_geo_coarse': 'geo', 'device_hardware_id': 'hid', 'device_os_id': 'os',
                 'device_application': 'app', 'device_cell_provider': 'cell',
                 'device_hardware_model': 'hm', 'device_clid': 'clid', 'device_app_uuid': 'uuid',
                 'scenario': 'scenario1'},
                dict(default_form_params, language='ru', display_language='ru',
                     country='ru', retpath='http://ya.ru/path', origin='origin',
                     service='service', device_language_sys='ls', device_locale='loc',
                     device_geo_coarse='geo', device_hardware_id='hid', device_os_id='os',
                     device_application='app', device_cell_provider='cell', device_app_uuid='uuid',
                     device_hardware_model='hm', device_clid='clid', scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'origin': 'or   ', 'service': '   '},
                dict(default_form_params, consumer='dev', language='ru', origin='or', service=''),
            ),
            # Проверяем что форма инициируется только с известными ей полями
            (
                {'consumer': 'dev', 'blabla': '1234'},
                dict(default_form_params),
            ),
        ]
        self.check_form(forms.CreateOtherTrackForm(), invalid_params, valid_params, None)

    def test_save_track(self):
        invalid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev'}, {'form': 'toofew'}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'language': 'lat'}, {'language': 'unsupported'}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'display_language': 'lat'},
             {'display_language': 'unsupported'}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'country': 'lala'}, {'country': 'badcountrycode'}),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'page_loading_info': 'a' * 1025},
                {'page_loading_info': 'toolong'},
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_css_load': 'a'},
                {'check_css_load': 'string'},
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_js_load': 'a'},
                {'check_js_load': 'string'},
            ),
        ]

        default_form_params = {
            'am_version': None,
            'am_version_name': None,
            'app_id': None,
            'app_platform': None,
            'app_version': None,
            'app_version_name': None,
            'check_css_load': None,
            'check_js_load': None,
            'consumer': 'dev',
            'country': None,
            'device_app_uuid': None,
            'device_application': None,
            'device_cell_provider': None,
            'device_clid': None,
            'device_geo_coarse': None,
            'device_hardware_id': None,
            'device_hardware_model': None,
            'device_id': None,
            'device_language_sys': None,
            'device_locale': None,
            'device_name': None,
            'device_os_id': None,
            'deviceid': None,
            'display_language': None,
            'frontend_state': None,
            'ifv': None,
            'language': None,
            'manufacturer': None,
            'model': None,
            'origin': None,
            'os_version': None,
            'page_loading_info': None,
            'retpath': None,
            'scenario': None,
            'service': None,
            'track_id': self.track_id,
            'uuid': None,
            'js_fingerprint': None,
        }
        valid_params = [
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru'},
                dict(default_form_params, language='ru'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_language_sys': 'ru'},
                dict(default_form_params, device_language_sys='ru'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_locale': 'locale'},
                dict(default_form_params, device_locale='locale'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_geo_coarse': 'gc'},
                dict(default_form_params, device_geo_coarse='gc'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_app_uuid': 'uuid'},
                dict(default_form_params, device_app_uuid='uuid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_application': 'app'},
                dict(default_form_params, device_application='app'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_clid': 'clid'},
                dict(default_form_params, device_clid='clid'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_id': 'id'},
                dict(default_form_params, device_hardware_id='id'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_hardware_model': 'model'},
                dict(default_form_params, device_hardware_model='model'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_os_id': 'os'},
                dict(default_form_params, device_os_id='os'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'device_cell_provider': 'cell'},
                dict(default_form_params, device_cell_provider='cell'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'scenario': 'scenario1'},
                dict(default_form_params, scenario='scenario1'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'page_loading_info': '{"trololo": true}'},
                dict(default_form_params, page_loading_info='{"trololo": true}'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'display_language': 'ru',
                 'country': 'ru', 'retpath': 'http://ya.ru/path', 'origin': 'origin',
                 'service': 'service', 'device_language_sys': 'ls', 'device_locale': 'loc',
                 'device_geo_coarse': 'geo', 'device_hardware_id': 'hid', 'device_os_id': 'os',
                 'device_application': 'app', 'device_cell_provider': 'cell',
                 'device_hardware_model': 'hm', 'device_clid': 'clid', 'device_app_uuid': 'uuid',
                 'page_loading_info': '{"blablabla": 1}', 'scenario': 'scenario1',
                 'check_css_load': 'true', 'check_js_load': 'true', 'js_fingerprint': 'foobar'},
                dict(default_form_params, language='ru', display_language='ru',
                     country='ru', retpath='http://ya.ru/path', origin='origin',
                     service='service', device_language_sys='ls', device_locale='loc',
                     device_geo_coarse='geo', device_hardware_id='hid', device_os_id='os',
                     device_application='app', device_cell_provider='cell', device_app_uuid='uuid',
                     device_hardware_model='hm', device_clid='clid',
                     page_loading_info='{"blablabla": 1}', scenario='scenario1',
                     check_css_load=True, check_js_load=True, js_fingerprint='foobar'),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'language': 'ru', 'origin': 'or   ', 'service': '   '},
                dict(default_form_params, consumer='dev', language='ru', origin='or', service=''),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_css_load': 'true'},
                dict(default_form_params, check_css_load=True),
            ),
            (
                {'track_id': self.track_id, 'consumer': 'dev', 'check_js_load': 'true'},
                dict(default_form_params, check_js_load=True),
            ),
        ]
        self.check_form(forms.SaveTrackForm(), invalid_params, valid_params, None)

    def test_simple_login_validation(self):
        invalid_params = [
            ({'consumer': 'dev'}, [{'login': 'missingvalue'}, {'track_id': 'missingvalue'}]),
            ({'login': 'testlogin'}, [{'consumer': 'missingvalue'}, {'track_id': 'missingvalue'}]),
            ({'consumer': 'dev', 'login': '', 'ignore_stoplist': ''},
             [{'login': 'empty'}, {'ignore_stoplist': 'empty'}, {'track_id': 'missingvalue'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'login': 'testlogin', 'ignore_stoplist': '1',
              'track_id': self.track_id},
             {'consumer': 'dev', 'login': 'testlogin', 'track_id': self.track_id,
              'ignore_stoplist': True}),
            ({'consumer': 'dev', 'login': 'testlogin', 'track_id': self.track_id},
             {'consumer': 'dev', 'login': 'testlogin', 'track_id': self.track_id,
              'ignore_stoplist': False}),
        ]
        self.check_form(forms.SimpleLoginValidation(), invalid_params, valid_params, None)

    def test_simple_password_validation(self):
        invalid_params = [
            ({'consumer': 'dev'}, [{'password': 'missingvalue'}]),
            ({'password': 'testpasswd', 'login': 'blabla'}, {'consumer': 'missingvalue'}),
            ({'consumer': 'dev', 'password': '', 'login': '', 'policy': '', 'phone_number': '', 'country': '1'},
             [{'policy': 'empty'}, {'password': 'empty'}, {'phone_number': 'empty'}, {'country': 'badcountrycode'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla'},
             {'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'policy': None, 'track_id': None,
              'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'policy': 'strong'},
             {'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'policy': 'strong', 'track_id': None,
              'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'track_id': self.track_id},
             {'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'track_id': self.track_id,
              'policy': None, 'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'track_id': self.track_id,
              'policy': 'basic'},
             {'consumer': 'dev', 'password': 'testpasswd', 'login': 'blabla', 'track_id': self.track_id,
              'policy': 'basic', 'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'login': '1blabla', 'track_id': self.track_id,
              'policy': 'strong'},
             {'consumer': 'dev', 'password': 'testpasswd', 'login': '1blabla', 'track_id': self.track_id,
              'policy': 'strong', 'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'track_id': self.track_id},
             {'consumer': 'dev', 'password': 'testpasswd', 'track_id': self.track_id, 'login': None, 'policy': None,
              'phone_number': None, 'country': None}),
            ({'consumer': 'dev', 'password': 'testpasswd', 'track_id': self.track_id, 'phone_number': '1234abcd',
              'country': 'ru'},
             {'consumer': 'dev', 'password': 'testpasswd', 'track_id': self.track_id, 'login': None, 'policy': None,
              'phone_number': '1234abcd', 'country': 'ru'}),
        ]
        self.check_form(forms.SimplePasswordValidation(), invalid_params, valid_params, None)

    def test_simple_phone_number_validation(self):
        invalid_params = [
            ({'consumer': 'dev'}, [{'phone_number': 'missingvalue'}, {'track_id': 'missingvalue'}]),
            ({'consumer': 'dev', 'phone_number': ''}, [{'phone_number': 'empty'}, {'track_id': 'missingvalue'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'phone_number': '+74951234567', 'ignore_phone_compare': '1', 'track_id': self.track_id},
             {'consumer': 'dev', 'phone_number': '+74951234567', 'country': None, 'track_id': self.track_id, 'ignore_phone_compare': True}),
            ({'consumer': 'dev', 'phone_number': '+74951234567', 'track_id': self.track_id, 'ignore_phone_compare': '1'},
             {'consumer': 'dev', 'phone_number': '+74951234567', 'track_id': self.track_id, 'country': None, 'ignore_phone_compare': True}),
            ({'consumer': 'dev', 'phone_number': '+74951234567', 'country': 'ru', 'track_id': self.track_id, 'ignore_phone_compare': '1'},
             {'consumer': 'dev', 'phone_number': '+74951234567', 'country': 'ru', 'track_id': self.track_id, 'ignore_phone_compare': True}),
        ]
        self.check_form(forms.SimplePhoneNumberValidation(), invalid_params, valid_params, None)

    def test_simple_hint_question_validation(self):
        invalid_params = [
            ({}, [{'consumer': 'missingvalue'}]),
            ({'consumer': 'dev', 'hint_question_id': '1', 'hint_question': 'bla'}, [{'form': 'toomany'}]),
            ({'consumer': 'dev', 'hint_question_id': '1', 'hint_question': 'bla', 'hint_answer': 'bla'}, [{'form': 'toomany'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'hint_answer': '', 'hint_question_id': ''},
             {'consumer': 'dev', 'hint_answer': '', 'hint_question_id': '', 'track_id': None, 'hint_question': None}),
            ({'consumer': 'dev', 'hint_answer': '', 'hint_question': ''},
             {'consumer': 'dev', 'hint_answer': '', 'hint_question': '', 'track_id': None, 'hint_question_id': None}),
            ({'consumer': 'dev', 'hint_question_id': '1', 'hint_answer': 'blabla', 'track_id': self.track_id},
             {'consumer': 'dev', 'hint_question_id': '1', 'hint_answer': 'blabla', 'track_id': self.track_id, 'hint_question': None}),
            ({'consumer': 'dev', 'hint_question': 'bla bla bla', 'hint_answer': 'blabla', 'track_id': self.track_id},
             {'consumer': 'dev', 'hint_question': 'bla bla bla', 'hint_answer': 'blabla', 'track_id': self.track_id, 'hint_question_id': None}),
        ]
        self.check_form(forms.SimpleHintValidation(), invalid_params, valid_params, None)

    def test_suggest_login(self):
        invalid_params = [
            ({'consumer': 'dev', 'firstname': '', 'lastname': ''},
             [{'firstname': 'empty'}, {'lastname': 'empty'}]),
            ({'consumer': 'dev', 'firstname': '', 'lastname': '', 'login': ''},
             [{'firstname': 'empty'}, {'lastname': 'empty'}, {'login': 'empty'}]),
            ({'consumer': 'dev', 'firstname': '', 'lastname': '', 'login': '        '},
             [{'firstname': 'empty'}, {'lastname': 'empty'}, {'login': 'empty'}]),
            ({'consumer': 'dev', 'login': ''}, {'login': 'empty'}),
            ({'consumer': 'dev'}, {'form': 'invalidset'}),
            ({'consumer': 'dev', 'firstname': 'aa'}, {'form': 'invalidset'}),
            ({'consumer': 'dev', 'lastname': 'aa'}, {'form': 'invalidset'}),
            ({'consumer': 'dev', 'login': 'aa', 'phone_number': 'abc'},
             {'phone_number': 'badphonenumber'}),
        ]
        valid_params = [
            ({'consumer': 'dev', 'login': 'foo'},
             dict({'consumer': 'dev', 'login': 'foo'},
                  **missing(['track_id', 'firstname', 'lastname', 'language', 'phone_number']))),
            ({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb'},
             dict({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb'},
                  **missing(['track_id', 'login', 'language', 'phone_number']))),
            ({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb', 'login': 'cc'},
             dict({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb', 'login': 'cc'},
                  **missing(['track_id', 'language', 'phone_number']))),
            ({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb', 'language': 'ru'},
             dict({'consumer': 'dev', 'firstname': 'aa', 'lastname': 'bb', 'language': 'ru'},
                  **missing(['track_id', 'login', 'phone_number']))),
            ({'consumer': 'dev', 'login': 'foo', 'phone_number': '+79261234567'},
             dict({'consumer': 'dev', 'login': 'foo',
                   'phone_number': phone_number.PhoneNumber.parse('+79261234567')},
                  **missing(['track_id', 'firstname', 'lastname', 'language']))),
        ]
        self.check_form(forms.SuggestLogin(), invalid_params, valid_params, None)

    def test_suggest_gender(self):
        invalid_params = [
            ({'consumer': 'dev'}, {'form': 'invalidset'}),
            ({'name': 'Janis Joplin'}, {'consumer': 'missingvalue'}),
            ({'consumer': 'dev', 'firstname': '', 'lastname': ''},
             [{'firstname': 'empty'}, {'lastname': 'empty'}]),
            ({'consumer': 'dev', 'name': ''}, {'name': 'empty'}),
            ({'consumer': 'dev', 'firstname': '', 'lastname': 'lastname'},
             {'firstname': 'empty'}),
            ({'consumer': 'dev', 'lastname': '', 'firstname': 'firstname'},
             {'lastname': 'empty'}),
            ({'consumer': 'dev', 'firstname': ''}, {'firstname': 'empty'}),
            ({'consumer': 'dev', 'lastname': ''}, {'lastname': 'empty'}),
            ({'consumer': 'dev', 'lastname': 'lastname', 'firstname': 'firstname', 'name': 'name'},
             {'form': 'abundantset'}),
        ]

        valid_params = [
            ({'consumer': 'dev', 'name': 'Janis Joplin'},
             {'consumer': 'dev', 'name': 'Janis Joplin', 'firstname': None,
              'lastname': None, 'track_id': None}),
            ({'consumer': 'dev', 'firstname': 'Janis'},
             {'consumer': 'dev', 'firstname': 'Janis', 'lastname': None,
              'name': None, 'track_id': None}),
            ({'consumer': 'dev', 'lastname': 'Joplin'},
             {'consumer': 'dev', 'lastname': 'Joplin', 'firstname': None,
              'name': None, 'track_id': None}),
            ({'consumer': 'dev', 'firstname': 'Janis', 'lastname': 'Joplin'},
             {'consumer': 'dev', 'firstname': 'Janis', 'lastname': 'Joplin',
              'name': None, 'track_id': None}),
            ({'consumer': 'dev', 'firstname': 'Janis', 'lastname': 'Joplin',
              'track_id': self.track_id},
             {'consumer': 'dev', 'firstname': 'Janis', 'lastname': 'Joplin',
              'name': None, 'track_id': self.track_id}),
        ]
        self.check_form(forms.SuggestGender(), invalid_params, valid_params, None)

    def test_suggest_name(self):
        invalid_params = [
            ({'consumer': 'dev'}, {'name': 'missingvalue'}),
            ({'name': 'Janis Joplin'}, {'consumer': 'missingvalue'}),
            ({'consumer': 'dev', 'name': ''}, {'name': 'empty'}),
        ]

        valid_params = [
            ({'consumer': 'dev', 'name': 'Janis Joplin'},
             {'consumer': 'dev', 'name': 'Janis Joplin', 'track_id': None}),
            ({'consumer': 'dev', 'name': 'Janis Joplin', 'track_id': self.track_id},
             {'consumer': 'dev', 'name': 'Janis Joplin', 'track_id': self.track_id}),
        ]
        self.check_form(forms.SuggestName(), invalid_params, valid_params, None)

    def test_control_questions(self):

        invalid_params = [
            ({'consumer': 'dev', 'display_language': 'abrakadabra'}, {'display_language': 'unsupported'}),
            ({'consumer': 'dev', 'display_language': ''}, {'display_language': 'empty'}),
        ]

        valid_params = [
            ({'consumer': 'dev', 'display_language': language},
             {'consumer': 'dev', 'display_language': language, 'track_id': None})
            for language in settings.DISPLAY_LANGUAGES
        ]

        self.check_form(forms.ControlQuestions(), invalid_params, valid_params, None)

    def test_captcha_generate_form(self):
        def build_params(**kwargs):
            base_params = {
                'consumer': 'dev',
                'checks': None,
                'display_language': None,
                'country': None,
                'track_id': self.track_id,
                'voice': False,
                'use_cached': False,
                'scale_factor': None,
                'type': None,
            }
            return dict(base_params, **kwargs)

        invalid_params = [
            ({'consumer': 'dev', 'display_language': 'cn', 'checks': 0}, [{'checks': 'toolow'}]),
            ({'consumer': 'dev', 'display_language': 'ru', 'checks': 10}, {'checks': 'toohigh'}),
            ({'consumer': 'dev', 'checks': 1}, {'form': 'toofew'}),
            ({'consumer': 'dev'}, {'form': 'toofew'}),
            ({'consumer': 'dev', 'display_language': 'ru', 'country': 'ru'}, {'form': 'toomany'}),
            ({'consumer': 'dev', 'type': 'wave'}, {'form': 'toofew'}),
            ({'consumer': 'dev', 'type': 'ocr', 'country': 'ru'}, {'type': 'notin'}),
            ({'consumer': 'dev', 'type': 'FAKE', 'country': 'ru'}, {'type': 'notin'}),
            ({'display_language': 'ru', 'checks': 1}, {'consumer': 'missingvalue'}),
            ({'consumer': '', 'display_language': '', 'checks': '', 'track_id': '', 'voice': ''},
             [{'checks': 'empty'}, {'consumer': 'empty'}, {'display_language': 'empty'},
              {'track_id': 'empty'}, {'voice': 'empty'}]),
            ({'consumer': 'dev', 'display_language': 'ru', 'scale_factor': 'qwerty'},
             [{'scale_factor': 'number'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'display_language': 'ru', 'checks': 1, 'track_id': self.track_id},
             build_params(display_language='ru', checks=1)),
            ({'consumer': 'dev', 'country': 'ru', 'checks': 1, 'track_id': self.track_id},
             build_params(country='ru', checks=1)),
            ({'consumer': 'dev', 'country': 'ru', 'checks': 1, 'track_id': self.track_id},
             build_params(country='ru', checks=1)),
            ({'consumer': 'dev', 'country': 'be', 'checks': 1, 'track_id': self.track_id},
             build_params(country='be', checks=1)),
            ({'consumer': 'dev', 'display_language': 'uk', 'checks': 9, 'track_id': self.track_id},
             build_params(display_language='uk', checks=9)),
            ({'consumer': 'dev', 'display_language': 'tr', 'track_id': self.track_id},
             build_params(display_language='tr')),
            ({'consumer': 'dev', 'display_language': 'ru', 'track_id': self.track_id, 'voice': 'true'},
             build_params(display_language='ru', voice=True)),
            ({'consumer': 'dev', 'display_language': 'ru', 'track_id': self.track_id, 'use_cached': 'true'},
             build_params(display_language='ru', use_cached=True)),
            ({'consumer': 'dev', 'display_language': 'ru', 'track_id': self.track_id, 'voice': '   ', 'use_cached': '  '},
             build_params(display_language='ru')),
            ({'consumer': 'dev', 'type': 'wave', 'country': 'ru', 'track_id': self.track_id},
             build_params(type='wave', country='ru')),
            # Проверим на неподдерживаемый язык капчи, форма должна вернуть ''
            ({'consumer': 'dev', 'display_language': 'vi', 'track_id': self.track_id, 'voice': '   ', 'use_cached': '  '},
             build_params(display_language='')),
            (
                {'consumer': 'dev', 'display_language': 'ru', 'track_id': self.track_id, 'scale_factor': '2'},
                build_params(display_language='ru', scale_factor=2),
            ),
            (
                {'consumer': 'dev', 'display_language': 'ru', 'track_id': self.track_id, 'scale_factor': '1.5'},
                build_params(display_language='ru', scale_factor=1.5),
            ),
        ]
        self.check_form(forms.CaptchaGenerateForm(), invalid_params, valid_params, None)

    def test_captcha_check_form(self):
        invalid_params = [
            ({'consumer': 'dev', 'display_language': '', 'answer': '', 'track_id': ''},
             [{'answer': 'empty'}, {'track_id': 'empty'}]),
            ({'consumer': 'dev', 'display_language': 'ru', 'key': '123456', 'track_id': self.track_id},
             {'answer': 'missingvalue'}),
            ({'consumer': 'dev'},
             [{'answer': 'missingvalue'}, {'track_id': 'missingvalue'}]),
            ({'key': '123456', 'answer': '3D5TE4', 'track_id': self.track_id},
             {'consumer': 'missingvalue'}),
            ({'consumer': 'dev', 'answer': 'a' * 101, 'key': 'a' * 101, 'track_id': self.track_id},
             [{'key': 'toolong'}, {'answer': 'toolong'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'display_language': 'ru', 'key': '10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF', 'answer': 123456, 'track_id': self.track_id},
             {'consumer': 'dev', 'key': '10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF', 'answer': '123456', 'track_id': self.track_id}),
            ({'consumer': 'dev', 'key': '123456', 'answer': '3D5TE4', 'track_id': self.track_id},
             {'consumer': 'dev', 'key': '123456', 'answer': '3D5TE4', 'track_id': self.track_id}),
            ({'consumer': 'dev', 'key': '', 'answer': '3D5TE4', 'track_id': self.track_id},
             {'consumer': 'dev', 'key': '', 'answer': '3D5TE4', 'track_id': self.track_id}),
            ({'consumer': 'dev', 'answer': '3D5TE4', 'track_id': self.track_id},
             {'consumer': 'dev', 'key': None, 'answer': '3D5TE4', 'track_id': self.track_id}),
        ]
        self.check_form(forms.CaptchaCheckForm(), invalid_params, valid_params, None)

    def test_social_provider_form(self):
        invalid_params = [
            ({'provider': 'aaa', 'consumer': 'dev', 'track_id': self.track_id}, {'provider': 'invalid'}),
            ({'provider': '%%', 'consumer': 'dev', 'track_id': self.track_id}, {'provider': 'invalid'}),
            ({'provider': 'a', 'consumer': 'dev', 'track_id': self.track_id}, {'provider': 'invalid'}),
            ({'provider': '', 'consumer': 'dev', 'track_id': self.track_id}, {'provider': 'empty'}),
            ({'provider': 'aa', 'consumer': 'dev', 'track_id': ''}, {'track_id': 'empty'}),
            ({'provider': 'aa', 'track_id': self.track_id}, {'consumer': 'missingvalue'}),
        ]
        valid_params = [
            ({'provider': 'aa', 'consumer': 'dev', 'track_id': self.track_id},
             {'provider': 'aa', 'consumer': 'dev', 'track_id': self.track_id}),
        ]
        self.check_form(forms.SocialProvider(), invalid_params, valid_params, None)

    def test_account_register_require_confirmed_phone(self):
        DEFAULT_VALID_PARAMS = {
            'birthday': '1950-05-01',
            'consumer': 'dev',
            'country': 'ru',
            'eula_accepted': 'True',
            'gender': 'm',
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            'language': 'ru',
            'login': 'test',
            'password': 'testpasswd',
            'timezone': 'Europe/Moscow',
            'track_id': self.track_id,
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            ({'consumer': 'dev'},
             [{'country': 'missingvalue'}, {'firstname': 'missingvalue'},
              {'language': 'missingvalue'}, {'lastname': 'missingvalue'},
              {'login': 'missingvalue'}, {'password': 'missingvalue'},
              {'track_id': 'missingvalue'},
              {'eula_accepted': 'missingvalue'}]),
            # empty
            ({'consumer': 'dev', 'track_id': self.track_id, 'country': '',
              'login': '', 'password': '', 'firstname': '', 'lastname': '',
              'language': '', 'eula_accepted': ''},
             [{'country': 'empty'}, {'firstname': 'empty'}, {'language': 'empty'},
              {'lastname': 'empty'}, {'login': 'empty'}, {'password': 'empty'},
              {'eula_accepted': 'empty'}]),
            # consumer
            build_params({'consumer': 'bad consumer'},
                         [{'consumer': 'notin'}]),
            # birthday
            build_params({'birthday': 'birthday'},
                         [{'birthday': 'badbirthday'}]),
            # country
            build_params({'country': 'country'},
                         [{'country': 'badcountrycode'}]),
            # eula_accepted
            build_params({'eula_accepted': 'noooooo'},
                         [{'eula_accepted': 'string'}]),
            # eula_accepted empty
            build_params({'eula_accepted': ' '},
                         [{'eula_accepted': 'empty'}]),
            # gender
            build_params({'gender': 'gender'},
                         [{'gender': 'badgender'}]),
            # empty firstname
            build_params({'firstname': ''},
                         [{'firstname': 'empty'}]),
            # empty lastname
            build_params({'lastname': ''},
                         [{'lastname': 'empty'}]),
            # empty firstname 2
            build_params({'firstname': '  '},
                         [{'firstname': 'empty'}]),
            # empty lastname 2
            build_params({'lastname': '  '},
                         [{'lastname': 'empty'}]),
            # language
            build_params({'language': 'language'},
                         [{'language': 'unsupported'}]),
            # login
            build_params({'login': '  '},
                         [{'login': 'empty'}]),
            # timezone
            build_params({'timezone': 'timezone'},
                         [{'timezone': 'badtimezone'}]),
            # track_id
            build_params({'track_id': '0'},
                         [{'track_id': 'invalidid'}]),
        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        valid_params = [
            # just default
            build_params(
                {},
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        self.check_form(forms.AccountRegisterRequireConfirmedPhone(), invalid_params, valid_params, state)

    def test_account_register_select_alternative(self):
        invalid_params = [
            ({},
             [{'consumer': 'missingvalue'},
              {'track_id': 'missingvalue'},
              {'validation_method': 'missingvalue'}]),
            ({'consumer': '', 'track_id': '', 'validation_method': ''},
             [{'consumer': 'empty'},
              {'track_id': 'empty'},
              {'validation_method': 'empty'}]),
            ({'consumer': 'dev', 'track_id': self.track_id, 'validation_method': '1'},
             [{'validation_method': 'notin'}]),
        ]

        base_params = {
            'consumer': 'dev',
            'track_id': self.track_id,
        }

        valid_params = [
            (
                merge_dicts(base_params, {'validation_method': 'phone'}),
                {
                    'consumer': 'dev',
                    'track_id': self.track_id,
                    'validation_method': 'phone',
                },
            ),
            (
                merge_dicts(base_params, {'validation_method': 'captcha'}),
                {
                    'consumer': 'dev',
                    'track_id': self.track_id,
                    'validation_method': 'captcha',
                },
            ),
        ]
        self.check_form(forms.AccountRegisterSelectAlternative, invalid_params, valid_params, None)

    def test_account_register_alternative_with_hint(self):
        DEFAULT_VALID_PARAMS = {
            'birthday': '1950-05-01',
            'consumer': 'dev',
            'country': 'ru',
            'display_language': 'ru',
            'eula_accepted': 'True',
            'gender': 'm',
            'hint_answer': 'answer',
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            'language': 'ru',
            'login': 'test',
            'password': 'testpasswd',
            'timezone': 'Europe/Moscow',
            'track_id': self.track_id,
            'plus_promo_code': None,
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            ({'consumer': 'dev'},
             [{'country': 'missingvalue'}, {'firstname': 'missingvalue'},
              {'language': 'missingvalue'}, {'lastname': 'missingvalue'},
              {'login': 'missingvalue'}, {'password': 'missingvalue'},
              {'track_id': 'missingvalue'}, {'display_language': 'missingvalue'},
              {'eula_accepted': 'missingvalue'}]),
            # empty
            ({'consumer': 'dev', 'track_id': self.track_id, 'country': '',
              'login': '', 'password': '', 'firstname': '', 'lastname': '',
              'language': '', 'display_language': '',
              'eula_accepted': ''},
             [{'country': 'empty'}, {'firstname': 'empty'}, {'language': 'empty'},
              {'lastname': 'empty'}, {'login': 'empty'}, {'password': 'empty'},
              {'display_language': 'empty'}, {'eula_accepted': 'empty'}]),
            # toomany
            build_params({'hint_question': 'qwerty', 'hint_question_id': '1'},
                         [{'form': 'abundantset'}]),
            # consumer
            build_params({'consumer': 'bad consumer'},
                         [{'consumer': 'notin'}]),
            # birthday
            build_params({'birthday': 'birthday'},
                         [{'birthday': 'badbirthday'}]),
            # display_language
            build_params({'display_language': 'language'},
                         [{'display_language': 'unsupported'}]),
            # country
            build_params({'country': 'country'},
                         [{'country': 'badcountrycode'}]),
            # eula_accepted
            build_params({'eula_accepted': 'noooooo'},
                         [{'eula_accepted': 'string'}]),
            # eula_accepted empty
            build_params({'eula_accepted': ' '},
                         [{'eula_accepted': 'empty'}]),
            # gender
            build_params({'gender': 'gender'},
                         [{'gender': 'badgender'}]),
            # hint_answer
            build_params({'hint_answer': '  '},
                         [{'hint_answer': 'empty'}]),
            # hint_question
            build_params({'hint_question': '  '},
                         [{'hint_question': 'empty'}]),
            # hint_question_id
            build_params({'hint_question_id': 'hint_id'},
                         [{'hint_question_id': 'integer'}]),
            # empty firstname
            build_params({'firstname': ''},
                         [{'firstname': 'empty'}]),
            # empty lastname
            build_params({'lastname': ''},
                         [{'lastname': 'empty'}]),
            # empty firstname 2
            build_params({'firstname': '  '},
                         [{'firstname': 'empty'}]),
            # empty lastname 2
            build_params({'lastname': '  '},
                         [{'lastname': 'empty'}]),
            # language
            build_params({'language': 'language'},
                         [{'language': 'unsupported'}]),
            # login
            build_params({'login': '  '},
                         [{'login': 'empty'}]),
            # timezone
            build_params({'timezone': 'timezone'},
                         [{'timezone': 'badtimezone'}]),
            # track_id
            build_params({'track_id': '0'},
                         [{'track_id': 'invalidid'}]),

        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        valid_params = [
            build_params(
                {'hint_question_id': 1},
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'hint_question_id': 1,
                    'hint_question': None,
                    'hint_answer': 'answer',
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'tmx_session': None,
                    'force_clean_web': False,
                    'plus_promo_code': '',
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            build_params(
                {
                    'hint_question': 'question',
                },
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'hint_question_id': None,
                    'hint_question': 'question',
                    'hint_answer': 'answer',
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'tmx_session': None,
                    'force_clean_web': False,
                    'plus_promo_code': '',
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            build_params(
                {
                    'hint_question': 'question',
                    'tmx_session': 'TMX',
                },
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'hint_question_id': None,
                    'hint_question': 'question',
                    'hint_answer': 'answer',
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'tmx_session': 'TMX',
                    'force_clean_web': False,
                    'plus_promo_code': '',
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            build_params(
                {
                    'hint_question': 'question',
                    'plus_promo_code': ' CODE ',
                    'unsubscribe_from_maillists': 'yes',
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'hint_question_id': None,
                    'hint_question': 'question',
                    'hint_answer': 'answer',
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'tmx_session': None,
                    'force_clean_web': False,
                    'plus_promo_code': 'CODE',
                    'unsubscribe_from_maillists': True,
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        self.check_form(forms.AccountRegisterAlternativeWithHint(), invalid_params, valid_params, state)

    def test_account_register_social(self):
        DEFAULT_VALID_PARAMS = {
            'birthday': '1950-05-01',
            'consumer': 'dev',
            'country': 'ru',
            'eula_accepted': 'True',
            'gender': 'm',
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            'language': 'ru',
            'login': 'uid-test',
            'provider': 'fb',
            'timezone': 'Europe/Moscow',
            'track_id': self.track_id,
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            ({'consumer': 'dev'},
             [{'country': 'missingvalue'}, {'firstname': 'missingvalue'},
              {'language': 'missingvalue'}, {'lastname': 'missingvalue'},
              {'provider': 'missingvalue'},
              {'track_id': 'missingvalue'},
              {'eula_accepted': 'missingvalue'}]),
            # empty
            ({'consumer': 'dev', 'track_id': self.track_id, 'country': '',
              'login': '', 'firstname': '', 'lastname': '',
              'language': '', 'provider': '',
              'eula_accepted': ''},
             [{'country': 'empty'}, {'firstname': 'empty'}, {'language': 'empty'},
              {'lastname': 'empty'}, {'login': 'empty'},
              {'provider': 'empty'},
              {'eula_accepted': 'empty'}]),
            # consumer
            build_params({'consumer': 'bad consumer'},
                         [{'consumer': 'notin'}]),
            # birthday
            build_params({'birthday': 'birthday'},
                         [{'birthday': 'badbirthday'}]),
            # country
            build_params({'country': 'country'},
                         [{'country': 'badcountrycode'}]),
            # eula_accepted
            build_params({'eula_accepted': 'noooooo'},
                         [{'eula_accepted': 'string'}]),
            # eula_accepted empty
            build_params({'eula_accepted': ' '},
                         [{'eula_accepted': 'empty'}]),
            # gender
            build_params({'gender': 'gender'},
                         [{'gender': 'badgender'}]),
            # empty firstname
            build_params({'firstname': ''},
                         [{'firstname': 'empty'}]),
            # empty lastname
            build_params({'lastname': ''},
                         [{'lastname': 'empty'}]),
            # empty firstname 2
            build_params({'firstname': '  '},
                         [{'firstname': 'empty'}]),
            # empty lastname 2
            build_params({'lastname': '  '},
                         [{'lastname': 'empty'}]),
            # language
            build_params({'language': 'language'},
                         [{'language': 'unsupported'}]),
            # login
            build_params({'login': 'blabla'},
                         [{'login': 'notsocial'}]),
            # provider
            build_params({'provider': 'provider'},
                         [{'provider': 'invalid'}]),
            # timezone
            build_params({'timezone': 'timezone'},
                         [{'timezone': 'badtimezone'}]),
            # track_id
            build_params({'track_id': '0'},
                         [{'track_id': 'invalidid'}]),

        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'uid-test': 'free'}),
        )

        valid_params = [
            # all fields
            build_params(
                {},
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'uid-test',
                    'provider': 'fb',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'force_clean_web': False,
                },
            ),
            (
                {
                    'consumer': 'dev',
                    'country': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'provider': 'fb',
                    'track_id': self.track_id,
                },
                {
                    'consumer': 'dev',
                    'country': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'provider': 'fb',
                    'login': None,
                    'track_id': self.track_id,
                    'timezone': None,
                    'birthday': None,
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        self.check_form(forms.AccountRegisterSocial(), invalid_params, valid_params, state)

    def test_account_register_uncompleted(self):
        DEFAULT_VALID_PARAMS = {
            'consumer': 'dev',
            'track_id': self.track_id,
            'login': 'test',
            'firstname': 'firstname',
            'lastname': 'lastname',
            'language': 'ru',
            'country': 'tr',
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            ({'consumer': 'dev'},
             [{'login': 'missingvalue'}, {'track_id': 'missingvalue'},
              {'country': 'missingvalue'}, {'firstname': 'missingvalue'},
              {'language': 'missingvalue'}, {'lastname': 'missingvalue'}]),
            # empty
            ({'consumer': 'dev', 'login': '',
              'firstname': '', 'lastname': '',
              'language': '', 'country': '', 'gender': '', 'birthday': '',
              'timezone': '', 'track_id': ''},
             [{'login': 'empty'}, {'firstname': 'empty'},
              {'lastname': 'empty'}, {'language': 'empty'},
              {'country': 'empty'}, {'track_id': 'empty'}]),
            # consumer
            build_params({'consumer': 'bad consumer'},
                         [{'consumer': 'notin'}]),
            # login
            build_params({'login': '  '},
                         [{'login': 'empty'}]),
            # language
            build_params({'language': 'language'},
                         [{'language': 'unsupported'}]),
            # country
            build_params({'country': 'country'},
                         [{'country': 'badcountrycode'}]),
            # gender
            build_params({'gender': 'gender'},
                         [{'gender': 'badgender'}]),
            # birthday
            build_params({'birthday': 'birthday'},
                         [{'birthday': 'badbirthday'}]),
            # timezone
            build_params({'timezone': 'timezone'},
                         [{'timezone': 'badtimezone'}]),
            # empty firstname
            build_params({'firstname': ''},
                         [{'firstname': 'empty'}]),
            # empty lastname
            build_params({'lastname': ''},
                         [{'lastname': 'empty'}]),
            # empty firstname 2
            build_params({'firstname': '  '},
                         [{'firstname': 'empty'}]),
            # empty lastname 2
            build_params({'lastname': '  '},
                         [{'lastname': 'empty'}]),
        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )
        self.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        valid_params = [
            # Проверка значений по-умолчанию
            build_params(
                {},
                {
                    'track_id': self.track_id,
                    'consumer': 'dev',
                    'login': 'test',
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'language': 'ru',
                    'country': 'tr',
                    'gender': None,
                    'birthday': None,
                    'timezone': None,
                    'force_clean_web': False,
                },
            ),
            # Все параметры
            build_params(
                {
                    'track_id': self.track_id,
                    'consumer': 'dev',
                    'login': 'test',
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'language': 'ru',
                    'country': 'tr',
                    'gender': '1',
                    'birthday': '1950-05-01',
                    'timezone': 'Europe/Paris',
                },
                {
                    'track_id': self.track_id,
                    'consumer': 'dev',
                    'login': 'test',
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'language': 'ru',
                    'country': 'tr',
                    'gender': Gender.Male,
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'timezone': pytz.timezone('Europe/Paris'),
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        self.check_form(forms.AccountRegisterUncompleted, invalid_params, valid_params, state)

    def test_session_check(self):
        invalid_params = [
            ({},
             [{'consumer': 'missingvalue'}, {'track_id': 'missingvalue'}, {'session': 'missingvalue'}]),
            ({'consumer': 'dev', 'session': '', 'track_id': ''},
             [{'track_id': 'empty'}]),
        ]

        valid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev', 'session': ''},
             {'track_id': self.track_id, 'consumer': 'dev', 'session': '', 'sslsession': None, 'sessguard': None}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'session': '', 'sslsession': '', 'sessguard': ''},
             {'track_id': self.track_id, 'consumer': 'dev', 'session': '', 'sslsession': '', 'sessguard': ''}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'session': '2:session'},
             {'track_id': self.track_id, 'consumer': 'dev', 'session': '2:session', 'sslsession': None, 'sessguard': None}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'session': '2:session', 'sslsession': '2:sslsession', 'sessguard': '1.sessguard'},
             {'track_id': self.track_id, 'consumer': 'dev', 'session': '2:session', 'sslsession': '2:sslsession', 'sessguard': '1.sessguard'}),
        ]

        self.check_form(forms.SessionCheck(), invalid_params, valid_params, None)

    def test_oauth_token_create(self):
        invalid_params = [
            ({},
             [{'consumer': 'missingvalue'}, {'track_id': 'missingvalue'},
              {'client_id': 'missingvalue'}, {'client_secret': 'missingvalue'}]),
            ({'consumer': '', 'track_id': '', 'client_id': '', 'client_secret': ''},
             [{'consumer': 'empty'}, {'track_id': 'empty'},
              {'client_id': 'empty'}, {'client_secret': 'empty'}]),
        ]

        valid_params = [
            (
                {
                    'track_id': self.track_id,
                    'consumer': 'dev',
                    'client_id': 'id',
                    'client_secret': 'secret',
                },
                {
                    'track_id': self.track_id,
                    'consumer': 'dev',
                    'client_id': 'id',
                    'client_secret': 'secret',
                },
            ),
        ]

        self.check_form(forms.OAuthTokenCreate(), invalid_params, valid_params, None)

    def test_retpath_validation(self):
        invalid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev', }, {'retpath': 'missingvalue'}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'retpath': ''}, {'retpath': 'empty'}),
        ]

        valid_params = [
            ({'track_id': self.track_id, 'consumer': 'dev', 'retpath': '//yandex.ru'},
             {'track_id': self.track_id, 'consumer': 'dev', 'retpath': '//yandex.ru'}),
            ({'track_id': self.track_id, 'consumer': 'dev', 'retpath': '//yandex.com.tr'},
             {'track_id': self.track_id, 'consumer': 'dev', 'retpath': '//yandex.com.tr'}),
        ]

        self.check_form(forms.RetPathValidation(), invalid_params, valid_params, None)

    def test_phone_confirmation(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'display_language': 'missingvalue'}, {'track_id': 'missingvalue'},
              {'country': 'missingvalue'}, {'phone_number': 'missingvalue'}]),

            ({'consumer': 'dev', 'track_id': self.track_id, 'country': '',
              'display_language': '', 'phone_number': ''},
             [{'country': 'empty'}, {'display_language': 'empty'}, {'phone_number': 'empty'}]),

            ({'consumer': 'dev', 'track_id': '     ', 'country': '    ',
              'display_language': '    ', 'phone_number': '+79161234567'},
             [{'country': 'badcountrycode'},
              {'display_language': 'empty'}, {'track_id': 'invalidid'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'track_id': self.track_id, 'country': 'ru',
              'display_language': 'ru', 'phone_number': '+79161234567', 'ignore_phone_compare': '1'},
             {'consumer': 'dev', 'track_id': self.track_id, 'country': 'ru',
              'display_language': 'ru', 'phone_number': '+79161234567',
              'ignore_phone_compare': True}),

            ({'consumer': 'dev', 'track_id': self.track_id, 'country': 'ru', 'ignore_phone_compare': '1',
              'display_language': 'ru', 'phone_number': '+74951234567'},
             {'consumer': 'dev', 'track_id': self.track_id, 'country': 'ru', 'ignore_phone_compare': True,
              'display_language': 'ru', 'phone_number': '+74951234567'}),
        ]

        self.check_form(forms.PhoneConfirmation(), invalid_params, valid_params, None)

    def test_confirm_phone(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'track_id': 'missingvalue'}, {'code': 'missingvalue'}]),
            ({'consumer': 'dev', 'track_id': '', 'code': ''},
             [{'track_id': 'empty'}, {'code': 'empty'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'track_id': self.track_id, 'code': '1234'},
             {'consumer': 'dev', 'track_id': self.track_id, 'code': '1234'}),
        ]

        self.check_form(forms.ConfirmPhone(), invalid_params, valid_params, None)

    def test_phone_copy(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'src_oauth_token': 'missingvalue'},
              {'dst_oauth_token': 'missingvalue'},
              {'phone_number': 'missingvalue'}]),
            ({'consumer': 'dev', 'src_oauth_token': '', 'dst_oauth_token': '',
              'phone_number': ''},
             [{'src_oauth_token': 'empty'}, {'dst_oauth_token': 'empty'},
              {'phone_number': 'empty'}]),
            ({'consumer': 'dev', 'src_oauth_token': '123', 'dst_oauth_token': '321',
              'phone_number': '8 909 999 88 77'},
             [{'phone_number': 'badphonenumber'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'src_oauth_token': '123', 'dst_oauth_token': '456',
              'phone_number': '+791234567802'},
             {'phone_number': phone_number.PhoneNumber.parse('+791234567802', allow_impossible=True),
              'consumer': 'dev', 'src_oauth_token': '123', 'dst_oauth_token': '456'}),
            ({'consumer': 'dev', 'src_oauth_token': '123', 'dst_oauth_token': '456',
              'phone_number': '+7912 33 33'},
             {'phone_number': phone_number.PhoneNumber.parse('+7912 33 33', allow_impossible=True),
              'consumer': 'dev', 'src_oauth_token': '123', 'dst_oauth_token': '456'}),
        ]

        self.check_form(forms.PhoneCopy(), invalid_params, valid_params, None)

    def test_phone(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'phone_number': 'missingvalue'}, {'uid': 'missingvalue'}]),
        ]

        valid_params = [
            ({'consumer': 'dev', 'uid': '1', 'phone_number': '+79031234567'},
             {'phone_number': phone_number.PhoneNumber.parse('+79031234567'),
              'confirmation_timestamp': None, 'consumer': 'dev', 'uid': 1}),
            ({'consumer': 'dev', 'uid': '1', 'phone_number': '+791234567802'},
             {'phone_number': phone_number.PhoneNumber.parse('+791234567802', allow_impossible=True),
              'consumer': 'dev', 'uid': 1, 'confirmation_timestamp': None}),
            ({'consumer': 'dev', 'uid': '1', 'phone_number': '9031234567'},
             {'phone_number': phone_number.PhoneNumber.parse('+9031234567', allow_impossible=True),
              'consumer': 'dev', 'uid': 1, 'confirmation_timestamp': None}),
        ]

        self.check_form(forms.AccountPhone(), invalid_params, valid_params, None)

    def test_set_password(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'track_id': 'missingvalue'}, {'password': 'missingvalue'}]),
            ({'consumer': 'dev', 'track_id': self.track_id}, {'password': 'missingvalue'}),
        ]

        valid_params = [
            ({'consumer': 'dev', 'track_id': self.track_id, 'password': 'testpasswd'},
             {'consumer': 'dev', 'track_id': self.track_id, 'password': 'testpasswd'}),
        ]

        self.check_form(forms.SetPassword(), invalid_params, valid_params, None)

    def test_uncompleted_set_password(self):
        invalid_params = [
            ({'consumer': 'dev'},
             [{'track_id': 'missingvalue'}, {'password': 'missingvalue'}, {'eula_accepted': 'missingvalue'}]),
            ({'consumer': 'dev', 'track_id': self.track_id, 'eula_accepted': '1'},
             {'password': 'missingvalue'}),
            ({'consumer': 'dev', 'track_id': self.track_id, 'password': 'Bl3kSdk', 'eula_accepted': 'bla'},
             {'eula_accepted': 'string'}),
            ({'consumer': '', 'track_id': '', 'password': '', 'eula_accepted': ''},
             [{'track_id': 'empty'}, {'password': 'empty'}, {'eula_accepted': 'empty'}, {'consumer': 'empty'}]),
        ]

        valid_params = [
            (
                {'consumer': 'dev', 'track_id': self.track_id, 'password': 'testpasswd', 'eula_accepted': '1'},
                {
                    'consumer': 'dev',
                    'track_id': self.track_id,
                    'password': 'testpasswd',
                    'eula_accepted': True,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        self.check_form(forms.SetPasswordUncompleted(), invalid_params, valid_params, state)

    def test_hint(self):
        invalid_params = [
            ({},
             [{'display_language': 'missingvalue'}]),
            ({'display_language': 'ru'},
             [{'form': 'invalidset'}]),
            ({'hint_question_id': '1', 'hint_answer': '   ', 'display_language': 'ru'},
             [{'hint_answer': 'empty'}]),
            ({'hint_question': 'qwerty', 'hint_question_id': '1', 'display_language': 'ru'},
             [{'form': 'invalidset'}]),
            ({'consumer': 'dev', 'hint_answer': 'qwerty', 'hint_question_id': 'a1', 'display_language': 'ru'},
             [{'hint_question_id': 'integer'}]),
        ]

        valid_params = [
            ({'display_language': 'ru', 'hint_question_id': '1', 'hint_answer': 'abc'},
             {'display_language': 'ru', 'hint_question_id': 1, 'hint_answer': 'abc',
              'hint_question': None}),
            ({'display_language': 'ru', 'hint_question': 'bla bla bla', 'hint_answer': 'lala lala'},
             {'display_language': 'ru', 'hint_question_id': None, 'hint_answer': 'lala lala',
              'hint_question': 'bla bla bla'}),
        ]

        self.check_form(forms.Hint(), invalid_params, valid_params, None)
