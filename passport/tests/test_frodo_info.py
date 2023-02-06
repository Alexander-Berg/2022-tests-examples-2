# -*- coding: utf-8 -*-

import time
from unittest import TestCase

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.frodo import FrodoInfo
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.cookies.cookie_l import CookieLUnpackError
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber

from .utils import (
    DEFAULT_QUERY_PARAMS,
    mock_track,
)


class FrodoInfoTestCase(TestCase):
    def test_new_with_empty_params(self):
        info = FrodoInfo()
        for value in info:
            eq_(value, '')

    def test_create(self):
        env = mock_env(cookies={'fuid00': 'f', 'yandexuid': 'uid'}, user_agent='ua', host='h')

        track_data = {
            'uid': '1',
            'captcha_generate_count': '1',
            'image_captcha_type': 'std',
            'voice_captcha_type': 'rus',
            'suggest_login_count': '2',
            'suggest_login_length': '2',
            'phone_confirmation_first_send_at': str(time.time()),
            'phone_confirmation_first_checked': str(time.time()),
            'sanitize_phone_changed_phone': '1',
            'sanitize_phone_error': '1',
            'phone_confirmation_sms_count': '2',
            'phone_confirmation_confirms_count': '3',
            'origin': 'origin',
            'phone_confirmation_last_checked': str(time.time()),
            'phone_confirmation_last_send_at': str(time.time()),

            'phone_confirmation_send_ip_limit_reached': '1',
            'phone_confirmation_send_count_limit_reached': '1',
            'phone_confirmation_confirms_count_limit_reached': '1',

            'device_language_sys': 'l_sys',
            'device_locale': 'locale',
            'device_geo_coarse': 'geo',
            'device_hardware_id': 'h_id',
            'device_os_id': 'os_id',
            'device_application': 'app',
            'device_cell_provider': 'cell',
            'device_hardware_model': 'h_model',
            'device_clid': 'clid',
            'device_app_uuid': 'uuid',

            'sanitize_phone_count': '8',
            'sanitize_phone_first_call': '10',
            'sanitize_phone_last_call': '11',
            'suggest_login_first_call': '12',
            'suggest_login_last_call': '13',
            'login_validation_count': 12,
            'login_validation_first_call': '16',
            'login_validation_last_call': '17',
            'password_validation_count': '2',
            'password_validation_first_call': '18',
            'password_validation_last_call': '19',
            'captcha_checked_at': '21',
            'captcha_generated_at': '22',
            'captcha_check_count': 11,
            'created': str(time.time()),
            'page_loading_info': '{"foo": true}',
        }

        query_params = dict(DEFAULT_QUERY_PARAMS)
        query_params['hint_question_id'] = 99
        query_params['hint_answer'] = 'hinta'
        query_params['service'] = 'mail'
        query_params['consumer'] = 'dev'

        track = mock_track(track_data=track_data)
        track._lists['suggested_logins'] = ['l', 'r2d2']

        info = FrodoInfo.create(env, query_params, track=track)
        eq_(info.login, DEFAULT_QUERY_PARAMS['login'])
        eq_(info.firstname, DEFAULT_QUERY_PARAMS['firstname'])
        eq_(info.lastname, DEFAULT_QUERY_PARAMS['lastname'])
        eq_(info.email, DEFAULT_QUERY_PARAMS['email'])
        eq_(info.service, 'mail')
        eq_(info.password, '0.0.0.0.0.0.0.0')
        eq_(info.password_ex, '0.0.0.0.0.0.0.0')
        eq_(info.password_quality, 0)
        eq_(info.hint_question_id, 99)
        eq_(info.hint_question_metadata, '5.2.3.0.0.0')
        eq_(info.hint_question_metadata_ex, '3.2.0.0.0')
        eq_(info.hint_answer_metadata, '5.0.5.0.0.0')
        eq_(info.hint_answer_metadata_ex, '2.3.0.0.0')
        eq_(info.phone_number, '79990004567'),
        eq_(info.yandexuid, 'uid')
        eq_(info.fuid, 'f')
        eq_(info.useragent, env.user_agent)
        eq_(info.host, env.host)
        eq_(info.ip_from, env.user_ip)
        eq_(info.ip, env.user_ip)
        ok_(info.server_time, TimeNow())
        eq_(info.social_provider, DEFAULT_QUERY_PARAMS['social_provider'])
        eq_(info.val_key, '0000000000')
        eq_(info.language, DEFAULT_QUERY_PARAMS['language'])
        eq_(info.country, DEFAULT_QUERY_PARAMS['country'])
        eq_(info.action, DEFAULT_QUERY_PARAMS['action'])
        eq_(info.suggest_login_count, 2)
        eq_(info.suggest_login_length, 2)
        eq_(info.captcha_generate_count, 1)
        eq_(info.image_captcha_type, 'std')
        eq_(info.voice_captcha_type, 'rus')
        eq_(info.step1time, 2000)
        eq_(info.step2time, 2000)

        eq_(info.phone_confirmation_first_sms_send_at, TimeNow())
        eq_(info.phone_confirmation_first_code_checked, TimeNow())
        eq_(info.phone_validation_changes, '1')
        eq_(info.phone_validation_error, '1')
        eq_(info.phone_confirmation_sms_count, 2)
        eq_(info.phone_confirms_count, 3)
        eq_(info.origin, 'origin')
        eq_(info.consumer, 'dev')
        eq_(info.is_suggested_login, '1')

        eq_(info.phone_confirmation_last_send_at, TimeNow())
        eq_(info.phone_confirmation_last_checked, TimeNow())

        eq_(info.phone_confirmation_send_ip_limit_reached, '1')
        eq_(info.phone_confirmation_send_count_limit_reached, '1')
        eq_(info.phone_confirmation_confirms_count_limit_reached, '1')
        eq_(info.language_sys, 'l_sys')
        eq_(info.locale, 'locale')
        eq_(info.geo_coarse, 'geo')
        eq_(info.hardware_id, 'h_id')
        eq_(info.os_id, 'os_id')
        eq_(info.application, 'app')
        eq_(info.cell_provider, 'cell')
        eq_(info.hardware_model, 'h_model')
        eq_(info.clid, 'clid')
        eq_(info.app_uuid, 'uuid')
        eq_(info.sanitize_phone_count, 8)
        eq_(info.sanitize_phone_first_call, '10')
        eq_(info.sanitize_phone_last_call, '11')
        eq_(info.suggest_login_first_call, '12')
        eq_(info.suggest_login_last_call, '13')
        eq_(info.login_validation_count, 12)
        eq_(info.login_validation_first_call, '16')
        eq_(info.login_validation_last_call, '17')
        eq_(info.password_validation_count, 2)
        eq_(info.password_validation_first_call, '18')
        eq_(info.password_validation_last_call, '19')
        eq_(info.captcha_checked_at, '21')
        eq_(info.captcha_generated_at, '22')
        eq_(info.captcha_check_count, 11)
        eq_(info.track_created, TimeNow())
        eq_(info.page_loading_info, '{"foo": true}')

    def test_create_none_headers(self):
        info = FrodoInfo.create(mock_env(), {})
        eq_(info.host, '')
        eq_(info.useragent, '')

    def test_create_with_confirmed_phone_in_track(self):
        test_phone = PhoneNumber.parse('+79151234567')
        track = mock_track(track_data={
            'phone_confirmation_is_confirmed': '1',
            'phone_confirmation_phone_number': test_phone.e164,
        })
        info = FrodoInfo.create(mock_env(), {}, track=track)
        eq_(info.phone_number, test_phone.masked_format_for_frodo)
        eq_(info.phone_number_hash, get_phone_number_hash(test_phone.e164))

    def test_create_with_phone_in_query_params_and_confirmed_phone_in_track(self):
        """Явно переданный телефон имеет приоритет над треком"""
        test_phone = PhoneNumber.parse('+79151234567')
        track = mock_track(track_data={
            'phone_confirmation_is_confirmed': '1',
            'phone_confirmation_phone_number': '+79999999999',
        })
        info = FrodoInfo.create(mock_env(), {'phone_number': test_phone.e164}, track=track)
        eq_(info.phone_number, test_phone.masked_format_for_frodo)
        eq_(info.phone_number_hash, get_phone_number_hash(test_phone.e164))

    def test_normalize_login(self):
        info = FrodoInfo.create(mock_env(), {'login': 'test.login'})
        eq_(info.login, 'test-login')

    def test_is_suggested_login(self):
        track = mock_track(track_data={'suggest_login_count': 1})
        track._lists['suggested_logins'] = ['test-login']
        info = FrodoInfo.create(mock_env(), {'login': 'test-login'}, track=track)
        eq_(info.is_suggested_login, '1')
        eq_(info.suggest_login_length, 1)

    def test_is_not_suggested_login(self):
        track = mock_track(track_data={})
        track._lists['suggested_logins'] = []
        info = FrodoInfo.create(mock_env(), {'login': 'test-login'}, track=track)
        eq_(info.is_suggested_login, '')
        eq_(info.suggest_login_length, '')

    def test_create__service_from_track(self):
        track_data = {
            'service': 'service',
        }
        info = FrodoInfo.create(mock_env(), {}, track=mock_track(track_data=track_data))
        eq_(info.service, 'service')

    def test_create__uid_from_track(self):
        track_data = {
            'uid': '1',
        }
        info = FrodoInfo.create(mock_env(), {'uid': '2'}, track=mock_track(track_data=track_data))
        eq_(info.uid, '1')

    def test_create__uid_from_query(self):
        track_data = {
            'uid': None,
        }
        info = FrodoInfo.create(mock_env(), {'uid': '2'}, track=mock_track(track_data=track_data))
        eq_(info.uid, '2')

    def test_invalid_l_cookie(self):
        with mock.patch(
            u'passport.backend.core.builders.frodo.frodo_info.CookieL',
        ) as CookieL:
            cookie_l = mock.Mock(name=u'cookie_l')
            cookie_l.unpack.side_effect = CookieLUnpackError
            CookieL.return_value = cookie_l
            info = FrodoInfo.create(mock_env(cookies={u'L': u'invalid'}), {})

            eq_(info.cookie_l_login, '')
            eq_(info.cookie_l_uid, '')
            eq_(info.cookie_l_timestamp, '')
