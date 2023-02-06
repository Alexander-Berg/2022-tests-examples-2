# -*- coding: utf-8 -*-

from datetime import datetime
import json
import time

import mock
from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.test.mixins import AccountHistoryTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_CALL_SESSION_ID,
    TEST_CONFIRMATION_CODE2,
    TEST_CONSUMER,
    TEST_DOMAIN,
    TEST_EMAIL,
    TEST_FAKE_PHONE_NUMBER,
    TEST_FAKE_PHONE_NUMBER_DUMPED,
    TEST_FIRSTNAME,
    TEST_HOST,
    TEST_LOCAL_PHONE_NUMBER,
    TEST_LOCAL_PHONE_NUMBER_DUMPED,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
    TEST_OPERATION_ID,
    TEST_OPERATION_ID2,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_OTHER_EXIST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER_DIGITAL,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_NUMBER_DUMPED1,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_SMS_TEXT,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_USER_TICKET1,
)
from passport.backend.api.views.bundle.mixins.phone import (
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    KOLMOGOR_COUNTER_SESSIONS_CREATED,
)
from passport.backend.api.views.bundle.phone.helpers import format_code_by_3
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.counters import (
    calls_per_ip,
    calls_per_phone,
    sms_per_ip,
    sms_per_ip_for_app,
    sms_per_ip_for_consumer,
)
from passport.backend.core.counters.change_password_counter import get_per_phone_number_buckets
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.consts import TEST_PASSWORD_HASH1
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import settings_context
from passport.backend.core.test.time_utils.time_utils import (
    DEFAULT_DELTA,
    TimeNow,
)
from passport.backend.core.tracks.track_manager import create_track_id
from passport.backend.core.types.phone_number.phone_number import mask_for_statbox
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .statbox_mixin import StatboxTestMixin


FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES = 'ELEGANT_CANE_FAKE_SESSION_ID'

TEST_SESSION_ID = '1'

HEADERS = mock_headers(host=TEST_HOST, user_ip=TEST_USER_IP, user_agent=TEST_USER_AGENT)
HEADERS_WITH_SESSIONID = mock_headers(host=TEST_HOST, user_ip=TEST_USER_IP, user_agent=TEST_USER_AGENT, cookie='Session_id=%s' % TEST_SESSION_ID)

TEST_LOGIN = 'vasya'
TEST_OTHER_LOGIN = 'petya'

TEST_PDD_USER_UID = 1130000000000001
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)

PDD_ACCOUNT_KWARGS = dict(
    uid=TEST_PDD_USER_UID,
    login=TEST_PDD_LOGIN,
    crypt_password=TEST_PASSWORD_HASH1,
    aliases={
        'pdd': TEST_PDD_LOGIN,
    },
)
LITE_ACCOUNT_KWARGS = dict(
    uid=TEST_UID,
    login='user@mk.ru',
    crypt_password=TEST_PASSWORD_HASH1,
    aliases={
        'lite': 'user@mk.ru',
    },
)

SUPER_LITE_ACCOUNT_KWARGS = LITE_ACCOUNT_KWARGS.copy()
del SUPER_LITE_ACCOUNT_KWARGS['crypt_password']

SOCIAL_ACCOUNT_KWARGS = dict(
    uid=TEST_UID,
    login='uid-123',
    aliases={
        'social': 'uid-123',
    },
)
PHONISH_ACCOUNT_KWARGS = dict(
    uid=TEST_UID,
    login='phne-123',
    aliases={
        'phonish': 'phne-123',
    },
)
MAILISH_ACCOUNT_KWARGS = dict(
    uid=TEST_UID,
    login='user@gmail.com',
    aliases={
        'mailish': 'user@gmail.com',
    },
)

TEST_DATE1 = datetime(2000, 1, 2, 0, 0, 1)

TEST_TAXI_APPLICATION = 'ru.yandex.taxi'
TEST_OTHER_APPLICATION = 'ru.yadex.taxinot'
TEST_DEVICE_APPLICATION_WITH_VERSION = 'ru.yandex.taxi version with spaces'

TEST_TOKEN = 'token1'

TEST_SMS_ROUTE_GRANTS_GROUP = 'sms_routes'
TEST_SMS_VALID_ROUTE = 'custom'
TEST_SMS_VALID_GRANTS = [TEST_SMS_VALID_ROUTE]
TEST_SMS_INVALID_ROUTE = 'invalid_custom'
TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'

TEST_FAKE_CODE = '000000'


class BaseConfirmTestCase(BaseBundleTestViews, StatboxTestMixin, AccountHistoryTestMixin):

    has_uid = True
    step = None
    track_state = None
    url = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['*']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.not_existing_track_id = create_track_id()

        self.number_response = {u'number': TEST_PHONE_NUMBER_DUMPED}

        self.base_response = merge_dicts(
            self.number_response,
            {u'status': u'ok'},
        )
        self.additional_ok_response_params = {}
        self.base_headers = {}

        self.confirmation_code = '5' * settings.SMS_VALIDATION_CODE_LENGTH

        self._code_generator_faker = CodeGeneratorFaker()
        self._code_generator_faker.set_return_value(self.confirmation_code)
        self._code_generator_faker.start()
        self.setup_statbox_templates()
        self.setup_antifraud_score_response()

    def setup_antifraud_score_response(self, allow=True, tags=None):
        response = antifraud_score_response(
            action=ScoreAction.ALLOW if allow else ScoreAction.DENY,
            tags=tags,
        )
        self.env.antifraud_api.set_response_value('score', response)

    @property
    def sms_text(self):
        return TEST_SMS_TEXT

    @property
    def sms_text_template_params(self):
        return json.dumps({'code': self.confirmation_code}).encode('utf-8')

    def query_params(self):
        return {}   # pragma: no cover

    def tearDown(self):
        self._code_generator_faker.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self._code_generator_faker

    def setup_track_for_commit(
        self,
        exclude=None,
        uid=TEST_UID,
        _defaults=None,
        **kwargs
    ):
        base_track_params = {
            'phone_confirmation_phone_number': TEST_PHONE_NUMBER.e164,
            'phone_confirmation_phone_number_original': TEST_PHONE_NUMBER.original,
            'phone_confirmation_code': self.confirmation_code,
            'phone_confirmation_sms_count': '1',
            'phone_confirmation_first_send_at': time.time(),
            'phone_confirmation_last_send_at': time.time(),
            'phone_confirmation_method': 'by_sms',
            'country': 'ru',
            'state': self.track_state,
        }
        if _defaults:
            base_track_params.update(_defaults)

        if self.has_uid:
            base_track_params.update({'uid': str(uid)})

        if exclude is not None:
            for key in exclude:
                del base_track_params[key]

        track_params = merge_dicts(base_track_params, kwargs)

        with self.track_transaction() as track:
            track._data.update(track_params)  # FIXME: плохо, но parse не умеет работать со счётчиками

    def make_request(self, data=None, headers=None):
        if data is None:
            data = self.query_params()
        return self.env.client.post(
            self.url,
            data=data,
            headers=self.build_headers(headers),
        )

    def build_headers(self, headers=None):
        if headers is None:
            headers = HEADERS
        return merge_dicts(self.base_headers, headers)


