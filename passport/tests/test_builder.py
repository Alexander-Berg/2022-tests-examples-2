# -*- coding: utf-8 -*-

import time
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.frodo.exceptions import FrodoError
from passport.backend.core.builders.frodo.faker import FakeFrodo
from passport.backend.core.builders.frodo.frodo_info import FrodoInfo
from passport.backend.core.builders.frodo.service import (
    Frodo,
    User,
)
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.useragent.sync import RequestError
from passport.backend.utils.string import smart_text

from .utils import (
    DEFAULT_QUERY_PARAMS,
    mock_track,
)


RESPONSE_BAD_XML = '<spamlist'
RESPONSE_BAD_CYRILLIC_XML = '<spamlist><spam_user login="xn--80akaqde8b@ЮМОЮКНБ.П" weight="85" />'
RESPONSE_CHANGE_PASS = '<spamlist><change_pass login="zxfzxf2" weight="85" /></spamlist>'
RESPONSE_EMPTY_LIST = '<spamlist></spamlist>'
RESPONSE_NO_SPAMLIST_TAG = '<list><user></user></list>'
RESPONSE_SPAM_USER = '''<spamlist>
                            <spam_user login="alpha" weight="85" />
                            <spam_user login="beta" weight="85" />
                            <spam_user login="gamma" weight="85" />
                            <spam_user login="delta" weight="75" />
                        </spamlist>'''
RESPONSE_SPAM_USER_PDD = '<spamlist><spam_user login="Orexovo1991" pdd="yes" weight="100" /></spamlist>'


class FrodoTestCaseBase(TestCase):
    def setUp(self):
        self.frodo = Frodo()

        self.fake_frodo = FakeFrodo()
        self.fake_frodo.start()

        track_data = {
            'uid': '1',
            'captcha_generate_count': '2',
            'image_captcha_type': 'std',
            'voice_captcha_type': 'rus',
            'suggest_login_count': '3',
            'phone_confirmation_first_send_at': str(time.time()),
            'phone_confirmation_first_checked': str(time.time()),
            'sanitize_phone_changed_phone': '1',
            'sanitize_phone_error': '1',
            'phone_confirmation_sms_count': '2',
            'phone_confirmation_confirms_count': '3',
            'origin': 'origin',
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
            'phone_confirmation_last_checked': str(time.time()),
            'phone_confirmation_last_send_at': str(time.time()),
            'phone_confirmation_send_ip_limit_reached': '1',
            'phone_confirmation_send_count_limit_reached': '1',
            'phone_confirmation_confirms_count_limit_reached': '1',
            'sanitize_phone_count': '8',
            'sanitize_phone_first_call': '10',
            'sanitize_phone_last_call': '11',
            'suggest_login_first_call': '12',
            'suggest_login_last_call': '13',
            'login_validation_count': '10',
            'login_validation_first_call': '16',
            'login_validation_last_call': '17',
            'password_validation_count': '3',
            'password_validation_first_call': '18',
            'password_validation_last_call': '19',
            'captcha_checked_at': '21',
            'captcha_generated_at': '22',
            'captcha_check_count': '11',
            'created': str(time.time()),
            'page_loading_info': 'foobar',
        }
        # TODO: Тут тестируются ВСЕ поля трека, уезжающие во ФО? Возможно ли
        # специфицировать по типам трека
        track = mock_track(track_data=track_data)
        track._lists['suggested_logins'] = ['r2d2']
        self.track = track

    def tearDown(self):
        self.fake_frodo.stop()
        del self.fake_frodo

    def _set_response(self, method, response, status_code=200):
        self.fake_frodo.set_response_value(method, response, status_code)

    def _set_side_effect(self, method, side_effect):
        self.fake_frodo.set_response_side_effect(method, side_effect)

    def _get_requests(self):
        return self.fake_frodo.requests


