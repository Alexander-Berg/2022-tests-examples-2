import pytest

from tests_coupons import util
from tests_coupons.referral import util as referral_util

USER_ID = 'test_user_id'
USER_YANDEX_UID = 'test_yandex_uid'

TAXI_TASK_KWARGS = {
    'promocode': 'basic_ok_code',
    'referral_promocode': 'basic_ok_referral',
    'yandex_uid': USER_YANDEX_UID,
    'idempotence_token': 'test_token',
}
GROCERY_TASK_KWARGS = {
    'promocode': 'basic_ok_code',
    'referral_promocode': 'grocery_ok_referral',
    'yandex_uid': USER_YANDEX_UID,
    'idempotence_token': 'test_token',
}

DEFAULT_APPLICATION = 'default_app'
DEFAULT_PHONE_ID = 'test_phone_id'
DEFAULT_GROCERY_APPLICATION = 'lavka_android'
DEFAULT_BRAND = 'default_brand'
DEFAULT_SETTINGS_CONFIG = {
    'enabled_for_applications': [DEFAULT_APPLICATION],
    'max_retries': 10,
}
DEFAULT_APP_BRAND_CONFIG = {DEFAULT_APPLICATION: DEFAULT_BRAND}

TAXI_DEFAULT_PUSH_MESSAGE = 'Taxi default reward message'
GROCERY_DEFAULT_PUSH_MESSAGE = 'Grocery default reward message'

TAXI_PUSH_MESSAGE = 'Taxi RUS reward message'
GROCERY_PUSH_MESSAGE = 'Grocery RUS reward message'

TAXI_INTENT = 'taxi_referral_reward'
GROCERY_INTENT = 'grocery_referral_reward'


def get_ucommunications_push_body(push_message, intent=TAXI_INTENT):
    return {
        'intent': intent,
        'data': {
            'payload': {},
            'repack': {
                'apns': {
                    'aps': {'alert': push_message, 'content-available': 1},
                },
                'fcm': {'notification': {'title': push_message}},
                'hms': {'notification_title': push_message},
                'mpns': {'toast': {'text1': push_message}},
                'wns': {'toast': {'text1': push_message}},
            },
        },
        'user': USER_ID,
    }


def get_created_date(day=20, month=9, year=2020):
    day = f'{day}' if day > 9 else f'0{day}'
    month = f'{month}' if month > 9 else f'0{month}'
    return f'{year}-{month}-{day}T12:00:00.000+0000'


def get_users_search_response_item(
        user_id,
        created=get_created_date(),
        application=DEFAULT_APPLICATION,
        phone_id=DEFAULT_PHONE_ID,
):
    return {
        'id': user_id,
        'created': created,
        'application': application,
        'phone_id': phone_id,
    }


DEFAULT_USERS_SEARCH_RESPONSE = [get_users_search_response_item(USER_ID)]


