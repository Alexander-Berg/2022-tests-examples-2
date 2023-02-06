import datetime

import pytest

from tests_contractor_balances import utils

ENDPOINT_URL = '/internal/v1/balance-limit-updated-trigger'

CONTRACTOR_PROFILE_ID = 'driver1'
UPDATED_AT = '2021-09-29T11:18:01+00:00'

DRIVER_BALANCE_ONLYCARD_ON_KEY = 'DriverBalance_OnlyCard_On'
DRIVER_BALANCE_ONLYCARD_OFF_KEY = 'DriverBalance_OnlyCard_Off'

UPDATE_PARAMS = [
    # old limit enabled, new limit enabled, balance between limits,
    # limit decreased
    # > alert send
    ('park1', '3', '1', '2', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY, True),
    # old limit enabled, new limit enabled, balance between limits,
    # limit increased
    # > alert send
    ('park1', '1', '3', '2', 'ru', DRIVER_BALANCE_ONLYCARD_ON_KEY, True),
    # old limit enabled, new limit enabled, balance above limits,
    # limit decreased
    # > alert not send
    ('park1', '2', '1', '2', 'ru', None, True),
    # old limit enabled, new limit enabled, balance above limits,
    # limit increased
    # > alert not send
    ('park1', '2', '1', '2', 'ru', None, True),
    # old limit enabled, new limit enabled, balance below limits,
    # limit decreased
    # > alert not send
    ('park1', '3', '1.99999', '1', 'ru', None, True),
    # old limit enabled, new limit enabled, balance below limits,
    # limit increased
    # > alert not send
    ('park1', '2', '3', '1.9999', 'ru', None, True),
    # old limit DISABLED, new limit enabled, balance between limits,
    # limit decreased
    # > alert not send
    ('park1', '0.00004', '-1.99999', '-1', 'ru', None, True),
    # old limit DISABLED, new limit enabled, balance between limits,
    # limit increased
    # > alert send
    ('park1', '0', '2', '1', 'ru', DRIVER_BALANCE_ONLYCARD_ON_KEY, True),
    # old limit DISABLED, new limit enabled, balance below limits,
    # limit decreased
    # > alert send
    ('park1', '0', '-1', '-2', 'ru', DRIVER_BALANCE_ONLYCARD_ON_KEY, True),
    # old limit DISABLED, new limit enabled, balance below limits,
    # limit increased
    # > alert send
    ('park1', '0', '1', '-2', 'ru', DRIVER_BALANCE_ONLYCARD_ON_KEY, True),
    # old limit DISABLED, new limit enabled, balance above limits,
    # limit decreased
    # > alert not send
    ('park1', '0.00004', '-1', '0', 'ru', None, True),
    # old limit DISABLED, new limit enabled, balance above limits,
    # limit increased
    # > alert not send
    ('park1', '0', '1', '2', 'ru', None, True),
    # old limit enabled, new limit DISABLED, balance between limits,
    # limit decreased
    # > alert send
    ('park1', '2', '0', '1', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY, True),
    # old limit enabled, new limit DISABLED, balance between limits,
    # limit increased
    # > alert not send
    ('park1', '-2', '0.00004', '-1', 'ru', None, True),
    # old limit enabled, new limit DISABLED, balance above limits,
    # limit decreased
    # > alert not send
    ('park1', '1', '0.', '2', 'ru', None, True),
    # old limit enabled, new limit DISABLED, balance above limits,
    # limit increased
    # > alert not send
    ('park1', '-1', '0', '0', 'ru', None, True),
    # old limit enabled, new limit DISABLED, balance below limits,
    # limit decreased
    # > alert send
    ('park1', '1', '0', '-2', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY, True),
    # old limit enabled, new limit DISABLED, balance below limits,
    # limit increased
    # > alert send
    ('park1', '-1', '0', '-2', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY, True),
    # old limit DISABLED, new limit DISABLED
    # > alert send
    ('park1', '0', '0', '0.99999', 'ru', None, True),
    # park_locale 'en'
    ('park2', '1', '-1', '0.1', 'en', DRIVER_BALANCE_ONLYCARD_OFF_KEY, True),
    # notification disabled by config
    ('park2', '1', '-1', '0.1', 'en', None, False),
]


def _convert_format(date):
    return datetime.datetime.fromisoformat(date).strftime(
        '%Y-%m-%dT%H:%M:%S%z',
    )


def _make_request(park_id, old_balance_limit, new_balance_limit):
    return {
        'park_id': park_id,
        'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        'balance_limit_updated_at': UPDATED_AT,
        'old_balance_limit': old_balance_limit,
        'new_balance_limit': new_balance_limit,
    }


def _make_driver_balance_request(park_id):
    return {
        'query': {
            'park': {
                'id': park_id,
                'driver_profile': {'ids': [CONTRACTOR_PROFILE_ID]},
            },
            'balance': {'accrued_ats': [UPDATED_AT]},
        },
    }


def _make_driver_balance_response(balance):
    return {
        'driver_profiles': [
            {
                'driver_profile_id': CONTRACTOR_PROFILE_ID,
                'balances': [
                    {'accrued_at': UPDATED_AT, 'total_balance': balance},
                ],
            },
        ],
    }