@with_settings(
    FRODO_URL='http://localhost/',
    FRODO_RETRIES=3,
)
class FrodoServiceTestCase(FrodoTestCaseBase):

    def setUp(self):
        super(FrodoServiceTestCase, self).setUp()

        self.env = mock_env(
            cookies={'fuid01': 'fuid111', 'yandex_gid': 'test_gid', 'yandexuid': 'test_uid', 'my': 'YycCAAMA'},
            user_agent='ua',
            host='h',
            accept_language='ru',
        )

        self.expected_params = {
            'so_codes': 'utf8',
            'captchareq': '0',
            'fuid': 'fuid111',
            'captchacount': 2,
            'lcheck': 3,
            'passwd': '0.0.0.0.0.0.0.0',
            'passwdex': '0.0.0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'hintqid': 1,
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'yandexuid': 'test_uid',
            'v2_yandex_gid': 'test_gid',
            'valkey': '0000000000',
            'step1time': 2000,
            'step2time': 2000,
            'phonenumber': '79990004567',
            'v2_phonenumber_hash': get_phone_number_hash('+79991234567'),
            'uid': '1',
            'login': 'l',
            'iname': u'fnфн',
            'fname': u'lnлн',
            'email': 'em',
            'from': 'from',
            'useragent': 'ua',
            'host': 'h',
            'ip_from': '127.0.0.1',
            'ip_prox': '',
            'social_provider': 'sp',
            'lang': 'l',
            'xcountry': 'c',
            'action': 'a',
            'time': TimeNow(),
            'utime': TimeNow(as_milliseconds=True),
            'consumer': 'dev',
            'origin': 'origin',
            'is_suggested_login': '0',

            'v2_phone_confirmation_first_sms_send_at': TimeNow(),
            'v2_phone_confirmation_first_code_checked': TimeNow(),
            'v2_phone_validation_changes': '1',
            'v2_phone_validation_error': '1',
            'v2_phone_confirmation_sms_count': 2,
            'v2_phone_confirmation_confirms_count': 3,
            'v2_phone_bindings_count': '',

            'v2_phone_confirmation_last_sms_send_at': TimeNow(),
            'v2_phone_confirmation_last_code_checked': TimeNow(),
            'v2_phone_confirmation_send_ip_limit_reached': '1',
            'v2_phone_confirmation_send_count_limit_reached': '1',
            'v2_phone_confirmation_confirms_count_limit_reached': '1',

            'v2_language_sys': 'l_sys',
            'v2_locale': 'locale',
            'v2_geo_coarse': 'geo',
            'v2_hardware_id': 'h_id',
            'v2_os_id': 'os_id',
            'v2_application': 'app',
            'v2_cell_provider': 'cell',
            'v2_hardware_model': 'h_model',
            'v2_clid': 'clid',
            'v2_ip': '127.0.0.1',
            'v2_app_uuid': 'uuid',
            'v2_image_captcha_type': 'std',
            'v2_voice_captcha_type': 'rus',
            'v2_password_quality': 0,
            'v2_old_password_quality': 80,
            'v2_suggest_login_length': 1,

            'v2_sanitize_phone_count': 8,
            'v2_sanitize_phone_first_call': '10',
            'v2_sanitize_phone_last_call': '11',
            'v2_suggest_login_first_call': '12',
            'v2_suggest_login_last_call': '13',
            'v2_login_validation_count': 10,
            'v2_login_validation_first_call': '16',
            'v2_login_validation_last_call': '17',
            'v2_password_validation_count': 3,
            'v2_password_validation_first_call': '18',
            'v2_password_validation_last_call': '19',
            'v2_captcha_checked_at': '21',
            'v2_captcha_generated_at': '22',
            'v2_captcha_check_count': 11,
            'v2_track_created': TimeNow(),

            'v2_account_karma': '',
            'v2_account_country': 'ru',
            'v2_account_language': 'ru',
            'v2_account_timezone': 'Europe/Paris',
            'v2_accept_language': 'ru',
            'v2_is_ssl': '1',
            'v2_is_ssl_session_cookie_valid': '',

            'v2_has_cookie_l': '0',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '1',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',

            'v2_cookie_my_block_count': 1,
            'v2_cookie_my_language': 'en',
            'v2_cookie_l_login': '',
            'v2_cookie_l_uid': '',
            'v2_cookie_l_timestamp': '',

            'v2_session_age': '',
            'v2_session_ip': '',
            'v2_session_create_timestamp': '',

            'v2_page_loading_info': 'foobar',
        }

    def tearDown(self):
        super(FrodoServiceTestCase, self).tearDown()
        del self.env

    @raises(FrodoError)
    def test_check_parse_bad_response(self):
        list(self.frodo._parse_check_response(RESPONSE_BAD_XML))

    @raises(FrodoError)
    def test_check_parse_bad_cyrillic_response(self):
        list(self.frodo._parse_check_response(RESPONSE_BAD_CYRILLIC_XML))

    @raises(FrodoError)
    def test_check_parse_response_with_no_spamlist(self):
        list(self.frodo._parse_check_response(RESPONSE_NO_SPAMLIST_TAG))

    def test_check_parse_response(self):
        users = list(self.frodo._parse_check_response(RESPONSE_CHANGE_PASS))
        eq_(len(users), 1)
        user = users[0]
        eq_(user.login, 'zxfzxf2')
        eq_(user.karma, 85)
        eq_(user.is_pdd, False)
        eq_(user.spam, False)
        ok_(user.change_pass)

        users = list(self.frodo._parse_check_response(RESPONSE_EMPTY_LIST))
        eq_(len(users), 0)

        users = list(self.frodo._parse_check_response(RESPONSE_SPAM_USER))
        eq_(len(users), 4)
        for i, expected in enumerate([
            ('alpha', 85),
            ('beta', 85),
            ('gamma', 85),
            ('delta', 75),
        ]):
            user = users[i]
            eq_(user.login, expected[0])
            eq_(user.karma, expected[1])
            eq_(user.is_pdd, False)
            ok_(user.spam)
            eq_(user.change_pass, False)

        users = list(self.frodo._parse_check_response(RESPONSE_SPAM_USER_PDD))
        eq_(len(users), 1)
        user = users[0]
        eq_(user.login, 'Orexovo1991')
        eq_(user.karma, 100)
        eq_(user.is_pdd, True)
        ok_(user.spam)
        eq_(user.change_pass, False)

    def test_build_check_params(self):
        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=self.track))
        eq_(params, self.expected_params)

    def test_build_check_params_valkey_empty_useragent(self):
        self.env.user_agent = ''
        params = self.frodo._build_check_params(FrodoInfo.create(self.env, {}, track=self.track))
        eq_(params['valkey'], '0000000100')

    def test_build_check_params__custom_hint_question__hint_question_stats_for_frodo(self):
        params = self.frodo._build_check_params(
            FrodoInfo.create(
                self.env,
                {'hint_question_id': 99, 'hint_question': 'ABC'},
                track=self.track,
            ),
        )
        eq_(params['hintqid'], 99)
        eq_(params['hintq'], '3.3.0.0.0.0')
        eq_(params['hintqex'], '1.2.0.0.0')

    def test_build_check_params__predefined_hint_question__empty_hint_question_stats_for_frodo(self):
        params = self.frodo._build_check_params(
            FrodoInfo.create(
                self.env,
                {'hint_question_id': 1, 'hint_question': 'ABC'},
                track=self.track,
            ),
        )
        eq_(params['hintqid'], 1)
        eq_(params['hintq'], '0.0.0.0.0.0')
        eq_(params['hintqex'], '0.0.0.0.0.0')

    def test_build_check_params__mail_service__from_param_is_mail(self):
        params = self.frodo._build_check_params(
            FrodoInfo.create(
                self.env,
                {'service': 'mail'},
                track=self.track,
            ),
        )
        eq_(params['from'], 'mail')

    def test_build_check_params__fuid_special_case(self):
        self.env.cookies = {'fuid00': 'fd'}
        params = self.frodo._build_check_params(FrodoInfo.create(self.env, {}, track=self.track))
        eq_(params['fuid'], 'fd')

    def test_build_check_params__empty_track__empty_frodo_params(self):
        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=mock_track({})))
        eq_(params['v2_language_sys'], '')
        eq_(params['v2_locale'], '')
        eq_(params['v2_geo_coarse'], '')
        eq_(params['v2_hardware_id'], '')
        eq_(params['v2_os_id'], '')
        eq_(params['v2_application'], '')
        eq_(params['v2_cell_provider'], '')
        eq_(params['v2_hardware_model'], '')

    def test_check(self):
        self._set_response(u'check', RESPONSE_SPAM_USER_PDD)

        users = self.frodo.check(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=self.track))
        eq_(len(users), 1)

        requests = self._get_requests()
        eq_(len(requests), 1)

        time_param_names = {
            u'time',
            u'utime',
            u'v2_phone_confirmation_first_sms_send_at',
            u'v2_phone_confirmation_first_code_checked',
            u'v2_phone_confirmation_last_sms_send_at',
            u'v2_phone_confirmation_last_code_checked',
            u'v2_track_created',
        }
        expected_query = {}
        for param_name in self.expected_params:
            param_value = self.expected_params[param_name]
            if param_name not in time_param_names:
                # Не преобразовываем в строку время, т.к. из-за этого потеряется
                # логика сравнения объекта-времени.
                param_value = smart_text(param_value)

            expected_query[param_name] = param_value

        requests[0].assert_url_starts_with(u'http://localhost/check?')
        requests[0].assert_query_equals(expected_query)

    def test_confirm(self):
        self._set_response('confirm', '')

        params = {'u1': 85, 'u2': 75, 'u3': 100}
        response = self.frodo.confirm(params)

        ok_(response)
        requests = self._get_requests()
        eq_(len(requests), 1)

        requests[0].assert_properties_equal(
            url=u'http://localhost/loginrcpt?u1=85&u3=100&u2=75',
        )

    def test_test_frodo_login(self):
        self._set_response('check', '')

        fi = FrodoInfo(login='frodo-spam-123456')
        users = self.frodo.check(fi)
        eq_(len(users), 1)
        eq_(
            users,
            [User(
                login='frodo-spam-123456',
                karma=85,
                is_pdd=False,
                spam=True,
                change_pass=False,
            )],
        )

        fi = FrodoInfo(login='frodo-pdd-spam-123456')
        users = self.frodo.check(fi)
        eq_(len(users), 1)
        eq_(
            users,
            [User(
                login='frodo-pdd-spam-123456',
                karma=100,
                is_pdd=True,
                spam=True,
                change_pass=False,
            )],
        )

        fi = FrodoInfo(login='frodo-change-pass-123456')
        users = self.frodo.check(fi)
        eq_(len(users), 1)
        eq_(
            users,
            [User(
                login='frodo-change-pass-123456',
                karma=85,
                is_pdd=False,
                spam=False,
                change_pass=True,
            )],
        )
        requests = self._get_requests()
        eq_(len(requests), 0)

    def test_page_loading_info_from_several_params(self):
        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=mock_track({'check_css_load': '1', 'check_js_load': '1'})))
        eq_(params['v2_page_loading_info'], '{"checkcssload": 1, "checkjsload": 1}')

        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=mock_track({'check_css_load': '1'})))
        eq_(params['v2_page_loading_info'], '{"checkcssload": 1}')

        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=mock_track({'check_js_load': '1'})))
        eq_(params['v2_page_loading_info'], '{"checkjsload": 1}')

        params = self.frodo._build_check_params(FrodoInfo.create(self.env, DEFAULT_QUERY_PARAMS, track=mock_track({})))
        eq_(params['v2_page_loading_info'], '')


@with_settings(
    FRODO_URL='http://localhost/',
    FRODO_RETRIES=3,
)
class FrodoServiceErrorsRetriesTestCase(FrodoTestCaseBase):

    def test_bad_request(self):
        self._set_response(u'check', u'', 400)
        with assert_raises(FrodoError):
            self.frodo.check(FrodoInfo.create(mock_env(), {}))
        requests = self._get_requests()
        eq_(len(requests), 3)

    def test_bad_request_with_nonascii_char(self):
        self._set_response(u'check', b'\xa9', 400)
        with assert_raises(FrodoError):
            self.frodo.check(FrodoInfo.create(mock_env(), {}))
        requests = self._get_requests()
        eq_(len(requests), 3)

    def test_retries(self):
        self._set_side_effect(u'confirm', RequestError)
        with assert_raises(FrodoError):
            self.frodo.confirm({})
        requests = self._get_requests()
        eq_(len(requests), 3)