class BaseConfirmSubmitterTestCase(BaseConfirmTestCase):

    step = 'submit'

    def setUp(self):
        super(BaseConfirmSubmitterTestCase, self).setUp()
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        self.base_submitter_response = merge_dicts(
            self.base_response,
            {'track_id': self.track_id},
        )
        self.base_send_code_response = merge_dicts(
            self.base_submitter_response,
            {
                'deny_resend_until': TimeNow(
                    offset=settings.SMS_VALIDATION_RESEND_TIMEOUT,
                    delta=int(DEFAULT_DELTA * 1.5),  # тестов много, они не укладываются в 30 секунд
                ),
                'code_length': settings.SMS_VALIDATION_CODE_LENGTH,
                'global_sms_id': '1',
            },
        )
        self.base_error_kwargs = merge_dicts(
            self.number_response,
            {'track_id': self.track_id},
        )
        self.env.kolmogor.set_response_value('inc', 'OK')
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])

        self.region_mock = mock.Mock(return_value=mock.Mock(
            AS_list=['AS1'],
            country={'id': 84},
            city={'id': 102630},
        ))
        self.region_patch = mock.patch(
            'passport.backend.api.common.ip.Region',
            self.region_mock,
        )
        self.region_patch.start()

    def tearDown(self):
        self.region_patch.stop()
        super(BaseConfirmSubmitterTestCase, self).tearDown()

    def check_ok_track(self, track, used_gate_ids=None, phone_number=TEST_PHONE_NUMBER, return_masked_number=None):
        eq_(track.phone_confirmation_phone_number, phone_number.e164)
        eq_(track.phone_confirmation_phone_number_original, phone_number.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        eq_(track.return_masked_number, return_masked_number)

        ok_(not track.phone_call_session_id)
        eq_(track.state, self.track_state)

        eq_(track.display_language, 'ru')

        ok_(track.phone_confirmation_confirms_count.get() is None)

        # проверяем counter СМС по ip адресу
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        eq_(counter.get(TEST_USER_IP), 1)
        eq_(track.phone_confirmation_used_gate_ids, used_gate_ids)

    def check_ok_track_by_call(self, track, call_session_id=TEST_CALL_SESSION_ID, code=None, confirm_method='by_call', phone_number=TEST_PHONE_NUMBER):
        code = code or str(format_code_by_3(self.confirmation_code))
        eq_(track.phone_confirmation_phone_number, phone_number.e164)
        eq_(track.phone_confirmation_phone_number_original, phone_number.original)
        eq_(track.phone_confirmation_code, code)
        eq_(track.phone_confirmation_first_called_at, TimeNow())
        eq_(track.phone_confirmation_last_called_at, TimeNow())
        eq_(track.phone_confirmation_calls_count.get(), 1)
        eq_(track.phone_call_session_id, call_session_id)
        eq_(track.phone_confirmation_method, confirm_method)
        ok_(not track.phone_confirmation_sms_count.get())
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_calls_count_limit_reached)
        ok_(not track.phone_confirmation_calls_ip_limit_reached)
        eq_(track.state, self.track_state)

        eq_(track.display_language, 'ru')

        ok_(track.phone_confirmation_confirms_count.get() is None)

    def check_ok_track_by_flash_call(self, *args, **kwargs):
        self.check_ok_track_by_call(*args, confirm_method='by_flash_call', **kwargs)

    def check_ok_counters_by_call(self, phone_number=TEST_PHONE_NUMBER):
        counter = calls_per_ip.get_counter(TEST_USER_IP)
        eq_(counter.get(TEST_USER_IP), 1)

        phone_counter = calls_per_phone.get_counter()
        eq_(phone_counter.get(phone_number.digital), 1)

    def assert_statbox_ok_with_call(
        self, action='call_with_code',
        call_session_id=TEST_CALL_SESSION_ID,
        phone_number=TEST_PHONE_NUMBER,
        with_antifraud_score=False,
    ):
        expected_entries = []
        if with_antifraud_score:
            expected_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=phone_number.masked_format_for_statbox,
                ),
            )
        expected_entries.extend([
            self.env.statbox.entry(
                'call_with_code',
                action=action,
                call_session_id=call_session_id,
                number=phone_number.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                number=phone_number.masked_format_for_statbox,
            ),
        ])
        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_ok_with_flash_call(
        self,
        action='flash_call',
        call_session_id=TEST_CALL_SESSION_ID,
        phone_number=TEST_PHONE_NUMBER,
        with_antifraud_score=False,
    ):
        expected_entries = []
        if with_antifraud_score:
            expected_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=phone_number.masked_format_for_statbox,
                ),
            )
        expected_entries.extend([
            self.env.statbox.entry(
                'flash_call',
                action=action,
                call_session_id=call_session_id,
                number=phone_number.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                number=phone_number.masked_format_for_statbox,
            ),
        ])
        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_no_send_entries(
        self,
        with_antifraud_score=False,
        phone_number=TEST_PHONE_NUMBER,
        **kwargs
    ):
        expected_entries = []
        if with_antifraud_score:
            expected_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=phone_number.masked_format_for_statbox,
                    **kwargs
                ),
            )
        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_antifraud_deny_ok(
        self,
        phone_number=TEST_PHONE_NUMBER,
        mask_denial=False,
        **kwargs
    ):
        self.env.statbox.assert_contains(
            self.env.statbox.entry(
                'antifraud_score_deny',
                number=phone_number.masked_format_for_statbox,
                mask_denial='1' if mask_denial else '0',
                **kwargs
            ),
        )

    def assert_statbox_antifraud_captcha_ok(self, antifraud_tags, phone_number=TEST_PHONE_NUMBER):
        self.env.statbox.assert_contains(
            self.env.statbox.entry(
                'antifraud_score_captcha',
                antifraud_tags=antifraud_tags,
                number=phone_number.masked_format_for_statbox,
            ),
        )

    def assert_statbox_ok(
        self,
        phone_number=TEST_PHONE_NUMBER,
        with_antifraud_score=False,
        with_check_cookies=False,
        **kwargs
    ):
        number = mask_for_statbox(phone_number.e164)
        expected_entries = []
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies'))
        if with_antifraud_score or getattr(self, 'with_antifraud_score', False):
            expected_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=phone_number.masked_format_for_statbox,
                    **kwargs
                ),
            )
        expected_entries.extend([
            self.env.statbox.entry('send_code', number=number, **kwargs),
            self.env.statbox.entry('success', number=number, **kwargs),
        ])
        self.env.statbox.assert_has_written(expected_entries)

    def assert_kolmogor_called(self, calls, with_inc=True, keys='sessions_created'):
        eq_(len(self.env.kolmogor.requests), calls)
        if with_inc:
            self.env.kolmogor.requests[-1].assert_properties_equal(
                method='POST',
                url='http://localhost/inc',
                post_args={'space': TEST_KOLMOGOR_KEYSPACE_COUNTERS, 'keys': keys},
            )

    def assert_antifraud_score_called(
        self,
        confirm_method='by_sms',
        scenario='register',
        **kwargs
    ):
        requests = self.env.antifraud_api.get_requests_by_method('score')
        self.assertEqual(len(requests), 1)
        request_data = json.loads(requests[0].post_args)

        features = PhoneAntifraudFeatures.default(
            sub_channel=TEST_CONSUMER,
            user_phone_number=TEST_PHONE_NUMBER,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.phone_confirmation_method = confirm_method
        features.scenario = scenario
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = self.url.split('?')[0]
        features.phone_confirmation_language = 'ru'
        features.add_headers_features(self.build_headers())
        features.add_dict_features(kwargs)
        features.add_track_features(self.track_manager.read(self.track_id))
        assert request_data == features.as_score_dict()

    def assert_antifraud_score_not_called(self):
        self.assertFalse(self.env.antifraud_api.requests)


class ConfirmSubmitterSpecificTestMixin(object):
    def test_specific_grant(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['base', 'bind_secure']}))

        rv = self.make_request()

        eq_(rv.status_code, 403, rv.data)
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['access.denied'])
        self.env.statbox.assert_has_written([])

    def test_specific_header(self):
        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
            mock_headers(
                user_ip=TEST_USER_IP,
                host=None,
                cookie='Session_id=' + TEST_SESSION_ID,
                user_agent=TEST_USER_AGENT,
            ),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'host.empty'], u'track_id': self.track_id},
            ),
        )

        self.env.statbox.assert_has_written([])


