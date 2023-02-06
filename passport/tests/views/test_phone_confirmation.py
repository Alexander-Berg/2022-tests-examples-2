# -*- coding: utf-8 -*-
from datetime import timedelta
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.phone_confirmation import PHONE_CONFIRMATION_STATE
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
)
from passport.backend.core.builders.yasms import (
    YaSmsAccessDenied,
    YaSmsError,
    YaSmsLimitExceeded,
    YaSmsPermanentBlock,
    YaSmsSecureNumberExists,
    YaSmsSecureNumberNotAllowed,
    YaSmsTemporaryBlock,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_ip_for_consumer,
)
from passport.backend.core.models.phones.faker import (
    assert_no_secure_phone,
    assert_simple_phone_bound,
    build_phone_being_bound,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    TimeSpan,
)
from passport.backend.core.tracks.track_manager import create_track_id
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
    remove_none_values,
)


TEST_IP = '123.123.123.123'
TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_CONFIRMATION_CODE = '1234'
TEST_OPERATION_TTL = timedelta(seconds=60)
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79259164525')
TEST_TAXI_APPLICATION = 'ru.yandex.taxi'
TEST_USER_AGENT = 'curl'


class TestPhoneConfirmationBase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['confirm']}))
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.not_existing_track_id = create_track_id()

        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        assert self.not_existing_track_id != self.track_id
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'sanitize_phone_number',
            action='sanitize_phone_number',
            sanitize_phone_result=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'send_code',
            action='send_code',
            uid='-',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'enter_code',
            action='enter_code',
            uid='-',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            good='1',
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_enqueued',
            caller='dev',
            action='enqueued',
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            rule='fraud',
            sender='passport',
            number=TEST_PHONE_NUMBER.e164,
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_not_sent',
            caller='dev',
            action='notdeliveredtosmsc',
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            rule='fraud',
            sender='passport',
            number=TEST_PHONE_NUMBER.e164,
        )


TEST_SMS_TEXT = u'sms {{code}} текст'


class _TranslationSettings(object):
    SMS = {'ru': {'APPROVE_CODE': TEST_SMS_TEXT}}
    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


