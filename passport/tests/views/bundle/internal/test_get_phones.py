# -*- coding: utf-8 -*-

from datetime import datetime
from functools import partial

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import (
    build_mark_operation,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


_UID = 1
_YANDEX_TEAM_LOGIN = 'yndxandrey'
_EXTERNAL_LOGIN = 'andrey'

_PHONE_ID = 1
_PHONE_NUMBER = PhoneNumber.parse('+79259163525')

_CREATED_TIME = datetime(2000, 1, 1)
_BOUND_TIME = datetime(2000, 1, 2)
_SECURE_TIME = datetime(2000, 1, 3)
_CONFIRMED_TIME = datetime(2000, 1, 4)
_ADMITTED_TIME = datetime(2000, 1, 5)

_OPERATION_ID = 1
_STARTED_TIME = datetime(2000, 2, 1)
_FINISHED_TIME = datetime(2000, 2, 2)
_CODE_LAST_SENT_TIME = datetime(2000, 2, 3)
_CONFIRMATION_CODE = '123456'


@with_settings_hosts()
class TestGetPhones(BaseBundleTestViews):
    def setUp(self):
        super(TestGetPhones, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestGetPhones, self).tearDown()

    def test_ok(self):
        self._given()

        response = self._make_request()

        self._assert_response_ok(response)
        self._assert_blackbox_called()

    def test_external_login(self):
        self._given(login=_EXTERNAL_LOGIN)

        response = self._make_request()

        self._assert_response_ok(response, is_real_phone_masked=True)

    def test_default_phone_not_selected(self):
        self._given(is_default_phone_selected=False)

        response = self._make_request()

        self._assert_response_ok(response, is_default_selected=False)

    def test_no_secure_phone(self):
        self._given(has_secure_phone=False)

        response = self._make_request()

        self._assert_response_ok(response, has_secure_phone=False)

    def test_phone_binding_request(self):
        self._given()

        response = self._make_request()

        self._assert_response_ok(response)

        request = self.env.blackbox.requests[1]
        request.assert_query_contains({
            'method': 'phone_bindings',
            'type': 'all',
            'numbers': _PHONE_NUMBER.e164,
        })

    def test_account_does_not_exist(self):
        self._given(does_account_exist=False)

        response = self._make_request()

        self.assert_error_response(response, ['account.not_found'])

    def test_race__no_phone_number(self):
        """
        Из-за гонки телефон остался без номера.
        """
        self._assign_grants()
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=_UID,
                login=_YANDEX_TEAM_LOGIN,
                phones=[{
                    'id': _PHONE_ID,
                    'admitted': _ADMITTED_TIME,
                }],
                phone_bindings=[],
                phone_operations=[],
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        response = self._make_request()

        self.assert_ok_response(
            response,
            phones=[{
                'id': _PHONE_ID,
                'attributes': {
                    'admitted': to_unixtime(_ADMITTED_TIME),
                },
                'binding': None,
                'operation': None,
            }],
            phone_operations=[],
            phone_bindings=[],
        )

    def _given(self, login=_YANDEX_TEAM_LOGIN, has_secure_phone=True,
               is_default_phone_selected=True, does_account_exist=True):
        self._assign_grants()

        if does_account_exist:
            if has_secure_phone:
                build_phone = partial(build_phone_secured, phone_secured=_SECURE_TIME)
            else:
                build_phone = build_phone_bound

            phone_data = deep_merge(
                build_phone(
                    phone_id=_PHONE_ID,
                    phone_number=_PHONE_NUMBER.e164,
                    phone_created=_CREATED_TIME,
                    phone_confirmed=_CONFIRMED_TIME,
                    phone_bound=_BOUND_TIME,
                    phone_admitted=_ADMITTED_TIME,
                    is_default=is_default_phone_selected,
                ),
                build_mark_operation(
                    operation_id=_OPERATION_ID,
                    phone_number=_PHONE_NUMBER.e164,
                    phone_id=_PHONE_ID,
                    started=_STARTED_TIME,
                    finished=_FINISHED_TIME,
                    code_last_sent=_CODE_LAST_SENT_TIME,
                    code_value=_CONFIRMATION_CODE,
                ),
            )
            userinfo_response = blackbox_userinfo_response(uid=_UID, login=login, **phone_data)
        else:
            userinfo_response = blackbox_userinfo_response(uid=None)

        self.env.blackbox.set_response_value('userinfo', userinfo_response)

        base_binding = {
            'number': _PHONE_NUMBER.e164,
            'phone_id': _PHONE_ID,
            'uid': _UID,
            'bound': _BOUND_TIME,
            'flags': 0,
        }

        phone_bindings = []
        if does_account_exist:
            phone_bindings.append(dict(base_binding, type='current'))
        phone_bindings.append(dict(base_binding, type='history'))

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )

    def _assert_response_ok(self, response, has_secure_phone=True, is_default_selected=True,
                            is_real_phone_masked=False, is_bank=False):
        if is_real_phone_masked:
            security_identity = -1
            code_value = '*****'
        else:
            security_identity = int(_PHONE_NUMBER)
            code_value = _CONFIRMATION_CODE

        phone_operations = {
            _OPERATION_ID: {
                'id': _OPERATION_ID,
                'type': 'mark',
                'security_identity': security_identity,
                'phone_id': _PHONE_ID,
                'phone_id2': None,
                'started': to_unixtime(_STARTED_TIME),
                'finished': to_unixtime(_FINISHED_TIME),
                'flags': 0,
                'password_verified': None,
                'code_value': code_value,
                'code_send_count': 1,
                'code_last_sent': to_unixtime(_CODE_LAST_SENT_TIME),
                'code_checks_count': 0,
                'code_confirmed': None,
                'uid': _UID,
            },
        }

        if is_real_phone_masked:
            phone_number = '*****'
        else:
            phone_number = _PHONE_NUMBER.e164

        current_binding = {
            'type': 'current',
            'phone_number': phone_number,
            'uid': _UID,
            'phone_id': _PHONE_ID,
            'binding_time': to_unixtime(_BOUND_TIME),
            'should_ignore_binding_limit': 0,
        }

        phone = {
            'id': _PHONE_ID,
            'attributes': {
                'number': phone_number,
                'created': to_unixtime(_CREATED_TIME),
                'bound': to_unixtime(_BOUND_TIME),
                'confirmed': to_unixtime(_CONFIRMED_TIME),
                'admitted': to_unixtime(_ADMITTED_TIME),
                'is_bank': is_bank,
            },
            'binding': current_binding,
            'operation': phone_operations[_OPERATION_ID],
        }

        if has_secure_phone:
            phone['attributes']['secured'] = to_unixtime(_SECURE_TIME)

        phone_bindings = [
            current_binding,
            {
                'type': 'history',
                'phone_number': phone_number,
                'uid': _UID,
                'phone_id': _PHONE_ID,
                'binding_time': to_unixtime(_BOUND_TIME),
                'should_ignore_binding_limit': 0,
            },
        ]

        expected = {
            'phones': [phone],
            'phone_operations': phone_operations.values(),
            'phone_bindings': phone_bindings,
        }

        if has_secure_phone:
            expected['secure_id'] = _PHONE_ID

        if is_default_selected:
            expected['default_id'] = _PHONE_ID

        self.assert_ok_response(response, **expected)

    def _assert_blackbox_called(self):
        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains({
            'method': 'userinfo',
            'uid': _UID,
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        request.assert_contains_attributes({'phones.secure', 'phones.default'})

    def _assign_grants(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['get_phones']}))

    def _make_request(self):
        return self.env.client.get(
            '/1/bundle/test/get_phones/',
            query_string={'uid': _UID, 'consumer': 'dev'},
        )