class ConfirmSubmitterLocalPhonenumberMixin(object):
    with_check_cookies = False

    def test_ok_with_local_phonenumber(self):
        rv = self.make_request(
            self.query_params(number=TEST_LOCAL_PHONE_NUMBER.original, country='ru'),
        )
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data).get(u'status'), u'ok')
        eq_(
            json.loads(rv.data).get(u'number'),
            TEST_LOCAL_PHONE_NUMBER_DUMPED,
        )

        self.assert_statbox_ok(
            with_antifraud_score=getattr(self, 'with_antifraud_score', False),
            with_check_cookies=self.with_check_cookies
        )


class ConfirmSubmitterAccountTestMixin(object):
    """
    Проверки доступности аккаунта
    """

    def test_account_not_found__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.not_found']},
            ),
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])


class ConfirmSubmitterAccountNoNumberTestMixin(object):
    """
    Проверки доступности аккаунта без телефона в ответе
    """

    def test_account_not_found__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()

        response = merge_dicts(
            self.base_submitter_response,
            {u'status': u'error', u'errors': [u'account.not_found']},
        )
        del response[u'number']

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            response,
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])


class ConfirmSubmitterSendSmsTestMixin(object):
    with_check_cookies = False

    def setup_track(self, track_id):
        """
        Функция должна переопределяться в потомках
        Подготавливает данные, необходимые для успешной проверки трека ручкой
        """

    def test_error_send_limit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for _ in range(3):
                track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        eq_(len(self.env.yasms.requests), 0)

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'sms_limit.exceeded'],
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_send_count_limit_reached)
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(
                self.env.statbox.entry('antifraud_score_allow'),
            )
        expected_statbox_entries.append(
            self.env.statbox.entry(
                'send_code_error',
                error='sms_limit.exceeded',
            ),
        )
        self.env.statbox.assert_has_written(expected_statbox_entries)
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='sms_limit.exceeded',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='sms_limit.exceeded',
            ),
        ])

    def test_error_send_limit_by_ip(self):
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        # Установим счетчик смсок на ip в limit - 1
        for _ in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)
        rv = self.make_request()

        eq_(len(self.env.yasms.requests), 1)

        # Одна отсылка ок
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )
        eq_(counter.get(TEST_USER_IP), counter.limit)

        other_track_id = self.track_manager.create('register', 'dev').track_id
        self.setup_track(other_track_id)

        # еще одна отсылка на другой трек - не ок
        rv = self.make_request(
            self.query_params(track_id=other_track_id),
        )

        eq_(len(self.env.yasms.requests), 1)

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'sms_limit.exceeded'],
                    u'track_id': other_track_id,
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )
        track = self.track_manager.read(other_track_id)
        ok_(track.phone_confirmation_send_ip_limit_reached)

        # Повторная отсылка с треком, в котором установлены флажки превышения лимитов - не ок
        rv = self.make_request(
            self.query_params(track_id=other_track_id),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'sms_limit.exceeded'],
                    u'track_id': other_track_id,
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )

    def test_track_state_flushed_on_phone_change_with_error(self):
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.reset()
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_last_send_at = time.time() - 100
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE2

        rv = self.make_request(
            self.query_params(),
        )

        eq_(len(self.env.yasms.requests), 0)

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'sms_limit.exceeded'],
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_send_ip_limit_reached)
        assert_is_none(track.phone_confirmation_code)
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_sms_count.get(default=0), 0)

    def test_error_resend_timeout(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.reset()
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_last_send_at = time.time() + 3600
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        eq_(len(self.env.yasms.requests), 0)

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'sms_limit.exceeded'],
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(self.env.statbox.entry('antifraud_score_allow'))
        expected_statbox_entries.append(
            self.env.statbox.entry(
                'send_code_error',
                error='sms_limit.exceeded',
            ),
        )
        self.env.statbox.assert_has_written(expected_statbox_entries)

    def test_resend_without_last_sms_time__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.reset()
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 2)
        ok_(track.phone_confirmation_is_confirmed is None)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(self.env.statbox.entry('antifraud_score_allow'))
        expected_statbox_entries.extend([
            self.env.statbox.entry(
                'send_code',
                sms_count='2',
            ),
            self.env.statbox.entry('success'),
        ])
        self.env.statbox.assert_has_written(expected_statbox_entries)

    def test_resend_sms_same_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_code = self.confirmation_code
            track.phone_confirmation_first_send_at = 21
            track.phone_confirmation_last_send_at = time.time() - 20  # < settings.SMS_VALIDATION_RESEND_TIMEOUT

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )

        eq_(self._code_generator_faker.call_count, 0)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_first_send_at, '21')
        eq_(track.phone_confirmation_sms_count.get(), 2)
        ok_(track.phone_confirmation_is_confirmed is None)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(self.env.statbox.entry('antifraud_score_allow'))
        expected_statbox_entries.extend([
            self.env.statbox.entry(
                'send_code',
                sms_count='2',
            ),
            self.env.statbox.entry('success'),
        ])
        self.env.statbox.assert_has_written(expected_statbox_entries)

    def test_resend_sms_new_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.reset()
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = '+79031234567'
            track.phone_confirmation_phone_number_original = '89031234567'
            track.phone_confirmation_sms = 'test 123'
            track.phone_confirmation_code = '123'
            track.phone_confirmation_first_send_at = 21
            for _ in range(2):
                track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_last_send_at = time.time() - 20

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)

        ok_(not track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_first_send_at, '21')
        eq_(track.phone_confirmation_sms_count.get(), 1)
        eq_(track.phone_confirmation_confirms_count.get(), None)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        self.assert_statbox_ok(
            with_antifraud_score=getattr(self, 'with_antifraud_score', False),
            with_check_cookies=self.with_check_cookies,
        )

    def test_send_sms_to_taxi_route(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = TEST_TAXI_APPLICATION

        rv = self.make_request()

        eq_(rv.status_code, 200)
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'route': 'taxi',
        })

    def test_send_sms_to_taxi_route__application_with_version(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = TEST_DEVICE_APPLICATION_WITH_VERSION

        rv = self.make_request()

        eq_(rv.status_code, 200)
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'route': 'taxi',
        })

    def test_send_sms_to_validate_route__different_application(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = TEST_OTHER_APPLICATION

        rv = self.make_request()

        eq_(rv.status_code, 200)
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'route': 'validate',
        })

    def test_send_sms_to_validate_route__by_experiment(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = TEST_TAXI_APPLICATION

        with settings_context(
            APP_ID_SPECIFIC_ROUTE_DENOMINATOR=0,
            APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
        ):
            rv = self.make_request()

        eq_(rv.status_code, 200)
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'route': 'validate',
        })

    def test_send_sms_with_yasms_errors(self):
        errors = [
            (yasms_exceptions.YaSmsError('error message'),
             {u'status': 'error', u'errors': [u'exception.unhandled']},
             'sms.isnt_sent'),
            (yasms_exceptions.YaSmsAccessDenied('error message'),
             {u'status': 'error', u'errors': [u'backend.yasms_access_denied']},
             'sms.isnt_sent'),
            (yasms_exceptions.YaSmsLimitExceeded('error message'),
             {u'status': u'error', u'errors': [u'sms_limit.exceeded']},
             'sms_limit.exceeded'),
            (yasms_exceptions.YaSmsPermanentBlock('error message'),
             {u'status': u'error', u'errors': [u'phone.blocked']},
             'phone.blocked'),
            (yasms_exceptions.YaSmsTemporaryBlock('error message'),
             {u'status': u'error', u'errors': [u'phone.blocked']},
             'phone.blocked'),
            (yasms_exceptions.YaSmsUidLimitExceeded('error message'),
             {u'status': u'error', u'errors': [u'sms_limit.exceeded']},
             'sms_limit.exceeded'),
            (yasms_exceptions.YaSmsSecureNumberNotAllowed('error message'),
             {u'status': u'error', u'errors': [u'exception.unhandled']},
             'sms.isnt_sent'),
            (yasms_exceptions.YaSmsSecureNumberExists('error message'),
             {u'status': u'error', u'errors': [u'exception.unhandled']},
             'sms.isnt_sent'),
            (yasms_exceptions.YaSmsPhoneNumberValueError('error message'),
             {u'status': u'error', u'errors': [u'number.invalid']},
             'sms.isnt_sent'),
            (yasms_exceptions.YaSmsDeliveryError('error message'),
             {u'status': u'error', u'errors': [u'backend.yasms_failed']},
             'sms.isnt_sent'),
        ]

        statbox_result = []
        for error, error_response, statbox_error in errors:
            self.env.yasms.set_response_side_effect('send_sms', error)

            rv = self.make_request()

            eq_(rv.status_code, 200)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_submitter_response,
                    error_response,
                    {
                        'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                    },
                ),
            )
            if self.with_check_cookies:
                statbox_result.append(self.env.statbox.entry('check_cookies'))
            if getattr(self, 'with_antifraud_score', False):
                statbox_result.append(
                    self.env.statbox.entry(
                        'antifraud_score_allow',
                    ),
                )
            statbox_result.append(
                self.env.statbox.entry(
                    'send_code_error',
                    error=statbox_error,
                ),
            )

        self.env.statbox.assert_has_written(statbox_result)

        eq_(
            len(self.env.yasms.requests),
            len(errors),
        )

        track = self.track_manager.read(self.track_id)

        ok_(not track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        ok_(track.phone_confirmation_first_send_at is None)
        ok_(track.phone_confirmation_last_send_at is None)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        ok_(track.phone_confirmation_sms_count.get() is None)

        # проверяем counter СМС по ip адресу
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        eq_(counter.get(TEST_USER_IP), 0)

    def test_already_confirmed_phone_with_same_phone(self):
        self.setup_track_for_commit(
            exclude=['country'],
            is_successful_phone_passed=1,
            phone_confirmation_is_confirmed=1,
            phone_confirmation_sms_count=1,
            phone_confirmation_confirms_count=1,
        )

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {
                    u'status': u'error',
                    u'errors': [u'phone.confirmed'],
                    u'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
                },
            ),
        )

        eq_(len(self.env.yasms.requests), 0)

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(track.is_successful_phone_passed)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_registration_sms_sent_limit_not_reached__ok(self):
        track = self.track_manager.create('register', 'dev')
        # Трек используется для регистрации
        self.setup_track(track.track_id)

        rv = self.make_request(self.query_params(track_id=track.track_id))

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'ok')
        # В statbox нет сообщения об ошибке
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

        eq_(sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).get(TEST_USER_IP), 1)

    def test_sms_send_ip_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_ip_limit_reached = True

        rv = self.make_request()

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['sms_limit.exceeded'])

        # В statbox нет сообщений об ошибке
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_sms_send_count_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = True

        rv = self.make_request()

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['sms_limit.exceeded'])

        # В statbox нет сообщений об ошибке
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_registration_sms_sent_by_ip_limit_reached__error(self):
        # Счетчик перешагнул лимит
        counter = sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP)
        for _ in range(counter.limit + 1):
            counter.incr(TEST_USER_IP)

        track = self.track_manager.create('register', 'dev')
        self.setup_track(track.track_id)

        # Запрос с превышением счетчика - ошибка
        rv = self.make_request(self.query_params(track_id=track.track_id))

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['sms_limit.exceeded'])

        # В трек записали стоп-флаг
        track = self.track_manager.read(track.track_id)
        ok_(track.phone_confirmation_send_ip_limit_reached)
        # Записали событие в statbox как ошибку
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    track_id=track.track_id,
                ),
            )
        expected_statbox_entries.append(
            self.env.statbox.entry(
                'submit_phone_confirmation_limit_exceeded',
                counter_current_value=str(counter.get(TEST_USER_IP)),
                counter_limit_value=str(counter.limit),
                track_id=track.track_id,
            ),
        )
        self.env.statbox.assert_has_written(expected_statbox_entries)
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='sms_limit.exceeded',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='sms_limit.exceeded',
            ),
        ])

    def test_registration_sms_sent_by_ip_limit_reached_but_whitelisted(self):
        counter = sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP)
        for _ in range(counter.limit + 1):
            counter.incr(TEST_USER_IP)

        track = self.track_manager.create('register', 'dev')
        self.setup_track(track.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = TEST_TAXI_APPLICATION

        with settings_context(
            YANGO_APP_IDS=(TEST_TAXI_APPLICATION,),
            TRUSTED_YANGO_PHONE_CODES=(TEST_PHONE_NUMBER.e164[:2],)
        ):
            rv = self.make_request(self.query_params(track_id=track.track_id))

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'ok')
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))
        eq_(sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).get(TEST_USER_IP), counter.limit + 2)

    def test_registration_sms_sent_by_ip_limit_reached_but_limit_by_consumer_and_ip_not_exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, 10)},
                REGISTRATION_SMS_SENT_PER_IP_LIMIT_COUNTER=(24, 3600, 1),
            )
        ):
            sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).incr(TEST_USER_IP)
            sms_per_ip_for_consumer.get_counter('dev').incr(TEST_USER_IP)

            track = self.track_manager.create('register', 'dev')
            self.setup_track(track.track_id)

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'ok')

            eq_(sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).get(TEST_USER_IP), 1)
            eq_(sms_per_ip_for_consumer.get_counter('dev').get(TEST_USER_IP), 2)

    def test_registration_sms_sent_by_ip_limit_reached_but_limit_by_app_and_ip_not_exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_app:ru.yandex.taxi': (24, 3600, 10)},
                REGISTRATION_SMS_SENT_PER_IP_LIMIT_COUNTER=(24, 3600, 1),
            )
        ):
            sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).incr(TEST_USER_IP)
            sms_per_ip_for_app.get_counter('ru.yandex.taxi').incr(TEST_USER_IP)

            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.device_application = 'ru.yandex.taxi 7.61'

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'ok')

            eq_(sms_per_ip.get_registration_sms_sent_counter(TEST_USER_IP).get(TEST_USER_IP), 1)
            eq_(sms_per_ip_for_app.get_counter('ru.yandex.taxi').get(TEST_USER_IP), 2)

    def test_change_password_per_phone_counter_reached__ok(self):
        """
        Проверим, что если значение счётчика "Сколько раз за сутки привязывался
        номер" ещё не достигло лимита, то ручка делает полезную работу.
        """
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit - 1):
            counter.incr(TEST_PHONE_NUMBER.e164)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = True

        rv = self.make_request()

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'ok')
        # В statbox нет сообщения об ошибке
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))
        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), counter.limit - 1)

    def test_change_password_disable_phone_experiment(self):
        with settings_context(
            DISABLE_CHANGE_PASSWORD_PHONE_EXPERIMENT=True,
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
        ):
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.is_password_change = True

            rv = self.make_request()

            eq_(rv.status_code, 200, [rv.status_code, rv.data])
            rv = json.loads(rv.data)
            eq_(rv['status'], 'error')
            # FIXME: нужен другой код ошибки
            eq_(rv['errors'], ['sms_limit.exceeded'])

    def test_confirmation_sms_limit_by_ip_whitelisted(self):
        with settings_context(
            YANGO_APP_IDS=(TEST_TAXI_APPLICATION,),
            TRUSTED_YANGO_PHONE_CODES=(TEST_PHONE_NUMBER.e164[:2],),
            **mock_counters(PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 1))
        ):
            sms_per_ip.get_counter(TEST_USER_IP).incr(TEST_USER_IP)

            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.device_application = TEST_TAXI_APPLICATION

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'ok')

            eq_(sms_per_ip.get_counter(TEST_USER_IP).get(TEST_USER_IP), 2)

    def test_confirmation_sms_limit_by_consumer_and_ip__not_exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, 10)},
                PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
            )
        ):
            for _ in range(5):
                sms_per_ip.get_counter(TEST_USER_IP).incr(TEST_USER_IP)

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'ok')

            eq_(sms_per_ip.get_counter(TEST_USER_IP).get(TEST_USER_IP), 5)
            eq_(sms_per_ip_for_consumer.get_counter('dev').get(TEST_USER_IP), 1)

    def test_confirmation_sms_limit_by_consumer_and_ip__exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, 5)},
                PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 10),
            )
        ):
            for _ in range(5):
                sms_per_ip.get_counter(TEST_USER_IP).incr(TEST_USER_IP)
                sms_per_ip_for_consumer.get_counter('dev').incr(TEST_USER_IP)

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'error')
            eq_(rv['errors'], ['sms_limit.exceeded'])

            eq_(sms_per_ip.get_counter(TEST_USER_IP).get(TEST_USER_IP), 5)
            eq_(sms_per_ip_for_consumer.get_counter('dev').get(TEST_USER_IP), 5)

    def test_confirmation_sms_limit_by_app_and_ip__not_exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_app:ru.yandex.taxi': (24, 3600, 10)},
                PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
            )
        ):
            for _ in range(5):
                sms_per_ip.get_counter(TEST_USER_IP).incr(TEST_USER_IP)

            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.device_application = 'ru.yandex.taxi 7.61'

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'ok')

            eq_(sms_per_ip.get_counter(TEST_USER_IP).get(TEST_USER_IP), 5)
            eq_(sms_per_ip_for_app.get_counter('ru.yandex.taxi').get(TEST_USER_IP), 1)

    def test_confirmation_sms_limit_by_app_and_ip__exceeded(self):
        with settings_context(
            inherit_if_set=[
                'ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT',
                'ANDROID_PACKAGE_PREFIXES_WHITELIST',
                'ANDROID_PACKAGE_PREFIX_TO_KEY',
            ],
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_app:ru.yandex.taxi': (24, 3600, 5)},
                PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 10),
            )
        ):
            for _ in range(5):
                sms_per_ip.get_counter(TEST_USER_IP).incr(TEST_USER_IP)
                sms_per_ip_for_app.get_counter('ru.yandex.taxi').incr(TEST_USER_IP)

            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.device_application = 'ru.yandex.taxi 7.61'

            rv = self.make_request()

            rv = json.loads(rv.data)
            eq_(rv['status'], 'error')
            eq_(rv['errors'], ['sms_limit.exceeded'])

            eq_(sms_per_ip.get_counter(TEST_USER_IP).get(TEST_USER_IP), 5)
            eq_(sms_per_ip_for_app.get_counter('ru.yandex.taxi').get(TEST_USER_IP), 5)

    def test_send_sms_to_valid_route(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'phone_bundle': ['*'],
                    TEST_SMS_ROUTE_GRANTS_GROUP: TEST_SMS_VALID_GRANTS,
                },
            ),
        )
        rv = self.make_request(
            self.query_params(
                route=TEST_SMS_VALID_ROUTE,
                code='1234',
            ),
        )
        eq_(rv.status_code, 200)
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'route': TEST_SMS_VALID_ROUTE,
        })

    def test_send_sms_to_invalid_route(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'phone_bundle': ['*'],
                    TEST_SMS_ROUTE_GRANTS_GROUP: TEST_SMS_VALID_GRANTS,
                },
            ),
        )
        rv = self.make_request(
            self.query_params(
                route=TEST_SMS_INVALID_ROUTE,
                code='1234',
            ),
        )
        self.assert_error_response(
            rv,
            status_code=403,
            error_codes=['access.denied'],
        )


