import pytest

from test_taxi_antifraud.utils import utils


@pytest.mark.parametrize(
    'params',
    [
        ({'order_id': 'not_existing_value'}),
        ({'phone_id': 'not_existing_value'}),
        ({'personal_phone_id': 'not_existing_value'}),
    ],
)
async def test_get_antifake_triggering_no_data(web_app_client, params):
    response = await web_app_client.get(
        '/v1/get_antifake_triggering_list', params=params,
    )
    assert response.status == 200

    assert await response.json() == []


@pytest.mark.parametrize(
    'params',
    [
        ({}),
        ({'phone_id': 'some_value', 'order_id': 'some_value'}),
        ({'order_id': 'some_value', 'personal_phone_id': 'some_value'}),
        (
            {
                'order_id': 'some_value',
                'personal_phone_id': 'some_value',
                'phone_id': 'some_value',
            }
        ),
    ],
)
async def test_get_antifake_triggering_bad_request(web_app_client, params):
    response = await web_app_client.get(
        '/v1/get_antifake_triggering_list', params=params,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'params,expected',
    [
        (
            {'phone_id': 'some_phone_id'},
            [
                {
                    'order_id': 'some_order',
                    'device_id': 'some_device',
                    'user_id': 'some_user',
                    'personal_phone_id': 'some_personal',
                    'triggered_rules': ['some_rule', 'another_rule'],
                    'triggering_time': '2019-12-20T09:05:39.000Z',
                    'phone_id': 'some_phone_id',
                },
            ],
        ),
        (
            {'order_id': 'some_order'},
            [
                {
                    'order_id': 'some_order',
                    'device_id': 'some_device',
                    'user_id': 'some_user',
                    'personal_phone_id': 'some_personal',
                    'triggered_rules': ['some_rule', 'another_rule'],
                    'triggering_time': '2019-12-20T09:05:39.000Z',
                    'phone_id': 'some_phone_id',
                },
            ],
        ),
        (
            {'personal_phone_id': 'some_personal'},
            [
                {
                    'order_id': 'some_order',
                    'device_id': 'some_device',
                    'user_id': 'some_user',
                    'personal_phone_id': 'some_personal',
                    'triggered_rules': ['some_rule', 'another_rule'],
                    'triggering_time': '2019-12-20T09:05:39.000Z',
                    'phone_id': 'some_phone_id',
                },
                {
                    'order_id': 'some_order1',
                    'device_id': 'some_device1',
                    'metrica_device_id': 'metrica_id',
                    'user_id': 'some_user1',
                    'personal_phone_id': 'some_personal',
                    'triggered_rules': ['some_rule1'],
                    'triggering_time': '2019-12-21T09:05:39.000Z',
                    'phone_id': 'some_phone_id1',
                    'orders_total': 45,
                    'orders_complete': 0,
                },
            ],
        ),
    ],
)
async def test_get_antifake_triggering_base(web_app_client, params, expected):
    response = await web_app_client.get(
        '/v1/get_antifake_triggering_list', params=params,
    )
    assert response.status == 200

    result = utils.convert_datetimes(
        await response.json(), ['triggering_time'],
    )
    expected = utils.convert_datetimes(expected, ['triggering_time'])

    assert result == expected
