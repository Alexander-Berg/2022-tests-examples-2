# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_DEVICE_INFO,
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
    blackbox_get_oauth_tokens_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import lastauth_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.time import datetime_to_integer_unixtime


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
    RECENT_ACCOUNT_USAGE_PERIOD=timedelta(minutes=1),
)
class AccountPhonishUidByPhoneTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/phonish/uid_by_phone/'
    http_query_args = dict(
        consumer='dev',
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
            'phonish': ['uid_by_phone'],
        }))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args['track_id'] = self.track_id

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

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
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)

    def test_lastauth_is_old_but_have_device_id(self):
        self.http_query_args['use_device_id'] = True

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([
                dict(
                    self.base_phone_binding,
                    number=TEST_PHONE_NUMBER.e164,
                    phone_id=TEST_PHONE_ID1,
                    uid=TEST_UID,
                ),
            ]),
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
                uids=[TEST_UID],
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=5)),
                ),
            ],
        )
        self.env.blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(tokens=[dict(device_id=TEST_DEVICE_INFO['device_id'])]),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_id = TEST_DEVICE_INFO['device_id']
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)

    def test_lastauth_is_old_but_account_is_whitelisted(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([
                dict(
                    self.base_phone_binding,
                    number=TEST_PHONE_NUMBER.e164,
                    phone_id=TEST_PHONE_ID1,
                    uid=TEST_UID,
                ),
            ]),
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
                uids=[TEST_UID],
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=5)),
                ),
            ],
        )
        self.env.blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(tokens=[]),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        with settings_context(
            RECENT_ACCOUNT_USAGE_PERIOD=timedelta(minutes=1),
            IGNORE_POSSIBLE_PHONE_OWNER_CHANGE_FOR_UIDS=[TEST_UID],
        ):
            rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)

    def test_no_accounts_for_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.not_found'])

    def test_account_disabled(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

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

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])

    def test_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False

        rv = self.make_request()

        self.assert_error_response(rv, ['user.not_verified'])

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

        with self.track_transaction() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = user_entered_phone_number.e164

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)

        self.env.blackbox.requests[0].assert_query_equals(
            dict(
                format='json',
                method='phone_bindings',
                numbers=','.join([user_entered_phone_number.e164, account_phone_number.e164]),
                type='current',
            ),
        )

    def test_invalid_phone(self):
        with self.track_transaction() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = 'invalid phone'

        rv = self.make_request()

        self.assert_error_response(rv, ['account.not_found'])