class TestSendCodeBase(TestPhoneConfirmationBase):

    def setUp(self):
        super(TestSendCodeBase, self).setUp()

        self.confirmation_code = 5555
        self.system_random = mock.Mock()
        self.system_random.randrange = mock.Mock(return_value=self.confirmation_code)

        self.patch = mock.patch('random.SystemRandom',
                                mock.Mock(return_value=self.system_random))
        self.patch.start()

    def tearDown(self):
        super(TestSendCodeBase, self).tearDown()
        self.patch.stop()
        del self.patch
        del self.system_random

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'country': 'RU',
            'display_language': 'ru',
            'phone_number': TEST_PHONE_NUMBER.e164,
            'ignore_phone_compare': '1',
        }

        if exclude:
            for key in exclude:
                del base_params[key]

        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/phonenumber/send_confirmation_code/?consumer=dev',
            data=data,
            headers=headers,
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    translations=_TranslationSettings,
    **mock_counters()
)
class TestSendCode(TestSendCodeBase):

    def test_without_need_headers(self):
        rv = self.make_request(
            self.query_params(),
            {},
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None, u'message': u'Missing required headers: "Ya-Consumer-Client-Ip"',
                          u'code': u'missingheader'}]},
        )

    def test_no_track_error(self):
        rv = self.make_request(
            self.query_params(
                track_id=self.not_existing_track_id,
            ),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Unknown track_id',
                          u'code': u'unknowntrack'}]})

    def test_unsupported_process_in_track_error(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'some process name'

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Track state is invalid',
                          u'code': u'invalidtrackstate'}]})

    def test_user_phone_differs_to_sanitized_error(self):
        rv = self.make_request(
            self.query_params(
                exclude=['ignore_phone_compare'],
            ),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': 'phone_number',
                          u'message': u'Normalized number is different to user input',
                          u'value': TEST_PHONE_NUMBER.international,
                          u'code': u'differentphonenumber'}]})

        track = self.track_manager.read(self.track_id)
        eq_(track.sanitize_phone_count.get(), 1)

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = False
            track.phone_confirmation_send_ip_limit_reached = False

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'code_length': 4,
            },
        )
        self.system_random.randrange.assert_called_once_with(1000, 10000)

        number = TEST_PHONE_NUMBER.e164
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
            'identity': 'send_confirmation_code',
            'caller': 'dev',
            'route': 'validate',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(self.confirmation_code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, number)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.sanitize_phone_first_call, TimeNow())
        eq_(track.sanitize_phone_last_call, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        eq_(track.state, PHONE_CONFIRMATION_STATE)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('send_code', sms_count='1', sms_id='1'),
        ])

    def test_ok__taxi_route(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = False
            track.phone_confirmation_send_ip_limit_reached = False
            track.device_application = TEST_TAXI_APPLICATION

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        eq_(rv.status_code, 200)
        number = TEST_PHONE_NUMBER.e164
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
            'identity': 'send_confirmation_code',
            'caller': 'dev',
            'route': 'taxi',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(self.confirmation_code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, number)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.sanitize_phone_first_call, TimeNow())
        eq_(track.sanitize_phone_last_call, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        eq_(track.state, PHONE_CONFIRMATION_STATE)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('send_code', sms_count='1', sms_id='1'),
        ])

    def test_error_send_limit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for _ in range(3):
                track.phone_confirmation_sms_count.incr()

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='limits',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='limits',
            ),
        ])

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'smssendlimitexceeded',
                          u'message': 'Resend reached sms limit'}]})
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_send_count_limit_reached)

    def test_error_send_limit_by_ip(self):
        counter = sms_per_ip.get_counter(TEST_IP)
        # Установим счетчик смсок на ip в limit - 1
        for i in range(counter.limit - 1):
            counter.incr(TEST_IP)

        rv = self.make_request(self.query_params(), mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT))

        # Одна отсылка ок
        eq_(rv.status_code, 200)

        other_track_id = self.track_manager.create('register', 'dev').track_id

        # еще одна отсылка на другой трек - не ок
        rv = self.make_request(
            self.query_params(track_id=other_track_id),
            mock_headers(user_ip=TEST_IP),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'code': 'smssendlimitexceeded',
                    u'message': 'Resend reached sms limit',
                }],
            },
        )
        track = self.track_manager.read(other_track_id)
        ok_(track.phone_confirmation_send_ip_limit_reached)

    def test_ok__ip_limit_reached__consumer_ip_limit_not_reached(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = False
            track.phone_confirmation_send_ip_limit_reached = False

        with settings_context(
            **mock_counters(DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, 5)})
        ):
            global_ip_counter = sms_per_ip.get_counter(TEST_IP)
            for _ in range(global_ip_counter.limit):
                global_ip_counter.incr(TEST_IP)

            rv = self.make_request(self.query_params(), mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT))

        eq_(rv.status_code, 200)

    def test_error_send_limit_by_ip_and_consumer(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = False
            track.phone_confirmation_send_ip_limit_reached = False

        with settings_context(
            **mock_counters(DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, 5)})
        ):
            for _ in range(5):
                sms_per_ip_for_consumer.get_counter('dev').incr(TEST_IP)

            rv = self.make_request(self.query_params(), mock_headers(user_ip=TEST_IP))

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'code': 'smssendlimitexceeded',
                    u'message': 'Resend reached sms limit',
                }],
            },
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_send_ip_limit_reached)

    def test_error_already_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'phonealreadyconfirmed',
                          u'message': 'Phone has been confirmed already'}]})

    def test_error_resend_timeout(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_last_send_at = time.time() - 4

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'smssendtooearly',
                          u'message': "Can't resend sms earlier than %d seconds from previous sending" % 10}]})

    def test_no_last_sms_time__ok(self):
        """
        В треке есть информация о том, что была отправлена одна sms, но нет времени отправки
        Пропускаем проверку минимального времени между отправками и отправляем sms нормально
        Записываем время текущей отправки как время первой и последней отправки
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = False
            track.phone_confirmation_send_ip_limit_reached = False
            track.phone_confirmation_sms_count.incr()

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        eq_(rv.status_code, 200)
        number = TEST_PHONE_NUMBER.e164
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
            'identity': 'send_confirmation_code',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(self.confirmation_code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, number)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.sanitize_phone_first_call, TimeNow())
        eq_(track.sanitize_phone_last_call, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 2)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(track.phone_confirmation_confirms_count.get() is None)
        eq_(track.state, PHONE_CONFIRMATION_STATE)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('send_code', sms_count='2', sms_id='1'),
        ])

    def test_resend_same_phone(self):
        code = '123'
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_code = code
            track.phone_confirmation_last_send_at = time.time() - 20

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        eq_(rv.status_code, 200)
        eq_(self.system_random.randrange.call_count, 0)

        number = TEST_PHONE_NUMBER.e164
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
            'identity': 'send_confirmation_code',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_code, '123')
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 2)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('send_code', sms_count='2', sms_id='1'),
        ])

    def test_resend_new_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_phone_number = '+79161234568'
            track.phone_confirmation_code = '123'
            track.phone_confirmation_first_send_at = 21
            track.sanitize_phone_first_call = 21
            for _ in range(2):
                track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_last_send_at = time.time() - 20

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
        )

        eq_(rv.status_code, 200)
        eq_(self.system_random.randrange.call_count, 1)
        number = TEST_PHONE_NUMBER.e164

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
        })
        requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(self.confirmation_code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        ok_(not track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_phone_number, number)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_first_send_at, '21')
        eq_(track.sanitize_phone_last_call, TimeNow())
        eq_(track.sanitize_phone_first_call, '21')
        eq_(track.phone_confirmation_sms_count.get(), 2)
        ok_(track.phone_confirmation_confirms_count.get() is None)

        # FIXME: тут кажется нужно наоборот делать reset счётчика смс-ок
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('send_code', sms_count='2', sms_id='1'),
        ])

    def test_send_sms_with_yasms_errors(self):
        errors = [
            (YaSmsError('error message'), 503,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'error message',
                           u'code': u'yasmserror'}]}),
            (YaSmsAccessDenied('error message'), 500,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'YaSms ACL failed',
                           u'code': u'yasmsacl'}]}),
            (YaSmsLimitExceeded('error message'), 400,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'Resend reached sms limit',
                           u'code': u'smssendlimitexceeded'}]}),
            (YaSmsPermanentBlock('error message'), 400,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'error message',
                           u'code': u'yasmspermanentblock'}]}),
            (YaSmsTemporaryBlock('error message'), 400,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'error message',
                           u'code': u'smssendtooearly'}]}),
            (YaSmsSecureNumberNotAllowed('error message'), 400,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'error message',
                           u'code': u'yasmssecurenumbernotallowed'}]}),
            (YaSmsSecureNumberExists('error message'), 400,
             {u'status': u'error',
              u'errors': [{u'field': None,
                           u'message': u'error message',
                           u'code': u'yasmssecurenumberalreadypresented'}]}),
        ]

        for error in errors:
            self.env.yasms.set_response_side_effect('send_sms', error[0])

            rv = self.make_request(
                self.query_params(),
                mock_headers(user_ip=TEST_IP, user_agent=TEST_USER_AGENT),
            )

            eq_(rv.status_code, error[1])
            eq_(json.loads(rv.data), error[2])

        number = TEST_PHONE_NUMBER.e164

        # 7 потому что внутри ручки происходит 1 вызов YaSms: sendsms
        requests = self.env.yasms.requests
        eq_(len(requests), 7)
        requests[1].assert_query_contains({
            'phone': number,
            'text': TEST_SMS_TEXT,
        })
        requests[1].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(self.confirmation_code)}).encode('utf-8'),
        })

        track = self.track_manager.read(self.track_id)

        # TODO: закомментированное - поведение со старыми треками. Удалить или пофиксить.
        # ok_(track.phone_confirmation_phone_number is None)
        # ok_(track.phone_confirmation_code is None)
        ok_(track.phone_confirmation_first_send_at is None)
        ok_(track.phone_confirmation_last_send_at is None)
        ok_(track.phone_confirmation_sms_count.get() is None)
        # ok_(track.phone_confirmation_is_confirmed is None)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(track.phone_confirmation_confirms_count.get() is None)

        log_entries = []
        for _ in range(len(errors)):
            log_entries.append(self.env.statbox.entry('sanitize_phone_number'))

        self.env.statbox.assert_has_written(log_entries)

    def test_invalid_track_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.state = 'bla'

        rv = self.make_request(
            self.query_params(),
            mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Track state is invalid',
                    u'code': u'invalidtrackstate',
                }],
            },
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
)
class TestCanResend(TestPhoneConfirmationBase):

    def can_resend_request(self, data, headers):
        return self.env.client.post(
            '/1/phonenumber/can_resend/?consumer=dev',
            data=data,
            headers=headers,
        )

    def test_no_track_error(self):
        rv = self.can_resend_request(
            {'track_id': self.not_existing_track_id},
            mock_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Unknown track_id',
                          u'code': u'unknowntrack'}]})

    def test_true(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_last_send_at = time.time() - 20
            track.phone_confirmation_sms_count.incr()

        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': True})

    def test_true_no_last_sms_time(self):
        """
        Сохранена информация о том, что sms была отправлена, но не сохранено время отправки
        Разрешаем повторную отправку sms
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()

        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': True})

    def test_false_by_timeout(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_last_send_at = time.time() - 3
            track.phone_confirmation_sms_count.incr()

        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': False})

    def test_false_no_sms_sent(self):
        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': False})

    def test_false_already_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_last_send_at = time.time() - 20
            track.phone_confirmation_sms_count.incr()

        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': False})

    def test_false_by_sms_limit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_last_send_at = time.time() - 20
            for _ in range(3):
                track.phone_confirmation_sms_count.incr()

        rv = self.can_resend_request(
            {'track_id': self.track_id},
            mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': False})


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
)
class TestConfirmPhone(TestPhoneConfirmationBase):

    def make_request(self):
        return self.env.client.post(
            '/1/phonenumber/confirm/?consumer=dev',
            data={
                'track_id': self.track_id,
                'code': TEST_CONFIRMATION_CODE,
            },
            headers=mock_headers(),
        )

    def test_no_track_error(self):
        rv = self.env.client.post(
            '/1/phonenumber/confirm/?consumer=dev',
            data={
                'track_id': self.not_existing_track_id,
                'code': TEST_CONFIRMATION_CODE,
            },
            headers=mock_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Unknown track_id',
                          u'code': u'unknowntrack'}]})

    def test_unsupported_process_in_track_error(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'some process name'

        rv = self.make_request()

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Track state is invalid',
                          u'code': u'invalidtrackstate'}]})

    # TODO: Можно ли разбить этот тест на два независимых?
    def test_confirm(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = '1111'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_confirms_count_limit_reached = False
            track.phone_confirmation_last_send_at = time.time() - 20

        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': False})

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_last_checked, TimeNow())
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_first_checked, track.phone_confirmation_last_checked)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE

        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': True})

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_last_checked, TimeNow())
        ok_(track.phone_confirmation_first_checked < track.phone_confirmation_last_checked)
        eq_(track.phone_confirmation_confirms_count.get(), 2)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.state, PHONE_CONFIRMATION_STATE)
        ok_(track.phone_confirmation_is_confirmed)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code', good='0', time_passed=TimeSpan(20)),
            self.env.statbox.entry('enter_code', time_passed=TimeSpan(20)),
        ])

    def test_confirm_no_last_sms_time__ok(self):
        """
        В треке нет информации о времени отправки последней sms - в статбокс нет поля time_passed
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_confirms_count_limit_reached = False

        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'result': True})

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_last_checked, TimeNow())
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_first_checked, track.phone_confirmation_last_checked)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.state, PHONE_CONFIRMATION_STATE)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_error_not_send(self):
        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'smsnotsent',
                          u'message': 'Validation code was not generated and sent'}]})

    def test_error_confirms_limit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            for _ in range(3):
                track.phone_confirmation_confirms_count.incr()

        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'confirmationslimitexceeded',
                          u'message': 'Fail confirm limit exceeded'}]})

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_confirms_count_limit_reached)

    def test_error_already_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_is_confirmed = True

        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'phonealreadyconfirmed',
                          u'message': 'Phone has been confirmed already'}]})

    def test_invalid_track_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.state = 'bla'

        rv = self.make_request()

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Track state is invalid',
                    u'code': u'invalidtrackstate',
                }],
            },
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
)
class TestCopyPhone(BaseTestViews):
    SRC_UID = 123
    DST_UID = 456

    SRC_TOKEN = '123456789'
    DST_TOKEN = '987654321'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['copy']}))
        src_blackbox_oauth_response = blackbox_oauth_response(uid=self.SRC_UID)
        dst_blackbox_oauth_response = blackbox_oauth_response(uid=self.DST_UID)
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [src_blackbox_oauth_response, dst_blackbox_oauth_response],
        )

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def get_account_kwargs(self, uid, login='test_login', alias_type='portal', phone_id=1, phone=None, bound=True):
        account_kwargs = dict(
            uid=uid,
            login=login,
            aliases={
                alias_type: login,
            },
        )

        if phone:
            if bound:
                phone_kwargs = build_phone_bound(
                    phone_id,
                    phone.e164,
                    is_default=False,
                )
            else:
                phone_kwargs = build_phone_being_bound(
                    phone_id,
                    phone.e164,
                    1000,
                )
            account_kwargs = deep_merge(account_kwargs, phone_kwargs)
        return account_kwargs

    def assert_blackbox_oauth_called(self, token, call_index=0):
        self.env.blackbox.requests[call_index].assert_query_contains(
            {
                'method': 'oauth',
                'oauth_token': token,
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
            },
        )
        self.env.blackbox.requests[call_index].assert_contains_attributes(
            {
                'phones.default',
                'phones.secure',
            },
        )

    def assert_blackbox_phone_bindings_called(self, phone, call_index=0):
        self.env.blackbox.requests[call_index].assert_query_contains(
            {
                'method': 'phone_bindings',
                'ignorebindlimit': '0',
                'numbers': phone.e164,
            },
        )

    def assert_historydb_ok(self):
        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                # Создание операции
                self.historydb_entry(self.DST_UID, 'phone.1.action', 'created'),
                self.historydb_entry(self.DST_UID, 'phone.1.created', TimeNow()),
                self.historydb_entry(self.DST_UID, 'phone.1.number', TEST_PHONE_NUMBER.e164),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.action', 'created'),
                self.historydb_entry(
                    self.DST_UID,
                    'phone.1.operation.1.finished',
                    TimeNow(offset=TEST_OPERATION_TTL.total_seconds()),
                ),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.security_identity', TEST_PHONE_NUMBER.digital),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.started', TimeNow()),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.type', 'bind'),
                self.historydb_entry(self.DST_UID, 'action', 'acquire_phone'),
                self.historydb_entry(self.DST_UID, 'consumer', 'dev'),
                # Привязка телефона
                self.historydb_entry(self.DST_UID, 'info.karma_prefix', '6'),
                self.historydb_entry(self.DST_UID, 'info.karma_full', '6000'),
                self.historydb_entry(self.DST_UID, 'phone.1.action', 'changed'),
                self.historydb_entry(self.DST_UID, 'phone.1.bound', TimeNow()),
                self.historydb_entry(self.DST_UID, 'phone.1.confirmed', TimeNow()),
                self.historydb_entry(self.DST_UID, 'phone.1.number', TEST_PHONE_NUMBER.e164),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.action', 'deleted'),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.security_identity', TEST_PHONE_NUMBER.digital),
                self.historydb_entry(self.DST_UID, 'phone.1.operation.1.type', 'bind'),
                self.historydb_entry(self.DST_UID, 'action', 'copy_phone'),
                self.historydb_entry(self.DST_UID, 'consumer', 'dev'),
            ],
        )

    def assert_db_ok(self, uid, ignore_bind_limit=False):
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_simple_phone_bound.check_db(
            self.env.db,
            uid=uid,
            phone_attributes={
                'id': 1,
                'number': TEST_PHONE_NUMBER.e164,
                'created': DatetimeNow(),
                'bound': DatetimeNow(),
                'confirmed': DatetimeNow(),
            },
            binding_flags=binding_flags if ignore_bind_limit else None,
        )
        assert_no_secure_phone(self.env.db, 1)

    def historydb_entry(self, uid=1, name=None, value=None):
        entry = {
            'uid': str(uid),
            'name': name,
            'value': value,
        }
        return remove_none_values(entry)

    def make_request(self, **params):
        base_params = {
            'src_oauth_token': self.SRC_TOKEN,
            'dst_oauth_token': self.DST_TOKEN,
            'phone_number': TEST_PHONE_NUMBER.e164,
        }
        return self.env.client.post(
            '/1/phonenumber/copy/?consumer=dev',
            data=merge_dicts(base_params, params),
            headers=mock_headers(),
        )

    def test_invalid_src_token(self):
        src_blackbox_oauth_response = blackbox_oauth_response(
            uid=self.SRC_UID,
            status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [src_blackbox_oauth_response],
        )
        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'invalidsrcoauthtoken',
                          u'message': 'Source OAuth token is invalid'}]})

    def test_invalid_dst_token(self):
        src_blackbox_oauth_response = blackbox_oauth_response(uid=self.SRC_UID)
        dst_blackbox_oauth_response = blackbox_oauth_response(
            uid=self.SRC_UID,
            status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [src_blackbox_oauth_response, dst_blackbox_oauth_response],
        )
        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'invaliddstoauthtoken',
                          u'message': 'Destination OAuth token is invalid'}]})

    def test_same_user(self):
        src_blackbox_oauth_response = blackbox_oauth_response(uid=self.SRC_UID)
        dst_blackbox_oauth_response = blackbox_oauth_response(uid=self.SRC_UID)
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [src_blackbox_oauth_response, dst_blackbox_oauth_response],
        )
        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'srcanddstuidequal',
                          u'message': 'Source and destination users have same uid'}]})

    def test_src_phone_not_found(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone=PhoneNumber.parse('+79168889977'),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(uid=self.DST_UID),
            ],
        )

        rv = self.make_request()

        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_blackbox_oauth_called(self.SRC_TOKEN, 0)
        self.assert_blackbox_oauth_called(self.DST_TOKEN, 1)

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'phonenotfound',
                          u'message': 'Phone not found'}]})

    def test_src_phone_not_confirmed(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone=TEST_PHONE_NUMBER,
            bound=False,
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(uid=self.DST_UID),
            ],
        )

        rv = self.make_request()

        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_blackbox_oauth_called(self.SRC_TOKEN, 0)
        self.assert_blackbox_oauth_called(self.DST_TOKEN, 1)

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'phonenotconfirmed',
                          u'message': 'Phone is not confirmed'}]})

    def test_already_confirmed(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone_id=1,
            phone=TEST_PHONE_NUMBER,
        )
        dst_account_kwargs = self.get_account_kwargs(
            uid=self.DST_UID,
            phone_id=2,
            phone=TEST_PHONE_NUMBER,
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(**dst_account_kwargs),
            ],
        )

        rv = self.make_request()

        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_blackbox_oauth_called(self.SRC_TOKEN, 0)
        self.assert_blackbox_oauth_called(self.DST_TOKEN, 1)

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'code': 'phonealreadyconfirmed',
                          u'message': 'Phone has been confirmed already'}]})

    def test_ignore_bindlimit_for_phonish(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone_id=1,
            phone=TEST_PHONE_NUMBER,
        )
        dst_account_kwargs = self.get_account_kwargs(
            uid=self.DST_UID,
            login='phne-login',
            alias_type='phonish',
            # Не бывает фонишей без телефонов, но на всякий случай
            # протестируем, что другой номер привяжется с правильным флажком.
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(**dst_account_kwargs),
            ],
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
            },
        )

        eq_(len(self.env.blackbox.requests), 3)
        self.assert_blackbox_oauth_called(self.SRC_TOKEN, 0)
        self.assert_blackbox_oauth_called(self.DST_TOKEN, 1)
        self.assert_blackbox_phone_bindings_called(TEST_PHONE_NUMBER, 2)

        self.assert_historydb_ok()
        self.assert_db_ok(self.DST_UID, ignore_bind_limit=True)

    def test_copy(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone_id=1,
            phone=TEST_PHONE_NUMBER,
        )
        dst_account_kwargs = self.get_account_kwargs(
            uid=self.DST_UID,
            phone_id=2,
            phone=PhoneNumber.parse('+79096841646'),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(**dst_account_kwargs),
            ],
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
            },
        )

        eq_(len(self.env.blackbox.requests), 4)
        self.assert_blackbox_oauth_called(self.SRC_TOKEN, 0)
        self.assert_blackbox_oauth_called(self.DST_TOKEN, 1)
        self.assert_blackbox_phone_bindings_called(TEST_PHONE_NUMBER, 2)
        self.assert_blackbox_phone_bindings_called(TEST_PHONE_NUMBER, 3)

        self.assert_historydb_ok()
        self.assert_db_ok(self.DST_UID)

    def test_phonish_bindings_limit(self):
        src_account_kwargs = self.get_account_kwargs(
            uid=self.SRC_UID,
            phone_id=2,
            phone=TEST_PHONE_NUMBER2,
        )
        dst_account_kwargs = self.get_account_kwargs(
            uid=self.DST_UID,
            login='phne-login',
            alias_type='phonish',
            phone_id=1,
            phone=TEST_PHONE_NUMBER,
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**src_account_kwargs),
                blackbox_oauth_response(**dst_account_kwargs),
            ],
        )

        rv = self.make_request(phone_number=TEST_PHONE_NUMBER2.e164)

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': None,
                        u'code': 'phonealreadyconfirmed',
                        u'message': 'Phone has been confirmed already',
                    },
                ],
            },
        )

        ok_(
            not self.env.db.select(
                'phone_bindings',
                uid=self.DST_UID,
                number=int(TEST_PHONE_NUMBER2.digital),
                db='passportdbshard1',
            ),
        )
