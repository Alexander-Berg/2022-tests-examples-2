# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import eq_
from passport.backend.api.test.mixins import (
    AccountHistoryTestMixin,
    AccountModificationNotifyTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_OAUTH_SCOPE,
    TEST_OAUTH_TOKEN,
    TEST_OPERATION_ID,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.blackbox.parsers import PHONE_OP_TYPE_IDX
from passport.backend.core.conf import settings
from passport.backend.core.db.schemas import phone_operations_table as p_op_t
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_TYPE
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import zero_datetime

from .base_test_data import (
    TEST_CONFIRMATION_CODE,
    TEST_EMAIL,
    TEST_FIRSTNAME,
    TEST_LOGIN,
    TEST_PHONE_ID,
)
from .statbox_mixin import StatboxTestMixin


class PhoneManageBaseTestCase(BaseBundleTestViews, StatboxTestMixin, AccountHistoryTestMixin, AccountModificationNotifyTestMixin):
    base_method_path = None
    base_request_args = None
    step = None
    mode = None
    with_check_cookies = False

    def setUp(self):
        super(PhoneManageBaseTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['*']}))

        self._fake_generate_random_code = CodeGeneratorFaker()
        self._fake_generate_random_code.set_return_value(TEST_CONFIRMATION_CODE)
        self._fake_generate_random_code.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.SMS_TEXT = settings.translations.SMS['ru']['APPROVE_CODE']
        self.setup_statbox_templates()
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.track_id_generator.stop()
        self._fake_generate_random_code.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self._fake_generate_random_code
        super(PhoneManageBaseTestCase, self).tearDown()

    def _build_account(self, emails=Undefined, **kwargs):
        if emails is Undefined:
            emails = [
                self.env.email_toolkit.create_native_email(
                    login=TEST_EMAIL.split(u'@')[0],
                    domain=TEST_EMAIL.split(u'@')[1],
                ),
            ]
        common_kwargs = deep_merge(
            dict(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password=TEST_PASSWORD_HASH,
                firstname=TEST_FIRSTNAME,
                language=TEST_LANGUAGE,
                emails=emails,
                attributes={u'account.2fa_on': False},
            ),
            kwargs,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **common_kwargs
            ),
        )

        common_kwargs = dict(common_kwargs)
        # Удаляю из common_kwargs параметры, которые нужно только в функциях
        # для работы с sessionid.
        common_kwargs.pop('have_password', None)

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                **common_kwargs
            ),
        )
        build_account(
            db_faker=self.env.db,
            **common_kwargs
        )

    def build_headers(self, **kwargs):
        base_headers = dict(
            user_ip=TEST_USER_IP,
            cookie=None,
            host=TEST_HOST,
            authorization=None,
            user_agent=TEST_USER_AGENT,
            accept_language=TEST_ACCEPT_LANGUAGE,
        )
        headers = merge_dicts(
            base_headers,
            kwargs,
        )
        return mock_headers(**headers)

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def make_request(self, url=None, headers=None, data=None, with_track_id=True):
        if headers is None:
            headers = self.build_headers(cookie=TEST_USER_COOKIE)

        if data is None:
            data = dict(self.base_request_args or {})
        if with_track_id:
            data.setdefault('track_id', self.track_id)

        return self.env.client.post(
            '%s?consumer=dev' % (url or self.base_method_path),
            data=data,
            headers=headers,
        )

    def assert_blackbox_auth_method_ok(self, by_token=False):
        specific_kwargs = {}
        if by_token:
            bb_method = 'oauth'
            bb_opposite_method = 'sessionid'
            specific_kwargs.update(oauth_token=TEST_OAUTH_TOKEN)
        else:
            bb_method = 'sessionid'
            bb_opposite_method = 'oauth'
        bb_kwargs = merge_dicts(
            {
                'method': bb_method,
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
                'emails': 'getall',
            },
            specific_kwargs,
        )
        requests = self.env.blackbox.get_requests_by_method(bb_method)
        eq_(len(requests), 1)
        requests[0].assert_query_contains(bb_kwargs)
        eq_(self.env.blackbox.get_requests_by_method(bb_opposite_method), [])

    def check_db_phone_operation(self, data, id_=1, uid=TEST_UID, phone_id=TEST_PHONE_ID):
        data['type'] = PHONE_OP_TYPE_IDX[data['type']]

        data.update(dict(uid=uid, phone_id=phone_id, id=id_))

        if 'started' not in data:
            data['started'] = DatetimeNow()

        for col in p_op_t.c:
            if col.default is None:
                continue

            if col.name not in data:
                data[col.name] = col.default.arg

        for key in ['finished', 'code_last_sent', 'code_confirmed', 'password_verified']:
            if key not in data:
                data[key] = zero_datetime

        self.env.db.check_line(
            'phone_operations',
            data,
            db='passportdbshard1',
            uid=uid,
            phone_id=phone_id,
            id=id_,
        )

    def check_db_phone_operation_missing(self, operation_id):
        self.env.db.check_missing(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID,
            id=operation_id,
        )

    def check_db_phone_attr(self, field_name, value, phone_id=TEST_PHONE_ID):
        self.env.db.check_db_ext_attr(
            TEST_UID,
            EXTENDED_ATTRIBUTES_PHONE_TYPE,
            phone_id,
            field_name,
            value,
        )

    def check_yasms_send_sms_request(self, request, code=TEST_CONFIRMATION_CODE):
        request.assert_query_equals({
            'sender': 'passport',
            'utf8': '1',
            'route': 'validate',
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.SMS_TEXT,
            'no_blackbox': '1',
            'from_uid': str(TEST_UID),
            'caller': 'dev',
            'identity': '%s.%s.send_confirmation_code' % (self.mode, self.step),
        })

        request.assert_post_data_equals({
            'text_template_params': json.dumps({'code': code}).encode('utf-8'),
        })

    def _assert_access_denied_response(self, rv):
        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def _test_error_operation_not_found(self, submitted_first=False):
        """
        Передаем id операции, которой не существует.
        """
        self.set_blackbox_response()

        data = dict(self.base_request_args, operation_id=567)
        rv = self.make_request(data=data)
        self.assert_error_response(rv, ['operation.not_found'])

        excluded = ['mode'] if self.step not in ['submit', 'commit'] else []

        entries = []

        if self.with_check_cookies:
            if submitted_first:
                entries.append(self.env.statbox.entry('submitted', _exclude=excluded, operation_id='567'))
                entries.append(self.env.statbox.entry('check_cookies'))
            else:
                entries.append(self.env.statbox.entry('check_cookies'))
                entries.append(self.env.statbox.entry('submitted', _exclude=excluded, operation_id='567'))
        else:
            entries.append(self.env.statbox.entry('submitted', _exclude=excluded, operation_id='567'))

        self.env.statbox.assert_has_written(entries)

    def _test_error_account_disabled(self):
        """
        Проверяем, что ручка падает с ошибкой для заблокированного аккаунта.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])

    def _test_error_account_disabled_on_deletion(self):
        """
        Проверяем, что ручка падает с ошибкой для заблокированного аккаунта.
        """

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def _test_ok_with_existing_track(self):
        """
        Ручки должны уметь работать с существующим треком.
        """
        self.set_blackbox_response()

        rv = self.make_request()

        data = json.loads(rv.data)
        eq_(data['status'], 'ok')
        eq_(data['track_id'], self.track_id)
        # Проверим, что в ручке трек не создавался
        eq_(self.track_id_generator._mock.call_count, 0)

        # Проверим, что смотрим куда нужно
        self.track_manager.create('authorize', 'dev')
        eq_(self.track_id_generator._mock.call_count, 1)

    def _test_ok_account_without_password(self):
        """
        Работа с защищенным телефоном разрешена и аккаунтам без пароля.
        Подсунем аккаунт без пароля для процесса, работающего с обычным номером.
        Ошибки быть не должно.
        """
        self.set_blackbox_response(password_is_set=False)

        rv = self.make_request()

        data = json.loads(rv.data)
        eq_(data['status'], 'ok')

    def _test_error_secure_number_exists(self):
        """
        У аккаунта есть защищенный номер, ручка должна ответить ошибкой phone_secure.already_exists.
        """
        phone = {
            'id': 678,
            'number': TEST_OTHER_EXIST_PHONE_NUMBER.e164,
            'created': datetime(2001, 2, 3, 12, 34, 56),
            'bound': datetime(2002, 2, 3, 12, 34, 56),
        }
        self.set_blackbox_response(phones=[phone], account_attributes={'phones.secure': phone['id']})

        rv = self.make_request()
        self.assert_error_response(rv, ['phone_secure.already_exists'])