class ConfirmSubmitterChangePasswordNewSecureNumberTestMixin(object):
    """
    Валидация по sms в рамках смены пароля:
    - с привязкой нового защищенного телефонного номера
    - c заменой утраченного  защищенного телефонного через карантин
    """
    with_check_cookies = False

    def test_change_password_per_phone_counter_reached__error(self):
        """
        На входе трек от смены пароля с требованием валидации по sms.
        Защищенного номера нет.

        Проверим, что если значение счётчика "Сколько раз за сутки привязывался
        номер" достигло лимита, то ручка возвращает ошибку.
        """
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.e164)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = True

        # Запрос с превышением счетчика - ошибка
        rv = self.make_request()
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['phone.compromised'])

        # Записали событие в statbox как ошибку
        expected_statbox_entries = []
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
                ),
            )
        expected_statbox_entries.append(
            self.env.statbox.entry(
                'phone_compromised',
                counter_current_value=str(counter.get(TEST_PHONE_NUMBER.e164)),
                counter_limit_value=str(counter.limit),
            ),
        )
        eq_(counter.get(TEST_PHONE_NUMBER.e164), counter.limit)

    def test_change_password_per_phone_counter_reached_replace_phone__error(self):
        """
        На входе трек от смены пароля с требованием валидации по sms.
        Защищенный номера есть. Пробуем заменить его через карантин.

        Проверим, что если значение счётчика "Сколько раз за сутки привязывался
        номер" достигло лимита, то ручка возвращает ошибку.
        """
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.e164)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_OTHER_EXIST_PHONE_NUMBER.e164

        # Запрос с превышением счетчика - ошибка
        rv = self.make_request()
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['phone.compromised'])

        # Записали событие в statbox как ошибку
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=TEST_PHONE_NUMBER.masked_format_for_statbox,
                ),
            )
        expected_statbox_entries.append(
            self.env.statbox.entry(
                'phone_compromised',
                counter_current_value=str(counter.get(TEST_PHONE_NUMBER.e164)),
                counter_limit_value=str(counter.limit),
            ),
        )
        self.env.statbox.assert_has_written(expected_statbox_entries)
        eq_(counter.get(TEST_PHONE_NUMBER.e164), counter.limit)


class ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin(object):
    with_check_cookies = False

    def test_already_confirmed_phone_with_new_phone(self):
        self.setup_track_for_commit(
            exclude=['country'],
            is_successful_phone_passed=1,
            phone_confirmation_is_confirmed=1,
            phone_confirmation_sms_count=2,
            phone_confirmation_confirms_count=2,
        )

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    u'number': {
                        u'international': u'+7 916 123-45-67',
                        u'e164': u'+79161234567',
                        u'original': '+79161234567',

                        u'masked_international': u'+7 916 ***-**-67',
                        u'masked_original': u'+7916*****67',
                        u'masked_e164': u'+7916*****67',
                    },
                },
                self.additional_ok_response_params,
            ),
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'text': self.sms_text,
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, TEST_NOT_EXIST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_NOT_EXIST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)
        eq_(track.phone_confirmation_confirms_count.get(), None)
        ok_(not track.is_successful_phone_passed)
        expected_statbox_entries = []
        if self.with_check_cookies:
            expected_statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if getattr(self, 'with_antifraud_score', False):
            expected_statbox_entries.append(
                self.env.statbox.entry(
                    'antifraud_score_allow',
                    number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
                ),
            )
        expected_statbox_entries.extend([
            self.env.statbox.entry(
                'send_code',
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])
        self.env.statbox.assert_has_written(expected_statbox_entries)


class BaseConfirmCommitterTestCase(BaseConfirmTestCase):

    step = 'commit'

    def setUp(self):
        super(BaseConfirmCommitterTestCase, self).setUp()
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            blackbox_userinfo_mock(found_by_login=False, subject_account={}),
        )