@pytest.fixture(name='task_client_mocks')
def _task_client_mocks(mockserver):
    # pylint: disable=protected-access
    # We need protected-access to use _vaiables_staring_with_underscore
    # in the @mockserver mock functions

    class Context:
        # /ucommunications/user/notification/push
        user_notification_push = None
        _expected_idempotence_token = None
        _expected_push_body = None
        _expected_user_id = None

        # C0103 = invalid-name (name is too long)
        def set_user_notification_push_expectations(  # pylint: disable=C0103
                self, user_id=None, token=None, push_body=None,
        ):
            self._expected_user_id = user_id
            self._expected_idempotence_token = token
            self._expected_push_body = push_body

        # /user-api/users/search
        users_search = None
        _users_search_response = None
        _expected_yandex_uid = None

        # /internal/communications/v1/referral-reward-notify
        referral_reward_push = None
        _expected_application = None
        _expected_locale = None
        _expected_country = None

        def set_users_search_expectations(self, yandex_uid=None):
            self._expected_yandex_uid = yandex_uid

        def set_users_search_response(self, response):
            self._users_search_response = {'items': response}

        def set_grocery_expectations(
                self,
                yandex_uid=None,
                taxi_user_id=None,
                application=None,
                locale=None,
                country=None,
                idempotency_token=None,
        ):
            self._expected_yandex_uid = yandex_uid
            self._expected_user_id = taxi_user_id
            self._expected_application = application
            self._expected_locale = locale
            self._expected_country = country
            self._expected_idempotence_token = idempotency_token

    context = Context()

    @mockserver.json_handler('/user-api/users/search')
    def _user_api_users_search_mock(request):
        if context._expected_yandex_uid is not None:
            assert request.json['yandex_uid'] == context._expected_yandex_uid
        return context._users_search_response

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _user_notification_push_mock(request):
        if context._expected_user_id is not None:
            assert request.json['user'] == context._expected_user_id
        if context._expected_idempotence_token is not None:
            assert (
                request.headers['X-Idempotency-Token']
                == context._expected_idempotence_token
            )
        if context._expected_push_body is not None:
            assert (
                util.sort_json(request.json, {'data.repack'})
                == context._expected_push_body
            )
        return {}

    @mockserver.json_handler(
        '/grocery-communications/internal/communications/v1/'
        'referral-reward-notify',
    )
    def _referral_reward_notify(request):
        if context._expected_yandex_uid is not None:
            assert request.json['yandex_uid'] == context._expected_yandex_uid
        if context._expected_user_id is not None:
            assert request.json['taxi_user_id'] == context._expected_user_id
        if context._expected_application is not None:
            assert request.json['application'] == context._expected_application
        if context._expected_locale is not None:
            assert request.json['locale'] == context._expected_locale
        if context._expected_country is not None:
            assert request.json['country'] == context._expected_country
        if context._expected_idempotence_token is not None:
            assert (
                request.json['idempotency_token']
                == context._expected_idempotence_token
            )
        return {}

    context.user_notification_push = _user_notification_push_mock
    context.users_search = _user_api_users_search_mock
    context.referral_reward_push = _referral_reward_notify

    return context


@pytest.mark.config(
    COUPONS_REFERRAL_REWARD_NOTIFY_SETTINGS={
        'enabled_for_applications': [
            DEFAULT_APPLICATION,
            DEFAULT_GROCERY_APPLICATION,
        ],
        'max_retries': 10,
    },
    APPLICATION_MAP_BRAND={
        '__default__': DEFAULT_BRAND,
        DEFAULT_APPLICATION: DEFAULT_BRAND,
    },
)
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME, files=['pg_user_referrals.sql'],
)
@pytest.mark.parametrize(
    'task_kwargs, push_message, intent, exp_filename, service',
    [
        pytest.param(
            TAXI_TASK_KWARGS,
            TAXI_PUSH_MESSAGE,
            TAXI_INTENT,
            'coupons_tanker_key_for_referral_reward_message.json',
            'taxi',
        ),
        pytest.param(
            GROCERY_TASK_KWARGS,
            GROCERY_PUSH_MESSAGE,
            GROCERY_INTENT,
            'coupons_tanker_key_for_referral_reward_message.json',
            'grocery',
        ),
        pytest.param(
            TAXI_TASK_KWARGS,
            TAXI_DEFAULT_PUSH_MESSAGE,
            TAXI_INTENT,
            None,
            'taxi',
        ),
        pytest.param(
            GROCERY_TASK_KWARGS,
            GROCERY_DEFAULT_PUSH_MESSAGE,
            GROCERY_INTENT,
            None,
            'grocery',
        ),
    ],
)
async def test_ok(
        experiments3,
        load_json,
        stq_runner,
        task_client_mocks,
        task_kwargs,
        push_message,
        intent,
        exp_filename,
        service,
):
    task_client_mocks.set_users_search_expectations(yandex_uid=USER_YANDEX_UID)

    task_client_mocks.set_users_search_response(
        [get_users_search_response_item(USER_ID)],
    )
    if service == 'taxi':
        task_client_mocks.set_user_notification_push_expectations(
            user_id=USER_ID,
            token=task_kwargs['idempotence_token'],
            push_body=get_ucommunications_push_body(push_message, intent),
        )
        task_client_mocks.set_users_search_response(
            DEFAULT_USERS_SEARCH_RESPONSE,
        )
    elif service == 'grocery':
        task_client_mocks.set_users_search_response(
            [
                get_users_search_response_item(
                    USER_ID, application=DEFAULT_GROCERY_APPLICATION,
                ),
            ],
        )
        task_client_mocks.set_grocery_expectations(
            yandex_uid=USER_YANDEX_UID,
            taxi_user_id=USER_ID,
            application=DEFAULT_GROCERY_APPLICATION,
            locale='ru',
            country='rus',
            idempotency_token=task_kwargs['idempotence_token'],
        )

    if exp_filename:
        experiments3.add_experiments_json(load_json(exp_filename))

    await stq_runner.referral_reward_notify.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    assert task_client_mocks.users_search.times_called == 1

    if service == 'taxi':
        assert task_client_mocks.user_notification_push.times_called == 1
        assert task_client_mocks.referral_reward_push.times_called == 0
    if service == 'grocery':
        assert task_client_mocks.user_notification_push.times_called == 0
        assert task_client_mocks.referral_reward_push.times_called == 1