@pytest.mark.parametrize(
    (
        'park_id',
        'old_balance_limit',
        'new_balance_limit',
        'balance',
        'park_locale',
        'notification_key',
        'notification_enabled',
    ),
    UPDATE_PARAMS,
)
async def test_success(
        taxi_config,
        taxi_contractor_balances,
        mockserver,
        client_notify_v2_push_context,
        mock_client_notify_v2_push,
        mock_fleet_parks_list,
        park_id,
        balance,
        old_balance_limit,
        new_balance_limit,
        park_locale,
        notification_key,
        notification_enabled,
):

    taxi_config.set(
        CONTRACTOR_BALANCES_CROSS_LIMIT_NOTIFICATION_ENABLED=(
            notification_enabled
        ),
    )

    push_id = utils.make_sha1(
        f'{park_id}{CONTRACTOR_PROFILE_ID}{_convert_format(UPDATED_AT)}',
    )
    client_notify_v2_push_context.set_data(
        park_id=park_id,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageNew',
        collapse_key=f'Alert:{push_id}',
        locale=park_locale,
        message_id=push_id,
        notification={
            'text': {
                'keyset': 'taximeter_backend_driver_messages',
                'key': notification_key,
            },
        },
        data={'id': push_id},
    )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _driver_balance(request):
        assert request.json == _make_driver_balance_request(park_id)
        return _make_driver_balance_response(balance)

    response = await taxi_contractor_balances.post(
        ENDPOINT_URL,
        json=_make_request(park_id, old_balance_limit, new_balance_limit),
    )

    assert _driver_balance.has_calls
    assert mock_client_notify_v2_push.has_calls == (
        notification_key is not None
    )
    assert response.status_code == 200


@pytest.mark.parametrize('notification_response_status', [400, 500])
async def test_notification_fail(
        taxi_contractor_balances,
        mockserver,
        mock_fleet_parks_list,
        notification_response_status,
):
    park_id = 'park2'

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _driver_balance(request):
        assert request.json == _make_driver_balance_request(park_id)
        return _make_driver_balance_response('0.1')

    @mockserver.json_handler('/client-notify/v2/push')
    def _driver_notification_push(request):
        return mockserver.make_response(status=notification_response_status)

    response = await taxi_contractor_balances.post(
        ENDPOINT_URL, json=_make_request(park_id, '1', '-1'),
    )
    assert _driver_balance.has_calls
    assert _driver_notification_push.has_calls
    assert response.status_code == 500


@pytest.mark.parametrize(
    ('driver_balance_response_status', 'driver_balance_response_body'),
    [
        (
            200,
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': (
                            '6d4a58cc4140f649fd428d639beb6825'
                        ),
                        'balances': [
                            {
                                'accrued_at': '2021-09-29T08:18:01+00:00',
                                'total_balance': '123',
                            },
                            {
                                'accrued_at': '2021-09-29T08:18:01+00:00',
                                'total_balance': '123',
                            },
                        ],
                    },
                ],
            },
        ),
        (400, None),
        (500, None),
    ],
)
async def test_driver_balance_request_fail(
        taxi_contractor_balances,
        mockserver,
        driver_balance_response_status,
        driver_balance_response_body,
):
    park_id = 'park1'

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _driver_balance(request):
        assert request.json == _make_driver_balance_request(park_id)
        return mockserver.make_response(
            status=driver_balance_response_status,
            json=driver_balance_response_body,
        )

    response = await taxi_contractor_balances.post(
        ENDPOINT_URL, json=_make_request(park_id, '1', '-1'),
    )

    assert _driver_balance.has_calls
    assert response.status_code == 500


@pytest.mark.parametrize('enabled', [True, False])
async def test_push_auto_locale_enabled_config(
        mockserver,
        taxi_contractor_balances,
        mock_parks_list,
        parks_list_context,
        mock_park_payment_methods,
        mock_client_notify_v2_push,
        client_notify_v2_push_context,
        stq_runner,
        taxi_config,
        enabled,
):
    taxi_config.set(CONTRACTOR_BALANCES_PUSH_AUTO_LOCALE_ENABLED=enabled)

    park_id = 'park1'
    park_locale = 'ru'
    parks_list_context.set_data(locale=park_locale)

    push_id = utils.make_sha1(
        f'park1{CONTRACTOR_PROFILE_ID}{_convert_format(UPDATED_AT)}',
    )
    client_notify_v2_push_context.set_data(
        park_id=park_id,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageNew',
        collapse_key=f'Alert:{push_id}',
        locale=(None if enabled else park_locale),
        message_id=push_id,
        notification={
            'text': {
                'keyset': 'taximeter_backend_driver_messages',
                'key': 'DriverBalance_OnlyCard_On',
            },
        },
        data={'id': push_id},
    )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _driver_balance(request):
        assert request.json == _make_driver_balance_request(park_id)
        return _make_driver_balance_response('5')

    response = await taxi_contractor_balances.post(
        ENDPOINT_URL, json=_make_request(park_id, '0', '10'),
    )
    assert response.status_code == 200
    assert _driver_balance.has_calls
    assert mock_client_notify_v2_push.has_calls