class ConfirmCommitterTestMixin(object):
    def test_with_empty_track(self):
        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'track.invalid_state']},
        )

        eq_(self.env.blackbox._mock.request.call_count, 0)
        eq_(len(self.env.yasms.requests), 0)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 0)
        self.env.statbox.assert_has_written([])

    def test_already_successful_complete_track(self):
        self.setup_track_for_commit()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_successful_phone_passed = True

        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)

        eq_(len(self.env.yasms.requests), 0)


class ConfirmCommitterLocalPhonenumberTestMixin(object):
    def test_ok_with_local_phonenumber(self):
        self.setup_track_for_commit(
            phone_confirmation_phone_number=TEST_LOCAL_PHONE_NUMBER.e164,
            phone_confirmation_phone_number_original=TEST_LOCAL_PHONE_NUMBER.original,
        )

        rv = self.make_request(
            self.query_params(number=TEST_LOCAL_PHONE_NUMBER.original, country='RU'),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data).get(u'status'), u'ok')
        eq_(
            json.loads(rv.data).get(u'number'),
            TEST_LOCAL_PHONE_NUMBER_DUMPED,
        )


class ConfirmCommitterSentCodeTestMixin(object):
    with_check_cookies = False

    def test_bad_code(self):
        self.setup_track_for_commit()

        rv = self.make_request(
            self.query_params(code='1234'),
        )
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'code.invalid']},
            ),
        )

        eq_(len(self.env.yasms.requests), 0)

        track = self.track_manager.read(self.track_id)

        ok_(not track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('code_invalid'))
        self.env.statbox.assert_has_written(entries)

    def test_bad_code_with_already_confirmed_phone(self):
        self.setup_track_for_commit(
            phone_confirmation_is_confirmed='1',
            phone_confirmation_confirms_count='1',
        )

        rv = self.make_request(
            self.query_params(code='1234'),
        )
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'code.invalid']},
            ),
        )

        eq_(len(self.env.yasms.requests), 0)

        track = self.track_manager.read(self.track_id)

        ok_(not track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 2)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('code_invalid'))
        self.env.statbox.assert_has_written(entries)

    def test_error_not_send(self):
        self.setup_track_for_commit(exclude=['phone_confirmation_sms_count'])

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'sms.not_sent']},
            ),
        )

        eq_(len(self.env.yasms.requests), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_error_confirms_limit(self):
        self.setup_track_for_commit(phone_confirmation_confirms_count='5')

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'confirmations_limit.exceeded']},
            ),
        )

        eq_(len(self.env.yasms.requests), 0)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_confirms_count_limit_reached)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'enter_code_error',
                error='confirmations_limit.exceeded',
            ),
        )

        self.env.statbox.assert_has_written(entries)


