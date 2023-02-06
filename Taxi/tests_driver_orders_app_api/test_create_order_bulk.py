import json

import pytest

import tests_driver_orders_app_api.redis_helpers as rh

CHAIN = {
    'destination': [39.207141, 51.662082],
    'left_time': 99,
    'left_dist': 500,
    'order_id': 'f3ae2a04966035119c3ea83c8d0197ae',
}


@pytest.mark.parametrize(
    'params',
    [
        {
            'park_id': 'park_id',
            'session': 'test_session',
            'driver_profile_id': 'driver_profile_id',
            'alias_id': 'alias_id',
        },
    ],
)
@pytest.mark.parametrize('send_force_polling_over_stq', [False, True])
@pytest.mark.parametrize('taximeter_platform', ['ios', 'android'])
@pytest.mark.parametrize('chain', [None, CHAIN])
async def test_create_order_bulk(
        taxi_driver_orders_app_api,
        driver_profiles,
        driver_orders_builder,
        redis_store,
        params,
        send_force_polling_over_stq,
        taxi_config,
        client_notify,
        stq,
        taximeter_platform,
        chain,
):
    taxi_config.set_values(
        {
            'DRIVER_ORDERS_APP_API_SEND_COMMUNICATIONS_SETTINGS': {
                'send_force_polling_order_over_stq': (
                    send_force_polling_over_stq
                ),
            },
        },
    )

    setcar_bulk_resp = {
        'setcars': [
            {
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'setcar': {'setcar_key': 'setcar_data'},
                'setcar_push': {'setcar_push_key': 'setcar_push_data'},
            },
        ],
    }

    if chain is not None:
        setcar_bulk_resp['setcars'][0]['setcar']['chain'] = chain

    driver_orders_builder.set_v2_setcar_bulk_resp(setcar_bulk_resp)
    driver_profiles.set_platform(taximeter_platform)

    response = await taxi_driver_orders_app_api.post(
        '/internal/v1/order/create_bulk',
        headers={'Content-type': 'application/json'},
        params=params,
        data=json.dumps(
            {
                'order_id': 'order_id',
                'drivers': [
                    {
                        'park_id': params['park_id'],
                        'driver_profile_id': params['driver_profile_id'],
                        'alias_id': params['alias_id'],
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200

    rh.check_order_setcar_items(
        redis_store, params['park_id'], params['alias_id'],
    )
    rh.check_setcar_driver_reserv(
        redis_store,
        params['park_id'],
        params['driver_profile_id'],
        params['alias_id'],
    )

    assert client_notify.times_called == 0
    assert (
        stq.driver_orders_send_communications_notifications.times_called == 1
    )

    kwargs = stq.driver_orders_send_communications_notifications.next_call()[
        'kwargs'
    ]

    if taximeter_platform == 'ios':
        assert [
            'action',
            'code',
            'collapse_key',
            'data',
            'driver_id',
            'log_extra',
            'order_id',
            'park_id',
            'platform',
        ] == sorted(kwargs.keys())
        assert kwargs['platform'] == 'ios'
        if chain is None:
            assert kwargs['action'] == 'OrderSetCarRequest'
        else:
            assert kwargs['action'] == 'OrderSetCarChain'
        assert kwargs['data'] == {'setcar_push_key': 'setcar_push_data'}
    else:
        assert [
            'action',
            'code',
            'collapse_key',
            'driver_id',
            'log_extra',
            'order_id',
            'park_id',
            'platform',
        ] == sorted(kwargs.keys())
        assert kwargs['platform'] == 'android'
        assert kwargs['action'] == 'ForcePollingOrder'