@pytest.mark.config(
    COUPONS_REFERRAL_REWARD_NOTIFY_SETTINGS=DEFAULT_SETTINGS_CONFIG,
    APPLICATION_MAP_BRAND=DEFAULT_APP_BRAND_CONFIG,
)
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME, files=['pg_user_referrals.sql'],
)
@pytest.mark.parametrize(
    'task_kwargs_overrides,user_application',
    [
        pytest.param(
            {'referral_promocode': 'bad'},
            DEFAULT_APPLICATION,
            id='Promocode is not in db',
        ),
        pytest.param(
            {'referral_promocode': 'bad_country_referral'},
            DEFAULT_APPLICATION,
            id='Country does not exist',
        ),
        pytest.param(
            {},
            DEFAULT_APPLICATION,
            marks=pytest.mark.config(
                COUPONS_REFERRAL_REWARD_NOTIFY_SETTINGS={
                    'enabled_for_applications': [],
                    'max_retries': 10,
                },
            ),
            id='Task is not enabled for application',
        ),
        pytest.param(
            {},
            DEFAULT_APPLICATION,
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={DEFAULT_APPLICATION: 'some_brand'},
            ),
            id='Task user app brand != promocode brand',
        ),
        pytest.param({}, None, id='User has no application'),
    ],
)
async def test_no_ucommunications_call(
        stq_runner, task_client_mocks, task_kwargs_overrides, user_application,
):
    task_kwargs = {**TAXI_TASK_KWARGS, **task_kwargs_overrides}

    task_client_mocks.set_users_search_expectations(yandex_uid=USER_YANDEX_UID)
    task_client_mocks.set_users_search_response(
        [
            get_users_search_response_item(
                USER_ID, application=user_application,
            ),
        ],
    )

    await stq_runner.referral_reward_notify.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    assert task_client_mocks.user_notification_push.times_called == 0


@pytest.mark.config(
    COUPONS_REFERRAL_REWARD_NOTIFY_SETTINGS=DEFAULT_SETTINGS_CONFIG,
    APPLICATION_MAP_BRAND=DEFAULT_APP_BRAND_CONFIG,
)
@pytest.mark.experiments3(
    filename='coupons_tanker_key_for_referral_reward_message.json',
)
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME, files=['pg_user_referrals.sql'],
)
@pytest.mark.parametrize(
    'users_search_response,expected_user_id',
    [
        pytest.param([], None, id='Empty response'),
        pytest.param(
            [
                get_users_search_response_item(
                    'wrong_id', created=get_created_date(day=10),
                ),
                get_users_search_response_item(
                    USER_ID, created=get_created_date(day=20),
                ),
            ],
            USER_ID,
            id='Newest user doc is used',
        ),
        pytest.param(
            [
                get_users_search_response_item(
                    'wrong_id', application='wrong_app',
                ),
                get_users_search_response_item(
                    USER_ID, application=DEFAULT_APPLICATION,
                ),
            ],
            USER_ID,
            id='Correct brand user doc is used',
        ),
    ],
)
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_users_search(
        stq_runner, task_client_mocks, users_search_response, expected_user_id,
):
    task_kwargs = TAXI_TASK_KWARGS

    task_client_mocks.set_user_notification_push_expectations(
        user_id=expected_user_id,
        token=task_kwargs['idempotence_token'],
        push_body=get_ucommunications_push_body(TAXI_PUSH_MESSAGE),
    )
    task_client_mocks.set_users_search_expectations(yandex_uid=USER_YANDEX_UID)
    task_client_mocks.set_users_search_response(users_search_response)

    await stq_runner.referral_reward_notify.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    assert task_client_mocks.users_search.times_called == 1
    assert (
        task_client_mocks.user_notification_push.times_called == 0
        if expected_user_id is None
        else 1
    )