def blackbox_userinfo_mock(found_by_login=True, not_found=False, subject_account=None):
    def blackbox_request(method, url, data=None, headers=None, cookies=None):
        if 'login' in data:
            if not found_by_login:
                response = blackbox_userinfo_response(uid=None)
            else:
                kwargs = deep_merge(
                    build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER.e164, is_alias=True),
                    {'login': TEST_PHONE_NUMBER.digital},
                )
                response = blackbox_userinfo_response(uid='2', **kwargs)
        elif not_found:
            response = blackbox_userinfo_response(uid=None)
        else:
            if subject_account is not None:
                kwargs = subject_account.copy()
            else:
                kwargs = {}
            response = blackbox_userinfo_response(uid=TEST_UID, **kwargs)

        return mock.Mock(content=response, status_code=200)

    return blackbox_request


class BaseConfirmAndBindSubmitterMixin(object):
    with_check_cookies = False

    def _test_ok(self, with_check_cookies=False):
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )

        self.assert_blackbox_sessionid_called()

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok(with_check_cookies=with_check_cookies)

    def test_ok_with_lite_account(self):
        kwargs = dict(LITE_ACCOUNT_KWARGS)
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_sessionid_multi_response(
                age=100500,
                **kwargs
            ),
        )
        self.test_ok()

    def test_ok_with_pdd_account(self):
        '''
        ПДДшнику можно привязать телефон только в режиме мультиавторизации
        '''
        kwargs = dict(PDD_ACCOUNT_KWARGS)
        kwargs['domain'] = TEST_DOMAIN
        # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
        # и есть персональная информация + КВ/КО
        kwargs['subscribed_to'] = [102]
        kwargs['dbfields'] = {
            'userinfo_safe.hintq.uid': u'99:вопрос',
            'userinfo_safe.hinta.uid': u'ответ',
        }
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **kwargs
            ),
        )
        with settings_context(
            YASMS_URL='http://localhost',
            SMS_VALIDATION_CODE_LENGTH=4,
            SMS_VALIDATION_RESEND_TIMEOUT=0,
            SMS_VALIDATION_MAX_SMS_COUNT=3,
            **mock_counters()
        ):
            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_send_code_response,
                    self.additional_ok_response_params,
                ),
            )

    def test_uid_in_track_differs_from_uid_in_cookie_error(self):
        """
        Пришли в ручку с треком, в котором лежит уид,
        а в куке его нет
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '12345'

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'track.invalid_state']},
            ),
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '12345')

    def test_invalid_sessionid(self):
        for status in [
            BLACKBOX_SESSIONID_EXPIRED_STATUS,
            BLACKBOX_SESSIONID_NOAUTH_STATUS,
            BLACKBOX_SESSIONID_INVALID_STATUS,
        ]:
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(status=status),
            )

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_submitter_response,
                    {u'status': u'error', u'errors': [u'sessionid.invalid']},
                ),
            )

        eq_(self.env.blackbox._mock.request.call_count, 3)
        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
            entries.append(self.env.statbox.entry('check_cookies'))
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )

        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )

        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PHONISH_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(
                    **account_kwargs
                ),
            )

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_submitter_response,
                    {u'status': u'error', u'errors': [u'account.invalid_type']},
                ),
            )

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)


class BaseConfirmAndBindCommitterMixin(object):
    with_check_cookies = False

    def test_invalid_sessionid(self):
        self.setup_track_for_commit()
        for status in [
            BLACKBOX_SESSIONID_EXPIRED_STATUS,
            BLACKBOX_SESSIONID_NOAUTH_STATUS,
            BLACKBOX_SESSIONID_INVALID_STATUS,
        ]:
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(status=status),
            )

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_response,
                    {u'status': u'error', u'errors': [u'sessionid.invalid']},
                ),
            )
        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
            entries.append(self.env.statbox.entry('check_cookies'))
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_disabled_account(self):
        self.setup_track_for_commit()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_DISABLED_STATUS),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )
        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_disabled_on_deletion_account(self):
        self.setup_track_for_commit()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )
        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_no_uid_in_track_error(self):
        """
        Пришли в ручку с треком, в котором нет уида
        """
        self.setup_track_for_commit()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'track.invalid_state']},
            ),
        )

    def test_uid_in_track_differs_from_uid_in_cookie_error(self):
        """
        Пришли в ручку с треком, в котором лежит один уид,
        а в куке его нет.
        """
        self.setup_track_for_commit()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '12345'

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'track.invalid_state']},
            ),
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '12345')


class CommonSubmitterCommitterTestMixin(object):
    def test_check_grants_missing_error(self):
        phone_bundle_grants = {'base', 'by_uid', 'low_level', 'bind_secure'}
        all_but_needed_grants = list(phone_bundle_grants.difference(self.specific_grants))
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': all_but_needed_grants}))
        rv = self.make_request()
        self.assert_error_response(rv, ['access.denied'], status_code=403)

        self.env.statbox.assert_has_written([])

    def test_check_headers_missing_error(self):
        rv = self.make_request(
            headers=mock_headers(user_ip=None),
        )
        self.assert_error_response(rv, ['ip.empty'])

        self.env.statbox.assert_has_written([])
