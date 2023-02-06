# -*- coding: utf-8 -*-
from datetime import datetime

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_HOST,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_UID,
    TEST_UID1,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import lastauth_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import datetime_to_integer_unixtime


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
)
class AccountPhonishCanLoginTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/phonish/can_login/'
    http_query_args = dict(
        consumer='dev',
        uid=TEST_UID,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
    )
    base_phone_binding = {
        'bound': datetime.now(),
        'flags': 0,
        'type': 'current',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'phonish': ['can_login'],
        }))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        phone_bindings = [
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER.e164,
                phone_id=TEST_PHONE_ID1,
                uid=TEST_UID,
            ),
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER1.e164,
                phone_id=TEST_PHONE_ID2,
                uid=TEST_UID1,
            ),
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'phonish': '_'},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
                uids=[TEST_UID, TEST_UID1],
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
                lastauth_response(
                    uid=TEST_UID1,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})
        self.assert_ok_response(rv)

    def test_no_accounts_for_phone(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})
        self.assert_error_response(rv, ['account.not_found'])

    def test_other_account_using_phone_number(self):
        phone_bindings = [
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER1.e164,
                phone_id=TEST_PHONE_ID2,
                uid=TEST_UID1,
            ),
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'phonish': '_'},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
                uid=TEST_UID1,
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID1,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})
        self.assert_error_response(rv, ['account.uid_mismatch'])

    def test_account_disabled(self):
        phone_bindings = [
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER1.e164,
                phone_id=TEST_PHONE_ID2,
                uid=TEST_UID1,
            ),
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                enabled=False,
                aliases={'phonish': '_'},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
                uid=TEST_UID1,
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID1,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})
        self.assert_error_response(rv, ['account.disabled'])

    def test_find_phonish_by_new_ivory_coast_phone(self):
        self.check_find_phonish_by_ivory_coast_phone(
            account_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_find_phonish_by_old_ivory_coast_phone(self):
        self.check_find_phonish_by_ivory_coast_phone(
            account_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_find_phonish_by_ivory_coast_phone(self, account_phone_number, user_entered_phone_number):
        """
        Проверяем, что если к фонишу привязан старый (новый) телефон
        Кот-Д'Ивуара, а пользователь входит по новому (старому) телефону, то
        его логинит в существующий аккаунт.
        """
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(
                [
                    dict(
                        self.base_phone_binding,
                        number=account_phone_number.e164,
                        phone_id=TEST_PHONE_ID1,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'phonish': '_'},
                phones=[
                    dict(
                        bound=datetime.now(),
                        confirmed=datetime.now(),
                        created=datetime.now(),
                        id=TEST_PHONE_ID1,
                        number=account_phone_number.e164,
                    ),
                ],
                uid=TEST_UID,
            ),
        )

        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args=dict(phone_number=user_entered_phone_number.international))

        self.assert_ok_response(rv)
